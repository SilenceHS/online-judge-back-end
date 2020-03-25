import json
import string
import random
import time, datetime
from django.core import serializers
from django.db.models import Q
from django.http import JsonResponse
from django.core.mail import send_mail
from redis import StrictRedis
from online_judge_back_end.models import User, Quiz, Answerlist
import os
import redis
import threading
from online_judge_back_end import judgeCore
import re
######DO NOT INSTALL Crypto!!!!!!######
#######please use 'pip install pycryptodome'######
import base64
from Crypto.Cipher import AES

front_end_ip='localhost'
front_end_port='9012'
back_end_ip='palipo.cn'
back_end_port='8000'

quizQueueRoot='/home/runact/quiz_queue/'
testCaseRoot='/home/runact/test_case/'

pool = redis.ConnectionPool(host='palipo.cn', port=6379,db=0, password='fhffhf')#redis连接池

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

def urlGenerator(size=32, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def login(request):
    u=User.objects.filter(Q(username=request.GET.get('username')) | Q(email=request.GET.get('username')),password=request.GET.get('password'))
    message = {"status": '401'}#401失败
    if len(u) != 0:
        avatar=u[0].avatar
        if u[0].avatar==None:
            avatar='default.png'
        message["status"]='200'#200成功
        message['user']={'userName':u[0].username,'avatar_url':'http://'+back_end_ip+':'+back_end_port+'/static/avatar/'+avatar,'type':u[0].type}
    return JsonResponse(message)

def firstRegister(request):
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

def quizList(request,courseid,username):
    message={"status":404,"quizList":[]}
    if courseid=="1":
        quizlist=Quiz.objects.filter(courseid=1)
        for i in quizlist:
            userr=User.objects.filter(username=username)
            status=Answerlist.objects.filter(userid=userr[0].id,status="ACCEPTED",quizid=i.id)
            if len(status) != 0:
                status="ACCEPTED"
            else:
                status=""
            message["quizList"].append({"id":i.id,"name":i.name,"level":i.level,"url":i.url,"status":status})
        message["status"]=200
    return JsonResponse(message)

def getQuiz(request,courseid,quizurl,username):
    message = {"status": 404, "quiz":{}}
    if courseid=="1":
        quiz=Quiz.objects.filter(url=quizurl)
        if len(quiz)==0:
            return JsonResponse(message)
        answerList=Answerlist.objects.filter(quizid=quiz[0].id,status="ACCEPTED")
        if len(answerList)!=0:
            message["accepted"]=True
        else:
            message["accepted"]=False
        message["quiz"]=json.loads(serializers.serialize("json",quiz))
        message["status"]=200

        return JsonResponse(message)

def postQuiz(request):
    message = {"status": '200',"tempid":""}
    code=request.POST.get('code')
    username=request.POST.get('username')
    quizurl=request.POST.get('quizurl')
    language=request.POST.get('language')
    tempid=urlGenerator()
    timestamp=str(int(time.time()))
    timelimit=0
    memorylimit=0
    fileformat=""
    if language=='Python3':
        fileformat=".py"
    if language == 'Java':
        fileformat = ".java"
    if language=="C":
        fileformat = ".c"
    if language == "C++":
        fileformat = ".cpp"
    filename=quizQueueRoot+username + '_' + quizurl + '_' + timestamp + fileformat
    f = open(filename, 'w')
    f.writelines(code)
    f.close()
    static_redis = redis.Redis(connection_pool=pool)
    quiz=Quiz.objects.filter(url=quizurl)
    if len(quiz)!=0:
        timelimit=quiz[0].timelimit
        memorylimit=quiz[0].memorylimit
    user=User.objects.filter(username=username)
    redis_queue={'userid':user[0].id,'filename':filename,'language':language,'tempid':tempid,'quizurl':quizurl,'timelimit':timelimit,'memorylimit':memorylimit,'testcase':[]}

    testcasecount=1
    while 1:
        if os.path.exists(testCaseRoot+quizurl+'/'+str(testcasecount)+".in"):
            redis_queue['testcase'].append({'input': testCaseRoot+quizurl+"/"+str(testcasecount)+'.in','output': testCaseRoot+quizurl+"/"+str(testcasecount)+'.out',})
            testcasecount+=1
        else:
            break
    static_redis.lpush('oj',str(redis_queue))
    message['tempid']=tempid
    return JsonResponse(message)

def getTempStatus(request):
    tempid = request.POST.get('tempid')
    static_redis = redis.Redis(connection_pool=pool)
    result = static_redis.hget('result',tempid)
    if  result!=None:
        result=eval(result)
        print(result)
        return JsonResponse({"status": '200', 'result':result['status']})
    return JsonResponse({"status": '205'})

def addQuiz(request):
    message={"status": '200'}
    name=request.POST.get('name')
    type=request.POST.get('type')
    description=request.POST.get('description')
    input=request.POST.get('input')
    output=request.POST.get('output')
    sampleinput=request.POST.get('sampleinput')
    sampleoutput=request.POST.get('sampleoutput')
    timelimit=request.POST.get('timelimit')
    memorylimit=request.POST.get('memorylimit')
    testcase=request.POST.get('testcase')
    courseid=request.POST.get('courseid')
    testCaseInput=[]
    testCaseOutput = []
    if courseid=="1" and type=='2':
        quiz=Quiz(url=urlGenerator(),
                  courseid=1,
                  name=name,
                  description=description,
                  input=input,
                  output=output,
                  sampleinput=sampleinput,
                  sampleoutput=sampleoutput,
                  language=3,
                  timelimit=timelimit,
                  memorylimit=memorylimit)
        #quiz.save()
        return JsonResponse(message)

#########################


class judgeThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        #print ("开始线程：")
        judge()
       # print ("退出线程：")
def judge():
    while 1:
        static_redis=redis.Redis(connection_pool=pool)
        receiver=static_redis.brpop('oj', 3)
        if receiver != None:
            receiver=eval(receiver[1])
            judgeCore.run(receiver,pool)

class redisToMysqlThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        save()

def save():
    while 1:
        static_redis=redis.Redis(connection_pool=pool)
        keys=static_redis.hkeys('result')
        if len(keys)!=0:
            time.sleep(10)
            for i in keys:
                print(i)
                result=static_redis.hget('result',i)
                print(result)
                result=eval(result)
                answerList=Answerlist(userid=result['userid'],
                                      quizid=result['quizid'],
                                      code=result['code'],
                                      language=result['language'],
                                      status=result['status'],
                                      date=result['date'],
                                      usetime=result['usetime'],
                                      usememory=result['usememory'])
                answerList.save()
                static_redis.hdel('result', i)
        time.sleep(3)
thread1 = judgeThread()
thread1.start()
thread1.daemon
thread2 = redisToMysqlThread()
thread2.start()
thread2.daemon






