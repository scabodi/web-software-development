from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse
from django.contrib.sites.models import Site

from django.views.decorators.csrf import requires_csrf_token

from hashlib import md5
from urllib.parse import urlencode

from datetime import date
import calendar
from calendar import HTMLCalendar
from .models import Game, Transaction, GameSession, GamePurchase
from accounts.models import Profile
from .forms import GameForm, PaymentForm
import json

from django.contrib.auth.decorators import login_required
from accounts.decorators import player_required, developer_required


def all_games(request):
    """
    Views that retrieves all the games available for purchase on the website
    """
    all_games = Game.objects.all()
    return render(request,"allgames.html", {"games" : all_games})

def categories_view(request):
    """
    View that retrieves all the categories available in the website
    """
    choices = Game._meta.get_field('category').choices
    return render(request,"categories.html", {"categories" : choices})

def one_category_view(request, c):
    """
    View that retrieves all the games available with the specified category
    """
    games = Game.objects.filter(category__iexact=c)
    return render(request,"one_category.html", {"games" : games})

def search_results_view(request):
    """
    View that retrieves all the games matching the search query.
    """
    query = request.GET.get('q','')
    results = []
    if query:
        results = Game.objects.filter(name__contains=query).distinct()

    return render(request, 'search.html', {'results':results, 'query':query})


@login_required
@developer_required
def add_game(request):
    """
    View that allows a logged in DEVELOPER to fill the form to create and add to
    the website a new game.
    """
    submitted = False
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
          form.save()
          return HttpResponseRedirect('/addgame/?submitted=True')
    else:
        form = GameForm(initial={'developer': Profile.objects.get(user_id=request.user.id)})
        if 'submitted' in request.GET:
          submitted = True
        return render(request, 'addgame.html', {'form': form, 'submitted': submitted})

@login_required
@developer_required
def modify_game(request, game_id):
    """
    View that allows a logged in DEVELOPER that owns the specific game to
    modify it through a game form.
    """
    try:
        game = Game.objects.get(id=game_id)
    except:
        return HttpResponse("Game not found", status=404)

    redirect_url, button = "", ""

    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():#
            form = GameForm(request.POST, instance = game)
            form.save()

            redirect_url = "http://"+str(request.get_host())+"/allgames"
    else:

        json = {
            "name": game.name,
            "category": game.category,
            "description": game.description,
            "price": game.price,
            "url": game.url,
            "developer": game.developer,
        }
        form = GameForm(initial=json)
        button = "modify"

    return render(request, 'game_modified.html', {'form': form,'game': game,
                'redirect_url': redirect_url, "button": button})

@login_required
@developer_required
def remove_game(request, game_id):
    """
    View that allows a logged in DEVELOPER that owns the specific game to
    remove it from the website.
    """
    try:
        game = Game.objects.get(id=game_id)
    except:
        return HttpResponse("Game not found", status=404)
    game.delete()
    redirect_url = "http://"+str(request.get_host())+"/"

    return render(request, 'game_removed.html', {'game': game,
                'redirect_url': redirect_url})

def game_description(request, game_id):
    """
    View that allow any user to see the information about a specific game (game_id).
    If the user is logged in and it's a PLAYER this view allows him/her
    to buy the game and after the successful purchase to play it (redirects to game_view in the template)
    If the user is logged in and it's the DEVELOPER that owns the specified game,
    this view allows him/her to press the buttons that redirects him/her to the
    views for the modification and removal of it.
    """

    try:
        game = Game.objects.get(id=game_id)
    except:
        return HttpResponse("Game not found", status=404)
    # information for the payment form
    sid = "cbkbcXdzZF9wcm9qZWN0"
    t = Transaction(amount=game.price, game=game)
    t.save()
    pid = "p"+str(t.id)
    secret = "Yqt-BO5TRqVh2mVRbWpzzug71g4A"
    checksumstr = "pid=%s&sid=%s&amount=%.2f&token=%s" % (pid, sid, game.price, secret)
    checksum = md5(checksumstr.encode('utf-8')).hexdigest()

    current_site = Site.objects.all()[0]
    url = "http://" + current_site.domain + "/payment_result"

    json = {
        "pid": pid,
        "sid":sid,
        "amount": game.price,
        "token": secret,
        "checksum": checksum,
        "success_url": url,
        "cancel_url": url,
        "error_url": url,
        "name": game.name,
        "category": game.category,
        "description": game.description,
        "price": game.price,
    }
    form = PaymentForm(initial=json)

    #if request.user.profile.is_player or game.developer != request.user.profile:
    form.fields['name'].widget.attrs['readonly'] = True
    form.fields['category'].widget.attrs['disabled'] = True
    form.fields['description'].widget.attrs['readonly'] = True
    form.fields['price'].widget.attrs['readonly'] = True

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()

    # depending on the type of user logged in and if he/she ows the game
    # display different buttons to allow different actions
    button = "not"
    if request.user.is_authenticated:
        if request.user.profile.is_player:
            # see if it already has the current game
            player = Profile.objects.get(user_id=request.user.id)
            purchased_games = get_games_for_player(player)
            if game in purchased_games:
                button = "play"
            else:
                button = "buy"
        elif request.user.profile.is_developer and game.developer == request.user.profile:
            developer = Profile.objects.get(user_id=request.user.id)
            if game.developer == developer:
                button = "developer"

    return render(request,"game_description.html",  {"form": form, "game":game, "button": button})

