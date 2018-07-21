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
def monsterkill(cok, quick=False, lvl=None,times=10, lines=5,wait=100, preset=-1):
    if lines>1:
        lines-=1
    print('Starting Monster loop')
    if not quick:
        cok.resetCam(worldMap=True)
        cok.wait(10)
        cok.vipsearch('monster',lvl)
    elif lvl is not None:
        cok.vipsearch('monster',lvl)
    n = 0
    print(' loop', times, 'times in %d' % math.ceil(times/(lines)), 'groups ..')
    while n < times:
        n += 1
        cok.killMonsterQuickOnce(preset=preset)
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
        cok.wait(wait/40)
    print(' end.')


@subtask
def sheild(cok,hour=8,miss=60):
    cok.shield(hour=hour,miss=miss)


@subtask
def takePotion(cok,pos=0):
    print('takePotion')
    cok.adb0.tap(580,390)


@subtask
def sendRss2(cok,loc,n=1,interval=None):
    "loc: (x,y,kindom=None)"
    cok.resetCam(worldMap=True)
    cok.wait(1)
    cok.move2loc(*loc)
    cok.wait()
    cok.tap('center')
    cok.wait(1)
    cok.tap('ResourceHelp',(520,580,0.8))  # button in same position
    cok.tap('food',(430,410,0.2))
    cok.tap('wood',(430,315,0.2))
    cok.tap('iron',(430,600,0.2))
    # cok.tap('mithril',(430,315,0.2))
    cok.tap('help button',(440,1230))
    n-=1
    while n>0:
        print('.', end='', flush=True)
        time.sleep(interval)
        cok.tap('center')
        cok.wait(1)
        cok.tap('ResourceHelp',(520,580,0.8))
        cok.tap('food',(430,410,0.2))
        cok.tap('wood',(430,315,0.2))
        cok.tap('iron',(430,600,0.2))
        # cok.tap('mithril',(430,315,0.2))
        cok.tap('help button',(440,1230))
        n-=1
    print()


@subtask
def dailyRewards(cok,t='quest'):
    cok.resetCam()
    cok.tap('dailyRewards',(650,413,0.8))
    if 'signin' in t:
        cok.tap('collect',(450,1180,0.5))
        n=0
        for _ in range(5):
            cok.tap('chests',(165+n, 330,0.2))
            n+=125
        cok.tap('ok',(360,980,0.5))
    if 'quest' in t:
        cok.adb0.swipe((cok.scrX * 600/720, cok.scrY * 180/1280),(cok.scrX * 190/720, cok.scrY * 180/1280))
        cok.wait(4)
        cok.tap('dailyQuest',(350,180,0.2))
        n=0
        for _ in range(5):
            cok.tap('dailyChest',(90+n, 570, 0.1))
            cok.tap('collect',(360,1020,0.1))
            cok.tap()
            cok.tap()
            n+=125
        n=0
        for _ in range(3):
            cok.tap('weeklyChest',(160+n,390,0.1))
            n+=200
        cok.tap('collect',(360,970,5))


@subtask
def donate(cok):
    cok.resetCam()
    cok.tap('alliance')
    cok.wait(0.5)
    cok.adb0.swipe((cok.scrX * 360/720, cok.scrY * 1140/1280),(cok.scrX * 360/720, cok.scrY * 360/1280))
    cok.wait(1)
    cok.tap('Alliance Science & Donation',(360,660,0.3))
    cok.tap('recommend',(360,350,0.3))
    for _ in range(20):
        cok.tap('10k',(530,930,1))
        cok.tap('2k',(210,930,1))
        cok.tap('400',(360,805,1))


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

    if args.adbpath:
        pycok.ADBPATH=args.adbpath

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
    s=schedule(configFile='./config.json',device=devices,emu=args.emu)

    n=0
    while True:
        try:
            s.schedule()
        except Exception as e:
            n+=1
            print('Error[%s]:' % time.strftime(pycok.TIMEFORMAT), e)
            print('count',n)
            time.sleep(10)

    # if args.device:
    #     for dev in args.device:
    #         for d in dev:
    #             s = threading.Thread(target=schedule, args=(d, args.file))
    # s.start()
    # s.join()
    print('%s ended' % s.getName())
