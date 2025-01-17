from django.contrib import admin
from django.urls import include, path

urlpatterns: list = [
	path('admin/', admin.site.urls),
	path("", include("world.urls")),
]
