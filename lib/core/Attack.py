import configparser
from datetime import datetime
import os
import shlex
import socket
import subprocess
import sys
import shutil

from lib.core.Config import *
from lib.output import Output
from lib.output.Logger import logger
from lib.utils.StringUtils import StringUtils

class Attack:
    def __init__ (self, settings):
        """
        Construct the Attack object.

        :param Settings settings: Settings from config file
        """
        self.settings = settings
        self.config = configparser.ConfigParser()
        self.config.read(HTTP_CONF_FILE + CONF_EXT)
        self.tools = self.config.sections()
        self.basepath = HTTP_TOOLBOX_DIR

    #------------------------------------------------------------------------------------
    
    # Attack methods    
    def set_target(self, target):
        """
        Set the target for the attack and execute the relevant commands.

        :param target: Target URL or IP address
        """
        # # Determine if target is an IP address or URL
        # if "http://" in target or "https://" in target:
        #     target_mode = "URL"
        # else:
        #     target_mode = "IP"

            
        # Extract the base target and check if a port is specified
        if "://" in target:
            # For URLs, split by "://" then check for a port after the domain
            base_target, _, path_port_fragment = target.partition("://")
            domain_port = path_port_fragment.split("/", 1)[0]  # Get the domain:port part
            if ':' in domain_port:
                base_target, specified_port = domain_port.rsplit(':', 1)
                base_target = base_target + "://" + specified_port  # Reconstruct base_target with protocol
            else:
                specified_port = None
                base_target = target
        else:
            # For IP or domain, simply split by ":"
            parts = target.split(':')
            if len(parts) == 2:
                base_target, specified_port = parts
            else:
                base_target, specified_port = target, None
        
        # Fetch the default port from the config if no port is specified
        default_port = self.config['config'].get('default_port', '80')
        port = specified_port if specified_port else default_port
            
        # List of section names to exclude
        excluded_sections = ["config", "specific_options", "products"]

        # Iterate through the tools in the config file and execute relevant commands
        for tool in self.tools:
            # Skip excluded sections
            if tool.lower() in excluded_sections:
                continue
            
            tool_config = self.config[tool]
            command_template = tool_config.get('command_1', None)
            if command_template:
                # Determine the correct command based on target type
                if "[URL]" in command_template:
                    command = command_template.replace("[URL]", base_target)
                elif "[IP]" in command_template:
                    command = command_template.replace("[IP]", base_target)
                elif "[DOMAIN]" in command_template:
                    command = command_template.replace("[DOMAIN]", base_target.split("//")[-1])  # Extract domain from URL
                
                # Apply the port to the command
                command = command.replace("[PORT]", port)
                
                # Check if the tool's execution directory exists
                tool_name = tool_config.get('tool', '').lower()
                tool_dir_path = HTTP_TOOLBOX_DIR + '/' + tool_name
                
                if os.path.isdir(tool_dir_path):
                    # Change to the tool's directory and execute the command
                    os.chdir(tool_dir_path)
                    print(f"Changed directory to {tool_dir_path}")
                else:
                    # Tool can be executed directly, no directory change needed
                    print(f"Executing {tool_name} directly without changing directory.")

                # Execute the command
                try:
                    print(f"Executing: {command}")
                    subprocess.run(shlex.split(command), check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error executing {tool}: {e}")
                finally:
                    # Change back to the original directory after execution
                    if os.path.isdir(tool_dir_path):
                        os.chdir(TOOL_BASEPATH)  # Adjust this path to return to the original directory as needed
                print('\n')
            else:
                print(f"No command template found for {tool}.\n")

        print("All applicable tools have been executed for the target.\n")
        
    
    def set_service(self, service):
        """
        Set the service to attack.

        :param str service: Service to attack
        """
        self.service = service
        
    
    def use_profile(self, profile):
        """
        Use the specified attack profile.

        :param str profile: Attack profile to use
        """
        self.profile = profile
        
    
    def run_only(self, checks):
        """
        Run only the specified checks.

        :param list categories: Categories of checks to run
        """
        self.checks = checks
        
    
    def run_exclude(self, checks):
        """
        Exclude the specified checks.

        :param list categories: Categories of checks to exclude
        """
        self.exclude = checks
        
        
    