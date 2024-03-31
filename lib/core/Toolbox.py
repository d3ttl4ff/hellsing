import configparser
from datetime import datetime
import os
import subprocess
import sys
import shutil

from lib.core.Config import *
from lib.output import Output
from lib.output.Logger import logger
from lib.utils.StringUtils import StringUtils

class Toolbox:
    def __init__ (self, settings):
        """
        Construct the Toolbox object.

        :param Settings settings: Settings from config file
        """
        self.settings = settings
        self.config = configparser.ConfigParser()
        self.config.read(TOOLBOX_CONF_FILE + CONF_EXT)
        self.tools = self.config.sections()
        
    #------------------------------------------------------------------------------------
    # Toolbox methods

    def show_toolbox(self):
        """
        Display a table showing the content of the toolbox.
        """
        #tool counter
        i = 0

        data = list()
        columns = [
            '#',
            'Name',
            'Service',
            'Status',
            'Installtion Date',
            'Last Update',
            # 'Last Repo Update',
            # 'Description',
        ]

        for tool in self.tools:
            
            # Construct the expected directory path for the tool based on its name
            tool_dir_path = os.path.join(HTTP_TOOLBOX_DIR, self.config.get(tool, 'name').lower())
            
            # last_repo_update = 'Unknown'
            last_update = 'Unknown'
            installation_date = 'Unknown'
            
            # Attempt to read the last update date
            last_update_path = os.path.join(tool_dir_path, 'last_update.txt')
            if os.path.exists(last_update_path):
                with open(last_update_path, 'r') as f:
                    last_update = f.read().strip()
                    
            # Attempt to read the installation date
            installed_date_path = os.path.join(tool_dir_path, 'installed_date.txt')
            if os.path.exists(installed_date_path):
                with open(installed_date_path, 'r') as f:
                    installation_date = f.read().strip()

            # Attempt to run the check_command if it exists and the tool directory exists
            if os.path.exists(tool_dir_path):
                # try:
                #     # Use git to get the last commit date in ISO format
                #     result = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=short'], cwd=tool_dir_path, text=True, capture_output=True, check=True)
                #     # Extract and format the last commit date
                #     last_repo_update = result.stdout.strip()
                # except subprocess.CalledProcessError:
                #     pass
                
                try:
                    check_command = self.config.get(tool, 'check_command')
                    result = subprocess.run(check_command, shell=True, cwd=tool_dir_path, text=True, capture_output=True)
                    # If the check_command runs successfully, the tool is operational
                    status = Output.colored('READY', color='green')      
                except (subprocess.CalledProcessError, configparser.NoOptionError, OSError):
                    # If the check_command fails or doesn't exist, the tool is not operational
                    status = Output.colored('Not operational', color='red')
            else:
                # If the directory doesn't exist, the tool is not installed
                status = Output.colored('Not installed', color='red')
            i += 1 
            
            # last_repo_update = 'Unknown'
                
            # Access configuration options
            name = self.config.get(tool, 'name')
            target_service = self.config.get(tool, 'target_service')
            description = self.config.get(tool, 'description')

            # Add line for the tool
            data.append([
                i,
                name,
                target_service,
                status,
                installation_date,
                last_update,
                # last_repo_update,
                # StringUtils.wrap(description, 120), # Max line length
            ])

        Output.table(columns, data, hrules=False)
        
    #------------------------------------------------------------------------------------
    
    def install_tool(self, tool_name):
        """
        Install a specified tool by its name. Ask for reinstallation if the tool is not operational or already exists.

        :param str tool_name: The name of the tool to install.
        """
        # Normalize the tool_name to lowercase for directory naming
        tool_name_lower = tool_name.lower()

        # Attempt to find the tool in the config, comparing lowercased names
        for tool in self.tools:
            original_name = self.config.get(tool, 'name')
            config_name = original_name.lower()
            if config_name == tool_name_lower:
                # Construct the directory path for the tool
                tool_dir = os.path.join(HTTP_TOOLBOX_DIR, config_name)

                # Check if the tool's directory exists and if it's operational
                tool_exists = os.path.exists(tool_dir)
                operational = False
                
                if tool_exists:
                    try:
                        check_command = self.config.get(tool, 'check_command')
                        subprocess.run(check_command, shell=True, cwd=tool_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        operational = True
                    except subprocess.CalledProcessError:
                        operational = False

                # Ask for reinstallation if the tool exists but is not operational
                if tool_exists and not operational:
                    logger.warning(f"{config_name} directory exists but is not operational.")
                    user_input = input(f"[>] Do you want to reinstall it? (y/n): ")
                    if user_input.lower() != 'y':
                        logger.info("Reinstallation cancelled by the user.\n")
                        return

                    # Attempt to uninstall before reinstalling
                    self.uninstall_tool(config_name)

                # Ensure the tool's directory exists
                os.makedirs(tool_dir, exist_ok=True)

                # Proceed with installation
                try:
                    install_command = self.config.get(tool, 'install')
                    logger.info(f"Installing {tool_name}...")
                    
                    if '[HTTPTOOLBOXDIR]' in install_command:
                        install_command = install_command.replace('[HTTPTOOLBOXDIR]', HTTP_TOOLBOX_DIR)
                    
                    if operational:
                        logger.success(f"{config_name} is already installed and operational.\n")
                        return True
                    else:
                        try:
                            subprocess.run(install_command, shell=True, cwd=tool_dir)
                            logger.success(f"{tool_name} installed successfully in {tool_dir}\n")
                            
                            # Write the current date to installed_date.txt
                            installed_date_path = os.path.join(tool_dir, 'installed_date.txt')
                            with open(installed_date_path, 'w') as f:
                                f.write(datetime.now().strftime('%Y-%m-%d'))
                                
                            return True
                        except Exception as e:
                            logger.error(f"Error installing {tool_name} in {tool_dir}: {e}\n")
                            return False
                        
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error installing {tool_name} in {tool_dir}: {e}\n")
                    return
                except configparser.NoOptionError:
                    logger.error(f"Install command not defined for {tool_name}\n")
                    return
                except OSError as e:
                    logger.error(f"Error creating directory {tool_dir} for {tool_name}: {e}\n")
                    return

        # If the loop completes without finding and installing the tool, it doesn't exist in the config
        logger.error(f"Tool {tool_name} not found in the toolbox configuration.\n")
    
    #------------------------------------------------------------------------------------
    
    def install_all(self):
        """
        Install all tools in the toolbox and report on success/failure.
        """
        success_count = 0
        failure_count = 0

        for tool in self.tools:
            original_name = self.config.get(tool, 'name')
            result = self.install_tool(original_name)
            if result:
                success_count += 1
            else:
                failure_count += 1

        total_tools = len(self.tools)
        if failure_count == 0:
            logger.success(f"All {total_tools} tools have been successfully installed.")
        else:
            logger.info(f"{success_count} out of {total_tools} tools have been successfully installed.")
            logger.warning(f"{failure_count} tools could not be installed. Check logs for more details.")
            
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
                tool_dir = os.path.join(HTTP_TOOLBOX_DIR, config_name)

                try:
                    # Check if the tool is operational
                    logger.info(f"Checking operational status of {tool_name}...")
                    check_command = self.config.get(tool, 'check_command')
                    subprocess.run(check_command, shell=True, cwd=tool_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    logger.success(f"{tool_name} is operational.")

                    # Proceed with update
                    update_command = self.config.get(tool, 'update')
                    logger.info(f"Updating {tool_name}...")
                    Output.begin_cmd(update_command)
                    subprocess.run(update_command, shell=True, cwd=tool_dir)
                    logger.success(f"{tool_name} updated successfully.\n")
                    
                     # Write the current date to last_update.txt
                    last_update_path = os.path.join(tool_dir, 'last_update.txt')
                    with open(last_update_path, 'w') as f:
                        f.write(datetime.now().strftime('%Y-%m-%d'))
                    return
                except subprocess.CalledProcessError:
                    logger.error(f"An error occurred during {tool_name} the update.\n")
                    return
                except configparser.NoOptionError:
                    logger.error(f"Command not defined for {tool_name}\n")
                    return
                except FileNotFoundError:
                    logger.error(f"Tool {tool_name} directory does not exist.\n")
                    return
                except OSError as e:
                    logger.error(f"An error occured updating {tool_name}: {e}\n")
                    return

        logger.error(f"Tool {tool_name} not found in the toolbox configuration.")
        
    #------------------------------------------------------------------------------------
    
    def update_all(self):
        """
        Update all tools in the toolbox.
        """
        for tool in self.tools:
            self.update_tool(tool)
            
    #------------------------------------------------------------------------------------
    
    def uninstall_tool(self, tool_name):
        """
        Remove the specified tool by deleting its directory.

        :param str tool_name: The name of the tool to remove.
        """
        # Normalize the tool_name to lowercase for consistency
        tool_name_lower = tool_name.lower()

        # Attempt to find the tool in the config, comparing lowercased names
        found = False
        for tool in self.tools:
            original_name = self.config.get(tool, 'name')
            config_name = original_name.lower()

            if config_name == tool_name_lower:
                # If found, construct the directory path for the tool
                tool_dir = os.path.join(HTTP_TOOLBOX_DIR, config_name)

                # Check if the tool's directory exists
                if os.path.exists(tool_dir):
                    try:
                        logger.info(f"Removing {config_name}...")
                        # Remove the tool's directory
                        shutil.rmtree(tool_dir)
                        logger.success(f"{config_name} has been successfully removed.\n")
                        found = True
                        return
                    except PermissionError:
                        # If permission is denied, suggest running with sudo
                        logger.error(f"Unable to delete directory {config_name}. " \
                    "Check permissions and/or re-run with sudo\n")
                        return
                    except OSError as e:
                        logger.error(f"Error removing {config_name}: {e}\n")
                        return
                else:
                    logger.error(f"Tool {config_name} directory does not exist.\n")
                    found = True
                    return

        if not found:
            # If the loop completes without finding the tool, it doesn't exist in the config
            logger.error(f"Tool {tool_name} not found in the toolbox configuration.")
    
    #------------------------------------------------------------------------------------
    
    def uninstall_all_tools(self):
        """
        Remove all tools in the toolbox.
        """
        for tool in self.tools:
            self.uninstall_tool(tool)
            
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
                tool_dir = os.path.join(HTTP_TOOLBOX_DIR, config_name)
                
                try:
                    check_command = self.config.get(tool, 'check_command')
                    logger.info(f"Checking {config_name} in {tool_dir}...")
                    subprocess.run(check_command, shell=True, cwd=tool_dir, text=True, capture_output=True)
                    # Success message without showing stdout
                    logger.success(f"{config_name} is operational.\n")
                    return
                except subprocess.CalledProcessError as e:
                    # Print error details including stderr
                    logger.error(f"Error checking {config_name}: {e}\nError Output:\n{e.stderr}")
                    return
                except configparser.NoOptionError:
                    logger.error(f"Check command not defined for {config_name}.\n")
                    return
                except FileNotFoundError:
                    logger.error(f"Tool {tool_name} directory does not exist.\n")
                    return
                except OSError as e:
                    logger.error(f"Error accessing directory {tool_dir} for {config_name}: {e}\n")
                    return

        # If the loop completes without finding and executing the check command, the tool doesn't exist in the config
        logger.error(f"Tool {tool_name} not found in the toolbox configuration or check command is not executable.\n")
        
    #------------------------------------------------------------------------------------
    
    def check_all(self):
        """
        Check all tools in the toolbox.
        """        
        for tool in self.tools:
            self.check_tool(tool)
            
    #------------------------------------------------------------------------------------

