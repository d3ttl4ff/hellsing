import configparser
import subprocess
import sys
import os

from lib.core.Config import *
from lib.core.Exceptions import SettingsException
from lib.core.Toolbox import Toolbox

class Settings:
    def __init__(self, config_file='settings/toolbox.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.tools = self.config.sections()
        
        # Instantiate Toolbox with the current settings instance
        self.toolbox = None
        self.toolbox = Toolbox(self)

        # Check for the Settings Directory 
        if not os.path.isdir(SETTINGS_DIR):
            raise SettingsException('Configuration Settings directory not found: {0}'.format(dir=SETTINGS_DIR))
        
        files = os.listdir(SETTINGS_DIR)
        
        # Parse configuration files and create objects
        self.__parse_all_config_files(files)
        self.__create_toolbox()
        
    def show_all_tools(self):
        Output.print_title("Installed tools status")
        self.toolbox.show_toolbox()

    def install_tool(self, tool_name):
        Output.print_title("Install tools")
        self.toolbox.install_tool(tool_name)

    def install_all_tools(self):
        Output.print_title("Install tools")
        self.toolbox.install_all()
        
    def update_tool(self, tool_name):
        Output.print_title("Update tools")
        self.toolbox.update_tool(tool_name)

    def update_all_tools(self):
        Output.print_title("Update tools")
        self.toolbox.update_all()

    def uninstall_tool(self, tool_name):
        Output.print_title("Uninstall tools")
        self.toolbox.uninstall_tool(tool_name)

    def uninstall_all_tools(self):
        Output.print_title("Uninstall tools")
        self.toolbox.uninstall_all_tools()

    def check_tool(self, tool_name):
        Output.print_title("Check tools")
        self.toolbox.check_tool(tool_name)
        
    def check_all_tools(self):
        Output.print_title("Check tools")
        self.toolbox.check_all()
        
    