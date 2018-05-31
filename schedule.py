#! /usr/bin/python3
# -*- coding:utf-8 -*-
import time,json,os
from contextlib import contextmanager
import pycok

cok=pycok.pycok()

_TASKLIST_default=[
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
        'time':int(time.time()),
            #time.mktime((2018, 5, 29, 3, 57, 3, 1, 149, 0))), #2:57
        'until':-1,#int(time.mktime((2018, 5, 29, 3, 57, 3, 1, 149, 0))),
        'enable':True,
        'fastrun':True,  #run this task as soon as manager started
    },

]

class TaskList(list):
    def __init__(self,it):
        tasklist=[]
        for task in it:
            tasklist.append(Task(task))
        super().__init__(tasklist)

class Task(dict):
    __slots__=tuple(_TASKLIST_default[0].keys())

    def __init__(self, it=None,**kw):
        d={}
        if it:
            for key in it:
                if key in self.__slots__:
                    d[key]=it[key]
        if kw:
            for key in kw:
                if key in self.__slots__:
                    d[key]=kw[key]
        super().__init__(d)

    def __getattr__(self, key):
        if key not in self:
            return _TASKLIST_default[0][key]
        return self[key]

    def __setattr__(self, key, value):
        if key not in self.__slots__:
            raise AttributeError("Task object don't have a attribute '%s'"%key)
        self[key] = value

    def __getitem__(self,key):
        #if key not in self.__slots__:
            #raise KeyError("Task object don't have a attribute '%s'"%key)
        try:
            return super().__getitem__(key)
        except KeyError:
            return _TASKLIST_default[0][key]

    def __setitem__(self,key,value):
        if key in self.__slots__:
            return super().__setitem__(key,value)
        #raise KeyError("a Task don't have a attribute named %s"%key)




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

    tasklist=TaskList(config.get('tasklist',_TASKLIST_default))
    yield tasklist

    config['tasklist']=tasklist
    with open(file,'w') as f:
        json.dump(config,f,indent=4)


def addtask(**ntask):
    with TasksFile() as tasklist:
        tasklist.append(ntask)


#TASKLIST=[]
#####################################
import coktask
#class coktask:
AUTOEXIT=10
TIMEFORMAT="%Y-%m-%d %a %H:%M:%S" #"%a %b %d %H:%M:%S %Y"

#def init(tasks):
#    coktask.AUTOEXIT=tasks["AUTOEXIT"]
#    coktask.TIMEFORMAT=tasks["TIMEFORMAT"]
#    for key in tasks:
#        if isinstance(task[key],function):
#            setattr(coktask,key,task[key])



def __runATask(s):
    if len(s)>1:
        return getattr(coktask,s[0])(**s[1])
    else:
        return getattr(coktask,s[0])()

#check tasklist : set fastruns ,
def init():
    with TasksFile() as tasklist:
        for task in tasklist:
            if not task.enable:
                continue
            if task.fastrun:
                task.time=int(time.time())
            #if task['until']>0 and task['until']<time.time():
            #    task.enable=False

def isTaskEnable(task):
    if task.enable:
        if task.until>0 and task.time>task.until:
            return False
        return True
    return False

#run task loop
informIdle=True
#while True:##################################
def schedule(listFile=None):
    global informIdle,timeIdleStart
    soon=None
    with TasksFile(listFile) as tasklist:
        index=0
        while index<len(tasklist):
            task=tasklist[index]
            if task.enable and task['time'] <= time.time():
                if task['until']>0 and task['until']<time.time():
                    task.enable=False
                    continue

                informIdle=True
                if task['loop']!=0:
                    if task['loop']>0:
                        task['loop']-=1
                    task['time']=int(time.time())+task['every']
                else:
                    task.enable=False

                startTime=time.time()
                print('Running task \'',task['name'],'\'in',time.strftime(TIMEFORMAT,time.localtime()))
                if task['prepare']!=None:
                    print('    preparing ...')
                    __runATask(task['prepare'])
                if task['run']:
                    print('    task \'',task['name'],'\'start at',time.strftime(TIMEFORMAT,time.localtime()))
                    __runATask(task['run'])
                if task['after']:
                    print('    running \'after\' ...')
                    __runATask(task['after'])
                print('Task \'%s\' ended in'%task['name'],time.strftime('%X',time.gmtime(time.time()-startTime)))
                print('\n')

            task.enable=isTaskEnable(task)
            if task["enable"]:
                if soon==None:
                    soon=task
                elif task.get('time',soon['time'])<soon['time']:
                    soon=task
            index+=1

    if informIdle:
        informIdle=False
        timeIdleStart=int(time.time())
        print('idle ...')
        if soon!=None:
            nextTime=time.strftime(TIMEFORMAT,time.localtime(soon['time']))
            print('the very soon task is \'%s\' at'%soon['name'], nextTime)
            print('\n')
        else:
            print('none task is waiting..')

    if soon==None:
        exitCountdown=AUTOEXIT-( int(time.time())-timeIdleStart)
        print('program will stop in %2ds'%exitCountdown,end='\r',flush=True)
        if exitCountdown<=0:
            print("\nAuto exit")
            exit()

    #time.sleep(10)########

