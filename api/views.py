from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponseForbidden, HttpResponse
from rest_framework.request import Request
from rest_framework.views import APIView

from world.models import WorldEnvironment, SystemLog


class UsersApiView(APIView):
	def get(self, request: Request) -> HttpResponse:
		usernames = [user.username for user in User.objects.all()]
		return JsonResponse(usernames, safe=False)


class WorldApiView(APIView):
	def get(self, request: Request) -> HttpResponse:
		data: dict = request.GET.copy()
		world_id: int = data.get("world_id")
		world: WorldEnvironment = WorldEnvironment.objects.get(id=world_id)
		if world.creator != request.user:
			return HttpResponseForbidden('unauthorized', status=403)
		return JsonResponse(world.to_json(), safe=False)


class WorldAdvanceApiView(APIView):
	def post(self, request: Request) -> HttpResponse:
		try:
			data: dict = request.POST.copy()
			world_id: int = data.get("world_id")
			world: WorldEnvironment = WorldEnvironment.objects.get(id=world_id)
			if world.creator != request.user:
				return HttpResponseForbidden('unauthorized', status=403)
			world.advance()
			return JsonResponse({"ok": True})
		except Exception as e:
			print(e)
			return JsonResponse({"ok": False}, status=500)


class SendCommandApiView(APIView):
	def post(self, request: Request) -> HttpResponse:
		try:
			data: dict = request.POST.copy()
			world_id: int = data.get("world_id")
			world: WorldEnvironment = WorldEnvironment.objects.get(id=world_id)
			if world.creator != request.user:
				return HttpResponseForbidden('unauthorized', status=403)
			text: str = data.get("text")
			world.listen(request.user, text)
			return JsonResponse({"ok": True})
		except Exception as e:
			print(e)
			return JsonResponse({"ok": False}, status=500)
