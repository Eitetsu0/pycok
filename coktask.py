#! /usr/bin/python3
# -*- coding:utf-8 -*-

import time
import json,os,math
import schedule

cok=schedule.cok

cok.speed=80
cok.lineSize=6
AUTOEXIT=10

TIMEFORMAT="%Y-%m-%d %a %H:%M:%S" #"%a %b %d %H:%M:%S %Y"

#tasks
def quickgather():
    print('Garthering start...')
    cok.vipsearch('iron',6)
    n=cok.lineSize
    while n>0:
        n-=1
        cok.gather(preset='speed')
        print('    gathering line left',n,' .')
        cok.wait(2)

def monsterkill(times=10,lines=5):
    print('Starting Monster loop')
    cok.vipsearch('monster')
    n=0
    print(' loop', times, 'times in %d'%math.ceil(times/lines),'groups ..')
    while n<times:
        n+=1
        cok.killMonsterQuickOnce(preset=-1)
        print('    Monster loop left',times-n,'times.')
        cok.wait(1)
        if n%(lines-1)==0:
            print('waitting ...',end='',flush=True)
            for _ in range(20):
                cok.wait(5)
                print('.',end='',flush=True)
            print(' continue.')



if __name__=='__main__':
    schedule.init()
    while True:
        schedule.schedule()
        time.sleep(10)
