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
from lib.utils.NetworkUtils import NetworkUtils

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
        
        # creating NetworkUtils object
        self.netutils = NetworkUtils()
        # creating Output object
        self.output = Output()

    #------------------------------------------------------------------------------------
    
    # Attack methods    
    def set_target(self, target):
        """
        Set the target for the attack and execute the relevant commands.

        :param target: Target URL or IP address
        """ 
        protocol, base_target, specified_port, domain = '', '', None, ''
        is_ip_address = False
        ip_address = ''
            
        # Check if the target is a URL
        if target.startswith('http://') or target.startswith('https://'):
            protocol, _, rest = target.partition("://")
            if '/' in rest:
                base_target = rest.split('/', 1)[0]
            else:
                base_target = rest
            if ':' in base_target:
                base_target, port_str = base_target.rsplit(':', 1)
                if self.netutils.is_valid_port(port_str):
                    specified_port = port_str
                else:
                    logger.error(f"Invalid port number: {port_str}.")
                    return
                
            # Check if base_target is an IP address
            try:
                socket.inet_aton(base_target)
                is_ip_address = True
                ip_address = base_target
                domain = self.netutils.reverse_dns_lookup(ip_address) or base_target
                logger.info('IP given as target in URL') 
                logger.success(f'Target IP : {ip_address}' + '\n')
            except socket.error:
                # Not an IP, treat as a domain
                is_ip_address = False
                domain = base_target  # Use the base target as the domain
                logger.info('Domain given as target in URL')
                logger.success(f'Target Domain : {domain}' + '\n')
            
            # Log warnings or info if service is specified or not
            logger.info('URL given as target')
            logger.success(f'Target URL : {protocol}://{base_target}' + '\n')

        else:
            # Target does not start with http:// or https://, check if it's an IP address or a plain hostname
            if ':' in target:
                base_target, port_str = target.split(':', 1)
                if self.netutils.is_valid_port(port_str):
                    specified_port = port_str
                else:
                    logger.error(f"Invalid port number: {port_str}")
                    return
            else:
                base_target = target

            # Check if the base target is an IP address
            try:
                socket.inet_aton(base_target)
                is_ip_address = True
                ip_address = base_target 
                domain = self.netutils.reverse_dns_lookup(base_target) or base_target
                
                logger.info('IP given as target') 
                logger.success(f'Target IP : {ip_address}' + '\n')
            except socket.error:
                is_ip_address = False
                domain = base_target.split("//")[-1].split("/")[0]
                ip_address = self.netutils.dns_lookup(domain) or base_target
                logger.info('Hostname given as target')
                logger.success(f'Target Hostname : {base_target}' + '\n')

        # Fetch the default port if not specified
        # default_port = self.config['config'].get('default_port', '80')
        default_port = NetworkUtils.get_port_from_url(protocol + "://" + base_target)
        port = str(specified_port if specified_port else default_port)
            
        print(f"Domain: {domain}")

        # To track the last printed category
        last_category = None

        # List of section names to exclude
        excluded_sections = ["config", "specific_options", "products"]

        for tool in self.tools:
            if tool.lower() in excluded_sections:
                continue
            
            tool_config = self.config[tool]
            current_category = tool_config.get('category', None)

            # Print the category title if it's different from the last one
            if current_category and current_category != last_category:
                self.output.print_title(current_category)
                last_category = current_category
                
            tool_config = self.config[tool]
            command_template = tool_config.get('command_1', None)
            if command_template:
                command = command_template
                if "[URL]" in command:
                    command = command.replace("[URL]", f"{protocol}://{domain if not is_ip_address else base_target}:{port}")
                if "[IP]" in command:
                    command = command.replace("[IP]", ip_address if not is_ip_address else base_target)
                if "[DOMAIN]" in command:
                    extracted_domain = self.netutils.extract_secondary_domain(domain)
                    command = command.replace("[DOMAIN]", extracted_domain)
                command = command.replace("[PORT]", port)
                
                # Check if the tool's execution directory exists
                tool_name = tool_config.get('tool', '').lower()
                tool_dir_path = HTTP_TOOLBOX_DIR + '/' + tool_name
                
                if os.path.isdir(tool_dir_path):
                    # Change to the tool's directory and execute the command
                    os.chdir(tool_dir_path)

                display_check_name = tool_config.get('name', None)
                display_check_tool_name = tool_config.get('tool', None)
                
                try:
                    self.output.print_subtitle(display_check_name, display_check_tool_name, command)
                    subprocess.run(shlex.split(command), check=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error executing {tool}: {e}")
                finally:
                    # Change back to the original directory after execution
                    if os.path.isdir(tool_dir_path):
                        os.chdir(TOOL_BASEPATH)  # Adjust this path to return to the original directory as needed
                print('\n')
            else:
                logger.error(f"No command template found for {tool}.\n")

        logger.success("All applicable tools have been executed for the target.\n")
        
    
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
        
        
    