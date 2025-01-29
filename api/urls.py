from django.urls import path

from .views import UsersApiView, WorldApiView, SendCommandApiView, WorldAdvanceApiView

urlpatterns: list = [
	path('userlist', UsersApiView.as_view()),
	path('world', WorldApiView.as_view()),
	path('send_command', SendCommandApiView.as_view()),
	path('advance', WorldAdvanceApiView.as_view()),
]
