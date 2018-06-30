# pycok
---
This project is just for learning purpose.

Based on Python3.

simulate operations via adb.

It may help you build bots in cok.

current version 0.8

```
usage: coktask [options]..

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -d DEVICE 
  --sleep SLEEP         sleep seconds before run
  --emu                 indicate that the decice is an emulator
  --speed SPEED
```

Edit [coktask.py](./coktask.py) to add your own subtask.
Call it in a Task.  
Edit [config.json](./config.json) to add new account and tasks.

structure of a Task (in Python):
```python
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
        #if start>time : time=start
        'start': 0,
        # stop repeating task if until<time.time() and until>0
        'until': -1,
        # when task stoped by over 'until' ,start+=every, until+=every
        'every': 0,
        'enable': False,
        'fastrun': True,  # run this task as soon as manager started
        # if fastrun==True，start and until represent a relative time，or it represent a absolute time
    }
```

structure of accounts' list:
```python
[
    {
        "name":"name",
        "username":"name Of Your facebook Account",
        "passw":"password",
        "package":"package of the game",  # playstore version for default
        "tasklist":[
            task1,
            task2,
            ...
        ]
    }
]
```
