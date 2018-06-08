#! /usr/bin/python3
# -*- coding:utf-8 -*-

import argparse
import json
import time
import multiprocessing
from contextlib import contextmanager
from os import path

from pyadb import adb


class CokException(Exception):
    pass


class pycok(object):
    __adbpath = ''

    def __init__(self, mode='adb', adbpath='default', device=None, package=None, vip=True):
        self.speed = 100
        if mode == 'api':
            # raise
            # TODO:webcok
            pass
        elif mode == 'adb':
            self.adb0 = adb(adbpath, device)
            self.set_screen(720, 1280)  # TODO:屏幕适配
            # set vip
            self.vip = vip

            if self.get_status() == 'sleeping':
                self.adb0.wakeup()
                self.wait()
                self.adb0.unlock()
                self.wait()

            # make sure the game is running
            # if self.get_status() == 'closing':
            if package:
                self.launchgame(package)
            else:
                try:
                    self.launchgame('gp')
                except CokException:
                    self.launchgame(0)
            self.wait(10)
            # else:  # TODO:
            #     self.__gamepackage = self.adb0.listPackage('cok')[0]

    # @property
    # def adbpath(self):
    #     return self.__adbpath

    # @adbpath.setter
    # def adbpath(self, path):
    #     # check the path
    #     __adbpath = path

    @property
    def speed(self):
        return int(100/self._waittingtime)

    @speed.setter
    def speed(self, val):
        if not isinstance(val, int):
            raise TypeError("pycok.speed should be int.")
        if val < 0:
            val = 0
        if val > 200:
            val = 200
        self._waittingtime = 100/val

    def get_status(self):
        s = self.adb0.adb('shell', 'dumpsys', 'window', 'policy')
        if s.find('mShowingLockscreen=false') < 0 or s.find('isStatusBarKeyguard=false') < 0:
            return 'sleeping'
        # TODO:cv
        self.adb0.adb('shell', 'am', 'kill-all')  # kill background processes
        self.wait()
        self.adb0.adb('shell', 'am', 'kill-all')  # kill background processes
        s = self.adb0.adb('shell', 'ps', 'com.hcg.cok').splitlines()[1:]
        if len(s) == 0:
            return 'closing'
        # return 'running'#TODO:

    def launchgame(self, p=None):
        packages = self.adb0.listPackage('cok')
        if isinstance(p, int):
            self.__gamepackage = packages[p]
        elif isinstance(p, str):
            i = 0
            while i <= len(packages):
                if i == len(packages):
                    raise CokException('no package name contains %s' % p)
                if p in packages[i]:
                    self.__gamepackage = packages[i]
                    break
                i += 1

        return self.adb0.launch(self.__gamepackage)

    def listGamepackage(self):
        return self.adb0.listPackage('cok')

    def killmonster(self, lv=None, interval=100, loop=10, preset=0, dragonWord=None):

        self.find(kind='monster', level=lv)
        return self.killmonsterin(preset=preset)

    def gather(self, preset=None, **kind):
        """
        kind:{kind1:level1,kind2:level2...}
        acceptable kind:
            'sawmill' , 'farm' , 'iron' , 'mithril' , 'gold'
        preset :
            a number in [-3,0];
            or a string in ('march','load','level','speed');
            default:None
        """

        s = {'sawmill', 'farm', 'iron', 'mithril', 'gold'}
        for key in kind:
            if key not in s:
                kind.pop(key)
        self.find(**kind)
        self.marchto(preset=preset)

    def marchto(self, x=None, y=None, preset=None, dragonWord=None):
        """
        preset: -3 ~ 0
             or a string in ('march','load','level','speed')
        """
        if x is not None and y is not None:
            self.move2loc(x, y)
        self.tap()
        self.tap('center')
        self.wait(0.5)
        self.tap('occupy')
        self.march(preset, dragonWord)

    def march(self, preset=None, dragonWord=None):
        'preset: -3 ~ 0'
        if preset is not None:
            self.selectpreset(preset)
        if dragonWord is not None:
            # TODO:
            pass
        self.adb0.tap(self.scrX * 600/720, self.scrY *
                      1210/1280)  # march button
        self.wait(0.5)

    def find(self, vip=None, **kind):
        """
        kind:{kind1:level1,kind2:level2...}
        acceptable kind:
            'sawmill' , 'farm' , 'iron' , 'mithril' , 'gold' , 'monster'
        """
        if vip is None:
            vip = self.vip
        if not isinstance(vip, bool):
            raise TypeError('arg \'vip\' should be bool type')
        if vip:
            if kind:
                key, lvl = kind.popitem()
                return self.vipsearch(key, lvl)
            return self.vipsearch()
        # none vip search:
        if not kind:
            raise Exception('kind must be given without vip search')
        # TODO:build method find with opencv

    def vipsearch(self, rsskind=None, lvl=None, unique=None):
        """
        acceptable kind:
            'sawmill' , 'farm' , 'iron' , 'mithril' , 'gold' , 'monster'
        """
        self.tap('vipsearch')
        self.wait(0.5)
        if rsskind == 'monster':
            self.adb0.tap(self.scrX * 100/720, self.scrY * 940/1280)
            if unique is not None:
                # TODO:opencv
                # search monster once
                self.adb0.tap(self.scrX * 438/720, self.scrY * 1210/1280)
                # self.tap('vipsearch')
                # tap vipsearch without killing tips
                self.adb0.tap(self.scrX * 50/720, self.scrY * 950/1280)
                # toggle 'unique'
                # cant judge without opencv
                self.adb0.tap(self.scrX * 100/720, self.scrY * 940/1280)
        elif rsskind is not None:
            # swipe so other icons shell be in their position
            self.adb0.swipe((self.scrX * 350/720, self.scrY * 940/1280),
                            (self.scrX * 190/720, self.scrY * 940/1280))
            self.wait(3)
        if rsskind == 'sawmill' or rsskind == 'wood':
            self.adb0.tap(self.scrX * 190/720, self.scrY * 940/1280)
        elif rsskind == 'farm' or rsskind == 'food':
            self.adb0.tap(self.scrX * 300/720, self.scrY * 940/1280)
        elif rsskind == 'iron':
            self.adb0.tap(self.scrX * 420/720, self.scrY * 940/1280)
        elif rsskind == 'mithril':
            self.adb0.tap(self.scrX * 530/720, self.scrY * 940/1280)
        elif rsskind == 'coin' or rsskind == 'gold':
            self.adb0.tap(self.scrX * 650/720, self.scrY * 940/1280)

        if lvl is not None:
            self.writeTextBox(self.scrX * 614/720, self.scrY * 1070/1280, lvl)

        # tap 'search' button
        self.adb0.tap(self.scrX * 438/720, self.scrY * 1210/1280)
        self.wait(0.5)

    def tap(self, obj='blank'):
        """
        acceptable obj by now:
            'blank','vipsearch','changeMap','keyback','tips','center'
        """
        if obj == 'blank':
            return self.adb0.tap(self.scrX * 550/720, self.scrY * 50/1280)
        if obj == 'vipsearch':
            self.resetCam(worldMap=True)
            # TODO:opencv
            # return self.adb0.tap(self.scrX* 50/720,self.scrY* 950/1280)
            return self.adb0.tap(self.scrX * 50/720, self.scrY * 870/1280)
        if obj == 'changeMap':
            return self.adb0.tap(self.scrX * 80/720, self.scrY * 1240/1280)
        if obj == 'keyback':
            return self.adb0.input('keyevent', 'KEYCODE_BACK')
        if obj == 'tips':
            # TODO:opencv needed
            return self.adb0.tap(self.scrX * 50/720, self.scrY * 1065/1280)
        if obj == 'center':  # a little lower than center
            return self.adb0.tap(self.scrX*0.5, self.scrY * 690/1280)
        if obj == 'occupy':
            return self.adb0.tap(self.scrX * 520/720, self.scrY * 650/1280)

    # def removetips(self):
    #     self.tap('tips')
    #     self.resetCam(worldMap=True)

    def killmonsterin(self, x=None, y=None, preset=0, dragonWord=None):
        'similar to marchto(), by default: the center of screen'
        if (x is None and y is not None) or (x is not None and y is None):
            raise Exception()
        if x is not None and y is not None:
            self.move2loc(x, y)
            # self.adb0.input('tap',str(self.scrX* 550/720),str(int(self.scrY* 50/1280)))
        self.wait()
        # tap monster ps:not the center of screen
        self.adb0.tap(self.scrX * 321/720, self.scrY * 657/1280)
        self.wait(0.5)
        # tap Attack button
        self.adb0.input('tap', str(self.scrX//2), str(int(self.scrY*0.73)))
        self.wait(0.3)
        self.march(preset, dragonWord)

    def move2loc(self, x=None, y=None, kingdom=None):
        "move camera to x,y in kingdom move to last coord with no arg"
        self.adb0.tap(self.scrX//2, self.scrY*980/1280)
        self.wait(0.2)
        if isinstance(kingdom, int):
            self.writeTextBox(self.scrX//2, self.scrY*555/1280, kingdom)
        if isinstance(x, int):
            self.writeTextBox(self.scrX*200/720, self.scrY*650/1280, x)
        if isinstance(y, int):
            self.writeTextBox(self.scrX*500/720, self.scrY*650/1280, y)
        self.adb0.tap(self.scrX//2, self.scrY*790/1280)
        if isinstance(kingdom, int):
            self.wait(2)
        else:
            self.wait(0.5)

    def resetCam(self, *, worldMap=False):
        n = 5
        while n > 0:
            n -= 1
            self.tap('keyback')
            self.wait(0.5)
        self.wait()
        self.tap('blank')
        self.wait(0.5)
        if worldMap:
            self.tap('changeMap')
            self.wait(2.5)

    def set_screen(self, x, y):
        self.scrX = x
        self.scrY = y

    def selectpreset(self, preset=0):
        """
        preset can be :
            a number in [-3,0];
            a string in ('march','load','level','speed')
        """
        if isinstance(preset, int):
            if preset > 0:
                preset = 0
            if preset < -3:
                preset = -3
            return self.adb0.input('tap', str(int(660+preset*70)), str(int(self.scrY * 335/1280)))
        elif isinstance(preset, str):
            self.adb0.tap(self.scrX * 70/720, self.scrY * 1210/1280)
            if preset == 'march':
                return self.adb0.tap(self.scrX * 180/720, self.scrY * 880/1280)
            elif preset == 'load':
                return self.adb0.tap(self.scrX * 180/720, self.scrY * 960/1280)
            elif preset == 'level':
                return self.adb0.tap(self.scrX * 180/720, self.scrY * 1040/1280)
            elif preset == 'speed':
                return self.adb0.tap(self.scrX * 180/720, self.scrY * 1120/1280)
            else:
                return self.adb0.tap(self.scrX * 70/720, self.scrY * 1210/1280)

    def killMonsterQuickOnce(self, preset=0):
        if not self.vip:
            return
        self.vipsearch()
        #self.adb0.input('tap',str(self.scrX* 550/720),str(int(self.scrY* 50/1280)))
        self.wait(1)
        self.killmonsterin(preset=preset)

    def writeTextBox(self, x, y, text, delete=5):
        self.adb0.tap(x, y)
        self.wait(0.2)
        while delete > 0:
            delete -= 1
            self.adb0.input('keyevent', 'KEYCODE_DEL')
        self.adb0.input('text', str(text))
        self.wait()
        self.adb0.input('keyevent', 'KEYCODE_NUMPAD_ENTER')
        self.wait()

    def wait(self, val=0.2):
        if val is not None:
            return time.sleep(self._waittingtime*val)

    def getBatteryLevel(self):
        inf = self.adb0.adb('shell', 'dumpsys', 'battery').splitlines()
        for i in inf:
            i = i.split()
            if i[0] == 'level:':
                return int(i[1])


####################################################################################################
if __name__ == '__main__':
    cok = pycok()

    cok.vipsearch('monster')
    n = 7
    while n > 0:
        n -= 1
        cok.killMonsterQuickOnce()
        cok.wait(1)
        print('Monster loop left', n, 'times..')
        # cok.resetCam()

    print("\nend")
####################################################################################################


###################### schedul section ####
parser = argparse.ArgumentParser(prog='coktask', description='Run cok tasks')
parser.add_argument('-v', '--version', action='version',
                    version='%(prog)s 0.5')
parser.add_argument('-s', '--server', action='version',
                    version='distributed sys is under working', help='connect to a remote server')
parser.add_argument('-f', '--task-file=', dest='file',
                    help="a taskfile or a config file that contains a tasklist. If the given file dosen't exist or dosen't contain a tasklist pycok will create one or rewrite it with default module")
parser.add_argument('-d', '--device', action='append',
                    nargs='+', help='add devices scrpit should be used to')
parser.add_argument('--sleep', type=int,
                    help='add devices scrpit should be used to')

cok = pycok()

_TASKLIST_default = [
    {
        # name of the task
        'name': 'gather',
        # a subtask run first
        'prepare': [
            # name of the subtask, {dict of possible args}
            'monsterkill', {}
        ],
        # the main subtask
        'run': [
            'quickgather', {}
        ],
        # a subtask run after 'run' is finished
        'after': None,
        # repeat this Task 'nloop' times by 'interval', -1 for a endless loop
        'nloop': -1,
        # next time to run this task
        'time': int(time.time()),
        'interval': 3600+1200,  # 1h20m
        # time.mktime((2018, 5, 29, 3, 57, 3, 1, 149, 0))), #2:57
        #if start>time : time=start
        'start': 0,
        # stop repeating task if until<time.time() and until>0
        'until': -1,  # int(time.mktime((2018, 5, 29, 3, 57, 3, 1, 149, 0))),
        # when task stoped by over 'until' ,start+=every, until+=every
        'every': 0,
        'enable': False,
        'fastrun': True,  # run this task as soon as manager started
        # 如果fastrun==True，start和until都代表相对时间，否则为绝对时间
    },

]


class TaskList(list):
    def __init__(self, it):
        tasklist = []
        for task in it:
            tasklist.append(Task(task))
        super().__init__(tasklist)

    def __setitem__(self, index, val):
        return super().__setitem__(index, Task(val))

    def __getitem__(self, index):
        return super().__getitem__(index)

    def append(self, task):
        super().append(Task(task))


class SubTask(tuple):
    pass  # TODO


class Task(dict):
    __slots__ = tuple(list(_TASKLIST_default[0].keys())+['countdown'])

    def __init__(self, it=None, **kw):
        d = {}
        if it:
            for key in it:
                if key in self.__slots__:
                    d[key] = it[key]
        if kw:
            for key in kw:
                if key in self.__slots__:
                    d[key] = kw[key]
        if 'nloop' in d:
            self.countdown = d['nloop']
        else:
            self.countdown = -1
        super().__init__(d)

    def __getattr__(self, key):
        if key not in self:
            return _TASKLIST_default[0][key]
        return self[key]

    def __setattr__(self, key, value):
        if key not in self.__slots__:
            raise AttributeError(
                "Task object don't have a attribute '%s'" % key)
        self[key] = value

    def __getitem__(self, key):
        # if key not in self.__slots__:
            #raise KeyError("Task object don't have a attribute '%s'"%key)
        try:
            return super().__getitem__(key)
        except KeyError:
            return _TASKLIST_default[0][key]

    def __setitem__(self, key, value):
        if key in self.__slots__:
            return super().__setitem__(key, value)
        raise KeyError("a Task don't have a attribute named %s" % key)

    def isActive(self):
        """
        返回一个every>=0的任务是否处于 [ start, until ) 的区间内
        并且 countdown!=0
        """
        if self.enable:
            # if self.every > 0:
            #     assert(self.start >= 0 and self.until > self.start)
            #     self.updateEvery()
            if self.start > time.time():
                return False
            if self.countdown == 0:
                return False
            if self.until > self.start and self.time > self.until:
                return False
            return True
        return False

    def updateEvery(self):
        "prepare for next outer loop"
        assert(self.every > 0)

        if not self.isActive():
            if self.until > 0:
                dur = self.until-self.start
                while self.until < time.time():
                    self.until += self.every
                self.start = self.until-dur
            else:
                if time.time() > self.start:
                    self.start += self.every
                while self.start + self.every < time.time():
                    self.start += self.every

            self.countdown = self.nloop
            if self.start > time.time():
                self.time = self.start
            else:
                self.time = time.time()

    def runTask(self, sub=None):  # TODO
        if sub:
            return self.__runSub(self[sub])
        if self.countdown > 0:
            self.countdown -= 1
        if self.fastrun:
            self.time = time.time()+self.interval
        else:
            self.time += self.interval

        if self.prepare:
            self.runTask('prepare')
        if self.run:
            self.runTask('run')
        if self.after:
            self.runTask('after')

    def __runSub(self, s):
        if len(s) > 1:
            return subp.get(s[0])(**s[1])
        else:
            return subp.get(s[0])()


__tasklist = None


@contextmanager
def GetTasklist(file=None, load=False, update=False):
    """
    usage:
        with TasksFile() as tasklist:
            mycode...
    """
    global __tasklist
    if file is None and not __tasklist:
        file = './config.json'
    config = None
    if file and path.exists(file):
        with open(file, 'r') as f:
            config = json.load(f)
    else:
        update = True

    if load or not __tasklist:  # read file only once
        if isinstance(config, dict):
            __tasklist = TaskList(config.get('tasklist', _TASKLIST_default))
        elif isinstance(config, list):
            __tasklist = TaskList(config)
        else:
            __tasklist = TaskList(_TASKLIST_default)

    yield __tasklist

    if update:
        if isinstance(config, dict):
            config['tasklist'] = __tasklist
        else:
            config = __tasklist
        with open(file, 'w') as f:
            json.dump(config, f, indent=4, sort_keys=True)


def addtask(**ntask):
    with GetTasklist() as tasklist:
        tasklist.append(Task(ntask))


subp = {}


def subtask(funcOrName):
    global subp
    if isinstance(funcOrName, str):
        def warper(func):
            subp[funcOrName] = func
        return warper
    subp[funcOrName.__name__] = funcOrName


AUTOEXIT = 60
TIMEFORMAT = "%Y-%m-%d %a %H:%M:%S"  # "%a %b %d %H:%M:%S %Y"
INTERVAL = 10


# check tasklist


def init(listFile=None):
    if cok.get_status() == 'sleeping':
        cok.adb0.wakeup()
        cok.wait()
        cok.adb0.unlock()
        cok.wait()

    # make sure the game is running
    cok.launchgame()
    cok.wait(10)

    with GetTasklist(listFile, True) as tasklist:
        for task in tasklist:
            # if not task.enable: #ignor disabled tasks
            #     continue
            if task.fastrun:
                lasts = task.until - task.start
                task.start += int(time.time())
                task.time = task.start
                if task.until > 0:
                    task.until = task.start + lasts
            elif task.every > 0:
                task.updateEvery()
                if task.time < task.start or task.time > task.until:
                    task.time = task.start
            # 把开始时间是很久之前的任务改到还差一个‘interval’就要等的时间点
            if task.nloop != 0 and task.interval > 0:
                while task.time+task.interval < time.time():
                    task.time += task.interval


# run task loop
###################################
def schedule(device=None, package=None):
    if device:
        cok.adb0.device = device

    informIdle = True
    sleep = False
    battery = cok.getBatteryLevel()

    with GetTasklist() as tasklist:
        while True:
            soon = None
            for task in tasklist:
                assert(type(task) == Task)
                if task.isActive() and task.time <= time.time():
                    startTime = time.time()
                    print('Running task \'%s\'in' % task['name'], time.strftime(
                        TIMEFORMAT, time.localtime()))

                    task.runTask()

                    print('Task \'%s\' ended in' % task['name'], time.strftime(
                        '%Hhr%Mm%Ss', time.gmtime(time.time()-startTime)))
                    print('\n')
                    informIdle = True

                if task.every > 0:
                    task.updateEvery()

                if task.enable:
                    if soon is None:
                        soon = task
                    elif task.isActive() or task.start > time.time():
                        if task.get('time', soon['time']) < soon['time']:
                            soon = task

            if informIdle:
                informIdle = False
                timeIdleStart = int(time.time())
                print('idle ...')
                if soon is not None:
                    nextTime = time.strftime(
                        TIMEFORMAT, time.localtime(soon['time']))
                    print('the very soon task is \'%s\' at' %
                          soon['name'], nextTime)
                    print('\n')
                else:
                    print('none task is waiting..')

            if soon is None:
                if not sleep:
                    cok.adb0.sleep()
                    sleep = True
                exitCountdown = AUTOEXIT-(int(time.time())-timeIdleStart)
                print('program will stop in %2ds' %
                      exitCountdown, end='\r', flush=True)
                if exitCountdown <= 0:
                    print("\nAuto exit")
                    # exit()
                    return 0

            time.sleep(INTERVAL)

            if not sleep:
                if cok.get_status() == 'sleeping':
                    cok.adb0.wakeup()
                    cok.wait()
                    cok.adb0.unlock()
                    cok.wait()
                    cok.launchgame()
                    cok.wait(10)
                battery = cok.getBatteryLevel()
                if battery < 20:
                    cok.adb0.sleep()
                    sleep = True
                elif soon.time-time.time() > 600:
                    cok.adb0.sleep()
                    sleep = True
            elif soon is not None and soon.time-time.time() < 120:
                cok.adb0.wakeup()
                cok.wait()
                cok.adb0.unlock()
                cok.wait()
                cok.launchgame()
                cok.wait(10)
                sleep = False
