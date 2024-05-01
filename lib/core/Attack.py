import configparser
from datetime import datetime
import os
import re
import shlex
import socket
import subprocess
import sys
import shutil
import time
from urllib.parse import urlparse

from lib.core.Config import *
from lib.filtermodules.matchstring import MatchString
from lib.filtermodules.exploit_operations import ExploitOperations
from lib.output import Output
from lib.output.Spinner import Spinner
from lib.output.Logger import logger
from lib.utils.StringUtils import StringUtils
from lib.utils.NetworkUtils import NetworkUtils
from lib.filtermodules.vuln.httpVulnRemediation import vuln_dic

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
        
        # creating spinner object
        self.spinner = Spinner()
        
        # creating matchstring object
        self.matchstring = MatchString()
        
        # creating httpVulnRemediation object
        self.httpVulnRemediation = vuln_dic
        
        # creating exploit operations object
        self.exploit_operations = ExploitOperations()
        
        self.created_files = []
        
        self.ERASE_LINE = '\x1b[2K'
    #------------------------------------------------------------------------------------
    
    # Attack methods    
    def set_target(self, target, banner_condition=False, run_only_condition=False, run_exclude_condition=False, categories=None, profile_condition=False, profile=None):
        """
        Set the target for the attack and execute the relevant commands.

        :param target: Target URL or IP address
        """ 
        #get the time
        now = datetime.now()
        
        # format it this way ex: 2024-12-31 23:59:59
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        Output.print_sub_scoreboard("Attack Launched", str(formatted_date))
        print()
        
        if run_only_condition:
            x = Output.colored(f"[+] Checks in the following categories will be executed: ", color='10', attrs='bold')
            y = Output.colored(f"{categories}", color='226', attrs='bold')
            
            Output.print(f"{x} {y}")
            print()
            
            check_count = 0
            
            for tool in self.tools:
                tool_config = self.config[tool]
                current_category = tool_config.get('category', None)
                if current_category in categories:
                    check_count += 1
            final_check_count = str(check_count) + " of " + str(len(self.tools))
            
            Output.print_sub_scoreboard("Loaded check count", str(final_check_count))
            print()
        
        elif run_exclude_condition:
            x = Output.colored(f"[+] Checks in the following categories will be excluded: ", color='10', attrs='bold')
            y = Output.colored(f"{categories}", color='226', attrs='bold')
            
            Output.print(f"{x} {y}")
            print()
            
            check_count = 0
            
            for tool in self.tools:
                tool_config = self.config[tool]
                current_category = tool_config.get('category', None)
                if current_category not in categories:
                    check_count += 1
            final_check_count = str(check_count) + " of " + str(len(self.tools))
            
            Output.print_sub_scoreboard("Loaded check count", str(final_check_count))
            print()
            
        elif profile_condition:
            x = Output.colored(f"[+] Checks in the following profile will be executed: [", color='10', attrs='bold')
            y = Output.colored(f"{profile['profile_name']}", color='226', attrs='bold')
            z = Output.colored(f"]", color='10', attrs='bold')
            
            Output.print(f"{x} {y} {z}")
            print()
            
            profile_checks = profile.get('http', [])
                    
            final_check_count = str(len(profile_checks)) + " of " + str(len(self.tools))
            
            Output.print_sub_scoreboard("Loaded check count", str(final_check_count))
            print()
            
        elif banner_condition:
            logger.success("Banner grab will be executed")
            print()
            
        else:
            logger.success("All checks in each phase will be executed")
            print()
            
            check_count = 0
            for tool in self.tools:
                check_count += 1
            final_check_count = str(check_count) + " of " + str(len(self.tools))
            
            Output.print_sub_scoreboard("Loaded check count", str(final_check_count))
            print()
        
        protocol, base_target, specified_port, domain = '', '', None, ''
        is_ip_address = False
        ip_address = ''
        target_mode = 'N/A'
            
        # Parse the target to see if it's a URL with a scheme (http/https)
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
                    logger.error(f"Invalid port number: {port_str}. Must be in the range [0-65535]")
                    return
                
            # Check if base_target is an IP address
            try:
                socket.inet_aton(base_target)
                is_ip_address = True
                ip_address = base_target
                domain = self.netutils.reverse_dns_lookup(ip_address) or base_target
                # logger.success(f'Target IP : {ip_address}' + '\n')
            except socket.error:
                is_ip_address = False
                domain = base_target
                ip_address = self.netutils.dns_lookup(domain) or base_target
                # logger.success(f'Target Domain : {domain}' + '\n')
            
            # Log warnings or info if service is specified or not
            logger.info('URL given as target')
            logger.success(f'Target URL : {protocol}://{base_target}\n')
            target_mode = 'URL'

        else:
            # Target does not start with http:// or https://, check if it's an IP address or a plain hostname
            if ':' in target:
                base_target, port_str = target.split(':', 1)
                if self.netutils.is_valid_port(port_str):
                    specified_port = port_str
                else:
                    logger.error(f"Invalid port number: {port_str}. Must be in the range [0-65535]")
                    return
            else:
                base_target = target

            # Check if the base target is an IP address
            try:
                socket.inet_aton(base_target)
                is_ip_address = True
                ip_address = base_target 
                domain = self.netutils.reverse_dns_lookup(base_target) or base_target
                
                protocol = self.netutils.determine_protocol(base_target)
                
                logger.info('IP given as target') 
                logger.success(f'Target IP : {ip_address}' + '\n')
                target_mode = 'IP'
            except socket.error:
                is_ip_address = False
                domain = base_target.split("//")[-1].split("/")[0]
                ip_address = self.netutils.dns_lookup(domain) or base_target
                
                protocol = self.netutils.determine_protocol(base_target)
                
                logger.info('Hostname given as target')
                logger.success(f'Target Hostname : {base_target}' + '\n')
                target_mode = 'Hostname'

        # Fetch the default port if not specified
        default_port = self.netutils.get_port_from_url(protocol + "://" + base_target)
        port = str(specified_port if specified_port else default_port)
        
        # Variables to store the reachability status of the target
        rechability = False

        # Check if the target is reachable 
        if not is_ip_address:
            # For URLs or domains
            logger.info(f"Checking the reachable status of {domain} on port {port}...")
            
            default_port = 443 if protocol == 'https' else 80
            port = int(specified_port) if specified_port else default_port
            if not self.netutils.is_host_reachable(domain, port):
                logger.error(f"Host {domain} is not reachable\n")
                pass
                # return
            else:
                logger.success(f"Host {domain} is reachable\n")
                rechability = True
        else:
            # For IP addresses
            logger.info(f"Checking the reachable status of {ip_address} on port {port}...")
            
            if not self.netutils.is_host_reachable(ip_address, 80):
                logger.error(f"IP address {ip_address} is not reachable\n")
                pass
                # return
            else:
                logger.success(f"IP address {ip_address} is reachable\n")
                rechability = True
        
        # Check if banner grab is specified
        if banner_condition:
            self.banner_grab(target, port, domain, ip_address, protocol, specified_port, rechability, target_mode)
        else:
            self.banner_grab(target, port, domain, ip_address, protocol, specified_port, rechability, target_mode)
            
            # Prompt the user to continue if the target is reachable or not 
            if rechability:
                rechability_input = input(f"\033[1m[>] The target is reachable. Do you want to continue? (Y/n) :\033[0m ")
                if rechability_input.lower() == 'y':
                    pass
                else:
                    return
            else:
                rechability_input = input(f"\033[1m[>] The target is not reachable. Do you want to continue? (Y/n) :\033[0m ")
                if rechability_input.lower() == 'y':
                    pass
                else:
                    return
            
            self.run_default(protocol, base_target, domain, is_ip_address, ip_address, str(port), run_only_condition, run_exclude_condition, categories=categories, profile_condition=profile_condition, profile=profile)
        
    #------------------------------------------------------------------------------------  
    
    # Banner grab the target
    def banner_grab(self, target, port, domain, ip_address, protocol, specified_port, rechability, target_mode):
        """
        Perform a banner grab on the specified target and port.

        :param str target: Target IP address or hostname
        :param str port: Port number
        """
        self.output.print_title("Banner Grab Information")
        self.output.print_banner_grabbing("banner-grabbing", f"mode: {target_mode}", f"{target}")
        
        try:
            rechable_status = self.output.colored("◉ unknown", "yellow") or '◉ unknown'
            
            if rechability:
                rechable_status = self.output.colored("◉ reachable", "green")
            else:
                rechable_status = self.output.colored("◉ not reachable", "red")
            
            logger.info(f"Target------------| {target}")
            logger.info(f"Port--------------| {port}")
            logger.info(f"Specified Port----| {specified_port}")
            logger.info(f"Host--------------| {domain}")
            logger.info(f"IP Address--------| {ip_address}")
            logger.info(f"Protocol----------| {protocol}")
            logger.info(f"Reachable Status--| {rechable_status}")
            print('')
        except socket.error as e:
            logger.error(f"Error performing banner grab: {e}\n")
       
    #------------------------------------------------------------------------------------
    
    # Run the attack tools in default mode
    def run_default(self, protocol, base_target, domain, is_ip_address, ip_address, port, run_only_condition=False, run_exclude_condition=False,categories=None, profile_condition=False, profile=None):
        """
        Run the attack tools in default mode.
        """
        # Convert the comma-separated categories string into a set for efficient lookup
        included_categories = categories
        
        # Retrieve profile-specific tools if profile_condition is True
        profile_tools = []
        if profile_condition and profile:
            if profile:
                profile_tools = profile.get('http', [])
            else:
                logger.error(f'Profile "{profile}" not found or has no tools specified.')
                return
        
        # To track the last printed category
        last_category = None

        # List of section names to exclude
        excluded_sections = ["config", "specific_options", "products"]

        for tool in self.tools:
            if tool.lower() in excluded_sections:
                continue
            
            tool_config = self.config[tool]
            current_category = tool_config.get('category', None)
            
            if run_only_condition:
                # Skip this tool if its category is not in the included categories
                if current_category not in included_categories:
                    continue
            elif run_exclude_condition:
                # Skip the tools that are in the included categories
                if current_category in included_categories:
                    continue
            elif profile_condition:
                adjusted_tool_name = tool.replace('check_', '')
                
                if adjusted_tool_name not in profile_tools:
                    continue

            # Print the category title if it's different from the last one
            if current_category and current_category != last_category:
                self.output.print_title(current_category)
                last_category = current_category
                
                if current_category == "vuln":
                    criticality_dashboard = {1: {"crit": "info",
                                                 "des": "Not classified as a vulnerability, just useful information."}, 
                                             2: {"crit": "low",
                                                 "des": "Not critical, but recommended to address this issue."},
                                             3: {"crit": "medium",
                                                "des": "Potential for sophisticated attacks if correlated with other vulnerabilities."},
                                             4: {"crit": "high",
                                                "des": "Significant probability of compromise if not addressed."},
                                             5: {"crit": "critical",
                                                "des": "Requires immediate attention to prevent compromise or service unavailability."}
                                            }
                    columns = ['Criticality', 'Description']
                    data = []
                    
                    logger.info(f"Criticality Dashboard:")
                    Output.print("=================================================================================================\n", color=247)    
                      
                    for i in range(1, 6):
                        crit_category = criticality_dashboard.get(i)
                        tmp_criticality = self.matchstring.criticality_color(crit_category['crit'])
                        tmp_description = self.output.colored(crit_category['des'])
                        print(f"{tmp_criticality} {tmp_description}\n")
                        # data.append([tmp_criticality, tmp_description])
                    # Output.table(columns, data)  
                    
                    Output.print("=================================================================================================", color=247)      
                    print("\n")
                
            tool_config = self.config[tool]
            command_template = tool_config.get('command_1', None)
            tool_description = tool_config.get('description', None)
            check_name = tool_config.get('name', None)
            criticality = tool_config.get('criticality', None)
            response = tool_config.get('response', None)
            vuln_pattern = tool_config.get('vuln_pattern', None)
            response_code = tool_config.get('response_code', None)
            remed_ref = tool_config.get('remed_ref', None)
            
            if command_template:
                command = command_template
                if "[URL]" in command:
                    command = command.replace("[URL]", f"{protocol}://{domain if not is_ip_address else base_target}:{port}")
                if "[IP]" in command:
                    command = command.replace("[IP]", ip_address if not is_ip_address else base_target)
                if "[DOMAIN]" in command:
                    extracted_domain = self.netutils.extract_secondary_domain(domain)
                    command = command.replace("[DOMAIN]", extracted_domain)
                if "[HOST]" in command:
                    command = command.replace("[HOST]", domain)
                command = command.replace("[PORT]", port)
                
                # Check if the tool's execution directory exists
                tool_name = tool_config.get('tool', '').lower()
                tool_dir_path = HTTP_TOOLBOX_DIR + "/" + tool_name
                display_check_name = tool_config.get('name', None)
                display_check_tool_name = tool_config.get('tool', None)
                
                if os.path.isdir(tool_dir_path):
                    # Change to the tool's directory and execute the command
                    os.chdir(tool_dir_path)
                else:
                    self.output.print_subtitle(display_check_name, display_check_tool_name, tool_description)
                    logger.error(f"{tool_name} is not installed. Install it using the 'install-tool' option.")
                    logger.info(f"Skipping...\n")
                    continue

                if "[TOOLDIR]" in command:
                    command = command.replace("[TOOLDIR]", tool_dir_path)
                    
                if "[WORDLISTSDIR]" in command:
                    command = command.replace("[WORDLISTSDIR]", WORDLISTS_DIR)
                    
                if "[WEBSHELLSDIR]" in command:
                    command = command.replace("[WEBSHELLSDIR]", WEBSHELLS_DIR)
                    
                if "[LOCALIP]" in command:
                    local_ip = self.netutils.get_local_ip_address()
                    command = command.replace("[LOCALIP]", local_ip)
                    
                if "[RESULTS_DIR]" in command:
                    command = command.replace("[RESULTS_DIR]", RESULTS_DIR)

                # display_check_name = tool_config.get('name', None)
                # display_check_tool_name = tool_config.get('tool', None)
                
                # Define the results file path for this tool
                results_file_path = os.path.join(RESULTS_DIR, f"{tool}_results.txt")
                self.created_files.append(results_file_path)
                
                try:
                    self.output.print_subtitle(display_check_name, display_check_tool_name, tool_description)
                    
                    # self.spinner.start()
                    # scan_start = time.time()
                    
                    # result = subprocess.run(command, shell=True, cwd=tool_dir_path, text=True, capture_output=True)
                    if current_category == "exploit":
                        try:
                            command = self.exploit_operations.please_exploit_tool(command, tool_name, check_name)
                        except Exception as e:
                            # print("\n")
                            logger.error(f"Error: {e}")
                            pass
                        # print("\n")
                    
                    if current_category == "exploit":
                        pass
                    else:
                        self.spinner.start()
                    
                    # self.spinner.start()
                    scan_start = time.time()
                            
                    # subprocess.run(command, shell=True, cwd=tool_dir_path)
                    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=tool_dir_path)
                    stdout, stderr = proc.communicate()
                    
                    if tool_name == 'wget' or tool_name == 'wapiti':
                        pass
                    else:
                        # store stdout and stderr
                        with open(results_file_path, "w") as file:
                            decoded_output = stdout.decode("utf-8")
                            cleaned_output = self.matchstring.strip_ansi_codes(decoded_output)
                            file.write(cleaned_output)
                            # file.write(stderr)
                            
                    # with open(results_file_path, "r") as file:
                    #     response = file.read()
                    #     print(response)
                                      
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error executing {tool}: {e}\n")
                    
                except KeyboardInterrupt:
                    self.spinner.stop()
                    sys.stdout.write(self.ERASE_LINE + '\r')
                    sys.stdout.flush()
                    
                    logger.warning(f"Execution of {tool} was skipped by user.")
                    continue
                
                finally:
                    # Change back to the original directory after execution
                    if os.path.isdir(tool_dir_path):
                        os.chdir(TOOL_BASEPATH)
                        
                    self.spinner.stop()
                    
                    scan_stop = time.time()
                    sys.stdout.write(self.ERASE_LINE + '\r')
                    sys.stdout.flush()
                    
                    # Process the tool output
                    try:
                        if current_category == "vuln":              
                            self.matchstring.process_vuln(tool_name, check_name, results_file_path, vuln_pattern, response, criticality, remed_ref, response_code)
                        # elif current_category == "exploit":
                        #     self.matchstring.process_tool_output(tool_name, check_name, results_file_path)
                        elif current_category == "postexploit":
                            pass
                        else:
                            self.matchstring.process_tool_output(tool_name, check_name, results_file_path)
                            
                    except Exception as e:
                        pass
                    
                    if scan_stop - scan_start > 60:
                        logger.info(f"Scan completed in {round((scan_stop - scan_start) / 60, 2)} minutes\n")
                    else:
                        logger.info(f"Scan completed in {scan_stop - scan_start:.2f} seconds\n")
                    
                    # self.clear_results_directory()
                     
            else:
                logger.error(f"No command template found for {tool}.\n")
                
        logger.success("All applicable tools have been executed for the target.\n")
        # self.clear_results_directory()
    
    #------------------------------------------------------------------------------------
    
    def clear_results_directory(self):
        """
        Clears all files from the results directory.
        """
        for filename in os.listdir(RESULTS_DIR):
            file_path = os.path.join(RESULTS_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f'Failed to delete {file_path}. Reason: {e}')
