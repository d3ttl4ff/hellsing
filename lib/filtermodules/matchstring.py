import re

class MatchString:
    def process_tool_output(self, check_name, output_file_path):
        with open(output_file_path, "r") as file:
            output = file.read()

        if check_name == "nmap-simple-recon":
            filtered_results = self.nmap_simple_recon_output(output)
            
            for result in filtered_results:
                print(result['SERVICE'])
                print(result['VERSION'])
                print(result['STATE'])
                print(result['PORT'])
                
        # elif tool_name == "another_tool":
        #     pass

     #------------------------------------------------------------------------------------
    
    def nmap_simple_recon_output(self, nmap_output):
        # Regular expression to match the lines containing port, state, service, and version information
        port_info_regex = re.compile(r'^(\d+)/tcp\s+(\w+)\s+(\w+)\s+(.*)$')

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
