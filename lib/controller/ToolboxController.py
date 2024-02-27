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
        :param Session sqlsession: SQLAlchemy session
        """
        self.arguments = arguments
        self.settings  = settings

    def run(self):

        toolname = self.arguments.args.install_tool \
            or self.arguments.args.update_tool \
            or self.arguments.args.uninstall_tool

        # --show-all
        if self.arguments.args.show_toolbox_all:
            self.settings.show_all_tools()

        # # --install-tool <tool-name>
        # elif self.arguments.args.install_tool:
        #     self.settings.toolbox.install_tool(toolname)

        # # --install-all
        # elif self.arguments.args.install_all:
        #     self.settings.toolbox.install_all()

        # --update-tool <tool-name>
        elif self.arguments.args.update_tool:
            self.settings.update_tool(toolname)

        # # --update-all
        # elif self.arguments.args.update_all:
        #     self.settings.toolbox.update_all()

        # # --uninstall-tool <tool-name>
        # elif self.arguments.args.uninstall_tool:
        #     self.settings.toolbox.remove_tool(toolname)

        # # --uninstall-all
        # elif self.arguments.args.uninstall_all:
        #     self.settings.toolbox.remove_all()

         
            # if arguments.args.show_toolbox_all:
            #     settings.show_all_tools() 
            # if arguments.args.install_tool:
            #     settings.install_tool()
            # if arguments.args.install_all:
            #     settings.install_all_tools()
            # if arguments.args.update_tool:
            #     settings.update_tool(toolname)
            # if arguments.args.update_all:
            #     settings.update_all_tools()
            # if arguments.args.uninstall_tool:
            #     settings.uninstall_tool()
            # if arguments.args.uninstall_all:
            #     settings.uninstall_all_tools()



