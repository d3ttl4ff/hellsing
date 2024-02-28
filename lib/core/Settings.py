import configparser
import subprocess
import sys
import os

from lib.core.Config import *
from lib.core.Toolbox import Toolbox

class Settings:
    def __init__(self, config_file='settings/toolbox.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.tools = self.config.sections()
        
        # Instantiate Toolbox with the current settings instance
        self.toolbox = Toolbox(self)

    def show_all_tools(self):
        self.toolbox.show_toolbox()

    def update_tool(self, tool_name):
        self.toolbox.update_tool(tool_name)

    def update_all_tools(self):
        self.toolbox.update_all()

    def install_tool(self, tool_name):
        self.toolbox.install_tool(tool_name)

    def install_all_tools(self):
        self.toolbox.install_all()

    def uninstall_tool(self, tool_name):
        self.toolbox.uninstall_tool(tool_name)

    def uninstall_all_tools(self):
        self.toolbox.uninstall_all_tools()

    def check_tool(self, tool_name):
        self.toolbox.check_tool(tool_name)
        
    def check_all_tools(self):
        self.toolbox.check_all()