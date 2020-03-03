import json
from django.db.models import Q
from django.http import JsonResponse
from django.core.mail import send_mail

from online_judge_back_end.models import User, Quiz, Answerlist
######DO NOT INSTALL Crypto!!!!!!######
#######please use 'pip install pycryptodome'######
import base64
from Crypto.Cipher import AES

front_end_ip='localhost'
front_end_port='9012'
back_end_ip='localhost'
back_end_port='8000'

'''
采用AES对称加密算法
'''
# str不是32的倍数那就补足
def add_to_32(value):
    while len(value) % 32 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes
#加密方法
def encryptAES(text):
    # 秘钥
    key = 'SilenceHS'
    # 待加密文本
    # 初始化加密器
    aes = AES.new(add_to_32(key), AES.MODE_ECB)
    #先进行aes加密
    encrypt_aes = aes.encrypt(add_to_32(text))
    #用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    return encrypted_text
#解密方法
def decryptAES(text):
    # 秘钥
    key = 'SilenceHS'
    # 密文
    # 初始化加密器
    aes = AES.new(add_to_32(key), AES.MODE_ECB)
    #优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
    #执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted),encoding='utf-8').replace('\0','')
    return decrypted_text

def login(request):
    u=User.objects.filter(Q(username=request.GET.get('username')) | Q(email=request.GET.get('username')),password=request.GET.get('password'))
    message = {"status": '401'}#401失败
    if len(u) != 0:
        avatar=u[0].avatar
        if u[0].avatar==None:
            avatar='default.png'
        message["status"]='200'#200成功
        message['user']={'username':u[0].username,'avatar_url':'http://'+back_end_ip+':'+back_end_port+'/static/avatar/'+avatar}
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
    msg={'username':username,'email':email,'password':password,'type':m[type]}
    msg=json.dumps(msg)
    msg=encryptAES(msg)
    msg=str(base64.encodebytes(msg.encode('utf-8')),encoding='utf-8')
    msg=msg.replace('\n','')
    message['status'] = '200'
    if mail(email,msg) == False:
        message['status'] = '500'#系统错误
    return JsonResponse(message)

def active(request,key):
    message = {"status": '200'}  # 200成功
    try:
        aesMsg=str(base64.decodebytes(key.encode('utf-8')),encoding='utf-8')
        userInfo=json.loads(decryptAES(aesMsg))
        u=User.objects.filter(Q(username=userInfo['username'])|Q(email=userInfo['email']))
        if len(u)!=0:
            raise Exception("重复注册！")
        u=User(username=userInfo['username'],email=userInfo['email'],password=userInfo['password'],type=userInfo['type'])
        u.save()
    except:
        print('解密失败')
        message['status']='401'
    return JsonResponse(message)

def mail(receiver, key):
    ret = True
    try:
        message=''
        html_message = '\
                <h2>欢迎注册在线判题系统, 离注册完成还有最后一步</h2>\
                <p><a href="http://'+front_end_ip+':'+front_end_port+'/#/active/?key='+key + '">点击此处以激活账号</a></p>\
                <h2>注意,此链接仅可使用一次</h2>\
                <h2>如果这并不是你本人操作, 请忽略这封邮件</h2>'
        sender='5724924@qq.com'
        subject = "激活你的在线判题系统账号"  # 邮件的主题，也可以说是标题
        send_mail(subject,message,sender,[receiver],html_message=html_message)
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        print(err)
        ret = False
    return ret

def quizlist(request,courseid,username):
    message={"status":404,"quizlist":[]}
    if courseid=="0":
        quizlist=Quiz.objects.filter(courseid=0)
        for i in quizlist:
            userr=User.objects.filter(username=username)
            userr[0].id
            status=Answerlist.objects.filter(userid=userr[0].id,status="AC")
            if len(status) != 0:
                status="AC"
            else:
                status=""
            message["quizlist"].append({"id":i.id,"name":i.name,"level":i.level,"url":i.url,"status":status})
        message["status"]=200
    return JsonResponse(message)




