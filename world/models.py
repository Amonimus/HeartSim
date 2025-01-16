from django.db import models


class Log(models.Model):
	time = models.DateTimeField(auto_now_add=True)
	text = models.TextField()
