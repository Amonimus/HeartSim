from django.contrib import admin
from django.urls import include, path

from .views import LoginView, LogoutView, RegistrationView, UnauthenticatedView, ForbiddenView

urlpatterns: list = [
	path('admin/', admin.site.urls),
	path('api/', include('api.urls')),
	path("", include("world.urls")),
	path("login", LoginView.as_view(), name="login"),
	path("logout", LogoutView.as_view(), name="logout"),
	path("register", RegistrationView.as_view(), name="register"),
	path("unauthenticated", UnauthenticatedView.as_view(), name="unauthenticated"),
	path("forbidden", ForbiddenView.as_view(), name="forbidden"),
]
