import re
from lib.filtermodules.products.httpWebApplicationFirewallProducts import httpWebApplicationFirewallProducts
from lib.filtermodules.products.httpWebApplicationFirewallProducts import WAFDetectionResults
from lib.output.Logger import logger  
from lib.output import Output

class MatchString:
    def __init__(self):
        # Initialize the WAF detection class
        self.waf_detector = httpWebApplicationFirewallProducts()
        
        # Initialize the WAF detection results class
        self.waf_results = WAFDetectionResults()
        
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
            print("\n")
            
        elif tool_name in ["wafw00f", "identywaf"]:
            if tool_name == "wafw00f":
                detected_wafs = self.waf_detector.parse_wafw00f_output(output)
                
                for entry in detected_wafs:
                    self.waf_results.add_or_update(entry['vendor'], entry['waf'])
            
            elif tool_name == "identywaf":
                waf_data, blocked_categories = self.waf_detector.parse_identywaf_output(output)
                
                for entry in waf_data:
                    self.waf_results.add_or_update(entry['vendor'], entry['waf'], blocked_categories)

            if self.waf_results.results:
                logger.success("WAF(s) Detected:")
                columns = ['Vendor', 'WAF', 'Blocked Categories']
                data = []
                for entry in self.waf_results.results:
                    wafs = ", ".join(entry['waf'])
                    data.append([entry['vendor'], wafs, entry['blocked_categories']])
                Output.table(columns, data)
                print("\n")
            else:
                logger.info("No WAFs detected.\n")
                
        # elif tool_name == "wafw00f":
        #     detected_wafs = self.waf_detector.parse_wafw00f_output(output)
            
        #     if detected_wafs:
        #         # Prepare the header and data for the table
        #         columns = ['Vendor', 'WAF']
        #         data = [[entry['vendor'], entry['waf']] for entry in detected_wafs]

        #         # Assuming Output.table is capable of handling this structure
        #         logger.success("Detected WAF(s):")
        #         Output.table(columns, data)
        #     else:
        #         logger.info("No WAFs detected.")
            
        # elif tool_name == "identywaf":
        #     pass

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
    
    
    