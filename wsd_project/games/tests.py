from django.test import TestCase, Client
from django.urls import reverse
from games.models import Game, GameSession, GamePurchase, Transaction
from accounts.models import Profile, update_profile_signal
from django.contrib.auth.models import User
import random, string, unittest, decimal, json
from hashlib import md5
from urllib.parse import urlencode
from django.test.client import RequestFactory
from games.views import add_game, game_view, sales_stats, modify_game, \
remove_game, game_description, payment_result
from django.db import models
from games.forms import GameForm, PaymentForm
from unittest import skip


class GameTestCase(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        # set up urls
        self.add_game_url = reverse('add_game')
        self.all_games_url = reverse('all_games')
        self.game_view_url = reverse('game_view', args=[1])
        self.description_url = reverse('description', args=[1])
        self.payment_result_url = reverse('payment_result')
        self.my_games_url = reverse('my_games')
        self.sales_stats_url = reverse('sales_stats')
        self.modify_game_url = reverse('modify_game', args=[1])
        self.remove_game_url = reverse('remove_game', args=[1])

        self.factory = RequestFactory()

        self.credentials = {
            'username' : 'sara_d',
            'password' : 'djangotests'
        }
        User.objects.create_user(**self.credentials)

        self.credentials = {
            'username' : 'sara_p',
            'password' : 'djangotests'
        }
        User.objects.create_user(**self.credentials)

        self.developer = Profile.objects.get(user_id=1)
        self.developer.first_name = 'sara_d'
        self.developer.last_name = 'cabodi'
        self.developer.email = 'sara_d@example.com'
        self.developer.is_developer = True
        self.developer.save()

        self.player = Profile.objects.get(user_id=2)
        self.player.first_name = 'sara_p'
        self.player.last_name = 'cabodi'
        self.player.email = 'sara_p@example.com'
        self.player.is_player = True
        self.player.save()

        Game.objects.create(
            name = 'game1',
            developer = self.developer,
            price = 4,
            url = 'https://users.aalto.fi/~oseppala/game/example_game.html',
            description = 'This is a fun game'
        ).save()
        self.game = Game.objects.get(id=1)


    def test_description_url(self):

        response = self.client.get(self.description_url)
        self.assertEqual(response.status_code, 200, "Testing that a request to /description/%d/ succeeded"%(1))
        response = self.client.get('/description/%d/'%(2))
        self.assertEqual(response.status_code, 404, "Testing that a request to /description/%d/ fails"%(2))

    def test_add_game_url(self):

        response = self.client.get(self.add_game_url)
        self.assertEqual(response.status_code, 302, "Testing that a request to /addgame/ redirects to login if user not logged in")

        self.client.login(username=self.player.user.username, password=self.player.user.password)
        request = self.factory.get(self.add_game_url)
        request.user = self.player.user
        response = add_game(request)
        self.assertEqual(response.status_code, 302, "Testing that a request to /addgame/ redirects to login if user is not a developer")

        self.client.login(username=self.developer.user.username, password=self.developer.user.password)
        request = self.factory.get(self.add_game_url)
        request.user = self.developer.user
        response = add_game(request)
        self.assertEqual(response.status_code, 200, "Testing that a request to /addgame/ succeeded if user is a logged developer")

    def test_game_view_url(self):

        response = self.client.get(self.game_view_url)
        self.assertEqual(response.status_code, 302, "Testing that a request to /game/1/ redirects to login if user not logged in")

        self.client.login(username=self.developer.user.username, password=self.developer.user.password)
        request = self.factory.get(self.game_view_url)
        request.user = self.developer.user
        response = game_view(request, game_id=1)
        self.assertEqual(response.status_code, 302, "Testing that a request to /game/1/ redirects to login if user is not a player")

        request = self.factory.get(self.game_view_url)
        request.user = self.player.user
        response = game_view(request, game_id=1)
        self.assertEqual(response.status_code, 200, "Testing that a request to /game/1/ succeeded if user is a logged player")
        response = game_view(request, game_id=2)
        self.assertEqual(response.status_code, 404, "Testing that a request to /game/2/ does not succeeded even if user is a logged player")

    def test_sales_stats_url(self):

        response = self.client.get(self.sales_stats_url)
        self.assertEqual(response.status_code, 302, "Testing that a request to /salesstats/ redirects to login if user not logged in")

        self.client.login(username=self.player.user.username, password=self.player.user.password)
        request = self.factory.get(self.sales_stats_url)
        request.user = self.player.user
        response = sales_stats(request)
        self.assertEqual(response.status_code, 302, "Testing that a request to /salesstats/ redirects to /my_games/ if user is a player")

        self.client.login(username=self.developer.user.username, password=self.developer.user.password)
        request = self.factory.get(self.sales_stats_url)
        request.user = self.developer.user
        response = sales_stats(request)
        self.assertEqual(response.status_code, 200, "Testing that a request to /salesstats/ succeeded if user is a logged developer")

    def _test_field_type(self, model, modelname, fieldname, type):
        try:
            field = model._meta.get_field(fieldname)
            self.assertTrue(isinstance(field, type), "Testing the type of %s field in model %s"%(fieldname, modelname))
        except models.fields.FieldDoesNotExist as e:
            self.assertTrue(False, "Testing if field %s exists in model %s"%(fieldname, modelname))
        return field

    def test_game_name(self):
        name = self._test_field_type(Game, 'Game', 'name', models.CharField)
        self.assertEquals(name.max_length, 30, "Testing the max_length of title field")
        self.assertFalse(name.blank, "Test that is not possible for the name to be blank")

    def test_game_price(self):
        price = self._test_field_type(Game, 'Game', 'price', models.DecimalField)
        self.assertEqual(price.max_digits, 20, "Testing max_digits of price field")
        self.assertEqual(price.decimal_places, 2, "Testing decimal_places of price field")
        self.assertIsInstance(self.game.price, decimal.Decimal, "Testing that game price is recorded correctly")

    def test_game_category(self):
        category = self._test_field_type(Game, 'Game', 'category', models.CharField)
        self.assertEquals(category.max_length, 20, "Testing the max_length of category field")
        self.assertEquals(category.default, 'Action', "Testing that category has default value set to Action")

    def test_game_modify_form(self):
        form_data = {
            'name': self.game.name,
            'category': self.game.category,
            'description': self.game.description,
            'price': self.game.price,
            'url': self.game.url,
            'developer': self.game.developer
        }
        form = GameForm(data=form_data)
        self.assertTrue(form.is_valid())


    def _add_5_games(self):
        for i in range(1, 6):
            Game.objects.create(
                name = 'game%d'%(i),
                developer = self.developer,
                price = i,
                url = 'https://users.aalto.fi/~oseppala/game/example_game.html',
                description = 'This is a fun game'
            ).save()

    def test_all_games_view(self):
        self._add_5_games()
        response = self.client.get(self.all_games_url)
        self.assertEqual(response.status_code, 200, "Testing that a request to /allgames/ succeeded")
        self.assertTemplateUsed(response, 'allgames.html', "Testing that the correct template (allgames.html) was rendered")
        available = response.context['games']
        all = Game.objects.all()
        for g in available:
            self.assertTrue(g in all, "Testing that the included games are correct")

    def test_game_purchase(self):
        # GET request
        self.client.login(username=self.player.user.username, password=self.player.user.password)
        request = self.factory.get(self.description_url)
        request.user = self.player.user
        response = game_description(request, 1)
        self.assertEqual(response.status_code, 200, "Testing that a request to /game_description/1/ succeeded")

        # test_payment_form()
        t = Transaction(amount=self.game.price, game=self.game)
        t.save()
        url = "http://localhost:8000/payment_result.html"
        checksumstr = "pid=%s&sid=%s&amount=%.2f&token=%s" % ("p"+str(t.id),
            "cbkbcXdzZF9wcm9qZWN0", self.game.price,
            "Yqt-BO5TRqVh2mVRbWpzzug71g4A")

        form_data = {
            "pid": "p"+str(t.id),
            "sid": "cbkbcXdzZF9wcm9qZWN0",
            "amount": self.game.price,
            "token": "secret",
            "checksum": md5((checksumstr).encode('utf-8')).hexdigest(),
            "success_url": url,
            "cancel_url": url,
            "error_url": url,
            "name": self.game.name,
            "category": self.game.category,
            "description": self.game.description,
            "price": self.game.price,
        }
        form = PaymentForm(data=form_data)
        request = self.factory.post(self.description_url, form_data)
        request.user = self.player.user
        form = PaymentForm(data=form_data)
        response = game_description(request, 1)
        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, 200, "Testing that a POST request to /game_description/1/ succeded")

    def test_payment_result(self):

        t = Transaction(amount=self.game.price, game=self.game)
        t.save()
        self.client.login(username=self.player.user.username, password=self.player.user.password)
        request = self.factory.get(self.payment_result_url, {'pid': 'p1', 'ref': 'ref', 'result': 'success'})
        request.user = self.player.user
        response = payment_result(request)
        self.assertEqual(response.status_code, 200, "Testing that a request to /payment_result/ succeeded")
        # try the cancel
        self.client.login(username=self.player.user.username, password=self.player.user.password)
        request = self.factory.get(self.payment_result_url, {'pid': 'p1', 'ref': 'ref', 'status': 'cancel'})
        request.user = self.player.user
        response = payment_result(request)
        self.assertEqual(response.status_code, 200, "Testing that a request to /payment_result/ to cancel succeeded")

    def test_modify_game_view(self):
        # simulate GET request
        self.client.login(username=self.developer.user.username, password=self.developer.user.password)
        request = self.factory.get(self.modify_game_url)
        request.user = self.developer.user
        response = modify_game(request, 1)
        self.assertEqual(response.status_code, 200, "Testing that a request to /modify_game/1/ succeeded")

        # simulate POST request
        form_data = {
            'name': 'changed_name',
            'category': self.game.category,
            'description': self.game.description,
            'price': self.game.price,
            'url': self.game.url,
            'developer': self.game.developer
        }
        request = self.factory.post(self.modify_game_url, form_data)
        request.user = self.developer.user
        form = GameForm(data=form_data)
        response = modify_game(request, 1)

        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, 200, "Testing that a POST request to /modify_game/1/ succeded")

    def test_remove_game_view(self):
        # simulate GET request
        self.client.login(username=self.developer.user.username, password=self.developer.user.password)
        request = self.factory.get(self.remove_game_url)
        request.user = self.developer.user
        response = remove_game(request, 1)
        self.assertEqual(response.status_code, 200, "Testing that a request to /remove_game/1/ succeeded")

        request = self.factory.get(self.game_view_url)
        request.user = self.player.user
        response = game_view(request, game_id=1)
        self.assertEqual(response.status_code, 404, "Testing that the game has been deleted")
