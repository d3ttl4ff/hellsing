#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### Core > Constants
###
from enum import Enum, auto

MANDATORY, OPTIONAL = range(2)

class CmdType(Enum):
    RUN     = auto()
    INSTALL = auto()
    UPDATE  = auto()
    CHECK   = auto()

class Mode(Enum):
    TOOLBOX = auto()
    INFO    = auto()
    DB      = auto()
    ATTACK  = auto()

class TargetMode(Enum):
    URL = auto()
    IP  = auto()

class OptionType(Enum):
    BOOLEAN = auto()
    LIST    = auto()
    VAR     = auto()