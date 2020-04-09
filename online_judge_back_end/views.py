import json
import shutil
import string
import random
import time, datetime
from django.core import serializers
from django.db.models import Q
from django.http import JsonResponse
from django.core.mail import send_mail
from redis import StrictRedis
from online_judge_back_end.models import User, Quiz, Answerlist, Course,UserCourse
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

def quizList(request,courseurl,username):
    message={"status":404,"quizList":[],"coursename":""}
    course = Course.objects.filter(url=courseurl).first()
    user = User.objects.filter(username=username).first()
    userCourse = UserCourse.objects.filter(courseid=course, studentid=user).first()
    if courseurl=="loDjDEx" or user.type!=0 or userCourse!=None:#如果是官方题库
        quizlist=Quiz.objects.filter(courseid=course)
        message["coursename"]=course.coursename
        for i in quizlist:
            userr=User.objects.filter(username=username)
            status=Answerlist.objects.filter(userid=userr[0].id,status="ACCEPTED",quizid=i.id)
            if len(status) != 0:
                status="ACCEPTED"
            else:
                status=""
            message["quizList"].append({"id":i.id,"name":i.name,"level":i.level,"url":i.url,"status":status,"tag":i.tag})
        message["status"]=200
    return JsonResponse(message)

def getQuiz(request,courseurl,quizurl,username):
    message = {"status": 404, "quiz":{}}
    course = Course.objects.filter(url=courseurl).first()
    user = User.objects.filter(username=username).first()
    userCourse = UserCourse.objects.filter(courseid=course, studentid=user).first()
    if courseurl=="loDjDEx" or user.type != 0 or userCourse != None:
        quiz=Quiz.objects.filter(url=quizurl)
        if len(quiz)==0:
            return JsonResponse(message)
        user=User.objects.filter(username=username).first()
        answerList=Answerlist.objects.filter(quizid=quiz[0].id,status="ACCEPTED",userid=user).first()
        if answerList!=None:
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
    if language == "JavaScript":
        fileformat = ".js"
    if language == "Shell":
        fileformat = ".sh"
    if language == "Lua":
        fileformat = ".lua"
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
    description=request.POST.get('description').replace("\n","<br/>")
    input=request.POST.get('input').replace("\n","<br/>")
    output=request.POST.get('output').replace("\n","<br/>")
    sampleinput=request.POST.get('sampleinput').replace("\n","<br/>")
    sampleoutput=request.POST.get('sampleoutput').replace("\n","<br/>")
    timelimit=request.POST.get('timelimit')
    memorylimit=request.POST.get('memorylimit')
    testcase=request.POST.get('testcase')
    courseurl=request.POST.get('courseurl')
    language=request.POST.get('language')
    level = request.POST.get('level')
    tag=request.POST.get('tag')
    course = Course.objects.filter(url=courseurl)
    if (courseurl=="loDjDEx" and type=='2') or (len(course)!=0 and type=='1'):
        pat = re.compile("(.*?)\n--InEnd--\n(.*?)\n--OutEnd--\n*", re.DOTALL)
        testCaseList=pat.findall(testcase)
        url=urlGenerator()
        testCasePath=testCaseRoot+url
        if not os.path.exists(testCasePath):
            os.makedirs(testCasePath)
        for i in range(len(testCaseList)):
            f=open(testCasePath+"/"+str(i+1)+".in","w")
            f.writelines(testCaseList[i][0])
            f.close()
            f = open(testCasePath + "/" + str(i + 1) + ".out", "w")
            f.writelines(testCaseList[i][1])
            f.close()
        quiz=Quiz(url=url,
                  courseid=course[0],
                  name=name,
                  description=description,
                  input=input,
                  output=output,
                  sampleinput=sampleinput,
                  sampleoutput=sampleoutput,
                  language=language,
                  level=level,
                  timelimit=timelimit,
                  memorylimit=memorylimit,
                  tag=tag)
        quiz.save()
        return JsonResponse(message)
def deleteQuiz(request):
    message={'status':'200'}
    qid=request.POST.get('id')
    username=request.POST.get('username')
    quiz=Quiz.objects.filter(id=qid)
    user=User.objects.filter(username=username)
    if len(user)==1 and user[0].type!=0:
        shutil.rmtree(testCaseRoot+quiz[0].url)
        quiz[0].delete()
        return JsonResponse(message)
    message['status']='403'
    return JsonResponse(message)

