from django.urls import path

from . import views
from . import ajax

urlpatterns: list = [
    path("", views.IndexView, name="index"),
    path("new_character", views.NewCharacterView, name="new_character"),
    path("character/<int:char_id>", views.CharacterView, name="character"),
    path("ajax/sendcommand", ajax.input, name="sendcommand"),
    path("ajax/getlogs", ajax.get_logs, name="getlogs"),
    path("ajax/advance", ajax.advance, name="advance"),
    path("ajax/getstats", ajax.get_stats, name="getstats"),
]