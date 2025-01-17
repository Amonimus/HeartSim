from django.http import JsonResponse, HttpRequest

from character.models import CharacterLog, Character
from .models import SystemLog


def input(request: HttpRequest) -> JsonResponse:
	try:
		data: dict = request.POST.copy()
		text: str = data.get("text")
		char_id: int = data.get("char_id")
		SystemLog.objects.create(text=text)
		character = Character.objects.get(id=char_id)
		CharacterLog.objects.create(character=character, text=text)
		return JsonResponse({"ok": True})
	except Exception as e:
		print(e)
		return JsonResponse({"ok": False}, status=500)


def get_logs(request: HttpRequest) -> JsonResponse:
	try:
		data: dict = request.GET.copy()
		char_id = data["char_id"]
		logs: list[CharacterLog] = CharacterLog.objects.filter(character=char_id).order_by('time')
		data: list[dict] = [log.to_dict() for log in logs]
		return JsonResponse(data, safe=False)
	except Exception as e:
		print(e)
		return JsonResponse({"ok": False}, status=500)


def get_stats(request: HttpRequest) -> JsonResponse:
	try:
		data: dict = request.GET.copy()
		char_id = data["char_id"]
		charater: Character = Character.objects.get(id=char_id)
		return JsonResponse(charater.to_dict(), safe=False)
	except Exception as e:
		print(e)
		return JsonResponse({"ok": False}, status=500)


def advance(request: HttpRequest) -> JsonResponse:
	try:
		data: dict = request.POST.copy()
		char_id: int = data.get("char_id")
		character = Character.objects.get(id=char_id)
		character.advance()
		return JsonResponse({"ok": True})
	except Exception as e:
		print(e)
		return JsonResponse({"ok": False}, status=500)
