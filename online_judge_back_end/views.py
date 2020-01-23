
from django.db.models import Q
from django.http import JsonResponse

from online_judge_back_end.models import User
######DO NOT INSTALL Crypto!!!!!!######
#######please use 'pip install pycryptodome'######
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA

def login(request):
    u=User.objects.filter(Q(username=request.GET.get('username')) | Q(email=request.GET.get('username')),password=request.GET.get('password'))
    message = {"status": '401'}#401失败
    if len(u) != 0:
        message["status"]='200'#200成功
    return JsonResponse(message)

def firstregister(request):
    message = {"status": '401', 'error': {'username':1,'email':1}}  # 401失败
    username=request.POST.get('username')
    email=request.POST.get('email')
    password = request.POST.get('password')
    type = request.POST.get('type')
    u1 = User.objects.filter(username=username)
    u2 = User.objects.filter(email=email)
    if len(u1)!=0:
        message['error']['username']=0
    if len(u2)!=0:
        message['error']['email']=0
    if len(u1)!=0 or len(u2)!=0 :
        return JsonResponse(message)

    m={'学生':0,'教师':1}
    u=User(username=username,email=email,password=password,type=m[type])
    u.save()
    message['status']='200'
    return JsonResponse(message)



