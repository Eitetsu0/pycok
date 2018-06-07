#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import math
import time

from pycok import cok, subtask, schedule
import pycok

cok.speed = 80
cok.lineSize = 6

pycok.AUTOEXIT = 10
pycok.INTERVAL = 10
pycok.TIMEFORMAT = "%Y-%m-%d %a %H:%M:%S"  # "%a %b %d %H:%M:%S %Y"


##########################################
# subtasks
##########################################
@subtask
def relaunch(hard=False):
    if hard:
        packages = cok.adb0.listPackage('cok')
        for p in packages:
            cok.adb0.adb('shell','am','force-stop',p)
    cok.launchgame()
    cok.wait(10)


@subtask
def vipsearch(rsskind=None, lvl=None, unique=None):
    cok.vipsearch(rsskind=rsskind, lvl=lvl, unique=unique)


@subtask
def quickgather(lines=3,stype='iron',lv=6,preset=None):
    # print('Garthering start...')
    cok.vipsearch(stype, lv)
    n = lines
    while n > 0:
        n -= 1
        cok.gather(preset=preset)
        print('    gathering line left', n, ' .')
        cok.wait(2)


@subtask
def monsterkill(times=10, lines=5,wait=100):
    if lines>1:
        lines-=1
    print('Starting Monster loop')
    cok.vipsearch('monster')
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

##############################################################


if __name__ == '__main__':

    args = pycok.parser.parse_args()  # TODO

    if args.sleep:
        time.sleep(args.sleep)

    if args.device is None:
        d = cok.adb0.listdevice()
        if len(d) == 0:
            print('no devices connected')
            exit(1)
        elif len(d) > 1:
            print('multiple connected devices:')
            i = 0
            while i < len(d):
                print('    [%d] %s' % (i, d))
                i += 1
            s = int(input('select number device:'))

    pycok.init()
    schedule()
    # if args.device:
    #     for dev in args.device:
    #         for d in dev:
    #             s = threading.Thread(target=schedule, args=(d, args.file))
    # s.start()
    # s.join()
    print('%s ended' % s.getName())
