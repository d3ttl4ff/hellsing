import configparser
import os
import subprocess
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
        Update a specified tool by its name.

        :param str tool_name: The name of the tool to update.
        """
        # Normalize the tool_name to lowercase
        tool_name_lower = tool_name.lower()

        # Attempt to find the tool in the config, comparing lowercased names
        for tool in self.tools:
            if self.config.get(tool, 'name').lower() == tool_name_lower:
                # If found, execute the update command
                try:
                    update_command = self.config.get(tool, 'update')
                    print(f"Updating {tool_name}...")
                    subprocess.run(update_command, shell=True, check=True)
                    print(f"{tool_name} updated successfully.")
                    return
                except subprocess.CalledProcessError as e:
                    print(f"Error updating {tool_name}: {e}")
                    return
                except configparser.NoOptionError:
                    print(f"Update command not defined for {tool_name}.")
                    return

        # If the loop completes without finding and updating the tool, it doesn't exist in the config
        print(f"Tool {tool_name} not found in the toolbox configuration.")
        
        
