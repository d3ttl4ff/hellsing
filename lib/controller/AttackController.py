
class AttackController:
    def __init__(self, arguments, settings):
        """ 
        Controller interface
        
        :param ArgumentsParser arguments: Arguments from command-line
        :param Settings settings: Settings from config files
        """
        
        self.arguments = arguments
        self.settings  = settings

    def run(self):
        
        # --set-target
        if self.arguments.args.target_ip_or_url:            
            if self.arguments.args.banner:
                self.settings.set_target(self.arguments.args.target_ip_or_url, banner_condition=True)
            else:
                self.settings.set_target(self.arguments.args.target_ip_or_url)
        
        # --run-only
        if self.arguments.args.run_only:
            self.settings.run_only(self.arguments.args.run_only)
            self.settings.set_target(self.arguments.args.target_ip_or_url,run_only_condition=True)