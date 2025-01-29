from django.urls import path

from .views import IndexView, NewWorldView, WorldView, DeleteWorldView, TutorialView, EditorView

urlpatterns: list = [
	path("", IndexView, name="index"),
	path("new_world", NewWorldView, name="new_world"),
	path("tutorial", TutorialView, name="tutorial"),
	path("editor", EditorView, name="editor"),
	path("world/<int:world_id>", WorldView, name="world"),
	path("delete/<int:world_id>", DeleteWorldView, name="delete"),
]