def getModifyQuiz(request,courseId,quizUrl,userName):
    message={'status':'200'}
    quiz=Quiz.objects.filter(url=quizUrl)
    message['name']=quiz[0].name
    message['description'] = quiz[0].description.replace("<br/>","\n")
    message['input'] = quiz[0].input.replace("<br/>","\n")
    message['output'] = quiz[0].output.replace("<br/>","\n")
    message['sampleinput'] = quiz[0].sampleinput.replace("<br/>","\n")
    message['sampleoutput'] = quiz[0].sampleoutput.replace("<br/>","\n")
    message['timelimit'] = quiz[0].timelimit
    message['memorylimit'] = quiz[0].memorylimit
    message['language'] = quiz[0].language
    message['level'] = quiz[0].level
    message['tag'] = quiz[0].tag

    testcasecount = 1
    testcase=""
    while 1:
        if os.path.exists(testCaseRoot + quizUrl + '/' + str(testcasecount) + ".in"):
            f=open(testCaseRoot + quizUrl + '/' + str(testcasecount) + ".in","r")
            input=f.read()
            f.close()
            testcase+=input+'\n--InEnd--\n'
            f = open(testCaseRoot + quizUrl + '/' + str(testcasecount) + ".out", "r")
            output=f.read()
            testcase += output + '\n--OutEnd--\n'
            testcasecount += 1
        else:
            break
    message['testcase'] =testcase
    return JsonResponse(message)

def modifyQuiz(request):
    message = {"status": '200'}
    name = request.POST.get('name')
    type = request.POST.get('type')
    description = request.POST.get('description').replace("\n", "<br/>")
    input = request.POST.get('input').replace("\n", "<br/>")
    output = request.POST.get('output').replace("\n", "<br/>")
    sampleinput = request.POST.get('sampleinput').replace("\n", "<br/>")
    sampleoutput = request.POST.get('sampleoutput').replace("\n", "<br/>")
    timelimit = request.POST.get('timelimit')
    memorylimit = request.POST.get('memorylimit')
    testcase = request.POST.get('testcase')
    courseurl = request.POST.get('courseurl')
    language = request.POST.get('language')
    level = request.POST.get('level')
    tag = request.POST.get('tag')
    url = request.POST.get('url')
    course = Course.objects.filter(url=courseurl)
    if (courseurl == "loDjDEx" and type == '2') or (len(course)!=0 and type=='1'):
        pat = re.compile("(.*?)\n*--InEnd--\n(.*?)\n--OutEnd--\n*", re.DOTALL)
        testCaseList = pat.findall(testcase)
        testCasePath = testCaseRoot + url
        if os.path.exists(testCasePath):
            shutil.rmtree(testCaseRoot + url)
        os.makedirs(testCasePath)
        for i in range(len(testCaseList)):
            f = open(testCasePath + "/" + str(i + 1) + ".in", "w")
            f.writelines(testCaseList[i][0])
            f.close()
            f = open(testCasePath + "/" + str(i + 1) + ".out", "w")
            f.writelines(testCaseList[i][1])
            f.close()

        quiz=Quiz.objects.filter(url=url).first()
        quiz.name=name
        quiz.description = description
        quiz.input = input
        quiz.output = output
        quiz.sampleinput = sampleinput
        quiz.sampleoutput = sampleoutput
        quiz.timelimit = timelimit
        quiz.memorylimit = memorylimit
        quiz.language = language
        quiz.level = level
        quiz.tag = tag
        quiz.save()
        return JsonResponse(message)

