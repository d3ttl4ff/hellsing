import configparser
import subprocess
import sys
import os

from lib.core.Config import *
from lib.core.Exceptions import SettingsException
from lib.core.ServicesConfig import ServicesConfig
from lib.core.Toolbox import Toolbox
from lib.utils.DefaultConfigParser import DefaultConfigParser
from lib.utils.FileUtils import FileUtils

class Settings:
    def __init__(self):
        self.config_parsers = configparser.ConfigParser()
        
        # Instantiate Toolbox with the current settings instance
        self.toolbox = None

        # Check for the Settings Directory 
        if not os.path.isdir(SETTINGS_DIR):
            raise SettingsException('Configuration Settings directory not found: {0}'.format(dir=SETTINGS_DIR))
        
        files = os.listdir(SETTINGS_DIR)
        
        # Parse configuration files and create objects
        self.__parse_all_config_files(files)
        self.__create_toolbox()
        
    #------------------------------------------------------------------------------------
    
    # Parse all configuration files into the settings directory
    def __parse_all_config_files(self, files):
        """
        Parse all configuration files into the settings directory.

        :param list files: List of files in settings directory
        """
        services = list()
        for f in files:
            name = FileUtils.remove_ext(f).lower().strip()
            if name not in (TOOLBOX_CONF_FILE,
                            ATTACK_PROFILES_CONF_FILE):
                services.append(name)

            full_path = FileUtils.concat_path(SETTINGS_DIR, f)
            self.config_parsers = DefaultConfigParser()
            # Utf8 to avoid encoding issues
            self.config_parsers.read(full_path, 'utf8') 

        self.services = ServicesConfig(services)

    #------------------------------------------------------------------------------------
    
    # Parse the toolbox configuration file
    def __create_toolbox(self):
        """
        Parse the toolbox configuration file.
        """
        self.toolbox = Toolbox(self)

    #------------------------------------------------------------------------------------
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
    
    #------------------------------------------------------------------------------------    
    