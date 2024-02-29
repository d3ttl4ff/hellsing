#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### Core > Main Controller
###
from lib.core.Constants import *
from lib.controller.ToolboxController import ToolboxController
# from lib.controller.DbController import DbController
# from lib.controller.AttackController import AttackController


class MainController():
        
    def __init__(self, arguments, settings):
        """
        Controller interface.

        :param ArgumentsParser arguments: Arguments from command-line
        :param Settings settings: Settings from config files
        """
        self.arguments = arguments
        self.settings  = settings

    def run(self):
        """Run the adapted controller"""
        {
            Mode.TOOLBOX : ToolboxController,
            # Mode.DB      : DbController,
            # Mode.ATTACK  : AttackController,
        }.get(self.arguments.mode)(self.arguments, self.settings).run()