def getCourseList(request,userName,type):
    message={'status':'200','courselist':[]}
    if type=='1':
        user=User.objects.filter(username=userName).first()
        courseList=Course.objects.filter(teacherid=user)
        for i in courseList:
            peopleNum=len(UserCourse.objects.filter(courseid=i))
            quizNum=len(Quiz.objects.filter(courseid=i))
            message['courselist'].append({'coursename':i.coursename,'detail':i.detail,'url':i.url,'teachername':i.teachername,'peoplenum':peopleNum,'quiznum':quizNum})
    if type=='0':
        user=User.objects.filter(username=userName).first()
        userCourse=UserCourse.objects.filter(studentid=user)
        for i in userCourse:
            quizList=Quiz.objects.filter(courseid=i.courseid)
            quizNum = len(quizList)
            solvedNum=0
            for j in range(quizNum):
                if Answerlist.objects.filter(quizid=quizList[j], status='ACCEPTED',userid=user).first() !=None:
                    solvedNum+=1
            message['courselist'].append(
                {'coursename': i.courseid.coursename, 'detail': i.courseid.detail, 'url': i.courseid.url, 'teachername': i.courseid.teachername,
                 'solvednum': solvedNum, 'quiznum': quizNum,'name':i.studentname})

    return JsonResponse(message)

def modifyCourse(request):
    # 要写用户验证
    message={'status':'200'}
    courseName=request.POST.get('coursename')
    detail=request.POST.get('detail')
    teacherName=request.POST.get('teachername')
    url=request.POST.get('url')
    course=Course.objects.filter(url=url).first()
    course.coursename=courseName
    course.detail=detail
    course.teachername=teacherName
    course.save()
    return JsonResponse(message)

def addCourse(request):
    # 要写用户验证
    message = {'status': '200'}
    courseName = request.POST.get('coursename')
    detail = request.POST.get('detail')
    teacherName = request.POST.get('teachername')
    userName = request.POST.get('username')
    teacher=User.objects.filter(username=userName).first()
    url = urlGenerator(7)
    course = Course(coursename = courseName,detail = detail,teachername = teacherName,url=url,teacherid=teacher)
    course.save()
    message['newcourse']={'coursename':courseName,'detail':detail,'url':url,'teachername':teacherName,'peoplenum':0,'quiznum':0}
    return JsonResponse(message)

def deleteCourse(request):
    #要写用户验证
    message={'status':'200'}
    url=request.POST.get('url')
    course = Course.objects.filter(url=url).first()
    course.delete()
    return JsonResponse(message)
def selectCourse(request):
    message={'status':'200'}
    url=request.POST.get('url')
    userName=request.POST.get('username')
    studentName = request.POST.get('studentname')
    course=Course.objects.filter(url=url).first()
    if course==None:
        message['status']='404'
        return JsonResponse(message)
    user=User.objects.filter(username=userName).first()
    usercourse =UserCourse.objects.filter(courseid=course,studentid=user)
    if len(usercourse)!=0:
        message['status'] = '403'
        return JsonResponse(message)
    usercourse=UserCourse(courseid=course,studentid=user,studentname=studentName)

    usercourse.save()
    quiznum=len(Quiz.objects.filter(courseid=course))
    message['newcourse'] = {'coursename': course.coursename, 'detail': course.detail, 'url': course.url, 'teachername': course.teachername,
                            'solvednum': 0, 'quiznum': quiznum}
    return JsonResponse(message)

def deleteSelectedCourse(request):
    message = {'status': '200'}
    url = request.POST.get('url')
    userName = request.POST.get('username')
    user = User.objects.filter(username=userName).first()
    course = Course.objects.filter(url=url).first()
    courseSelected=UserCourse.objects.filter(courseid=course,studentid=user).first()
    courseSelected.delete()
    return JsonResponse(message)
def modifyStudentCourseName(request):
    message = {'status': '200'}
    name = request.POST.get('name')
    url = request.POST.get('url')
    userName=request.POST.get('username')
    course = Course.objects.filter(url=url).first()
    user=User.objects.filter(username=userName).first()
    userCourse=UserCourse.objects.filter(courseid=course,studentid=user).first()
    userCourse.studentname=name
    userCourse.save()
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
                user=User.objects.filter(id=result['userid'])
                quiz=Quiz.objects.filter(id=result['quizid'])
                answerList=Answerlist(userid=user[0],
                                      quizid=quiz[0],
                                      code=result['code'],
                                      language=result['language'],
                                      status=result['status'],
                                      date=result['date'],
                                      usetime=result['usetime'],
                                      usememory=result['usememory'])
                answerList.save()
                print("保存成功")
                static_redis.hdel('result', i)
        time.sleep(3)
thread1 = judgeThread()
thread1.start()
thread1.daemon
thread2 = redisToMysqlThread()
thread2.start()
thread2.daemon