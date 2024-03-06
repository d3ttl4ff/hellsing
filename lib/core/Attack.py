import configparser
from datetime import datetime
import os
import shlex
import socket
import subprocess
import sys
import shutil
from urllib.parse import urlparse

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
    def set_target(self, target, banner_condition=False):
        """
        Set the target for the attack and execute the relevant commands.

        :param target: Target URL or IP address
        """ 
        protocol, base_target, specified_port, domain = '', '', None, ''
        is_ip_address = False
        ip_address = ''
            
        # Parse the target to see if it's a URL with a scheme (http/https)
        parsed_url = urlparse(target)
        if parsed_url.scheme in ['http', 'https']:
            protocol = parsed_url.scheme
            base_target = parsed_url.hostname
            specified_port = parsed_url.port  # This can be None if no port is specified
            target_path = parsed_url.path
            
            logger.info('URL given as target')
            logger.success(f'Target URL: {protocol}://{base_target}')
        else:
            # Handle case without scheme - could be IP or domain
            if ':' in target:
                base_target, port_str = target.split(':', 1)
                if self.netutils.is_valid_port(port_str):
                    specified_port = port_str
                else:
                    logger.error(f"Invalid port number: {port_str}. Must be in the range [0-65535]")
                    return
            else:
                base_target = target
            
        # Validate IP address or perform DNS lookup
        try:
            socket.inet_aton(base_target)
            
            is_ip_address = True
            ip_address = base_target
            domain = self.netutils.reverse_dns_lookup(ip_address) or base_target
            
            logger.info('IP address given as target')
            logger.success(f'Target IP: {ip_address}')
        except socket.error:
            # If it's not a valid IP address, treat it as a domain
            is_ip_address = False
            domain = base_target
            
            if protocol:  # If protocol was parsed, it's a URL without a port
                ip_address = self.netutils.dns_lookup(domain) or base_target
                logger.info('Domain name in URL given as target')
            else:
                logger.info('Hostname given as target')
                
            logger.success(f'Target Domain: {domain}')

        # Fetch the default port if not specified
        default_port = NetworkUtils.get_port_from_url(protocol + "://" + base_target)
        port = str(specified_port if specified_port else default_port)

        # # Perform DNS or reverse DNS lookups as necessary
        # if is_ip_address:
        #     domain = self.netutils.reverse_dns_lookup(base_target) or base_target
        # else:
        #     domain = base_target.split("//")[-1].split("/")[0]
        #     ip_address = self.netutils.dns_lookup(domain) or base_target

        # For URLs or domains
        if not is_ip_address:
            # If it's a URL/domain, use HTTPS port by default if the scheme is https, else use HTTP port
            default_port = 443 if protocol == 'https' else 80
            port = specified_port if specified_port else default_port
            if not self.netutils.is_host_reachable(domain, port):
                logger.error(f"Host {domain} is not reachable.")
                return
            logger.info(f"Host {domain} is reachable.")
        else:
            # For IP addresses
            if not self.netutils.is_host_reachable(ip_address, 80):
                logger.error(f"IP address {ip_address} is not reachable.")
                return
            logger.info(f"IP address {ip_address} is reachable.")
        
        # Check if banner grab is specified
        if banner_condition:
            self.banner_grab(target, port, domain, ip_address, protocol, specified_port)
        else:
            self.banner_grab(target, port, domain, ip_address, protocol, specified_port)
            self.run_default(protocol, base_target, specified_port, domain, is_ip_address, ip_address, port)
        
    #------------------------------------------------------------------------------------  
    
    # Banner grab the target
    def banner_grab(self, target, port, domain, ip_address, protocol, specified_port):
        """
        Perform a banner grab on the specified target and port.

        :param str target: Target IP address or hostname
        :param str port: Port number
        """
        try:
            print(f"[>] Banner grabbing...")
            logger.info(f"Target---------| {target}")
            logger.info(f"Port-----------| {port}")
            logger.info(f"Domain---------| {domain}")
            logger.info(f"IP-------------| {ip_address}")
            logger.info(f"Protocol-------| {protocol}")
            logger.info(f"Specified port-| {specified_port}")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            logger.error(f"Error performing banner grab: {e}")
       
    #------------------------------------------------------------------------------------
    
    # Run the attack tools in default mode
    def run_default(self, protocol, base_target, specified_port, domain, is_ip_address, ip_address, port):
        """
        Run the attack tools in default mode.
        """
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
    
    #------------------------------------------------------------------------------------
    

    
    #------------------------------------------------------------------------------------
     
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
        
        
    