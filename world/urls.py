from django.urls import path

from . import views
from . import ajax

urlpatterns: list = [
    path("", views.IndexView, name="index"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("register", views.RegistrationView.as_view(), name="register"),
    path("new_character", views.NewCharacterView, name="new_character"),
    path("character/<int:char_id>", views.CharacterView, name="character"),
    path("ajax/sendcommand", ajax.input, name="sendcommand"),
    path("ajax/getlogs", ajax.get_logs, name="getlogs"),
    path("ajax/advance", ajax.advance, name="advance"),
    path("ajax/getstats", ajax.get_stats, name="getstats"),
]