from django.urls import path

from . import views
from . import ajax

urlpatterns: list = [
    path("", views.index, name="index"),
    path("ajax/sendcommand", ajax.input, name="sendcommand"),
    path("ajax/getlogs", ajax.get_logs, name="getlogs"),
    path("ajax/advance", ajax.advance, name="advance"),
]