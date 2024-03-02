class AttackScope:
    def __init__(self):
        self.targets = []

    def add_target(self, target):
        if target not in self.targets:
            self.targets.append(target)
            print(f"Target {target} added to the scope.")
        else:
            print(f"Target {target} is already in the scope.")

    def update_target(self, old_target, new_target):
        try:
            index = self.targets.index(old_target)
            self.targets[index] = new_target
            print(f"Target {old_target} updated to {new_target}.")
        except ValueError:
            print(f"Target {old_target} not found in the scope.")

    def list_targets(self):
        if self.targets:
            print("Current targets in scope:")
            for target in self.targets:
                print(target)
        else:
            print("No targets in the scope.")
