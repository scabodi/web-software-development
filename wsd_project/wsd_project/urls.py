"""signup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url
from accounts.views import login_view, signup_view, activation_sent_view, activate, logout_view, \
register_as_player, register_as_developer
from games.views import add_game, all_games, categories_view, game_view, game_description, \
my_games_view, payment_result, search_results_view, one_category_view, update_game, sales_stats, \
modify_game, remove_game
from wsd_project.views import home_view

urlpatterns = [
    path('secret_admin/', admin.site.urls),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('', home_view, name="home"),
    path('signup/', signup_view, name="signup"),
    path('logout/', logout_view, name="logout"),
    path('login/', login_view, name="login"),
    path('sent/', activation_sent_view, name="activation_sent"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('activate/<slug:uidb64>/<slug:token>/', activate, name='activate'),
    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
    path('addgame/', add_game, name='add_game'),
    path('allgames/', all_games, name='all_games'),
    path('categories/', categories_view, name='categories'),
    path('game/<int:game_id>/', game_view, name='game_view'),
    path('description/<int:game_id>/', game_description, name="description"),
    path('payment_result/', payment_result, name="payment_result"),
    path('mygames/', my_games_view, name='my_games'),
    path('search/', search_results_view, name='search'),
    path('categories/<str:c>/', one_category_view, name='category'),
    path('updategame/', update_game, name='update_game'),
    path('salesstats/', sales_stats, name="sales_stats"),
    path('modify_game/<int:game_id>/', modify_game, name="modify_game"),
    path('remove_game/<int:game_id>/', remove_game, name="remove_game"),
    path('register_social_as_player/', register_as_player),
    path('register_social_as_developer/', register_as_developer)
]
