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
            
            # Construct the expected directory path for the tool based on its name
            tool_dir_path = os.path.join(HTTP_TOOLBOX_DIR, self.config.get(tool, 'name'))
            
            last_update = 'Unknown'

            # Attempt to run the check_command if it exists and the tool directory exists
            if os.path.exists(tool_dir_path):
                try:
                    # Use git to get the last commit date in ISO format
                    result = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=iso'], cwd=tool_dir_path, text=True, capture_output=True, check=True)
                    # Extract and format the last commit date
                    last_update = result.stdout.strip()
                except subprocess.CalledProcessError:
                    pass
                
                try:
                    check_command = self.config.get(tool, 'check_command')
                    result = subprocess.run(check_command, shell=True, check=True, cwd=tool_dir_path, text=True, capture_output=True)
                    # If the check_command runs successfully, the tool is operational
                    status = Output.colored('OK', color='green')   
                except (subprocess.CalledProcessError, configparser.NoOptionError, OSError):
                    # If the check_command fails or doesn't exist, the tool is not operational
                    status = Output.colored('Not operational', color='red')
            else:
                # If the directory doesn't exist, the tool is not installed
                status = Output.colored('Not installed', color='red')
            
            # last_update = 'Unknown'
                
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
        Update a specified tool by its name, only if the tool is currently operational.

        :param str tool_name: The name of the tool to update.
        """
        # Normalize the tool_name to lowercase
        tool_name_lower = tool_name.lower()

        # Attempt to find the tool in the config, comparing lowercased names
        for tool in self.tools:
            original_name = self.config.get(tool, 'name')
            config_name = original_name.lower()

            if config_name == tool_name_lower:
                # Construct the directory path for the tool
                tool_dir = os.path.join(HTTP_TOOLBOX_DIR, original_name)

                try:
                    # Check if the tool is operational
                    check_command = self.config.get(tool, 'check_command')
                    subprocess.run(check_command, shell=True, check=True, cwd=tool_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    # If check_command succeeds, print operational status
                    Output.print(f"{tool_name} is operational.", color='yellow')

                    # Proceed with update
                    update_command = self.config.get(tool, 'update')
                    print(f"Updating {tool_name}...")
                    Output.begin_cmd(update_command)
                    subprocess.run(update_command, shell=True, check=True, cwd=tool_dir)
                    Output.print(f"{tool_name} updated successfully.", color='green')
                    return
                except subprocess.CalledProcessError:
                    print(f"An error occurred during {tool_name} the update.")
                    return
                except configparser.NoOptionError:
                    print(f"Command not defined for {tool_name}.")
                    return
                except OSError as e:
                    print(f"Error accessing directory {tool_dir} for {tool_name}: {e}")
                    return

        print(f"Tool {tool_name} not found in the toolbox configuration.")
        
    #------------------------------------------------------------------------------------
    
    def update_all(self):
        """
        Update all tools in the toolbox.
        """
        for tool in self.tools:
            self.update_tool(tool)
        
    #------------------------------------------------------------------------------------
    
    def install_tool(self, tool_name):
        """
        Install a specified tool by its name.

        :param str tool_name: The name of the tool to install.
        """
        # Normalize the tool_name to lowercase for directory naming
        tool_name_lower = tool_name.lower()

        # Attempt to find the tool in the config, comparing lowercased names
        for tool in self.tools:
            original_name = self.config.get(tool, 'name')
            config_name = original_name.lower()
            if config_name == tool_name_lower:
                # If found, construct the directory path for the tool
                tool_dir = os.path.join(HTTP_TOOLBOX_DIR, original_name)
                
                # Ensure the tool's directory exists
                os.makedirs(tool_dir, exist_ok=True)

                try:
                    install_command = self.config.get(tool, 'install')
                    Output.print(f"\n[+] Installing {tool_name}...", color='turquoise_2')
                    
                    subprocess.run(install_command, shell=True, check=True, cwd=tool_dir)
                    Output.print(f"[*] {tool_name} installed successfully in {tool_dir}.", color='green_yellow')
                    return
                except subprocess.CalledProcessError as e:
                    Output.print(f"[-] Error installing {tool_name} in {tool_dir}: {e}", color='light_red')
                    return
                except configparser.NoOptionError:
                    Output.print(f"[-] Install command not defined for {tool_name}.", color='green_yellow')
                    return
                except OSError as e:
                    Output.print(f"[-] Error creating directory {tool_dir} for {tool_name}: {e}", color='green_yellow')
                    return

        # If the loop completes without finding and installing the tool, it doesn't exist in the config
        print(f"Tool {tool_name} not found in the toolbox configuration.")

    #------------------------------------------------------------------------------------
    
    def install_all(self):
        """
        Install all tools in the toolbox.
        """
        for tool in self.tools:
            self.install_tool(tool)
            
    #------------------------------------------------------------------------------------
    
    def check_tool(self, tool_name):
        """
        Check the specified tool by executing its check_command.

        :param str tool_name: The name of the tool to check.
        """
        # Normalize the tool_name to lowercase
        tool_name_lower = tool_name.lower()

        # Attempt to find the tool in the config, comparing lowercased names
        for tool in self.tools:
            original_name = self.config.get(tool, 'name')
            config_name = original_name.lower()
            
            if config_name == tool_name_lower:
                # If found, construct the directory path for the tool
                tool_dir = os.path.join(HTTP_TOOLBOX_DIR, original_name)
                
                try:
                    check_command = self.config.get(tool, 'check_command')
                    print(f"Checking {original_name} in {tool_dir}...")
                    subprocess.run(check_command, shell=True, check=True, cwd=tool_dir, text=True, capture_output=True)
                    # Success message without showing stdout
                    print(f"{original_name} check completed successfully. Tool's available and operational.")
                    return
                except subprocess.CalledProcessError as e:
                    # Print error details including stderr
                    print(f"Error checking {original_name}: {e}\nError Output:\n{e.stderr}")
                    return
                except configparser.NoOptionError:
                    print(f"Check command not defined for {original_name}.")
                    return
                except OSError as e:
                    print(f"Error accessing directory {tool_dir} for {original_name}: {e}")
                    return

        # If the loop completes without finding and executing the check command, the tool doesn't exist in the config
        print(f"Tool {tool_name} not found in the toolbox configuration or check command is not executable.")
        
    #------------------------------------------------------------------------------------
    
    def check_all(self):
        """
        Check all tools in the toolbox.
        """
        for tool in self.tools:
            self.check_tool(tool)
            
    #------------------------------------------------------------------------------------
    

