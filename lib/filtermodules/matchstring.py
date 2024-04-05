import re

from lib.filtermodules.products.httpWebApplicationFirewallProducts import httpWebApplicationFirewallProducts
from lib.filtermodules.products.httpWebApplicationFirewallProducts import WAFDetectionResults
from lib.filtermodules.products.httpWebApplicationFingerprint import httpWebApplicationFingerprint 
from lib.filtermodules.vuln.httpVulnRemediation import vuln_dic
from lib.output.Logger import logger  
from lib.output import Output
from lib.utils.StringUtils import StringUtils

class MatchString:
    def __init__(self):
        # Initialize the WAF detection class
        self.waf_detector = httpWebApplicationFirewallProducts()
        
        # Initialize the WAF detection results class
        self.waf_results = WAFDetectionResults()
        
        # Initialize the fingerprinting class
        self.fingerprinter = httpWebApplicationFingerprint()
        
        self.waf_detected = False
        
    #------------------------------------------------------------------------------------
    
    def strip_ansi_codes(self, text):
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', text)

    #------------------------------------------------------------------------------------
    def process_tool_output(self, tool_name, output_file_path):
        with open(output_file_path, "r") as file:
            output = file.read()

        if tool_name == "nmap":
            filtered_results = self.nmap_simple_recon_output(output)
                
            columns = ['Port', 'Service', 'Version', 'State']
            data = []
            for result in filtered_results:
                row = [result['PORT'], result['SERVICE'], result['VERSION'], result['STATE']]
                data.append(row)
                
            if data!=[]:
                logger.success("Found the following ports:")
                Output.table(columns, data)
            else:
                logger.info("No ports found.")
                
        #------------------------------------------------------------------------------------
        elif tool_name in ["wafw00f", "identywaf"]:
            initial_detection = False
            
            if tool_name == "wafw00f":
                detected_wafs = self.waf_detector.parse_wafw00f_output(output)
                
                if detected_wafs and not self.waf_detected:
                    initial_detection = True
                    self.waf_detected = True
                
                for entry in detected_wafs:
                    self.waf_results.add_or_update(entry['vendor'], entry['waf'])
                    
            elif tool_name == "identywaf":
                waf_data, blocked_categories = self.waf_detector.parse_identywaf_output(output)
                
                if waf_data and not self.waf_detected:
                    initial_detection = True
                    self.waf_detected = True
                
                for entry in waf_data:
                    self.waf_results.add_or_update(entry['vendor'], entry['waf'], blocked_categories)

            if self.waf_results.results:
                if initial_detection:
                    logger.success("WAF(s) Detected:")
                else:
                    logger.success("WAF(s) Detected:")
                    logger.success("WAF table updated.")

                columns = ['Vendor', 'WAF', 'Blocked Categories']
                data = [] 
                for entry in self.waf_results.results:
                    wafs = ", ".join(entry['waf'])
                    data.append([entry['vendor'], wafs, entry['blocked_categories']])
                Output.table(columns, data)
            else:
                logger.info("No WAFs detected.")
                
        #------------------------------------------------------------------------------------
        elif tool_name == "whatweb":
            self.fingerprinter.parse_whatweb_output(output)

            # Initialize a dictionary to hold consolidated plugin information
            consolidated_plugins = {}

            for result in self.fingerprinter.results:
                for plugin, version in result["Plugins"].items():
                    # Create a unique key for each plugin-version pair
                    plugin_version_key = f"{plugin}:{version}"

                    if plugin_version_key not in consolidated_plugins:
                        consolidated_plugins[plugin_version_key] = {
                            "Plugin": plugin,
                            "Version": version,
                            "Locations": [result["Location"]]
                        }
                    else:
                        # If this plugin-version pair is already listed, append the location
                        consolidated_plugins[plugin_version_key]["Locations"].append(result["Location"])

            # Prepare columns and data for the consolidated table
            columns = ['Plugin', 'Version']
            data = []

            for details in consolidated_plugins.values():
                # Join all locations into a single string for display
                locations_str = ", ".join(details["Locations"])
                data.append([details["Plugin"], details["Version"]])

            # Display the consolidated table
            if data:
                logger.success("Plugins Found:")
                Output.table(columns, data)
            else:
                print("No significant plugin data detected.")
        
        #------------------------------------------------------------------------------------
        elif tool_name in ["cmseek"]:
            self.display_cms_detection_results(tool_name, output)
        
        #------------------------------------------------------------------------------------
        elif tool_name == "theharvester":
            harvester_data = self.fingerprinter.parse_harvester_output(output)
            
            if harvester_data and not harvester_data['Hosts'] == [] and not harvester_data['IPs'] == [] and not harvester_data['Emails'] == []:
                logger.success("Information Gathered:")
                columns = ['Hosts', 'IPs', 'Emails']
                data = [
                    ["The Harvester", "Host Discovery", "N/A", "\n".join(harvester_data['Hosts'])],
                    ["The Harvester", "IP Discovery", "N/A", "\n".join(harvester_data['IPs'])],
                    ["The Harvester", "Email Discovery", "N/A", "\n".join(harvester_data['Emails'])]  # Include emails
                ]
                Output.table(columns, data)
            else:   
                logger.info("No Hosts, IPs, or Emails detected by The Harvester.")

        #------------------------------------------------------------------------------------
        elif tool_name == "sublist3r":
            domain, sublist3r_subdomains = self.fingerprinter.parse_sublist3r_output(output)
            
            if sublist3r_subdomains:
                logger.success(f"Subdomain Discovery Detected for: {domain}")
                columns = ['Domain', 'Subdomains']
                data = [[domain, "\n".join(sublist3r_subdomains)]]
                Output.table(columns, data)
            else:
                print(f"No subdomains detected for {domain}.")   
        # print("\n")

    #------------------------------------------------------------------------------------
    
    # filter nmap simple recon output
    def nmap_simple_recon_output(self, nmap_output):
        # Regular expression to match the lines containing port, state, service, and version information
        # port_info_regex = re.compile(r'^(\d+)/tcp\s+(\w+)\s+(\w+)\s+(.*)$')
        port_info_regex = re.compile(r'^(\d+)/tcp\s+(\w+)\s+([^\s]+)\s+(.*)$')

        parsed_results = []

        # Split the output into lines for processing
        for line in nmap_output.splitlines():
            # Search for lines that match the regular expression
            match = port_info_regex.search(line)
            if match:
                # Extract the information from the matching line
                port, state, service, version = match.groups()
                parsed_results.append({
                    'PORT': port,
                    'STATE': state,
                    'SERVICE': service,
                    'VERSION': version.strip()  # Remove leading/trailing whitespace from the version
                })

        return parsed_results

    #------------------------------------------------------------------------------------
    
    def display_cms_detection_results(self, tool_name, output):
        parser_functions = {
            "cmseek": self.fingerprinter.parse_cmseek_output,
        }
        
        # Get the relevant parser function based on the tool_name
        parser_function = parser_functions.get(tool_name)
        
        if not parser_function:
            print(f"No parser available for tool: {tool_name}")
            return
        
        # Parse the output using the selected parser function
        parsed_data = parser_function(output)
        
        if parsed_data and not parsed_data.get("Product") == "<name and/or cms url>":
            logger.success(f"{tool_name.capitalize()} CMS Detected:")
            columns = ['Product', 'Type', 'Version', 'Info']
            data = [[parsed_data['Product'], parsed_data['Type'], parsed_data['Version'], parsed_data['Info']]]
            Output.table(columns, data)
        else:
            logger.info(f"No CMS version detected by {tool_name}.")

    #------------------------------------------------------------------------------------
    
    # vulnerability filter
    def process_vuln(self, tool_name, check_name, output_file_path, vuln_pattern, response, criticality, remed_ref, response_code):
        with open(output_file_path, "r") as file:
            output = file.read()
        # print(output)

        try:
            vulnerability_found = self.check_vulnerability(check_name, output, response_code)
            # vulnerability_found = False
            
            # #------------------------------------------------------------------------------------
            # if check_name == "host-ipv6":
            #     pattern = re.compile(r"has IPv6 address ([\w:]+)")
                
            #     for line in output.splitlines():
            #         if pattern.search(line):
            #             vulnerability_found = False
            #             break
            #         else:
            #             vulnerability_found = True

            # #------------------------------------------------------------------------------------
            # elif check_name == "aspnet-config-error" or check_name == "wordpress-check" or check_name == "drupal-check" or check_name == "joomla-check":
            #     pattern = re.compile(r"HTTP request sent, awaiting response... 200 OK")
                
            #     for line in output.splitlines():
            #         if pattern.search(line):
            #             vulnerability_found = True
                        
            # #------------------------------------------------------------------------------------
            # elif check_name == "uniscan-robots-&-sitemap":
            #     pattern = re.compile(r"[+]")
                
            #     for line in output.splitlines():
            #         if pattern.search(line):
            #             vulnerability_found = True
            
            # #------------------------------------------------------------------------------------
            # elif check_name == "dnsrecon-multiple-zone-transfers":
            #     pattern = re.compile(r"Zone Transfer was successful!!")
                
            #     for line in output.splitlines():
            #         if pattern.search(line):
            #             vulnerability_found = True
                
            # #------------------------------------------------------------------------------------
            # elif check_name == "whois-admin-contact":
            #     pattern = re.compile(r"Admin Email: ([\w.-]+@[\w.-]+)")
                
            #     for line in output.splitlines():
            #         if pattern.search(line):
            #             vulnerability_found = True
            
            #------------------------------------------------------------------------------------       
                
        except Exception as e:
            logger.error(f"Error: {e}")
            
        finally:
            if vulnerability_found:
                vuln_info = vuln_dic.get(int(remed_ref))
                
                if vuln_info:
                    response = response.replace('"', '').replace("'", "")
                    criticality = criticality.replace('"', '').replace("'", "")
                    
                    description_text = StringUtils.wrap(vuln_info['description'], 100)
                    remediation_text = StringUtils.wrap(vuln_info['remediation'], 100)

                    colname_vulnerability_info = Output.colored("[~] Vulnerbility Information ", attrs="bold")
                    columns = [colname_vulnerability_info]
                    
                    # variables for vulnerability information
                    rowname_vulnerability_name = Output.colored("[~] Vulnerability Name ", attrs="bold")    
                    rowname_criticality = Output.colored("[*] Criticality ", attrs="bold")
                    rowname_description = Output.colored("[-] Description ", attrs="bold")
                    rowname_remediation = Output.colored("[+] Remediation ", attrs="bold")
                    
                    response = Output.colored(response, color=135)
                    
                    if criticality == "informational":
                        criticality_color = 16
                        criticality_highlight = 76
                    elif criticality == "low":
                        criticality_color = 16
                        criticality_highlight = 45
                    elif criticality == "medium":
                        criticality_color = 16
                        criticality_highlight = 184
                    elif criticality == "high":
                        criticality_color = 15
                        criticality_highlight = 160
                    elif criticality == "critical":
                        criticality_color = 15
                        criticality_highlight = 197
                        
                    temp_criticality = Output.colored(f" {criticality} ", color=criticality_color, highlight=criticality_highlight)
                    criticality_left_connector = Output.colored("▒", color=criticality_highlight)
                    criticality_right_connector = Output.colored("▒ ●", color=criticality_highlight)
                        
                    final_criticality = temp_criticality + criticality_right_connector
                    description_text = Output.colored(description_text, color=197)
                    remediation_text = Output.colored(remediation_text, color=190)
                    
                    data = [
                        [response],
                        [rowname_criticality], [final_criticality],
                        [rowname_description], [description_text],
                        [rowname_remediation], [remediation_text],
                    ]
                    logger.success("Vulnerability Detected:")
                    Output.table(columns, data)
                    
            else:
                logger.success("No vulnerabilities detected for this check.")
            print("")
    
    #------------------------------------------------------------------------------------
    def check_vulnerability(self, check_name, output, response_code):
        print(output)
        # Mapping of check names to their regex patterns
        check_patterns = {
            "host-ipv6": r"has IPv6 address ([\w:]+)",
            "aspnet-config-error": r"HTTP request sent, awaiting response... 200 OK",
            "wordpress-check": r"HTTP request sent, awaiting response... 200 OK",
            "drupal-check": r"HTTP request sent, awaiting response... 200 OK",
            "joomla-check": r"HTTP request sent, awaiting response... 200 OK",
            "uniscan-robots-&-sitemap": r"[+]",
            "dnsrecon-multiple-zone-transfers": r"Zone Transfer was successful!!",
            "whois-admin-contact": r"Admin Email: ([\w.-]+@[\w.-]+)",
            "xss-protection-header": r"XSS filter is disabled.",
            "slowloris-denial-of-service": r"Vulnerable:",
            "sslyze-heartbleed-vulnerability": r"Server is vulnerable to Heartbleed",
            "nmap-heartbleed-vulnerability": r"VULNERABLE",
            "nmap-poodle-vulnerability": r"VULNERABLE",
            "nmap-ccs-injection-vulnerability": r"VULNERABLE",
            "nmap-freak-vulnerability": r"vulnerable",
            "nmap-logjam-vulnerability": r"VULNERABLE",
            "sslyze-ocsp-stapling": r"NOT SUPPORTED - Server did not send back an OCSP response",
            "sslyze-zlib-deflate-compression": r"VULNERABLE",
            "sslyze-secure-renegotiation": r"VULNERABLE",
            "sslyze-session-resumption": r"VULNERABLE",
            "lbd-dns-http-load-balancers": r"does NOT use Load-balancing",
            "golismero-dns-malware-scan": r"No vulnerabilities found",
            "golismero-heartbleed-scan": r"No vulnerabilities found",
            "golismero-brute-url-predictables-scan": r"No vulnerabilities found",
            "golismero-brute-directories-scan": r"No vulnerabilities found",
            "golismero-sqlmap-scan": r"No vulnerabilities found",
            "dirb-brute-open-directories": r"FOUND: 0",
            "xsser-cross-site-scripting": r"Total XSS Discovered: 0",
            "golismero-ssl-scan": r"Occurrence ID",
            "golismero-zone-transfer": r"DNS Zone Transfer Enabled",
            "golismero-nikto-scan": r"Nikto found 0 vulnerabilities",
            "golismero-brute-subdomains": r"Possible subdomain leak",
            "dnsenum-zone-transfer": r"AXFR record query failed:",
            "dmitry-email-harvesting": r"Found 0 E-Mail(s)",
            "nmap-telnet-service": r"open",
            "nmap-ftp-service": r"open",
            "nmap-stuxnet-worm": r"open",
            "webdav-enabled": r"SUCCEED",
            "golismero-fingerprint-web": r"No vulnerabilities found",
            "uniscan-filebrute": r"[+]",
            "uniscan-dirbrute": r"[+]",
            "uniscan-ministresser": r"[+]",
            "uniscan-rfi": r"[+]",
            "uniscan-xss": r"[+]",
            "nikto-xss-header": r"0 item(s) reported",
            # "nikto-shellshock-bug": r"",
            # "nikto-internal-ip-leak": r"",
            # "nikto-put-del": r"",
            # "nikto-headers": r"",
            # "nikto-ms10-070": r"",
            # "nikto-server-msgs": r"",
            # "nikto-outdated": r"",
            # "nikto-http-options": r"",
            # "nikto-cgi": r"",
            # "nikto-ssl": r"",
            # "nikto-sitefiles": r"",
            # "nikto-paths": r"",
            # "nmap-sqlserver-db": r"",
            # "nmap-mysql-db": r"",
            # "nmap-oracle-db": r"",
            # "nmap-rdp-udp": r"",
            # "nmap-rdp-tcp": r"",
            # "nmap-snmp-service": r"",
            # "aspnet-elmah-logger": r"",
            # "nmap-tcp-smb": r"",
            # "nmap-udp-smb": r"",
            # "wapiti-sqli-rce-xss": r"",
            # "nmap-iis-webdav-vuln": r"",
            # "whatweb-x-xss-protection": r"",
            # "dmitry-subdomain-scan": r""
        }

        # Default to False, will be set to True if a pattern match is found
        vulnerability_found = False
        
        # Get the appropriate pattern for the current check
        pattern = re.compile(check_patterns.get(check_name, ""))
        
        if check_name in check_patterns:
            for line in output.splitlines():
                match = pattern.search(line)
                if response_code == "1":
                    if match:
                        vulnerability_found = False
                        break
                    else:
                        vulnerability_found = True
                else:
                    if match:
                        vulnerability_found = True
                        break

        return vulnerability_found