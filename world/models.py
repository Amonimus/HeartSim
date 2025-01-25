from datetime import datetime

from django.db import models
from django.db.models import Manager, DateTimeField, TextField


class SystemLog(models.Model):
	objects: Manager = Manager()
	time: datetime = DateTimeField(auto_now_add=True)
	text: str = TextField()

	def to_dict(self) -> dict:
		data: dict = {
			"time": self.time.strftime("%m-%d-%Y %H:%M:%S"),
			"text": self.text
		}
		return data
