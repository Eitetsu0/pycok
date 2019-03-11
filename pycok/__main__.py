#! /bin/env python3
# -*- coding:utf-8 -*-

import time
import os
import sys

if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)

import pycok

if __name__ == '__main__':

    args = pycok.parser.parse_args()  # TODO

    # cok.lineSize = 6

    pycok.AUTOEXIT = 10
    pycok.INTERVAL = 10
    pycok.TIMEFORMAT = "%Y-%m-%d %a %H:%M:%S"  # "%a %b %d %H:%M:%S %Y"
    pycok.COKSPEED = 80

    if args.adbpath:
        pycok.ADBPATH = args.adbpath

    if args.speed:
        pycok.COKSPEED = int(args.speed)

    devices = []
    if args.device is None:
        d = pycok.pycok(mode='list', adbpath=pycok.ADBPATH).adb0.listdevice()
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
        devices = args.device[0][0]  # TODO

    if args.sleep:
        print('now:', time.strftime(pycok.TIMEFORMAT),
              ' ; ', 'sleep', args.sleep, 'seconds')
        time.sleep(args.sleep)
    s = pycok.schedule(configFile='./config.json',
                       device=devices, emu=args.emu)
    s.forceStop = True

    n = 0
    timestamp = 0
    while True:
        try:
            s.schedule()
        except Exception as e:
            if time.time()-timestamp > 600:
                n = 0
                timestamp = time.time()
            n += 1
            print('Error[%s]:' % time.strftime(pycok.TIMEFORMAT), e)
            print('count', n)
            if n >= 20:
                raise
            time.sleep(20)

    # if args.device:
    #     for dev in args.device:
    #         for d in dev:
    #             s = threading.Thread(target=schedule, args=(d, args.file))
    # s.start()
    # s.join()
    # print('%s ended' % s.getName())
