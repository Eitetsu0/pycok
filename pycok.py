#! /usr/bin/python3
# -*- coding:utf-8 -*-

import argparse
import json
import time
import multiprocessing
from os import path

from pyadb import adb


class CokException(Exception):
    pass


class pycok(object):
    # __adbpath = ''

    def __init__(self, mode='adb', adbpath='default', device=None, package=None, vip=True):
        self.speed = 100
        self.acc = ''
        if mode == 'api':
            # raise
            # TODO:webcok
            pass
        elif mode == 'list':
            self.adb0 = adb(adbpath)
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

            if package:
                self.launchgame(package, update=True)
            else:
                try:
                    self.launchgame('gp', update=True)
                except CokException:
                    self.launchgame(0, update=True)
            self.wait()

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

    @property
    def package(self):
        return self.__gamepackage

    # @package.setter
    # def package(self,val):
    #     return self.launchgame(val,True)

    def get_status(self):
        s = self.adb0.adb('shell', 'dumpsys', 'window', 'policy')
        if ('mShowingLockscreen=false'not in s) or ('isStatusBarKeyguard' in s and 'isStatusBarKeyguard=false' not in s):
            return 'sleeping'
        # TODO:cv
        self.adb0.adb('shell', 'am', 'kill-all')  # kill background processes
        self.wait()
        self.adb0.adb('shell', 'am', 'kill-all')  # kill background processes
        s = self.adb0.adb('shell', 'ps', 'com.hcg.cok').splitlines()[1:]
        if len(s) == 0:
            return 'closing'
        # return 'running'#TODO:

    def launchgame(self, p=None, update=False):
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
        if not update:
            return self.adb0.launch(self.__gamepackage)

    def forceStop(self):
        return self.adb0.adb('shell', 'am', 'force-stop', self.__gamepackage)

    def listGamepackage(self):
        return self.adb0.listPackage('cok')

    def killmonster(self, lv=None, interval=100, loop=10, preset=0, dragonWord=None):

        self.find(kind='monster', level=lv)
        return self.killmonsterin(preset=preset)

    def gather(self, preset=None, **kind):
        """
        kind:{kind1:level1,kind2:level2...}
        acceptable kind:
            'sawmill' ,'wood', 'farm' ,'food', 'iron' , 'mithril' , 'gold'
        preset :
            a number in [-3,0];
            or a string in ('march','load','level','speed');
            default:None
        """

        s = {'sawmill', 'wood', 'farm', 'food', 'iron', 'mithril', 'gold'}
        for key in kind.keys():
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
            'sawmill' , 'farm' , 'iron' , 'mithril' , 'gold' , 'monster' , 'camp'
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
            # if unique is not None:
            #     # TODO:opencv
            #     # search monster once
            #     self.adb0.tap(self.scrX * 438/720, self.scrY * 1210/1280)
            #     # self.tap('vipsearch')
            #     # tap vipsearch without killing tips
            #     self.adb0.tap(self.scrX * 50/720, self.scrY * 950/1280)
            #     # toggle 'unique'
            #     # cant judge without opencv
            #     self.adb0.tap(self.scrX * 100/720, self.scrY * 940/1280)
        elif rsskind is not None:
            # swipe so other icons shell be in their position
            self.adb0.swipe((self.scrX * 600/720, self.scrY * 940/1280),
                            (self.scrX * 190/720, self.scrY * 940/1280))
            self.wait(4)
        if rsskind == 'sawmill' or rsskind == 'wood':
            self.adb0.tap(self.scrX * 80/720, self.scrY * 940/1280)
        elif rsskind == 'farm' or rsskind == 'food':
            self.adb0.tap(self.scrX * 190/720, self.scrY * 940/1280)
        elif rsskind == 'iron':
            self.adb0.tap(self.scrX * 300/720, self.scrY * 940/1280)
        elif rsskind == 'mithril':
            self.adb0.tap(self.scrX * 420/720, self.scrY * 940/1280)
        elif rsskind == 'coin' or rsskind == 'gold':
            self.adb0.tap(self.scrX * 530/720, self.scrY * 940/1280)
        elif rsskind == 'camp' or rsskind == 'tent':
            self.adb0.tap(self.scrX * 650/720, self.scrY * 940/1280)

        if lvl is not None:
            self.writeTextBox(self.scrX * 614/720, self.scrY * 1070/1280, lvl)

        # tap 'search' button
        self.adb0.tap(self.scrX * 438/720, self.scrY * 1210/1280)
        self.wait(0.5)

    def tap(self, obj='blank', behav=None):
        """
        acceptable obj by now:
            'blank','vipsearch','changeMap','keyback','tips','center'...
        """
        if behav is not None:
            self.adb0.tap(self.scrX * behav[0]/720, self.scrY * behav[1]/1280)
            if len(behav)>=3:
                self.wait(behav[2])
            return

        if obj == 'blank':
            return self.adb0.tap(self.scrX * 480/720, self.scrY * 56/1280)
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
            return self.adb0.tap(self.scrX * 520/720, self.scrY * 610/1280)
        if obj == 'citybuff':
            return self.adb0.tap(self.scrX * 360/720, self.scrY * 390/1280)
        # if obj == 'user_icon':
        #     return self.adb0.tap(self.scrX * 50/720, self.scrY * 50/1280)
        # if obj == 'setting':
        #     return self.adb0.tap(self.scrX * 670/720, self.scrY * 1230/1280)

        loc = {
            'alliance': (650,1240),
            'user_icon': (50, 50),
            'setting': (670, 1230),
            'Account': (110, 360),
            'switchAccount': (360, 960),
            'facebook': (360, 370),
            'next': (360, 1000),
            'ok_mid': (360, 785),
        }
        try:
            return self.adb0.tap(self.scrX * loc[obj][0]/720, self.scrY * loc[obj][1]/1280)
        except KeyError:
            raise CokException('pycok.tap: unknown object %s' % obj)

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
            a number in [-4,0];
            a string in ('march','load','level','speed')
        """
        if isinstance(preset, int):
            if preset > 0:
                preset = 0
            if preset < -4:
                preset = -4
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

    def writeTextBox(self, x, y, text, delete=5, enter=True):
        self.adb0.tap(x, y)
        self.wait(0.5)
        while delete > 0:
            delete -= 1
            self.adb0.input('keyevent', 'KEYCODE_DEL')
        self.adb0.input('text', str(text))
        self.wait()
        if enter:
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

    def changeAcc(self, user=None, passw=None, package=None):
        if package is not None and package not in self.__gamepackage:
            self.forceStop()
            self.wait()
            self.launchgame(package)
            self.wait(10)
        if user is not None and passw is not None:
            self.resetCam()
            self.wait()
            self.tap('user_icon')
            self.wait(1)
            self.tap('setting')
            self.wait(2)
            self.tap('Account')
            self.wait(1)
            self.tap('switchAccount')
            self.wait(1)
            self.tap('facebook')
            self.wait(4)
            self.writeTextBox(self.scrX * 250/720,
                              self.scrY*610/1280, user, 0, False)
            self.adb0.tap(self.scrX * 250/720, self.scrY*700/1280)
            self.wait()
            self.writeTextBox(self.scrX * 250/720,
                              self.scrY*700/1280, passw, 0)
            self.wait(3)
            self.tap('next')
            self.wait(3)
            self.tap('ok_mid', (360, 785, 0.5))
            self.wait(1)
            self.tap('ok_mid', (360, 785, 0.5))
            self.wait(1)
            self.tap('ok_mid', (360, 785))
            self.wait(1)
            self.tap('ok_mid', (360, 785))
            self.wait(10)

    def shield(self, hour=8, miss=60):
        assert hour in (8, 24, 72)
        self.resetCam(worldMap=True)
        self.wait()
        self.tap('center')
        self.wait()
        self.tap('citybuff')
        self.wait(2)
        self.adb0.tap(self.scrX * 360/720, self.scrY * 190/1280)
        self.wait(0.5)

        for _ in range(miss//5):
            self.adb0.tap(self.scrX * 600/720, self.scrY * 310/1280)
            print('.', end='', flush=True)
            self.wait(5)
        print('')


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
                    version='%(prog)s 0.8')
parser.add_argument('-s', '--server', action='version',
                    version='distributed sys is under working', help='connect to a remote server')
parser.add_argument('-f', '--task-file=', dest='file',
                    help="""
                    a taskfile or a config file that contains a tasklist. If the given file dosen't
                    exist or dosen't contain a tasklist pycok will create one or rewrite it with
                    a default module
                    """)
parser.add_argument('-d', '--device', action='append',
                    nargs='+', help='add devices')
parser.add_argument('--sleep', type=int, help='sleep seconds before run')
parser.add_argument('--emu', action='store_true',
                    help='indicate that the decice is an emulator')
parser.add_argument('--speed', type=int, help='')
parser.add_argument('--adbpath', type=str, help='set adbpath')


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
        # if fastrun==True，start and until represent a relative time，or it represent a absolute time
    },

]


class Acc(dict):
    def __init__(self, d):
        super().__init__()
        self['tasklist'] = TaskList(d.pop('tasklist'))  # ,_TASKLIST_default)
        self['name'] = d.get('name', None)
        self['username'] = d.get('username', None)
        self['passw'] = d.get('passw', None)
        self['package'] = d.get('package', None)
        self.enable = d.get('enable',True)

        if self['name'] is None and self['username']:
            self['name'] = self['username']

    def __getattr__(self, att):
        return self[att]

    def run(self, cok, login=False, waittime=300):
        """
        run tasks in tasklist until the next task need to wait more than waittime.
        return the next task
        """
        soon = self.tasklist.getsoon()
        now = int(time.time())
        if soon is None or soon.time - now > waittime:
            return soon
        print('Running TaskList of', self.name)
        startstamp = time.time()
        if (login or cok.acc != self.name) and self.username is not None and self.passw is not None:
            print('login..')
            cok.wait(10)
            cok.changeAcc(self.username, self.passw, self.package)
            cok.acc = self.name
            cok.wait(5)
        while True:
            soon = self.tasklist.getsoon(update=True)
            now = int(time.time())
            if soon is not None:
                if soon.time <= now:
                    assert soon.isActive()
                    startTime = time.time()
                    print('Running task \'%s\' at' % soon.name,
                          time.strftime(TIMEFORMAT, time.localtime()))
                    soon.runTask(cok)
                    print('Task \'%s\' ended in' % soon.name, time.strftime(
                        '%Hhr%Mm%Ss', time.gmtime(time.time()-startTime)), end='')
                    if soon.every > 0:
                        soon.updateEvery()
                    if soon.time > now:
                        print(' , will be called next time in', time.strftime(
                            TIMEFORMAT, time.localtime(soon.time)))
                    print('\n')
                    continue
                elif waittime >= soon.time - now:
                    print('next task is', soon.name,
                          'after', soon.time-now, 'seconds')
                    time.sleep(soon.time - now)
                    continue

            print('Stop tasklist of', self.name, 'in', time.strftime(
                '%Hhr%Mm%Ss', time.gmtime(time.time()-startstamp)))
            return soon

    def login(self,cok):
        print('login..')
        cok.changeAcc(self.username, self.passw, self.package)
        cok.acc = self.name


class TaskList(list):
    def __init__(self, it):
        super().__init__()
        for task in it:
            self.append(task)

        # update tasklist
        for task in self:
            if task.fastrun:
                lasts = task.until - task.start
                task.start += int(time.time())
                task.time = task.start
                if task.until > 0:
                    task.until = task.start + lasts
            elif task.every > 0:
                task.updateEvery(force=True)
                # if task.time < task.start or task.time > task.until:
                #     task.time = task.start
            # 把开始时间是很久之前的任务改到还差一个‘interval’就要等的时间点
            if task.nloop != 0 and task.interval > 0:
                # while task.time+task.interval < time.time():
                #     task.time += task.interval
                if task.time < time.time():
                    task.time += ((time.time()-task.time) //
                                  task.interval)*task.interval

    def __setitem__(self, index, val):
        return super().__setitem__(index, Task(val))

    def __getitem__(self, index):
        return super().__getitem__(index)

    def append(self, task):
        super().append(Task(task))

    def getsoon(self,update=False):
        soon = None
        for task in self:
            assert isinstance(task, Task)
            if update and task.every > 0:
                task.updateEvery()
            if task.enable:
                if task.isActive() or task.start > time.time():
                    if soon is None:
                        soon = task
                    elif task.time < soon.time:
                        soon = task
        return soon


class SubTask(tuple):
    pass  # TODO


class Task(dict):
    __slots__ = tuple(list(_TASKLIST_default[0].keys())+['countdown'])

    def __str__(self):
        return '\'%s\' in ' % self.name + time.strftime(TIMEFORMAT, time.localtime(self.time))

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
        if not self.enable:
            return False
        if self.start > time.time():
            return False
        if self.countdown == 0:
            return False
        if self.until > self.start and self.time > self.until:
            return False
        return True

    def updateEvery(self, force=False):
        "prepare for next outer loop"
        assert(self.every > 0)

        if force or not self.isActive():
            now = int(time.time())
            if self.until > 0:
                assert self.until>self.start
                dur = self.until-self.start
                if self.countdown == 0:
                    self.until += self.every
                if self.until < now:
                    self.until += ((now-self.until)//self.every+1)*self.every
                self.start = self.until-dur
            else:
                if now > self.start and self.countdown == 0:
                    self.start += self.every
                if self.start < now:
                    self.start += ((now-self.start)//self.every)*self.every

            self.countdown = self.nloop
            if self.start > now:
                self.time = self.start
            else:
                self.time = int(time.time())

    def runTask(self, cok, sub=None):  # TODO
        if sub:
            return self.__runSub(cok, self[sub])
        if self.countdown > 0:
            self.countdown -= 1
        if self.fastrun:
            self.time = int(time.time())+self.interval
        else:
            self.time += self.interval

        if self.prepare:
            self.runTask(cok, 'prepare')
        if self.run:
            self.runTask(cok, 'run')
        if self.after:
            self.runTask(cok, 'after')

    def __runSub(self, cok, s):
        if len(s) > 1:
            return subp.get(s[0])(cok, **s[1])
        else:
            return subp.get(s[0])(cok)


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
COKSPEED = 80
ADBPATH='default'


class schedule():
    def __init__(self, configFile=None, device=None, package=None, vip=True, emu=False):
        self.cok = pycok(device=device, adbpath=ADBPATH, package=package, vip=vip)
        self.cok.speed = COKSPEED

        self.emu = emu
        self.forceStop = False

        self.acclist = []
        if configFile and path.exists(configFile):
            with open(configFile, 'r') as f:
                conf = json.load(f)
                if isinstance(conf, list):
                    for c in conf:
                        self.acclist.append(Acc(c))
                elif isinstance(conf, dict):
                    self.acclist.append(Acc(conf))

    def load(self, file):
        conf = json.load(file)
        if isinstance(conf, list):
            for c in conf:
                self.acclist.append(Acc(c))
        elif isinstance(conf, dict):
            self.acclist.append(Acc(conf))

    def schedule(self):
        sleeping = False
        battery = self.cok.getBatteryLevel()

        if self.cok.get_status() == 'sleeping':
            self.cok.adb0.wakeup()
            self.cok.wait()
            self.cok.adb0.unlock()
            self.cok.wait()
        self.cok.launchgame()
        self.cok.wait(20)

        while True:
            soon = None
            for acc in self.acclist:
                if acc.enable:
                    ntask = acc.run(self.cok,login=False)  # TODO
                    print('Next task in', acc.name, 'is', ntask)
                if ntask is None:
                    acc.enable = False

                if soon is None or ntask.time < soon.time:
                    soon = ntask

            if soon is not None:
                print('Idle until', time.strftime(
                    TIMEFORMAT, time.localtime(soon.time)))
                # time.sleep(soon.time - time.time() - 120)
                if not self.emu:
                    if not sleeping:
                        battery = self.cok.getBatteryLevel()
                        if battery < 20:
                            self.cok.adb0.sleep()
                            sleeping = True
                            print('low battery.\nsleeping..')
                            while self.cok.getBatteryLevel() < 30:
                                time.sleep(300)
                        elif soon.time-time.time() > 600:
                            if self.forceStop:
                                self.cok.adb0.input(
                                    'keyevent', 'KEYCODE_HOME')
                                self.cok.wait()
                                self.cok.forceStop()
                            self.cok.adb0.sleep()
                            sleeping = True
                            print('sleeping...')
                        # elif self.cok.get_status() == 'sleeping':
                        #     self.cok.adb0.wakeup()
                        #     self.cok.wait()
                        #     self.cok.adb0.unlock()
                        #     self.cok.wait()
                        #     self.cok.launchgame()
                        #     self.cok.wait(10)

                idleTime=int(soon.time-time.time())
                if idleTime > 300:
                    time.sleep(idleTime-290)

                if sleeping or self.cok.get_status() == 'sleeping':
                    print('wake up\n')
                    sleeping = False
                    self.cok.adb0.wakeup()
                    self.cok.wait()
                    self.cok.adb0.unlock()
                    self.cok.wait()
                    self.cok.launchgame()
                    self.cok.wait(30)
                    self.cok.resetCam(worldMap=True)
                # else:
                    # time.sleep(soon.time - time.time() - 120)  # TODO
            else:
                print('No task is waitting.')
                if self.forceStop:
                    self.cok.adb0.input('keyevent', 'KEYCODE_HOME')
                    self.cok.wait()
                    self.cok.forceStop()
                if not self.emu:
                    self.cok.adb0.sleep()
                print('exit')
                return
