from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import HttpResponse, redirect, render, reverse
from django.views import View

from character.forms import CharacterForm
from character.models import CharacterStats, Character
from .forms import CustomAuthenticationForm


def IndexView(request: HttpRequest) -> HttpResponse:
	characters = Character.objects.filter(creator=request.user)
	context = {"characters": characters}
	return render(request, "index.html", context)


def NewCharacterView(request: HttpRequest) -> HttpResponse:
	if request.method == "POST":
		form = CharacterForm(request.POST)
		if form.is_valid():
			character = form.save(commit=False)
			character.stats = CharacterStats.objects.create()
			character.save()
			return redirect('index')
	form = CharacterForm()
	context = {"form": form}
	return render(request, "new_character.html", context)


def CharacterView(request: HttpRequest, char_id: int) -> HttpResponse:
	character = Character.objects.get(id=char_id)
	context = {"character": character}
	return render(request, "character.html", context)


class LoginView(View):
	form_class = CustomAuthenticationForm
	template_name = 'login.html'

	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = self.form_class(data=request.POST)
		if form.is_valid():
			user = form.get_user()
			if user is not None:
				login(request, user)
				return redirect(reverse('index'))
		else:
			print(f'FORM {form.errors} {form.non_field_errors()}')
		return render(request, self.template_name, {'form': form})


class RegistrationView(View):
	template_name = 'register.html'

	def get(self, request):
		return render(request, self.template_name)

	def post(self, request):
		data = request.POST.copy()
		if data['password'] != data['confirm_password']:
			raise Exception("Password don't match")
		user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
		login(request, user)
		return redirect(reverse('index'))


class LogoutView(View):

	def get(self, request):
		request.session.flush()
		logout(request)
		return redirect(reverse('index'))
