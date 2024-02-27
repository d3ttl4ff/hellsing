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


    def show_all_tools(self):
        # Instantiate Toolbox with the current settings instance
        toolbox = Toolbox(self)
        toolbox.show_toolbox()

    def update_tool(self, tool_name):
        if tool_name in self.tools:
            update_cmd = self.config[tool_name]['update']
            subprocess.run(update_cmd, shell=True)
        else:
            print(f"Tool {tool_name} not found.")

    def update_all_tools(self):
        print(f"Current working directory: {os.getcwd()}")
        for tool in self.tools:
            self.update_tool(tool)



    def install_tool(self, tool_name):
        if tool_name in self.tools:
            install_cmd = self.config[tool_name]['install']
            subprocess.run(install_cmd, shell=True)
        else:
            print(f"Tool {tool_name} not found.")

    def install_all_tools(self):
        for tool in self.tools:
            self.install_tool(tool)

    def update_tool(self, tool_name):
        if tool_name in self.tools:
            update_cmd = self.config[tool_name]['update']
            subprocess.run(update_cmd, shell=True)
        else:
            print(f"Tool {tool_name} not found.")

    def update_all_tools(self):
        print(f"Current working directory: {os.getcwd()}")
        for tool in self.tools:
            self.update_tool(tool)

    def uninstall_tool(self, tool_name):
        # Uninstallation logic here
        pass

    def uninstall_all_tools(self):
        for tool in self.tools:
            self.uninstall_tool(tool)
