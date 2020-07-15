from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    CHOICES = [('Player', 'Player'), ('Developer', 'Developer')]

    first_name = forms.CharField(max_length=100, help_text='Last Name', required=True)
    last_name = forms.CharField(max_length=100, help_text='Last Name', required=True)
    email = forms.EmailField(max_length=150, help_text='Email', required=True)
    type_of_user = forms.ChoiceField(widget=forms.Select, choices=CHOICES ,required=True)


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'type_of_user', )
