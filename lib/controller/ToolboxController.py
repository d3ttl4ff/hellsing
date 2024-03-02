#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### Core > Toolbox Controller
###

class ToolboxController():

    def __init__(self, arguments, settings):
        """
        Controller interface.

        :param ArgumentsParser arguments: Arguments from command-line
        :param Settings settings: Settings from config files
        """
        self.arguments = arguments
        self.settings  = settings

    def run(self):

        toolname = self.arguments.args.install_tool \
            or self.arguments.args.update_tool \
            or self.arguments.args.uninstall_tool \
            or self.arguments.args.check_tool

        # --show-all
        if self.arguments.args.show_toolbox_all:
            self.settings.show_all_tools()

        # --install-tool <tool-name>
        elif self.arguments.args.install_tool:
            self.settings.install_tool(toolname)

        # --install-all
        elif self.arguments.args.install_all:
            self.settings.install_all_tools()

        # --update-tool <tool-name>
        elif self.arguments.args.update_tool:
            self.settings.update_tool(toolname)

        # --update-all
        elif self.arguments.args.update_all:
            self.settings.update_all_tools()

        # --uninstall-tool <tool-name>
        elif self.arguments.args.uninstall_tool:
            self.settings.uninstall_tool(toolname)

        # --uninstall-all
        elif self.arguments.args.uninstall_all:
            self.settings.uninstall_all_tools()
            
        # --check-tool <tool-name>
        elif self.arguments.args.check_tool:
            self.settings.check_tool(toolname)
            
        # --check-all
        elif self.arguments.args.check_all:
            self.settings.check_all_tools()



