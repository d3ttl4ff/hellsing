#!/usr/bin/env python3
###
### Core > Arguments parser
###

import argparse
import sys

from lib.core.Config import *
from lib.core.Constants import *
from lib.core.Config import ARGPARSE_MAX_HELP_POS, USAGE
from lib.core.Exceptions import ArgumentsException
# from lib.core.Settings import Settings
from lib.core.Constants import Mode
from lib.output.Output import Output
from lib.output.Logger import logger
from lib.utils.ArgParseUtils import LineWrapRawTextHelpFormatter
from lib.utils.WebUtils import WebUtils

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
            # Mode.DB      : 'db',
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
    
    #Attack Subcommand Parsing
    def attack(self):
        """Arguments for subcommand Attack"""
        self.mode = Mode.ATTACK
        
        parser = self.__create_subcmd_parser()
        
        target = parser.add_argument_group(
            Output.colored('Mode: Single target', attrs='bold'), 
            'Run security checks against a target.')
        
        target.add_argument(
            '-t','--target',
            help    = 'Target IP[:PORT] (default port if not specified) or URL',
            action  = 'store',
            dest    = 'target_ip_or_url',
            metavar = '<target>',
            default = None)
        target.add_argument(
            '-s', '--service',
            help    = 'Target service',
            action  = 'store',
            dest    = 'service',
            metavar = '<service>',
            default = None)
        target.add_argument(
            '--addop',
            help    = 'Add/update the target into a given task scope in the database (default: task "default")',
            action  = 'store',
            dest    = 'add',
            metavar = '<task>',
            default = 'default')
        
        selection = parser.add_argument_group(
            Output.colored('Attack configuration', attrs='bold'),
            'Select a subset of checks to run, either manually or by using a ' \
            'pre-defined attack profile.')

        selection_mxg = selection.add_mutually_exclusive_group()
        selection_mxg.add_argument(
            '--profile',
            help    = 'Use a pre-defined attack profile',
            action  = 'store',
            dest    = 'profile',
            metavar = '<profile>',
            default = None)
        selection_mxg.add_argument(
            '--run-only', 
            help    = 'Run only checks in specified category(ies) (comma-separated)', 
            action  = 'store', 
            dest    = 'run_only', 
            metavar = '<cat1,cat2...>', 
            default = None)
        selection_mxg.add_argument(
            '--run-exclude', 
            help    = 'Run all checks except the ones in specified ' \
                      'category(ies) (comma-separated)',
            action  = 'store',
            dest    = 'run_exclude',
            metavar = '<cat1,cat2...>',
            default = None)

        self.subparser = parser
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
            logger.error('Invalid mode:toolbox arguments. Please provide exactly one action at a time.')
            return False
        else:
            return True

    #------------------------------------------------------------------------------------

    def check_args_attack(self):
        """Check arguments for subcommand Attack"""
        status=True
        if self.args.target_ip_or_url:
            status &= self.check_args_target()
        else:
            logger.error('Invalid mode:attack arguments. Please provide exactly one action at a time.')
            return False

        status &= self.__check_args_attack_selection()
        
        return status
    
    def check_args_target(self):
        """Check arguments for subcommand Attack"""
        
        target = self.args.target_ip_or_url
        
        if not target:
            return True
        
        # Check if target is an URL
        if target.startswith('http://') or target.startswith('https://'):
            self.args.target_mode = TargetMode.URL   
            
            if self.args.service and self.args.service.lower() != 'http':
                    logger.warning('URL only supported for HTTP service. ' \
                        'Automatically switch to HTTP')
            elif not self.args.service:
                logger.info('URL given as target, targeted service is HTTP')
                
            self.args.service = 'http' 
            self.args.target_port = WebUtils.get_port_from_url(target)
        
        # Check if target is an IP      
        else:
            self.args.target_mode = TargetMode.IP
            self.args.target_port = None
            s = target.split(':')
            self.args.target_ip_or_url = s[0]
            
            # Extract port 
            if len(s) == 2:
                self.args.target_port = int(s[1])
                if not (0 <= self.args.target_port <= 65535):
                    logger.error('Target port is invalid. Must be in the ' \
                        'range [0-65535]')
                    return False

            elif len(s) > 2:
                logger.error('Incorrect target format. Must be either an IP[:PORT] or ' \
                    'an URL')
                return False
            
            # Check or set target service and port
            if self.args.service:
                
                # Check if service is supported
                if not self.settings.services.is_service_supported(
                    self.args.service, multi=False):

                    logger.error('Service "{service}" is not supported. ' \
                        'Check "info --services".'.format(
                            service=self.args.service.upper()))
                    return False

                # Get the default port for the service if not specified
                if not self.args.target_port:
                    self.args.target_port = self.settings.services.get_default_port(
                        self.args.service)
                    
                    if not self.args.target_port:
                        logger.info('Default port for service {service} will be used: ' \
                            '{port}/{proto}'.format(
                                service = self.args.service,
                                port    = self.args.target_port,
                                proto   = self.settings.services.get_protocol(
                                    self.args.service)))

                    else:
                        logger.error('Target port is not specified and No default port for service {service}. ' \
                            'You must specify a port.'.format(
                                service=self.args.service))
                        return False
                    
            # Try to get the default service for the provided port if not specified
            else:
                if not self.args.target_port:
                    logger.error('Target port and/or service must be specified')
                    return False
                
                else:
                    self.args.service = self.settings.services.get_service_by_port(
                        self.args.target_port)
                    
                    if not self.args.service:
                        logger.error('Cannot automatically specify the target ' \
                            'service for port {port}/tcp, use --target IP:PORT ' \
                            'syntax'.format(port=self.args.target_port))
                        return False
                    
                    logger.info('Service {service} will be used for target'.format(
                        service=self.args.service))
                    
        return True
              
    def __check_args_attack_selection(self):
        """Check arguments for subcommand Attack (selection)"""
        
        # Select a subset of checks to run
        categories = self.args.run_only or self.args.run_exclude
        
        if categories:
            categories = categories.split(',')
            for cat in categories:
                if not self.settings.services.list_all_categories():
                    logger.error('Category "{cat}" is not supported. ' \
                        'Check "info --categories".'.format(cat=cat))
                    return False
            
            # Store the list of categories
            if self.args.run_only:
                self.args.run_only = categories
            else:
                self.args.cat_exclude = categories
                
        # Select attack profile
        elif self.args.profile:
            profile = self.settings.attack_profiles.get(self.args.profile.lower())
            
            if not profile:
                logger.error('Attack profile "{profile}" does not exist. ' \
                    'Check "info --attack-profiles".'.format(profile=self.args.profile))
                return False
            
            elif self.args.target_ip_or_url \
                 and not profile.is_service_supported(self.args.service):
                     
                logger.error('Attack profile "{profile}" does not support service ' \
                    'service "{service}"'.format(profile=self.args.profile, service=self.args.service))
                return False
            
            # Store attack profile
            self.args.profile = profile
            
        return True
                    
    #------------------------------------------------------------------------------------ 