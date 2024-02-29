#!/usr/bin/env python3
###
### Core > Arguments parser
###

import argparse
import sys

from lib.core.Config import ARGPARSE_MAX_HELP_POS, USAGE
from lib.core.Exceptions import ArgumentsException
from lib.core.Settings import Settings
from lib.core.Constants import Mode
from lib.output.Output import Output
from lib.output.Logger import logger
from lib.utils.ArgParseUtils import LineWrapRawTextHelpFormatter

class ArgumentsParser:
    formatter_class = lambda prog: LineWrapRawTextHelpFormatter(
        prog, max_help_position=ARGPARSE_MAX_HELP_POS)
    
    def __init__(self, settings):
        self.settings = settings
        self.mode     = None
        self.args     = None

        parser = argparse.ArgumentParser(
            usage=USAGE, 
            formatter_class=ArgumentsParser.formatter_class)
        parser.add_argument('command', help=argparse.SUPPRESS)

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            logger.error('Unrecognized command')
            parser.print_help()
            raise ArgumentsException()

        self.subparser = None

        # Use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

        # Check arguments
        if not self.check_args():
            raise ArgumentsException()

    #------------------------------------------------------------------------------------

    def __create_subcmd_parser(self):
        """Create subcommand parser."""

        subcmd = {
            Mode.TOOLBOX : 'toolbox',
            Mode.DB      : 'db',
            Mode.ATTACK  : 'attack'
        }.get(self.mode)

        return argparse.ArgumentParser(
            usage='python3 hellsing.py {subcmd} <args>'.format(subcmd=subcmd),
            formatter_class=ArgumentsParser.formatter_class) 

    #------------------------------------------------------------------------------------
    # Toolbox Subcommand Parsing
    
    def toolbox(self):
        """Arguments for subcommand Toolbox"""

        self.mode = Mode.TOOLBOX

        parser = self.__create_subcmd_parser()
        toolbox = parser.add_argument_group(
            Output.colored('Toolbox management', attrs='bold'), 
            'The Toolbox contains all the tools used by hellsing for running the security' \
            ' checks.\nThey are classified by the services they target.')

        toolbox_mxg = toolbox.add_mutually_exclusive_group()
        toolbox_mxg.add_argument(
            '--show-all', 
            help    = 'Show full toolbox content', 
            action  = 'store_true', 
            dest    = 'show_toolbox_all', 
            default = False)
        toolbox_mxg.add_argument(
            '--install-tool', 
            help    = 'Install a given tool', 
            action  = 'store', 
            dest    = 'install_tool', 
            metavar = '<tool-name>', 
            default = None)
        toolbox_mxg.add_argument(
            '--install-all', 
            help    = 'Install all the tools in the toolbox',
            action  = 'store_true', 
            dest    = 'install_all', 
            default = False)
        toolbox_mxg.add_argument(
            '--update-tool', 
            help    = 'Update a given tool', 
            action  = 'store', 
            dest    = 'update_tool', 
            metavar = '<tool-name>', 
            default = None)
        toolbox_mxg.add_argument(
            '--update-all',
            help    = 'Update all installed tools in the toolbox',
            action  = 'store_true', 
            dest    = 'update_all', 
            default = False)
        toolbox_mxg.add_argument(
            '--uninstall-tool', 
            help    = 'Uninstall a given tool',
            action  = 'store', 
            dest    = 'uninstall_tool', 
            metavar = '<tool-name>', 
            default = None)
        toolbox_mxg.add_argument(
            '--uninstall-all', 
            help    = 'Uninstall all tools in the toolbox',
            action  = 'store_true', 
            dest    = 'uninstall_all', 
            default = False)
        toolbox_mxg.add_argument(
            '--check-tool', 
            help    = 'Check the operational status of a given tool',
            action  = 'store', 
            dest    = 'check_tool', 
            metavar = '<tool-name>', 
            default = None)
        toolbox_mxg.add_argument(
            '--check-all', 
            help    = 'Check the operational status of all tools in the toolbox',
            action  = 'store_true', 
            dest    = 'check_all', 
            default = False)

        self.subparser = parser
        # Inside Mode, so ignore the first TWO argvs
        self.args = parser.parse_args(sys.argv[2:])
        
    #------------------------------------------------------------------------------------

    def check_args(self):
        """Main routine for arguments checking, dispatch to correct function"""
        
        if self.mode == Mode.TOOLBOX :  
            return self.check_args_toolbox()
        elif self.mode == Mode.DB :  
            return self.check_args_db()
        else:  
            return self.check_args_attack()

    #------------------------------------------------------------------------------------

    def check_args_toolbox(self):
        # Since the arguments are mutually exclusive, only one should be true or not None at a time.
        # Count how many of the mutually exclusive arguments have been set.
        args_count = sum([
            self.args.show_toolbox_all,
            self.args.install_tool is not None,
            self.args.install_all,
            self.args.update_tool is not None,
            self.args.update_all,
            self.args.uninstall_tool is not None,
            self.args.uninstall_all,
            self.args.check_tool is not None,
            self.args.check_all,
        ])

        # Since they are mutually exclusive, exactly one of them should be true/not None.
        if args_count != 1:
            logger.error('Invalid toolbox arguments. Please provide exactly one action at a time.')
            return False
        else:
            return True

    #------------------------------------------------------------------------------------
