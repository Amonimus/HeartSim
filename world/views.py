from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from character.forms import CharacterForm
from character.models import CharacterStats, Character


def IndexView(request: HttpRequest) -> HttpResponse:
	characters = Character.objects.all()
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
