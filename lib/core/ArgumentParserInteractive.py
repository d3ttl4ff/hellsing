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
from lib.utils.NetworkUtils import NetworkUtils

class ArgumentsParser:
    formatter_class = lambda prog: LineWrapRawTextHelpFormatter(
        prog, max_help_position=ARGPARSE_MAX_HELP_POS)
        
    def __init__(self, settings):
        self.settings = settings
        self.mode = None
        self.args = None

        # Set up the initial parser to capture the command or check for absence of commands
        parser = argparse.ArgumentParser(
            usage=USAGE, 
            formatter_class=ArgumentsParser.formatter_class)
        parser.add_argument('command', nargs='?', help=argparse.SUPPRESS)  # 'nargs' is set to '?' to make the command optional

        # Parse only the first argument which is expected to be the command
        args, unknown = parser.parse_known_args(sys.argv[1:2])

        # If no command is provided (i.e., the user just runs the script without arguments)
        if not args.command:
            self.prompt_user()  # Call the interactive prompt
            return  # Return after handling interaction to avoid further parsing errors

        # Handle the command if provided
        if not hasattr(self, args.command):
            logger.error('Unrecognized command')
            parser.print_help()
            raise ArgumentsException()

        # Proceed with the command-specific method
        getattr(self, args.command)()

        # Check arguments for validity
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
        target.add_argument(
            '--banner',
            help    = 'Retrieve the banner of the target',
            action  = 'store_true',
            dest    = 'banner',
            default = None)
        
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
            # status &= self.check_args_target()
            if self.args.banner:      
                pass
            pass
        else:
            logger.error('Invalid mode:attack arguments. Please provide exactly one action at a time.')
            return False

        status &= self.__check_args_attack_selection()
        
        return status
    
    def __check_args_attack_selection(self):
        """Check arguments for subcommand Attack (selection)"""
        
        # Select a subset of checks to run
        categories = self.args.run_only or self.args.run_exclude
        
        if categories:
            categories = categories.split(',')
            
            # Get the list of all supported categories
            supported_categories = NetworkUtils.list_all_categories()
            
            for cat in categories:
                if cat not in supported_categories:
                    logger.error('Category "{cat}" is not supported. ' \
                        'Check "attack -h for more information".'.format(cat=cat))
                    return False
            
            # Store the list of categories
            if self.args.run_only:
                self.args.run_only = categories
            else:
                self.args.run_exclude = categories
                
        # Select attack profile
        elif self.args.profile:
            
            profile_details = self.settings.get_profile_details(self.args.profile.lower())
            
            if not profile_details:
                logger.error(f'Profile "{self.args.profile}" is not supported. Check "attack -h" for more information.')
                return False
                
            # Store attack profile
            self.args.profile = profile_details
            
        return True
    
    #------------------------------------------------------------------------------------
    def prompt_user(self):
        """Prompt user for inputs if no arguments are provided."""
        mode_input = input("Select mode:\n 1. Toolbox\n 2. Attack\nEnter choice (1 or 2): ")
        
        if mode_input == '1':
            self.prompt_toolbox_mode()
        elif mode_input == '2':
            self.prompt_attack_mode()
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)

    def prompt_toolbox_mode(self):
        """Interactive prompt for Toolbox mode."""
        print("Select an operation:")
        operations = {
            'A': '--show-all',
            'B': '--install-tool',
            'C': '--install-all',
            'D': '--update-tool',
            'E': '--update-all',
            'F': '--uninstall-tool',
            'G': '--uninstall-all',
            'H': '--check-tool',
            'I': '--check-all'
        }
        for key, value in operations.items():
            print(f"{key}: {value}")
        operation_key = input("Enter your choice: ").upper()

        if operation_key in operations:
            option = operations[operation_key]
            if option in ['--install-tool', '--update-tool', '--uninstall-tool', '--check-tool']:
                tool_name = input("Enter tool name: ")
                sys.argv = ['hellsing.py', 'toolbox', option, tool_name]
            else:
                sys.argv = ['hellsing.py', 'toolbox', option]
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)

        self.toolbox()
        print("Operation completed.")

    def prompt_attack_mode(self):
        """Interactive prompt for Attack mode."""
        target = input("Enter target (IP/URL/Domain): ")
        if not target:
            print("Target is mandatory. Exiting.")
            sys.exit(1)

        banner_info = input("Retrieve banner information? (yes/no): ")
        if banner_info.lower() == 'yes':
            sys.argv = ['hellsing.py', 'attack', '--target', target, '--banner']
        else:
            print("Select additional configurations:")
            print(" 1. Profile")
            print(" 2. Run only certain categories")
            print(" 3. Exclude certain categories")
            config_choice = input("Enter choice: ")
            if config_choice == '1':
                print("Available profiles: basic, fast, aggressive")
                profile = input("Enter profile: ")
                sys.argv = ['hellsing.py', 'attack', '--target', target, '--profile', profile]
            elif config_choice == '2':
                categories = input("Enter categories to run (comma-separated): ")
                sys.argv = ['hellsing.py', 'attack', '--target', target, '--run-only', categories]
            elif config_choice == '3':
                categories = input("Enter categories to exclude (comma-separated): ")
                sys.argv = ['hellsing.py', 'attack', '--target', target, '--run-exclude', categories]
            elif config_choice == '4':
                sys.argv = ['hellsing.py', 'attack', '--target', target]
            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)

        self.attack()
        print("Attack operation completed.")

