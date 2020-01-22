import json
from django.http import JsonResponse, HttpResponse

from online_judge_back_end.models import User


def login(request):
    print(request.GET.get('username'))
    u=User.objects.filter(username=request.GET.get('username'),password=request.GET.get('password'))
    message = {"status": '401'}#401失败
    if len(u) != 0:
        message["status"]='200'#200成功
    return JsonResponse(message)