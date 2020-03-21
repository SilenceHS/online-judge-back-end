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
def run(receiver,pool):
    static_redis=redis.Redis(connection_pool=pool)

    opts = {
        'user-code': receiver['filename'],
        'max-cpu-time': int(receiver['timelimit'])/1000,
        'max-compiler-cpu-time': '10',
        'max-memory': int(receiver['memorylimit'])*1024,
        'testcase': receiver['testcase']
    }
    result=''
    try:
        a = ljudge.run(opts)
    except:
        result='COMPILATION_ERROR'
    memory=0
    time=0
    print(a)
    result = 'ACCEPTED'
    if(a['compilation']['success'])==False:
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
    judge_result={'userid':receiver['userid'],
            'code':receiver['filename'],
            'language':receiver['language'],
            'status':result,
            'date':datetime.now(),
            'usetime':time,
            'usememory':memory
            }
    static_redis.hset('result',receiver['tempid'], str(judge_result))




