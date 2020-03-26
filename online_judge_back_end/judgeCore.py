import ljudge
import redis
from datetime import datetime
# NON_ZERO_EXIT_CODE
# MEMORY_LIMIT_EXCEEDED
# TIME_LIMIT_EXCEEDED
# OUTPUT_LIMIT_EXCEEDED
# PRESENTATION_ERROR
# ACCEPTED
# RUNTIME_ERROR
# FLOAT_POINT_EXCEPTION
# SEGMENTATION_FAULT
# WRONG_ANSWER
# SKIPPED
from online_judge_back_end.models import Quiz


def run(receiver,pool):
    static_redis=redis.Redis(connection_pool=pool)

    opts = {
        'user-code': receiver['filename'],
        'max-cpu-time': int(receiver['timelimit'])/1000,
        'max-compiler-cpu-time': '10',
        'max-memory': int(receiver['memorylimit'])*1024,
        'testcase': receiver['testcase']
    }
    result='ACCEPTED'
    a=''
    try:
        a = ljudge.run(opts)
    except:
        result='COMPILATION_ERROR'
    memory=0
    time=0
    print(a)
    if result=="COMPILATION_ERROR":
        print("sb")
    if result=="COMPILATION_ERROR" or a['compilation']['success']==False:
        result='COMPILATION_ERROR'
    else:
        for i in a['testcases']:
            if i['result']!='ACCEPTED':
                if i['result']=='TIME_LIMIT_EXCEEDED':
                    time = -1
                if i['result'] == 'MEMORY_LIMIT_EXCEEDED':
                    memory = -1
                result=i['result']
                break
            if i['memory']>memory:
                memory=i['memory']
            if i['time']>time:
                time=i['time']
    memory/=1024
    time*=1000
    quiz=Quiz.objects.filter(url=receiver['quizurl'])
    judge_result={'userid':receiver['userid'],
                  'quizid':quiz[0].id,
            'code':receiver['filename'],
            'language':receiver['language'],
            'status':result,
            'date':datetime.now(),
            'usetime':time,
            'usememory':memory
            }
    static_redis.hset('result',receiver['tempid'], str(judge_result))




