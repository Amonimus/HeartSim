from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


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
