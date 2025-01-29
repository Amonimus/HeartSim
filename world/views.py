from django.http import HttpRequest
from django.shortcuts import HttpResponse, redirect, render, reverse

from .forms import WorldForm, StateForm
from .models import WorldEnviroment, Entity, Task, State


def IndexView(request: HttpRequest) -> HttpResponse:
	if request.user.is_authenticated:
		worlds: list[WorldEnviroment] = WorldEnviroment.objects.filter(creator=request.user)
		context: dict = {"worlds": worlds}
	else:
		context = {}
	return render(request, "index.html", context)


def NewWorldView(request: HttpRequest) -> HttpResponse:
	if not request.user.is_authenticated:
		return redirect('unauthenticated')
	if request.method == "POST":
		form: WorldForm = WorldForm(request.POST)
		if form.is_valid():
			world: WorldEnviroment = form.save(commit=False)
			world.creator = request.user
			character = Entity.objects.create(name=world.name, creator=world.creator)
			world.save()
			world.entities.add(character)
			return redirect('index')
	form = WorldForm()
	context: dict = {"form": form}
	return render(request, "new_world.html", context)


def WorldView(request: HttpRequest, world_id: int) -> HttpResponse:
	if not request.user.is_authenticated:
		return redirect('unauthenticated')
	world: WorldEnviroment = WorldEnviroment.objects.get(id=world_id)
	if world.creator != request.user:
		return redirect('unauthenticated')
	context: dict = {"world": world}
	return render(request, "world.html", context)


def DeleteWorldView(request: HttpRequest, world_id: int) -> HttpResponse:
	if not request.user.is_authenticated:
		return redirect('unauthenticated')
	world: WorldEnviroment = WorldEnviroment.objects.get(id=world_id)
	if world.creator != request.user:
		return redirect('unauthenticated')
	world.delete()
	return redirect(reverse('index'))


def TutorialView(request: HttpRequest) -> HttpResponse:
	if not request.user.is_authenticated:
		return redirect('unauthenticated')
	return render(request, "tutorial.html")


def EditorView(request: HttpRequest) -> HttpResponse:
	if not request.user.is_authenticated:
		return redirect('unauthenticated')
	if request.method == "POST":
		state_id = request.POST.get("state_id")
		state = State.objects.get(id=state_id)
		form: StateForm = StateForm(request.POST, instance=state)
		if form.is_valid():
			form.save()

	tasks = Task.objects.all()
	states = State.objects.all()
	state_forms = []
	for state in states:
		form = StateForm(instance=state)
		state_forms.append(form)
	context: dict = {"tasks": tasks, "states": states, "state_forms": state_forms}
	return render(request, "editor.html", context)
