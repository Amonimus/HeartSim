from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager, FloatField, CharField, BooleanField, ForeignKey, DateTimeField, OneToOneField, ManyToManyField, Model, QuerySet, TextField

from world.models import SystemLog


# class Character(Model):
# 	objects: Manager = Manager()
# 	name: str = CharField(max_length=60)
# 	alive: bool = BooleanField(default=True)
# 	creator: User = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
# 	creation_time: datetime = DateTimeField(auto_now_add=True)
# 	stats: "CharacterStats" = OneToOneField("CharacterStats", null=True, blank=True, on_delete=models.CASCADE)
# 	tasks: list["CharacterTask"] | QuerySet = ManyToManyField("CharacterTask")
# 	logs: list["CharacterLog"] | QuerySet = ManyToManyField("CharacterLog", related_name="log_character")
#
# 	def to_dict(self) -> dict:
# 		stats: dict = {
# 			"name": self.name,
# 			"stats": self.stats.to_dict(),
# 			"tasks": [task.name for task in self.task_list]
# 		}
# 		print(stats)
# 		return stats
#
# 	@property
# 	def task_list(self) -> list["CharacterTask"] | QuerySet:
# 		return self.tasks.all()
#
# 	def log(self, text: str) -> None:
# 		CharacterLog.objects.create(character=self, text=text)
#
# 	def advance(self) -> None:
# 		if self.alive:
# 			self.idle()
#
# 	def listen(self, user: User, text: str) -> None:
# 		entry: str = f"{user} says: \"{text}\""
# 		CharacterLog.objects.create(character=self, text=entry)
# 		if "sleep" in text.lower():
# 			task: CharacterTask = self.create_task("Sleep")
# 			self.log("Going to sleep...")
# 			self.stats.add_status("Sleeping")
#
# 	def check_task(self, task_name: str) -> tuple["CharacterTask", bool]:
# 		task, new = CharacterTask.objects.get_or_create(name=task_name)
# 		if task in self.task_list:
# 			return task, True
# 		else:
# 			return task, False
#
# 	def create_task(self, task_name: str) -> "CharacterTask":
# 		task, check = self.check_task(task_name)
# 		if not check:
# 			self.tasks.add(task)
# 		return task
#
# 	def remove_task(self, task_name: str) -> "CharacterTask":
# 		task, check = self.check_task(task_name)
# 		if check:
# 			self.tasks.remove(task)
# 		return task
#
# 	def idle(self) -> None:
# 		self.stats.add_status("Healthy")
# 		status, check = self.stats.check_status("Sleeping")
# 		if not check:
# 			self.stats.add_status("Idle")
# 			self.reduce_stamina()
# 		else:
# 			self.stats.remove_status("Idle")
# 			self.sleeping()
# 		self.stats.save()
#
# 	def reduce_stamina(self) -> None:
# 		if self.stats.stamina > 0:
# 			self.stats.stamina -= 0.1
# 		else:
# 			self.stats.stamina = 0
# 			self.reduce_health(1)
#
# 	def sleeping(self) -> None:
# 		if self.stats.stamina < 100:
# 			self.stats.stamina += 1
# 		else:
# 			self.stats.stamina = 100
# 			self.remove_task("Sleep")
# 			self.stats.remove_status("Sleeping")
#
# 	def reduce_health(self, amount: float) -> None:
# 		if self.health > 0:
# 			self.health -= amount
# 			self.log("This hurts...")
# 		else:
# 			self.health = 0
# 			self.alive = False
# 			self.log("I'm sorry...")
# 			SystemLog.objects.create(text=f"{self.name} has perished!")
#
#
# class CharacterLog(Model):
# 	objects: Manager = Manager()
# 	character: Character = ForeignKey(Character, on_delete=models.CASCADE)
# 	time: datetime = DateTimeField(auto_now_add=True)
# 	text: str = TextField()
#
# 	def to_dict(self) -> dict:
# 		data: dict = {
# 			"time": self.time.strftime("%m-%d-%Y %H:%M:%S"),
# 			"text": self.text
# 		}
# 		return data
#
#
# class CharacterTask(Model):
# 	objects: Manager = Manager()
# 	name: str = TextField()
#
# 	def on_create(self):
# 		pass
#
# 	def on_complete(self):
# 		pass
#
#
# class CharacterStatus(Model):
# 	objects: Manager = Manager()
# 	name: str = TextField()
#
#
# class CharacterStats(Model):
# 	objects: Manager = Manager()
# 	health: float = FloatField(default=100.0)
# 	stamina: float = FloatField(default=100.0)
# 	statuses: list[CharacterStatus] | QuerySet = ManyToManyField(CharacterStatus)
#
# 	@property
# 	def status_list(self) -> list[CharacterStatus] | QuerySet:
# 		return self.statuses.all()
#
# 	def to_dict(self) -> dict:
# 		stats: dict = {
# 			"health": round(self.health, 2),
# 			"stamina": round(self.stamina, 2),
# 			"statuses": [status.name for status in self.status_list]
# 		}
# 		return stats
#
# 	def check_status(self, status_name: str) -> tuple[CharacterStatus, bool]:
# 		status, new = CharacterStatus.objects.get_or_create(name=status_name)
# 		if status in self.status_list:
# 			return status, True
# 		else:
# 			return status, False
#
# 	def add_status(self, status_name: str) -> CharacterStatus:
# 		status, check = self.check_status(status_name)
# 		if not check:
# 			self.statuses.add(status)
# 		return status
#
# 	def remove_status(self, status_name: str) -> CharacterStatus:
# 		status, check = self.check_status(status_name)
# 		if check:
# 			self.statuses.remove(status)
# 		return status
