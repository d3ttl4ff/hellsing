from collections import defaultdict
import configparser
import subprocess
import sys
import os

from configparser import ConfigParser
from lib.core.Config import *
from lib.core.Exceptions import SettingsException
from lib.core.ServicesConfig import ServicesConfig
from lib.core.Toolbox import Toolbox
from lib.core.Attack import Attack
from lib.utils.DefaultConfigParser import DefaultConfigParser
from lib.utils.FileUtils import FileUtils

class Settings:
    def __init__(self):
        self.config_parsers = configparser.ConfigParser()
        
        # Instantiate Toolbox with the current settings instance
        self.toolbox = None
        # Instantiate Attack with the current settings instance
        self.attack = None
        # Instantiate ServicesConfig with the current settings instance
        self.services = None

        # Check for the Settings Directory 
        if not os.path.isdir(SETTINGS_DIR):
            raise SettingsException('Configuration Settings directory not found: {0}'.format(dir=SETTINGS_DIR))
        
        files = os.listdir(SETTINGS_DIR)
        
        # Parse configuration files and create objects
        self.__parse_all_config_files(files)
        self.__create_toolbox()
        self.__create_attack()
        
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
    
    # Toolbox methods
    def show_all_tools(self):
        Output.print_title("Toolbox status")
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
    
    # Parse the attack configuration file
    def __create_attack(self):
        """
        Parse the attack configuration file.
        """
        self.attack = Attack(self)
    
    #------------------------------------------------------------------------------------  
    
    # Attack methods
    # Set the target for the attack and execute the relevant commands
    def set_target(self, target, banner_condition=False, run_only_condition=False, run_exclude_condition=False, categories=None, profile_condition=False, profile=None):
        """
        Set the target for the attack and execute the relevant commands.

        :param target: Target URL or IP address
        """
        
        self.attack.set_target(target, 
                               banner_condition=banner_condition, 
                               run_only_condition=run_only_condition, 
                               run_exclude_condition=run_exclude_condition, 
                               categories=categories,
                               profile_condition=profile_condition,
                               profile=profile)
        
    #------------------------------------------------------------------------------------ 

    # Get profile details
    def get_profile_details(self, profile_name):
        """
        Retrieve the details for a specified profile from the configuration file.
        
        :param config_file_path: Path to the configuration file.
        :param profile_name: The name of the profile to retrieve.
        :return: A dictionary with the profile's details, or None if the profile is not found.
        """
        config = configparser.ConfigParser()
        config.read(ATTACK_PROFILES_CONF_FILE + CONF_EXT)
        
        if profile_name in config:
            http_tools = config[profile_name].get('http', '').strip().split(',')
            # Filter out commented or empty lines
            http_tools = [tool.strip() for tool in http_tools if tool.strip() and not tool.strip().startswith('#')]
            return {
                'description': config[profile_name].get('description', '').strip(),
                'http': http_tools
            }
        else:
            return None
