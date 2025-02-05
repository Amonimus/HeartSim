import json

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .models import WorldEnvironment, State, Task


class CustomAuthenticationForm(AuthenticationForm):

	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		try:
			self.user_cache = User._default_manager.get(username__iexact=username)
			if self.user_cache is None:
				raise self.get_invalid_login_error()
			self.confirm_login_allowed(self.user_cache)
			self.user_cache = authenticate(username=self.user_cache.username, password=password)
			if self.user_cache is None:
				raise self.get_invalid_login_error()
		except User.DoesNotExist:
			raise self.get_invalid_login_error()
		except Exception as e:
			print(f'LOGIN EXCEPTION: {e}')
			raise e
		return self.cleaned_data


class WorldForm(forms.ModelForm):
	class Meta:
		model = WorldEnvironment
		fields = ["name"]


class PrettyJSONEncoder(json.JSONEncoder):
	def __init__(self, *args, indent, sort_keys, **kwargs):
		super().__init__(*args, indent=2, sort_keys=True, **kwargs)


class StateForm(forms.ModelForm):
	logic = forms.JSONField(encoder=PrettyJSONEncoder, widget=forms.Textarea(attrs={"class": "jsonfield", "cols": 60, "rows": 40}))

	class Meta:
		model = State
		fields = ["id", "logic"]


class TaskForm(forms.ModelForm):
	logic = forms.JSONField(encoder=PrettyJSONEncoder, widget=forms.Textarea(attrs={"class": "jsonfield", "cols": 60, "rows": 40}))

	class Meta:
		model = Task
		fields = ["id", "logic"]
