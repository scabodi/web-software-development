from django.contrib.auth import login, authenticate, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.template.loader import render_to_string
#from django.contrib.auth.models import Group
from django.db import transaction
from django.contrib import messages

from .forms import SignUpForm
from .tokens import account_activation_token
from .models import Profile

def home_view(request):
    return render(request, 'home.html')

def activation_sent_view(request):
    return render(request, 'activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        #User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.signup_confirmation = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')
    else:
        return render(request, 'activation_invalid.html')

@transaction.atomic
def signup_view(request):
    if request.method  == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.email = form.cleaned_data.get('email')
            group_name = form.cleaned_data.get('type_of_user')
            user.is_active = False
            user.save()
            #group = Group.objects.get(name=group_name)
            #user.groups.add(group)
            if(group_name == "Player"):
                tizio = Profile.objects.get(user=user)
                tizio.is_player = True
                tizio.save()
            else:
                tizio = Profile.objects.get(user=user)
                tizio.is_developer = True
                tizio.save()
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('activation_sent')
        else:
             # context['form_errors'] = form.errors
             return render(request, 'signup.html', {'form': form,
                'form_errors': 'There are errors in the submitted form! \
                Pleas check under the empty fields for suggestions on what went wrong!'})
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def login_view(request):
    return redirect('login')

def register_as_player(request):
    p = Profile.objects.get(user_id=request.user.id)
    p.is_player = True
    p.save()
    return redirect('home')

def register_as_developer(request):
    p = Profile.objects.get(user_id=request.user.id)
    p.is_developer = True
    p.save()
    return redirect('home')
