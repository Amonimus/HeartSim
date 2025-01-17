from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class Character(models.Model):
	objects = models.Manager()
	name: str = models.CharField(max_length=60)
	alive: bool = models.BooleanField(default=True)
	creator: User = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	creation_time: datetime = models.DateTimeField(auto_now_add=True)
	stats: "CharacterStats" = models.OneToOneField("CharacterStats", null=True, blank=True, on_delete=models.CASCADE)
	logs = models.ManyToManyField("CharacterLog", related_name="log_character")

	def to_dict(self):
		return {"name": self.name, "stats": self.stats.to_dict()}

	def advance(self):
		print("Advance")
		if self.alive:
			self.reduce_stamina()
			self.stats.save()

	def reduce_stamina(self):
		if self.stats.stamina > 0:
			self.stats.stamina -= 0.1
		else:
			self.stats.stamina = 0
			self.reduce_health()

	def reduce_health(self):
		if self.stats.health > 0:
			self.stats.health -= 0.1
		else:
			self.stats.health = 0


class CharacterLog(models.Model):
	objects = models.Manager()
	character: Character = models.ForeignKey(Character, on_delete=models.CASCADE)
	time: datetime = models.DateTimeField(auto_now_add=True)
	text: str = models.TextField()

	def to_dict(self):
		return {"time": self.time.strftime("%m-%d-%Y %H:%M:%S"), "text": self.text}


class CharacterStats(models.Model):
	objects = models.Manager()
	health: float = models.FloatField(default=100.0)
	stamina: float = models.FloatField(default=100.0)

	def to_dict(self):
		return {
			"health": round(self.health, 2),
			"stamina": round(self.stamina, 2)
		}
