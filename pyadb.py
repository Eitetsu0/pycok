# -*- coding:utf-8 -*-

import subprocess
import os
import math

class adb(object):
    def __init__(self,adbpath='default',device=None,cache='/tmp/pycok.cache'):
        if adbpath=='default':
            self.adbpath=subprocess.run(['which','adb'],stdout=subprocess.PIPE).stdout
        else:
            self.adbpath=adbpath

        #TODO:device
        self.device=None
        if device:
            self.device=device
        else:
            self.device=self.listdevice()[0][0]
        if not os.path.isdir(cache):
            os.makedirs(cache)
        self.cache=cache

    def __call__(self,*cmd, timeout=None,byt=False):
        #TODO: check cmd
        precmd=[self.adbpath,]
        if self.device and cmd[0]!='devices':
            precmd.append(b'-s')
            precmd.append(self.device)
        p=subprocess.run(precmd+list(cmd),stdout=subprocess.PIPE)
        p.check_returncode()
        if byt:
            return p.stdout
        return p.stdout.decode()

    def adb(self, *cmd, timeout=None):
        return self.__call__(*cmd,timeout=timeout)

    @property
    def cache(self):
        return self._cache
    @cache.setter
    def cache(self,val):
        if not os.path.isdir(val):
            os.makedirs(val)
        self._cache=val

    @property
    def adbpath(self):
        return self.__adbpath
    @adbpath.setter
    def adbpath(self,path):
        if not isinstance(path,(str,bytes)):
            raise ValueError('path must be a string')
        path=path.strip()
        if not os.path.exists(path):
            raise FileNotFoundError('no adb found')
        self.__adbpath=path

    @property
    def device(self):
        return self.__device
    @device.setter
    def device(self,val):
        if val:
            self.__device=val
            self.timeout=3
        else:
            self.__device=None
            self.timeout=False

    def listdevice(self):
        devices=[]
        s=self.adb('devices','-l').splitlines()
        s.remove('')
        for line in s[1:]:
            fields=line.split()
            line=fields[:2]
            line.append({})
            for field in fields[2:]:
                key,val=field.split(':',1)
                line[2][key]=val
            devices.append(line)
        return devices

    def get_scrcap(self,name=None,path=None):
        self.adb('shell','screencap','-p','/sdcard/scrcap.png')

        if path!=None and isinstance(path,(str,bytes)):
            savefile=path
        else:
            savefile=self.cache

        if name!=None and isinstance(name,(str,bytes)):
            savefile=os.path.join(savefile,name)
        else:
            savefile=os.path.join(savefile,'scrcap.png')
        self.adb('pull','/sdcard/scrcap.png',savefile.encode('utf-8'))
        return savefile

    def __getattr__(self,attr):
        raise AttributeError("'adb'object has no attribute '%s'" % attr)

    def input(self,*cmd,sources=None):
        """
        The commands and default sources are:
            text <string> (Default: touchscreen)
            keyevent [--longpress] <key code number or name> ... (Default: keyboard)
            tap <x> <y> (Default: touchscreen)
            swipe <x1> <y1> <x2> <y2> [duration(ms)] (Default: touchscreen)
            press (Default: trackball)
            roll <dx> <dy> (Default: trackball)
        """
        cmdlist=['shell','input']
        if sources!=None:
            if sources in ('mouse','keyboard','joystick','touchnavigation','touchpad','trackball','stylus','dpad','touchscreen','gamepad'):
                cmdlist.append(sources)
        cmdlist.extend(cmd)
        return self.adb(*cmdlist)

    def tap(self,x,y):
        return self.input('tap',str(x),str(y))

    def swipe(self,xy1,xy2=None,angle=None,dist=200):
        ashellcmd=['swipe',str(xy1[0]),str(xy1[1])]
        if isinstance(xy2,tuple):
            ashellcmd.append(str(xy2[0]))
            ashellcmd.append(str(xy2[1]))
        elif angle!=None:

            rad=angle*math.pi/180
            x=math.cos(rad)
            y=math.sin(rad)
            ######## is this ok ?
            if x<1: x=1
            if y<1: y=1
            #########
            ashellcmd.append(str(x))
            ashellcmd.append(str(y))
        else:
            return
        return self.input(*ashellcmd)

if __name__=='__main__':
    #print("test class 'adb'"+ '\n'+ "print Enter to start..")
    import time
    a=adb()
    a.get_scrcap(time.strftime('%Y_%m_%d %X',time.localtime())+'.png','.')
    a.listdevice()