@login_required
@player_required
def payment_result(request):
    """
    View that handles the result of the payment from the mockup website.
    It saves the Transaction if the status is SUCCESS, otherwise it delets it.
    """

    pid = request.GET.get('pid', None)
    rid = request.GET.get('ref', None)
    status = request.GET.get('result', None)

    id = int(pid[1:])
    try:
        t = Transaction.objects.get(id = id)
    except:
        if status == 'cancel':
            return render(request, "payment_result.html", {"pid" : pid,
                "rid": rid, "status" : "cancel"})
        else:
            return render(request, "payment_result.html", {"pid" : pid,
                "rid": rid, "status" : "error"})

    if status == "success" and t.status != "success":
        t.status = status
        t.save()
        # add game to player
        game = t.game
        try:
            player = Profile.objects.get(user_id=request.user.id)
        except:
            return HttpResponse("Player not found", status=404)
        purchased_game = GamePurchase(game=game, player=player)
        purchased_game.save()
        player.save()
    elif status != "success" and t.status == "success":
        # it means that the user has gone back and changed the result
        return render(request, "payment_result.html", {"pid" : pid,
            "rid": rid,
            "status" : "error: you tried to change the result, when the transaction has already been successful"})
    elif status != "success":
        t.delete()

    return render(request, "payment_result.html", {"pid" : pid,
        "rid": rid, "status" :status})


@player_required
def get_games_for_player(player):
    """
    Function that collects all the games of a specified player.
    """
    purchased_games = GamePurchase.objects.filter(player=player)
    result = []
    if purchased_games:
        for purchase in purchased_games:
            result.append(Game.objects.get(id=purchase.game.id))

    return result

@login_required
def my_games_view(request):
    """
    View that allow a logged in user to see his/her profile information. If it's
    a PLAYER this views collects also the information about his/her purchased games.
    If it's a DEVELOPER it redirects to sales_stats view.
    """
    query_set = []
    if request.user.profile.is_developer:
        return redirect(sales_stats)
    elif request.user.profile.is_player:
        if request.user.is_authenticated:
          player = Profile.objects.get(user_id=request.user.id)
          result = get_games_for_player(player)
        return render(request,"mygames.html", {"games" : result})
    else:
        return HttpResponse("Profile type not specified. Please return to the Home page and define it.", status=404)

@login_required
def sales_stats(request):
    """
    View that allow a logged in user to see his/her profile information. If it's
    a DEVELOPER this views collects also the information about his/her
    developed games.
    If it's a PLAYER it redirects to my_games_view view.
    """
    if request.user.profile.is_player:
      return redirect(my_games_view)
    elif request.user.profile.is_developer:
        # display how many games have been bough and when - for developer only
        json, counter = {}, {}
        transactions = Transaction.objects.filter(status='success')
        logged_developer = Profile.objects.get(user_id=request.user.id)

        for t in transactions:
            game = t.game
            developer = game.developer

            if developer == logged_developer:
                # if there is already a list of purchase add the timestamp
                if game in json:
                    counter[game] += 1
                    json[game].append(t.dateTime)
                else:
                    counter[game] = 1
                    json[game] = [t.dateTime]
        all_games = Game.objects.filter(developer=logged_developer)

        return render(request, 'sales_stats.html', {'json':json,
                    'counter':counter, "games": all_games})


@login_required
@player_required
def game_view(request, game_id):
    """
    View that allowas a logged in PLAYER to play the specified game.
    It creates/retrieves the game session and collects both global and personal
    highest scores (just for finished sessions!)
    If the PLAYER does not own the game, it redirects to /allgames/
    """

    try:
        game = Game.objects.get(id=game_id)
    except:
        return HttpResponse("Game not found", status=404)
    try:
        player = Profile.objects.get(user_id=request.user.id)
    except:
        return HttpResponse("Player not found", status=404)
    # if the palyer owns the game then procede
    if GamePurchase.objects.filter(game=game, player=player):
        try:
            session = GameSession.objects.filter(game=game, player=player, status='saved').latest('id')
        except:
            session = GameSession(game=game, player=player)
            session.save()

        best_session = GameSession.objects.filter(game=game, status='finished').order_by('-score').first()
        if best_session:
            game.global_highscore = best_session.score
            game.save()

        personal_scores = GameSession.objects.filter(game=game, player=player, status='finished').order_by('-score')
        top3 = []
        tot = 3
        if personal_scores:
            if len(personal_scores) < tot:
                tot = len(personal_scores)
            for i in range(tot):
                if personal_scores[i]:
                    top3.append(personal_scores[i].score)

        return HttpResponse(render(request,"game_view.html", {"found": True, "game" : game,
                "session": session, "player":player, "top3": top3}), status=200)

    redirect_url = "http://"+str(request.get_host())+"/allgames"
    return HttpResponse(render(request, "game_view.html", {"found": False, "url": redirect_url}), status=200)


@requires_csrf_token
def update_game(request):
    """
    View that handles the interactions with the game through ajax requests.
    """
    if request.is_ajax():
        if request.method == 'POST':
          content = json.loads(request.POST.get('content'))
          session_id = json.loads(request.POST.dict()['sessionid'])
        elif request.method == 'GET':
          content = json.loads(request.GET.get('content'))
          session_id = json.loads(request.GET.dict()['sessionid'])

        session = GameSession.objects.get(id=session_id)

        if content['messageType'] == "SAVE":
          session.state = json.dumps(content['gameState'])
          session.status = "saved"
          session.save()
        elif content['messageType'] == "SCORE":
          score = float(content['score'])
          session.score = round(score,1)
          session.status = "finished"
          session.save()
        elif content['messageType'] == "LOAD_REQUEST":
          state = session.state
          session.status = "saved"
          session.save()
          return HttpResponse(state)

    return HttpResponse(json.dumps({}), content_type="application/json")
