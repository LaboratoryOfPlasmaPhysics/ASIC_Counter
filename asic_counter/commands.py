import os
import subprocess

from amaranth import *
from amaranth.lib import enum
from amaranth.build import *
from amaranth_boards.resources import *
from amaranth_boards.icestick import *


class Commands(enum.Enum, shape=3):
    Enable = 1
    Reset = 2
    Read = 3
    SetMux = 4
    