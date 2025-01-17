from django.contrib.auth.models import User
from django.db import models


class Character(models.Model):
	objects = models.Manager()
	name = models.CharField(max_length=60)
	creator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	creation_time = models.DateTimeField(auto_now_add=True)
	stats = models.OneToOneField("CharacterStats", on_delete=models.CASCADE)


class CharacterStats(models.Model):
	objects = models.Manager()
	health = models.FloatField()
