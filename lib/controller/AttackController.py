from lib.core.AttackScope import AttackScope
from lib.core.ServicesConfig import ServicesConfig
from lib.core.Toolbox import Toolbox

class AttackController:
    def __init__(self, settings, arguments):
        self.settings = settings
        self.arguments = arguments
        self.attack_scope = AttackScope()
        self.services_config = ServicesConfig(self.settings.list_services())
        self.toolbox = Toolbox(self.settings)

    def run_attack(self):
        # Example: Running an attack based on provided arguments
        target = self.arguments.target_ip_or_url
        service = self.arguments.service
        if not service:
            print("Service not specified.")
            return

        if not self.services_config.is_service_supported(service):
            print(f"Service {service} is not supported.")
            return

        self.attack_scope.add_target(target)
        # This is a placeholder for actual attack logic
        print(f"Executing attacks against {target} for service {service}...")

        # Example: Fetching and using tools from the toolbox for the specified service
        tools = self.toolbox.list_tools(service)
        for tool in tools:
            print(f"Using tool {tool} for attacking {target} on service {service}...")
            # Placeholder for executing the tool

    def add_target_to_scope(self, target):
        self.attack_scope.add_target(target)

    def update_target_in_scope(self, old_target, new_target):
        self.attack_scope.update_target(old_target, new_target)

    def list_attack_scope(self):
        self.attack_scope.list_targets()
