#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### Core > Config
###
import colored
import os

from lib.core.Constants import *
from lib._version import __version__
from lib.output import Output

#----------------------------------------------------------------------------------------
# Banner/Help
__version__ = Output.colored(f'{__version__}                            ', color='black', highlight='red', attrs='bold')
prefix = Output.colored('                         v ', color='black', highlight='red', attrs='bold')
subtitle = Output.colored('█▓▓░░░░░░░░░[ Web Pentesting Automation Suite ]░░░░░░░░░▒▓█', color='black', highlight='red', attrs='bold')
context = Output.colored(
  """▒ ░░▒░▒░░ ▒░ ░░ ▒░▓  ░░ ▒░▓  ░▒ ▒▓▒ ▒ ░░▓  ░ ▒░   ▒ ▒  ░▒   ▒
  ▒ ░▒░ ░ ░ ░  ░░ ░ ▒  ░░ ░ ▒  ░░ ░▒  ░ ░ ▒ ░░ ░░   ░ ▒░  ░   ░
  ░  ░░ ░   ░     ░ ░     ░ ░   ░  ░  ░   ▒ ░   ░   ░ ░ ░ ░   ░ 
  ░  ░  ░   ░  ░    ░  ░    ░  ░      ░   ░           ░       ░ 
    011010001100100110110011011001110010110100011011101100111""", color='red', attrs='bold')

BANNER = colored.stylize("""
                         
  ██╗  ██╗███████╗██╗     ██╗     ███████╗██╗███╗   ██╗ ██████╗ 
  ██║  ██║██╔════╝██║     ██║     ██╔════╝██║████╗  ██║██╔════╝ 
  ███████║█████╗  ██║     ██║     ███████╗██║██╔██╗ ██║██║  ███╗
  ██╔══██║██╔══╝  ██║     ██║     ╚════██║██║██║╚██╗██║██║   ██║
  ██║  ██║███████╗███████╗███████╗███████║██║██║ ╚████║╚██████╔╝
  ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝
   {subtitle}
  {context}                                                              
{version}
                 
""".format(version=prefix + __version__, subtitle=subtitle, context=context), colored.fg('red') + colored.attr('bold'))

USAGE = """
python3 hellsing.py <command> [<args>]

Supported commands:
   toolbox    Manage the toolbox
   info       View supported services/options/checks
   db         Define missions scopes, keep tracks of targets & view attacks results
   attack     Run security checks against targets
   
"""

ATTACK_EXAMPLES = colored.stylize('Examples:', colored.attr('bold')) + """
  - Run all security checks against an URL in interactive mode (break before each check):
  python3 hellsing.py attack -t http://www.example.com/ 

  - Run all security checks against a MS-SQL service (without user interaction) and add results to the mission "mayhem" in db:
  python3 hellsing.py attack -t 192.168.1.42:1433 -s mssql --add2db mayhem --fast

  - Run only "recon" and "vulnscan" security checks against an FTP service and add results to the mission "mayhem" in db:
  python3 hellsing.py attack -t 192.168.1.142:21 -s ftp --cat-only recon,vulnscan --add2db mayhem

  - Run security checks against all FTP services running on 2121/tcp and all HTTP services from the mission "mayhem" in db:
  python3 hellsing.py attack -m mayhem -f "port=2121;service=ftp" -f "service=http"

  - Search for "easy wins" (critical vulns / easy to exploit) on all services registered in mission "mayhem" in db:
  python3 hellsing.py attack -m mayhem --profile red-team --fast
"""

DB_INTRO = """
The local database stores the missions, targets info & attacks results.
This shell allows for easy access to this database. New missions can be added and
scopes can be defined by importing new targets.
"""


#----------------------------------------------------------------------------------------
# Arguments Parsing Settings

ARGPARSE_MAX_HELP_POS    = 45
# TARGET_FILTERS           = {
#     'ip'       : FilterData.IP, 
#     'host'     : FilterData.HOST,
#     'port'     : FilterData.PORT, 
#     'service'  : FilterData.SERVICE, 
#     'url'      : FilterData.URL,
#     'osfamily' : FilterData.OS_FAMILY,
#     'banner'   : FilterData.BANNER,
# }

#----------------------------------------------------------------------------------------
# Basic Settings

TOOL_BASEPATH             = os.path.dirname(os.path.realpath(__file__+'/../..'))
TOOLBOX_DIR               = TOOL_BASEPATH + '/toolbox'
HTTP_TOOLBOX_DIR          = TOOLBOX_DIR + '/http'

TOOL_RELATED_BASEPATH     = os.path.dirname(os.path.relpath(__file__))
TOOLBOX_RELATIVE_DIR      = TOOL_RELATED_BASEPATH + '/toolbox'
HTTP_TOOLBOX_RELATIVE_DIR = TOOLBOX_RELATIVE_DIR + '/http'
# DEFAULT_OUTPUT_DIR = 'output'
WEBSHELLS_DIR      = TOOL_BASEPATH + '/webshells'
WORDLISTS_DIR      = TOOL_BASEPATH + '/wordlists'
# DB_FILE            = TOOL_BASEPATH + '/local.db'
# DB_HIST_FILE       = TOOL_BASEPATH + '/.dbhistory'
# REPORT_TPL_DIR     = TOOL_BASEPATH + '/lib/reporter/templates'
# REPORT_PATH        = TOOL_BASEPATH + '/reports'
# VIRTUALENVS_DIR    = TOOL_BASEPATH + '/toolbox/virtualenvs'

#----------------------------------------------------------------------------------------
# # Display Settings

# ATTACK_SUMMARY_TABLE_MAX_SIZE = 18

# #----------------------------------------------------------------------------------------
# # Settings Files

SETTINGS_DIR              = TOOL_BASEPATH + '/settings'
CONF_EXT                  = '.conf'
TOOLBOX_CONF_FILE         = SETTINGS_DIR + '/toolbox'
HTTP_CONF_FILE            = SETTINGS_DIR + '/http'

ATTACK_PROFILES_CONF_FILE = SETTINGS_DIR + '/attack_profiles'
# INSTALL_STATUS_CONF_FILE  = '_install_status'
# PREFIX_SECTION_CHECK      = 'check_'
# MULTI_CONF                = 'multi'
# MULTI_TOOLBOX_SUBDIR      = 'multi'

# TOOL_OPTIONS = {
#     MANDATORY: [
#         'name',
#         'description',
#         'target_service',
#     ],
#     OPTIONAL: [
#         'virtualenv',
#         'install',
#         'update',
#         'check_command',
#     ]
# }

# SERVICE_CHECKS_CONFIG_OPTIONS = {
#     MANDATORY: [
#         'default_port',
#         'protocol',
#         'categories',
#     ],
#     OPTIONAL: [
#         'auth_types'
#     ]
# }

# CHECK_OPTIONS = {
#     MANDATORY: [
#         'name',
#         'category',
#         'description',
#         'tool',
#         # command
#     ],
#     OPTIONAL: [
#         'apikey',
#     ]
# }

# OPTIONS_ENCRYTPED_PROTO = (
#     'ftps',
#     'https',
#     'rmissl',
#     'smtps',
#     'telnets',
# )

