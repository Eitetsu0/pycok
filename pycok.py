#! /usr/bin/python3
# -*- coding:utf-8 -*-

import time

from pyadb import adb


class pycok(object):
    __adbpath=''
    def __init__(self,mode='adb',adbpath='default',device=None,vip=True):
        if mode == 'web':
            #raise
            #TODO:webcok
            pass
        elif mode == 'adb':
            self.adb0=adb(adbpath,device)
            self.set_screen(720,1280) #TODO:屏幕适配
            #set vip
            self.vip=vip
            
            #make sure the game is running
            if self.get_status=='closing':
                try:
                    self.lauchgame()
                except Exception:
                    #TODO:failed lauch game
                    pass
        self.speed=100

    @property
    def adbpath(self):
        return self.__adbpath
    @adbpath.setter
    def adbpath(self,path):
        #check the path

        __adbpath=path

    @property
    def speed(self):
        return int(100/self._waittingtime)
    @speed.setter
    def speed(self,val):
        if not isinstance(val,int):
            raise TypeError("pycok.speed should be int.")
        if val<0:
            val=0
        if val>200:
            val=200
        self._waittingtime=100/val

    def get_status(self):
        #TODO:cv
        return 'running'

    def lauchgame(self):
        #TODO:adb
        pass

    def killmonster(self,lv=None,interval=100,loop=10,preset=0,dragonWord=None):

        self.find(kind='monster',level=lv)
        return self.killmonsterin(preset=preset)

    def gather(self,preset=None,**kind):
        """
        kind:{kind1:level1,kind2:level2...}
        acceptable kind:
            'sawmill' , 'farm' , 'iron' , 'mithril' , 'gold'
        preset : 
            a number in [-3,0];
            a string in ('march','load','level','speed')
        """

        s={'sawmill' , 'farm' , 'iron' , 'mithril' , 'gold'}
        for key in kind:
            if key not in s:
                kind.pop(key)
        self.find(**kind)
        self.marchto(preset=preset)
        

    def marchto(self,x=None,y=None,preset=None,dragonWord=None):
        'preset: -3 ~ 0'
        if x!=None and y!=None:
            self.move2loc(x,y)
        self.tap()
        self.tap('center')
        self.wait(0.5)
        self.tap('occupy')
        self.march(preset,dragonWord)

    def march(self,preset=None,dragonWord=None):
        'preset: -3 ~ 0'
        if preset!=None:
            self.selectpreset(preset)
        if dragonWord!=None:
            #TODO:
            pass
        self.adb0.tap(self.scrX* 600/720,self.scrY* 1210/1280) #march button
        self.wait(0.5)


    def find(self,vip=None,**kind):
        """
        kind:{kind1:level1,kind2:level2...}
        acceptable kind:
            'sawmill' , 'farm' , 'iron' , 'mithril' , 'gold' , 'monster'
        """
        if vip==None:
            vip=self.vip
        if not isinstance(vip,bool):
            raise TypeError('arg \'vip\' should be bool type')
        if vip:
            if kind:
                key,lvl=kind.popitem()
                return self.vipsearch(key,lvl)
            return self.vipsearch()
        #none vip search:
        if not kind:
            raise Exception #TODO
        #TODO:build method find with opencv
        pass

    def vipsearch(self,rsskind=None,lvl=None,unique=None):
        """
        acceptable kind:
            'sawmill' , 'farm' , 'iron' , 'mithril' , 'gold' , 'monster'
        """
        self.tap('vipsearch')
        self.wait(0.5)
        if rsskind=='monster':
            self.adb0.tap(self.scrX* 100/720,self.scrY* 940/1280)
            if unique!=None:
                #TODO:opencv
                #search monster once 
                self.adb0.tap(self.scrX* 438/720,self.scrY* 1210/1280)
                #self.tap('vipsearch')
                #tap vipsearch without killing tips
                self.adb0.tap(self.scrX* 50/720,self.scrY* 950/1280)
                #toggle 'unique' 
                #cant judge without opencv
                self.adb0.tap(self.scrX* 100/720,self.scrY* 940/1280)
        elif rsskind!=None:
            #swipe so other icons shell be in their position
            self.adb0.swipe((self.scrX* 350/720,self.scrY* 940/1280),(self.scrX* 190/720,self.scrY* 940/1280))
            self.wait(3)
        if rsskind=='sawmill' or rsskind=='wood':
            self.adb0.tap(self.scrX* 190/720,self.scrY* 940/1280)
        elif rsskind=='farm' or rsskind=='food':
            self.adb0.tap(self.scrX* 300/720,self.scrY* 940/1280)
        elif rsskind=='iron':
            self.adb0.tap(self.scrX* 420/720,self.scrY* 940/1280)
        elif rsskind=='mithril':
            self.adb0.tap(self.scrX* 530/720,self.scrY* 940/1280)
        elif rsskind=='coin' or rsskind=='gold':
            self.adb0.tap(self.scrX* 650/720,self.scrY* 940/1280)

        if lvl!=None:
            self.writeTextBox(self.scrX* 614/720,self.scrY* 1070/1280,lvl)
        
        #tap 'search' button
        self.adb0.tap(self.scrX* 438/720,self.scrY* 1210/1280)
        self.wait(0.5)

    def tap(self,obj='blank'):
        """
        acceptable obj by now:
            'blank','vipsearch','changeMap','keyback','tips','center'
        """
        if obj=='blank':
            return self.adb0.tap(self.scrX* 550/720,self.scrY* 50/1280)
        if obj=='vipsearch':
            self.resetCam(worldMap=True)
            #TODO:opencv
            #return self.adb0.tap(self.scrX* 50/720,self.scrY* 950/1280)
            return self.adb0.tap(self.scrX* 50/720,self.scrY* 870/1280)
        if obj=='changeMap':
            return self.adb0.tap(self.scrX* 80/720,self.scrY* 1240/1280)
        if obj=='keyback':
            return self.adb0.input('keyevent','KEYCODE_BACK')
        if obj=='tips':
            #TODO:opencv needed
            return self.adb0.tap(self.scrX* 50/720,self.scrY* 1065/1280)
        if obj=='center': #a little lower than center
            return self.adb0.tap(self.scrX*0.5,self.scrY* 690/1280)
        if obj=='occupy':
            return self.adb0.tap(self.scrX* 520/720,self.scrY* 650/1280)
    
    def removetips(self):
        self.tap('tips')
        self.resetCam(worldMap=True)
        


    def killmonsterin(self,x=None,y=None,preset=0,dragonWord=None):
        'similar to marchto(), by default: the center of screen'
        if (x==None and y!=None) or (x!=None and y==None):
            raise Exception() #TODO
        if x!=None and y!=None:
            self.move2loc(x,y)
            #self.adb0.input('tap',str(self.scrX* 550/720),str(int(self.scrY* 50/1280)))
        self.wait()
        #tap monster ps:not the center of screen
        self.adb0.tap(self.scrX* 321/720,self.scrY* 657/1280)
        self.wait(0.5)
        #tap Attack button
        self.adb0.input('tap',str(self.scrX//2),str(int(self.scrY*0.73)))
        self.wait(0.3)
        self.march(preset,dragonWord)
        

    
    def move2loc(self,x=None,y=None,kingdom=None):
        "move camera to x,y in kingdom move to last coord with no arg"
        self.adb0.tap(self.scrX//2,self.scrY*980/1280)
        self.wait(0.2)
        if isinstance(kingdom,int):
            self.writeTextBox(self.scrX//2,self.scrY*555/1280,kingdom)
        if isinstance(x,int):
            self.writeTextBox(self.scrX*200/720,self.scrY*650/1280,x)
        if isinstance(y,int):
            self.writeTextBox(self.scrX*500/720,self.scrY*650/1280,y)
        self.adb0.tap(self.scrX//2,self.scrY*790/1280)
        if isinstance(kingdom,int):
            self.wait(2)
        else:
            self.wait(0.5)
    
    def resetCam(self,*,worldMap=False):
        n=5
        while n >0:
            n-=1
            self.tap('keyback')
            self.wait(0.5)
        self.wait()
        self.tap('blank')
        self.wait(0.5)
        if worldMap:
            self.tap('changeMap')
            self.wait(2.5)

    def set_screen(self,x,y):
        self.scrX=x
        self.scrY=y

    def selectpreset(self,preset=0):
        """
        preset can be : 
            a number in [-3,0];
            a string in ('march','load','level','speed')
        """
        if isinstance(preset,int):
            if preset>0: preset=0
            if preset<-3: preset=-3
            return self.adb0.input('tap',str(int(660+preset*70)),str(int(self.scrY* 335/1280)))
        elif isinstance(preset,str):
            self.adb0.tap(self.scrX* 70/720,self.scrY* 1210/1280)
            if preset=='march':
                return self.adb0.tap(self.scrX* 180/720,self.scrY* 880/1280)
            elif preset=='load':
                return self.adb0.tap(self.scrX* 180/720,self.scrY* 960/1280)
            elif preset=='level':
                return self.adb0.tap(self.scrX* 180/720,self.scrY* 1040/1280)
            elif preset=='speed':
                return self.adb0.tap(self.scrX* 180/720,self.scrY* 1120/1280)
            else:
                return self.adb0.tap(self.scrX* 70/720,self.scrY* 1210/1280)
    
    def killMonsterQuickOnce(self,preset=0):
        if self.vip==False:
            return
        self.vipsearch()
        #self.adb0.input('tap',str(self.scrX* 550/720),str(int(self.scrY* 50/1280)))
        self.wait(1)
        self.killmonsterin(preset=preset)

    def writeTextBox(self,x,y,text,delete=5):
        self.adb0.tap(x,y)
        self.wait(0.2)
        while delete>0:
            delete-=1
            self.adb0.input('keyevent','KEYCODE_DEL')
        self.adb0.input('text',str(text))
        self.wait()
        self.adb0.input('keyevent','KEYCODE_NUMPAD_ENTER')
        self.wait()

    def wait(self,val=0.2):
        return time.sleep( self._waittingtime*val)

if __name__=='__main__':
    cok=pycok()

    cok.vipsearch('monster')
    n=7
    while n>0:
        n-=1
        cok.killMonsterQuickOnce()
        cok.wait(1)
        print('Monster loop left',n,'times..')
        #cok.resetCam()

    print("\nend")

