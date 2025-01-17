from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpRequest

from .models import Log


def input(request: HttpRequest) -> JsonResponse:
	data: dict = request.POST.copy()
	text: str = data.get("text")
	Log.objects.create(text=text)
	return JsonResponse({"ok": True})


def get_logs(_request: HttpRequest) -> JsonResponse:
	logs: list[Log] = Log.objects.order_by('time')
	data: list[dict] = [model_to_dict(log) for log in logs]
	return JsonResponse(data, safe=False)


def advance(_request: HttpRequest) -> JsonResponse:
	return JsonResponse({"ok": True})
