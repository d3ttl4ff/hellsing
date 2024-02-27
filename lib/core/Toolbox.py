import configparser
import os
import sys

from lib.core.Config import *
from lib.output import Output
from lib.utils.StringUtils import StringUtils

class Toolbox:
    def __init__ (self, settings, config_file='settings/toolbox.conf'):
        """
        Construct the Toolbox object.

        :param Settings settings: Settings from config file
        """
        self.settings = settings
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.tools = self.config.sections()
        # print(f"Loaded tools: {self.tools}")
        
    #------------------------------------------------------------------------------------
    # Output Methods

    def show_toolbox(self):
        """
        Display a table showing the content of the toolbox.
        """

        data = list()
        columns = [
            'Name',
            'Service',
            'Status',
            'Last Update',
            'Description',
        ]

        for tool in self.tools:

            # Install status format style
            if tool in self.tools:
                status = Output.colored('OK',
                color='green')
            else:
                status = Output.colored('Not installed',  color='red')
            
            last_update = 'Unknown'
                
            # Access configuration options
            name = self.config.get(tool, 'name')
            target_service = self.config.get(tool, 'target_service')
            description = self.config.get(tool, 'description')

            # Add line for the tool
            data.append([
                name,
                target_service,
                status,
                last_update,
                StringUtils.wrap(description, 120), # Max line length
            ])

        Output.table(columns, data, hrules=False)

    #------------------------------------------------------------------------------------
    
    def update_tool(self, tool_name):
        """
        Update the specified tool.

        :param str tool_name: Name of the tool to update
        """
        
        
