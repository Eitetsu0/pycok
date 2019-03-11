# pycok

[![Gitter][gitter-picture]][gitter] ![py35][py35] [English version][english-version]

This project is for learning purpose only.

## Usage

Firstly ensure you know how connect your Android phone to your computer via ADB.

#### As individual app

If you already have a `config.json` file, just run `python3 pycok` and the program shell just run as you wish. Otherwise it will generate a new `config.json` in your current path. So you cant edit it for your own use.

Or you can run `python3 pycok --help` to get some help. 

If you are using windows you may need to tell the script where the adb is by `python3 pycok --adbpath 'your adb path'`.

#### As python module
[`__main__.py`](pycok/__main__.py) should be an easy reference.

For example , `cp pycok/__main__.py test.py` , then run `python3 test.py` .

#### and some more
```
usage: coktask [options]..

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -d DEVICE 
  --sleep seconds       sleep seconds before script start
  --emu                 indicate that the decice is an emulator
  --speed SPEED         percentage of speed , 80 by default
  --adbpath Path2adb
```

## Format of config.json

There is a list of Accounts. Every account can have its own configurations.

### Structure of accounts' list:
```python
[
    {
        "name":"name",
        "enable":ture,
        "username":"name Of Your facebook Account",
        "passw":"password",
        "package":"package of the game",  # playstore version for default
        "tasklist":[
            task1,
            task2,
            ...
        ]
    },
    .....
]
```
All configrations can be omited.
If you have only one account the `[]` outside can be omited as well, like:

```python
{
    "tasklist":[
        task1,
        task2,
        ...
    ]
}
```

### Structure of a Task (in Python):
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

