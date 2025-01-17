from django.db import models


class Log(models.Model):
	objects = models.Manager()
	time = models.DateTimeField(auto_now_add=True)
	text = models.TextField()
