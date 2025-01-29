from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.shortcuts import HttpResponse, redirect, render, reverse
from django.views import View

from world.forms import CustomAuthenticationForm


class LoginView(View):
	form_class = CustomAuthenticationForm
	template_name = 'login.html'

	def get(self, request: HttpRequest) -> HttpResponse:
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	def post(self, request: HttpRequest) -> HttpResponse:
		form: CustomAuthenticationForm = self.form_class(data=request.POST)
		if form.is_valid():
			user: User = form.get_user()
			if user is not None:
				login(request, user)
				return redirect(reverse('index'))
		else:
			print(f'FORM {form.errors} {form.non_field_errors()}')
		return render(request, self.template_name, {'form': form})


class RegistrationView(View):
	template_name = 'register.html'

	def get(self, request: HttpRequest) -> HttpResponse:
		return render(request, self.template_name)

	def post(self, request: HttpRequest) -> HttpResponse:
		data: dict = request.POST.copy()
		if data['password'] != data['confirm_password']:
			raise Exception("Password don't match")
		user: User = User.objects.create_user(
			username=data['username'],
			email=data['email'],
			password=data['password']
		)
		login(request, user)
		return redirect(reverse('index'))


class LogoutView(View):

	def get(self, request: HttpRequest) -> HttpResponse:
		request.session.flush()
		logout(request)
		return redirect(reverse('index'))


class ForbiddenView(View):
	def get(self, request: HttpRequest) -> HttpResponse:
		return render(request, "forbidden.html", status=401)


class UnauthenticatedView(View):
	def get(self, request: HttpRequest) -> HttpResponse:
		return render(request, "unauthenticated.html", status=403)
