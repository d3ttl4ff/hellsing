#!/usr/bin/env python3
### Hellsing main function

import signal
import sys
import traceback
import os

# from lib.core.ArgumentsParser import ArgumentsParser
from lib.core.ArgumentParserInteractive import ArgumentsParser
from lib.core.Config import *
from lib.core.Exceptions import *
from lib.core.Settings import Settings
from lib.controller.MainController import MainController
# from lib.db.Mission import Mission
# from lib.db.Session import *
from lib.output.Logger import logger

# Signal handler for SIGTSTP (Ctrl+Z)
def sigtstp_handler(signum, frame):
    print()
    logger.error('Ctrl+Z received! Terminating...')
    sys.exit(0)

class Program:
    def __init__(self):
        # Check for root privileges
        if os.geteuid() != 0:
            logger.error("This program needs to be run with sudo or as root.")
            sys.exit(1)
        
        # Register the SIGTSTP (Ctrl+Z) handler
        signal.signal(signal.SIGTSTP, sigtstp_handler)

        try:
            print(BANNER)
            
            # Parse settings files
            settings = Settings()

            # Parse command-line arguments
            arguments = ArgumentsParser(settings)
            
            # Controller
            controller = MainController(arguments, settings)
            controller.run()

        except KeyboardInterrupt:
            print('\n')
            # logger.error('Ctrl+C received ! Terminating...')
            # sys.exit(0)
        
            try:
                exit_key = input(Output.input_exit_choice('Do you want to exit (y/n)? '))
                
                if exit_key == 'y':
                    logger.error('Terminating...')
                    sys.exit(0)
                else:
                    print()
                    Output.print('>>> Program restarting...', color='10', attrs='bold')
                    Program()
            except KeyboardInterrupt:
                print()
                logger.error('Ctrl+C received! Terminating...')
                sys.exit(0)
            
        except (SettingsException, AttackException) as e:
            logger.error(e)
            sys.exit(1)
        except (ValueError, ArgumentsException):
            print
            sys.exit(1)
        except Exception as e:
            print
            logger.error('Unexpected error occured: {0}'.format(str(e)))
            traceback.print_exc()
            sys.exit(1)
        # finally:
        #     print()
        #     exit_key = input(Output.input_exit_choice('Do you want to exit (y/n)? '))
            
        #     if exit_key == 'y':
        #         logger.error('Terminating...')
        #         sys.exit(0)
        #     else:
        #         print()
        #         Output.print('>>> Program restarting...', color='10', attrs='bold')
        #         Program()

if __name__ == '__main__':
    main = Program()