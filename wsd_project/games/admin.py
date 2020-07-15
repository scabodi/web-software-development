from django.contrib import admin
from .models import GameSession, Game, Transaction

# Register your models here.
admin.site.register(Game)
admin.site.register(GameSession)

admin.site.register(Transaction)
