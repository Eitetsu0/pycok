#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import math
import time

from pycok import subtask, schedule
import pycok


##########################################
# subtasks
##########################################
@subtask
def relaunch(cok,hard=False):
    if hard:
        packages = cok.adb0.listPackage('cok')
        for p in packages:
            cok.adb0.adb('shell','am','force-stop',p)
    cok.launchgame()
    cok.wait(10)


@subtask
def vipsearch(cok,rsskind=None, lvl=None, unique=None):
    cok.vipsearch(rsskind=rsskind, lvl=lvl, unique=unique)


@subtask
def quickgather(cok,lines=3,stype='iron',level=6,preset=None):
    # print('Garthering start...')
    cok.vipsearch(stype, level)
    cok.gather(preset=preset,**{stype:level})
    n = lines - 1
    print('    gathering line left', n, '.')
    while n > 0:
        n -= 1
        cok.gather(preset=preset)
        print('    gathering line left', n, '.')
        cok.wait(1)


@subtask
def monsterkill(cok, lvl=None,times=10, lines=5,wait=100):
    if lines>1:
        lines-=1
    print('Starting Monster loop')
    cok.resetCam(worldMap=True)
    cok.wait(10)
    cok.vipsearch('monster',lvl)
    n = 0
    print(' loop', times, 'times in %d' % math.ceil(times/(lines)), 'groups ..')
    while n < times:
        n += 1
        cok.killMonsterQuickOnce(preset=-1)
        print('    Monster loop left', times-n, 'times.')
        cok.wait(1)
        if n<times and n % (lines) == 0:
            print('waitting ...', end='', flush=True)
            for _ in range(20):
                print('.', end='', flush=True)
                cok.wait(wait/20)
            print(' continue.')
    print('waitting ...', end='', flush=True)
    for _ in range(20):
        print('.', end='', flush=True)
        cok.wait(wait/20)
    print(' end.')


@subtask
def sheild(cok,hour=8,miss=60):
    cok.shield(hour=hour,miss=miss)


@subtask
def takePotion(cok,pos=0):
    print('takePotion')
    cok.adb0.tap(580,390)

###############################################################
# end subtasks
###############################################################


if __name__ == '__main__':

    args = pycok.parser.parse_args()  # TODO

    # cok.lineSize = 6

    pycok.AUTOEXIT = 10
    pycok.INTERVAL = 10
    pycok.TIMEFORMAT = "%Y-%m-%d %a %H:%M:%S"  # "%a %b %d %H:%M:%S %Y"
    pycok.COKSPEED = 80

    if args.speed:
        pycok.COKSPEED=int(args.speed)

    devices = []
    if args.device is None:
        d = pycok.pycok(mode='list').adb0.listdevice()
        if len(d) == 0:
            print('no device connected')
            exit(1)
        elif len(d) > 1:
            print('multiple connected devices:')
            i = 0
            while i < len(d):
                print('    [%d] %s' % (i, d[i]))
                i += 1
            s = int(input('select device:'))
            devices = d[s][0]
    else:
        devices=args.device[0][0]  # TODO

    if args.sleep:
        print('now:',time.strftime(pycok.TIMEFORMAT), ' ; ', 'sleep',args.sleep,'seconds')
        time.sleep(args.sleep)
    s=schedule(configFile='./config.json',device=None,emu=args.emu)
    s.schedule()

    # if args.device:
    #     for dev in args.device:
    #         for d in dev:
    #             s = threading.Thread(target=schedule, args=(d, args.file))
    # s.start()
    # s.join()
    print('%s ended' % s.getName())
