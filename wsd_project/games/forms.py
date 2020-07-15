from django import forms
from django.forms import ModelForm, Form
from .models import Game, Transaction
from django.utils import timezone

CATEGORY_CHOICES = [('Action','Action'),
                    ('Adventure','Adventure'),
                    ('Arcade','Arcade'),
                    ('FPS','FPS'),
                    ('Racing','Racing'),
                    ('Simulation','Simulation'),
                    ('Sport','Sport'),
                    ('Strategy','Strategy')]

class GameForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Game
        fields = ["name", "category", "price", "description", "url", "developer"]
        widgets = {
            'developer': forms.HiddenInput(),
        }

class PaymentForm(Form):
    pid = forms.CharField(widget = forms.HiddenInput())
    sid = forms.CharField(widget = forms.HiddenInput()) # seller id
    checksum = forms.CharField(widget = forms.HiddenInput())
    amount = forms.DecimalField(widget = forms.HiddenInput())
    success_url = forms.CharField(widget = forms.HiddenInput())
    cancel_url = forms.CharField(widget = forms.HiddenInput())
    error_url = forms.CharField(widget = forms.HiddenInput())
    # game info
    name = forms.CharField(max_length=30, label="Game name")
    category = forms.ChoiceField(choices = CATEGORY_CHOICES, label="Category")
    description =  forms.CharField(label="Description")
    price = forms.DecimalField(label="Price")

    def save(self):
        data = self.cleaned_data
    
