import re

class httpWebApplicationFingerprint:
    def __init__(self):
        self.results = []

    def parse_output(self, output):
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
    
