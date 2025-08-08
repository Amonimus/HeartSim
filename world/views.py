from typing import List

from django.http import HttpRequest
from django.shortcuts import HttpResponse, redirect, render, reverse

from app.logger import logger
from .forms import WorldForm, StateForm, TaskForm
from .models import State, Task, Entity, WorldEnvironment


def IndexView(request: HttpRequest) -> HttpResponse:
	if request.user.is_authenticated:
		worlds: list[WorldEnvironment] = WorldEnvironment.objects.filter(creator=request.user)
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
			world: WorldEnvironment = form.save(commit=False)
			world.creator = request.user
			world.save()
			entity: Entity = Entity.objects.create(
				world=world,
				name=world.name,
				creator=world.creator,
				properties={
					"alive": True,
					"can_hear": True,
					"health": 100.0,
					"stamina": 100.0
				}
			)
			entity.set_default_state()
			Entity.objects.create(
				world=world,
				name="Fridge",
				creator=world.creator,
				properties={
					"food": 50,
				}
			)
			return redirect('index')
		else:
			logger.error(form.errors)
	form = WorldForm()
	context: dict = {"form": form}
	return render(request, "new_world.html", context)


def WorldView(request: HttpRequest, world_id: int) -> HttpResponse:
	if not request.user.is_authenticated:
		return redirect('unauthenticated')
	world: WorldEnvironment = WorldEnvironment.objects.get(id=world_id)
	if world.creator != request.user:
		return redirect('unauthenticated')
	context: dict = {"world": world}
	return render(request, "world.html", context)


def DeleteWorldView(request: HttpRequest, world_id: int) -> HttpResponse:
	if not request.user.is_authenticated:
		return redirect('unauthenticated')
	world: WorldEnvironment = WorldEnvironment.objects.get(id=world_id)
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

	tasks: List[Task] = Task.objects.all()
	states: List[State] = State.objects.all()
	state_forms = {}
	for state in states:
		state_forms[state.id] = StateForm(instance=state)
	task_forms = {}
	for task in tasks:
		task_forms[task.id] = TaskForm(instance=task)

	if request.method == "POST":
		logger.debug(request.POST)
		state_id = request.POST.get("state_id")
		if state_id:
			state: State = State.objects.get(id=state_id)
			form: StateForm = StateForm(request.POST, instance=state)
			if form.is_valid():
				form.save()
			else:
				logger.error(form.errors)
			state_forms[state.id] = form
		task_id = request.POST.get("task_id")
		if task_id:
			task: Task = Task.objects.get(id=task_id)
			form: TaskForm = TaskForm(request.POST, instance=task)
			if form.is_valid():
				form.save()
			else:
				logger.error(form.errors)
			task_forms[task.id] = form

	context: dict = {
		"states": states,
		"state_forms": state_forms.values(),
		"tasks": tasks,
		"task_forms": task_forms.values()
	}
	return render(request, "editor.html", context)
