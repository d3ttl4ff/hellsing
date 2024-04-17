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

#----------------------------------------------------------------------------------------
step_arrows = Output.colored('┃⥏', color='10', attrs='bold')
step_arrows2 = Output.colored('┃⥏', color='white', attrs='bold')
step_info1 = Output.colored('To check whether the tools are properly installed and configured, go through the following steps:', color='105', attrs='bold')
step_info2 = Output.colored('To launch security checks against a target, follow these steps:', color='105', attrs='bold')
step_numbers1 = Output.colored('[1]', color='148', attrs='bold')
step_numbers2 = Output.colored('[2]', color='148', attrs='bold')
step_numbers3 = Output.colored('[3]', color='148', attrs='bold')

GENERAL_HELP = step_arrows2 + " To begin launching security assesments on a target, follow these steps:"

GENERAL_HELP_STEPS = colored.stylize("""
{arw} {info1}
    {one} Choose the "toolbox" option when prompted
    {two} Choose the "show-all" option to view all available tools and their availability
    {three} Choose the "install-all" option to install all available tools to fix or install missing tools
    
{arw} {info2}
    {one} Choose the "attack" option when prompted
    {two} Enter the target URL/IP address and the service to be checked
    {three} Choose additional options to customize the security checks when prompted
    
""".format(arw=step_arrows, info1=step_info1, info2=step_info2, one=step_numbers1, two=step_numbers2, three=step_numbers3), colored.fg('white'))

#----------------------------------------------------------------------------------------
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
DB_FILE            = TOOL_BASEPATH + '/hellsing.db'
# DB_HIST_FILE       = TOOL_BASEPATH + '/.dbhistory'

RESULTS_DIR     = TOOL_BASEPATH + '/results'
RESULTS_EXT          = '.txt'

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

