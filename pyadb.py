# -*- coding:utf-8 -*-

import subprocess
import os
import math

class adb(object):
    def __init__(self,adbpath='default',device='',cache='/tmp/pycok.cache'):
        if adbpath=='default':
            self.adbpath=subprocess.run(['which','adb'],stdout=subprocess.PIPE).stdout
        else:
            self.adbpath=adbpath
        
        #TODO:device

        if not os.path.isdir(cache):
            os.makedirs(cache)
        self.cache=cache

    def __call__(self,*cmd, timeout=None,byt=False):
        #TODO: check cmd
        p=subprocess.run([self.adbpath,]+list(cmd),stdout=subprocess.PIPE)
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

    def get_scrcap(self,name=None,path=None):
        self.adb('shell','screencap','-p','/tmp/scrcap.png')
        
        if path!=None and isinstance(path,(str,bytes)):
            savefile=path
        else:
            savefile=self.cache

        if name!=None and isinstance(name,(str,bytes)):
            savefile=os.path.join(savefile,name)
        else:
            savefile=os.path.join(savefile,'scrcap.png')
        self.adb('pull','/tmp/scrcap.png',savefile.encode('utf-8'))
        return savefile

    def __getattr__(self,attr):
        raise AttributeError("'adb'object has on attribute '%s'" % attr)

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
    ###print('\n\n''a.dir :\n       ',a.__dir__(),'\n')

    #a.get_scrcap('sc1.png')
    #print("Run: a.input('swipe','150','650','550','650') :")
    #print('    ',a.input('swipe','150','650','550','650'))
    #a.get_scrcap('sc2.png')
