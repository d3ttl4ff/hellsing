import re

class httpWebApplicationFingerprint:
    def __init__(self):
        self.results = []

    #------------------------------------------------------------------------------------

    # filter whatweb output
    def parse_whatweb_output(self, output):
        self.results.clear()

        # Pattern to capture the beginning of each WhatWeb report section
        report_pattern = re.compile(r'WhatWeb report for (.+)')
        # Plugins to exclude from the results
        excluded_plugins = {
            "Content-Language", "Cookies", "X-Powered-By", "Google-Analytics",
            "Index-Of", "Open-Graph-Protocol", "UncommonHeaders",
            "X-Frame-Options", "X-UA-Compatible", "probably Index-Of"
        }

        # Split the output into lines for processing
        lines = output.split('\n')
        current_location = ""
        for line in lines:
            report_match = report_pattern.search(line)
            if report_match:
                # Found a new report section, prepare to store its details
                current_location = report_match.group(1)
                self.results.append({"Location": current_location, "Plugins": {}})
                continue

            summary_match = re.search(r'Summary\s+:\s+(.+)', line)
            if summary_match and current_location:
                plugins_summary = summary_match.group(1)
                plugins = plugins_summary.split(', ')
                for plugin in plugins:
                    name, version = self._extract_name_version(plugin)
                    if name and name not in excluded_plugins:
                        # Store plugin and version under the current location's details
                        self.results[-1]["Plugins"][name] = version

    def _extract_name_version(self, plugin):
        # Special handling for "HTML" and similar cases
        if plugin.startswith("HTML"):
            return "HTML", plugin[4:]

        # Special handling for email addresses to extract just the email part
        if "Email" in plugin:
            email_match = re.search(r'Email\[(.+)\]', plugin)
            if email_match:
                emails = email_match.group(1)
                # Split by commas in case there are multiple emails, then validate
                valid_emails = [email for email in emails.split(',') if self.is_valid_email(email)]
                if valid_emails:
                    # Join valid emails back with a comma and space
                    return "Email", ", ".join(valid_emails)
                else:
                    # If no valid emails found, skip this plugin
                    return None, None

        # Handling for other plugins with name and version
        name_version_match = re.match(r'([^[]+)\[([^]]*)\]', plugin)
        if name_version_match:
            name, version = name_version_match.groups()
            return name.strip(), version.strip()

        # For plugins without a version specified
        return plugin.strip(), "N/A"

    def is_valid_email(self, email):  
        # Basic check to exclude strings that likely aren't emails
        if "@" in email and not email.endswith((".png", ".jpg", ".jpeg")) and not "-@" in email:
            return email is not None
        return False
    
    #------------------------------------------------------------------------------------
    
    # filter cmsseek output
    def parse_cmseek_output(self, output):
        """
        Parses the CMSeeK results from a given text file and extracts CMS name and URL.
        Returns a dictionary with extracted data.
        """
        data = {"Product": "N/A", "Type": "CMS", "Version": "N/A", "Info": "N/A"}
    
        cms_name_match = re.search(r'CMS: (.+)', output)
        cms_url_match = re.search(r'URL: (.+)', output)
        

        if cms_name_match:
            data["Product"] = cms_name_match.group(1).strip()
        if cms_url_match:
            data["Info"] = f"{cms_url_match.group(1).strip()}"

        return data
    
    #------------------------------------------------------------------------------------
    
    # filter drupwn output
    def parse_drupwn_output(output):
        """
        Parses the output of the drupwn tool to extract CMS version information.
        """
        pattern = r'Version detected: ([\d.]+)'
        match = re.search(pattern, output)
        if match:
            return {
                "Product": "Drupal",
                "Type": "CMS",
                "Version": match.group(1),
                "Info": ""
            }
        else:
            return None
        
    #------------------------------------------------------------------------------------
    
    # filter theharvester output
    def parse_harvester_output(self, output):
        """
        Parses The Harvester output to extract hosts, IP addresses, and emails.
        """
        # Initialize the lists to store hosts, IPs, and emails
        hosts = []
        ips = []
        emails = []
        
        # Split the output into lines for processing
        lines = output.split('\n')
        
        # Flags to track which section we are currently parsing
        parsing_hosts = False
        parsing_ips = False
        parsing_emails = False  # New flag for emails
        
        for line in lines:
            # Check for the start of the hosts section
            if line.strip() == "[*] Hosts found:":
                parsing_hosts = True
                parsing_ips = False
                parsing_emails = False
                continue
            # Check for the start of the IPs section
            elif line.strip() == "[*] IPs found:":
                parsing_hosts = False
                parsing_ips = True
                parsing_emails = False
                continue
            # New: Check for the start of the emails section
            elif line.strip() == "[*] Emails found:":
                parsing_hosts = False
                parsing_ips = False
                parsing_emails = True
                continue
            
            # Extract the information based on the current section
            if parsing_hosts and line.strip() and not line.startswith("[*]"):
                host = line.split()[0].strip()
                if host not in hosts:
                    hosts.append(host)
            elif parsing_ips and line.strip() and not line.startswith("[*]"):
                ip = line.split()[0].strip()
                if ip not in ips:
                    ips.append(ip)
            elif parsing_emails and line.strip() and not line.startswith("[*]"):  # Extract emails
                email = line.strip()
                if email not in emails:
                    emails.append(email)
                    
        # Return the extracted data, including emails
        return {"Hosts": hosts, "IPs": ips, "Emails": emails}
