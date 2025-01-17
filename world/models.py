from django.db import models


class SystemLog(models.Model):
	objects = models.Manager()
	time = models.DateTimeField(auto_now_add=True)
	text = models.TextField()

	def to_dict(self):
		return {"time": self.time.strftime("%m-%d-%Y %H:%M:%S"), "text": self.text}