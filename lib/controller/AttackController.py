
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
            
            # --banner            
            if self.arguments.args.banner:
                self.settings.set_target(self.arguments.args.target_ip_or_url, 
                                         banner_condition=True)
                
            # --run-only
            elif self.arguments.args.run_only:
                self.settings.set_target(self.arguments.args.target_ip_or_url,
                                         run_only_condition=True, 
                                         categories=self.arguments.args.run_only)
                
            # --run-exclude
            elif self.arguments.args.run_exclude:
                self.settings.set_target(self.arguments.args.target_ip_or_url, 
                                         run_exclude_condition=True, 
                                         categories=self.arguments.args.run_exclude)
            # --profile
            elif self.arguments.args.profile:
                self.settings.set_target(self.arguments.args.target_ip_or_url, 
                                         profile_condition=True, 
                                         profile=self.arguments.args.profile)
            
            # Default
            else:
                self.settings.set_target(self.arguments.args.target_ip_or_url)
        