
class AttackController:
    def __init__(self, arguments, settings):
        self.arguments = arguments
        self.settings = settings
        self.services_config = settings.services

    def run(self):
        target = self.arguments.target_ip_or_url
        run_only = self.arguments.run_only.split(',') if self.arguments.run_only else []
        run_exclude = self.arguments.run_exclude.split(',') if self.arguments.run_exclude else []

        for service_name in self.services_config.services:
            for check_name, check in self.services_config[service_name].items():
                if run_only and check['category'] not in run_only:
                    continue
                if run_exclude and check['category'] in run_exclude:
                    continue
                self.execute_check(check, target)

    def execute_check(self, check, target):
        # Assume command is stored in check['command_1']
        # Replace [URL] or [IP] with the actual target
        command = check['command_1'].replace('[URL]', target).replace('[IP]', target)
        print(f"Executing {check['name']}: {command}")
        # Execution logic here, e.g., subprocess.run(command, shell=True)
