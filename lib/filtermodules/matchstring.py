import re
from lib.filtermodules.products.httpWebApplicationFirewallProducts import httpWebApplicationFirewallProducts
from lib.filtermodules.products.httpWebApplicationFirewallProducts import WAFDetectionResults
from lib.filtermodules.products.httpWebApplicationFingerprint import httpWebApplicationFingerprint 
from lib.output.Logger import logger  
from lib.output import Output

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
                
        elif tool_name in ["cmseek", "drupwn"]:
            self.display_cms_detection_results(tool_name, output)
            
        elif tool_name == "harvester":
            harvester_data = self.fingerprinter.parse_harvester_output(output)
            
            if harvester_data:
                logger.success("Information Gathered:")
                columns = ['Hosts', 'IPs', 'Emails']
                data = [
                    ["The Harvester", "Host Discovery", "N/A", "\n".join(harvester_data['Hosts'])],
                    ["The Harvester", "IP Discovery", "N/A", "\n".join(harvester_data['IPs'])],
                    ["The Harvester", "Email Discovery", "N/A", "\n".join(harvester_data['Emails'])]  # Include emails
                ]
                Output.table(columns, data)

        elif tool_name == "sublist3r":
            domain, sublist3r_subdomains = self.fingerprinter.parse_sublist3r_output(output)
            
            if sublist3r_subdomains:
                logger.success(f"Subdomain Discovery Detected for: {domain}")
                columns = ['Domain', 'Subdomains']
                data = [[domain, "\n".join(sublist3r_subdomains)]]
                Output.table(columns, data)
            else:
                print(f"No subdomains detected for {domain}.")
                
        
                
        print("\n")




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
            "drupwn": self.fingerprinter.parse_drupwn_output,
            # Add more tools and their parsers as needed
        }
        
        # Get the relevant parser function based on the tool_name
        parser_function = parser_functions.get(tool_name)
        
        if not parser_function:
            print(f"No parser available for tool: {tool_name}")
            return
        
        # Parse the output using the selected parser function
        parsed_data = parser_function(output)
        
        if parsed_data:
            print(f"{tool_name.capitalize()} CMS Detected:")
            columns = ['Product', 'Type', 'Version', 'Info']
            data = [[parsed_data['Product'], parsed_data['Type'], parsed_data['Version'], parsed_data['Info']]]
            Output.table(columns, data)
        else:
            print(f"No CMS version detected by {tool_name}.")

    
    