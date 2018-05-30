#! /usr/bin/python3
# -*- coding:utf-8 -*-
import time,json,os
from contextlib import contextmanager
import coktask

TASKLIST=[
    {
        'name':'gather',
        'device':None,
        'prepare':[
            'monsterkill',{}
        ],
        'run':[
            'quickgather',{}
        ],
        'after':None,
        'loop':-1,      #loop n times , -1 for endless
        'every':3600+1200, #1h20m
        'time':int(time.mktime((2018, 5, 29, 3, 57, 3, 1, 149, 0))), #2:57
        'until':-1,#int(time.mktime((2018, 5, 29, 3, 57, 3, 1, 149, 0))),
        'enable':True,
        'fastrun':True,  #run this task as soon as manager started
    },
    
]
@contextmanager
def TasksFile(file='./config.json'):
    """
    usage: 
        with TasksFile() as tasklist:
            mycode...
    """
    config={}
    if os.path.exists(file):
        with open(file,'r+') as f:
            config=json.load(f)

    assert isinstance(config,dict), 'config isn\'t a dict'    

    tasklist=config.get('tasklist',TASKLIST)
    yield tasklist
    config['tasklist']=tasklist
    with open(file,'w') as f:
        json.dump(config,f,indent=4)


def addtask(**ntask):
    with TasksFile() as tasklist: 
        tasklist.append(ntask)


#TASKLIST=[]
#####################################
AUTOEXIT=coktask.AUTOEXIT




TIMEFORMAT="%Y-%m-%d %a %H:%M:%S" #"%a %b %d %H:%M:%S %Y"

def runATask(s):
    if len(s)>1:
        return getattr(coktask,s[0])(**s[1])
    else:
        return getattr(coktask,s[0])()

#chack tasklist
with TasksFile() as tasklist:
    for task in tasklist:
        if not task['enable']:
            continue
        if task['fastrun']:
            task['time']=int(time.time())
        if task['until']>0 and task['until']<time.time():
            task['enable']=False
        

#run task loop
informIdle=True
while True:
    soon=None
    with TasksFile() as tasklist:
        index=0
        while index<len(tasklist):
            task=tasklist[index]
            if task['enable'] and task['time'] <= time.time():
                if task['until']>0 and task['until']<time.time():
                    task['enable']=False
                    continue

                informIdle=True
                if task['loop']!=0:
                    if task['loop']>0:
                        task['loop']-=1
                    task['time']=int(time.time())+task['every']
                else:
                    task['enable']=False
                
                startTime=time.time()
                print('Running task \'',task['name'],'\'in',time.strftime(TIMEFORMAT,time.localtime()))
                if task['prepare']!=None:
                    print('    preparing ...')
                    runATask(task['prepare'])
                if task['run']:
                    print('    task \'',task['name'],'\'start at',time.strftime(TIMEFORMAT,time.localtime()))
                    runATask(task['run'])
                if task['after']:
                    print('    running \'after\' ...')
                    runATask(task['after'])
                print('Task \'%s\' ended in'%task['name'],time.strftime('%X',time.gmtime(time.time()-startTime)))
                print('\n')

            if task["enable"]:
                if soon==None:
                    soon=index
                elif task.get('time',tasklist[soon]['time'])<tasklist[soon]['time']:
                    soon=index
            index+=1
    
    if informIdle:
        informIdle=False
        timeIdleStart=int(time.time())
        print('idle ...')
        if soon!=None:
            nextTime=time.strftime(TIMEFORMAT,time.localtime(tasklist[soon]['time']))
            print('the very soon task is \'%s\' at'%tasklist[soon]['name'], nextTime)
            print('\n')
        else:
            print('none task is waiting..')

    if soon==None:
        exitCountdown=AUTOEXIT-( int(time.time())-timeIdleStart)
        print('program will stop in %2ds'%exitCountdown,end='\r',flush=True)
        if exitCountdown<=0:
            print("\nAuto exit")
            exit()

    time.sleep(10)########

