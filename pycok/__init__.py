#! /bin/env python3
# -*- coding:utf-8 -*-

__title__ = 'pycok'
__version__ = '0.9'
__author__ = 'Eitetsu'

# __all__=[]

# from .Cok import *

from .consts import *
from .Cok import subtask, pycok, schedule
from . import subtasks

import argparse

parser = argparse.ArgumentParser(prog='pycok', description='')
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
