import os
import sys

from lib.core.Config import *
from lib.output import Output
from lib.utils.StringUtils import StringUtils

class Toolbox:
    def __init__ (self, settings):
        """
        Construct the Toolbox object.

        :param Settings settings: Settings from config file
        """
        self.settings = settings
        self.tools = self.config.sections()
        
    #------------------------------------------------------------------------------------
    # Output Methods

    def show_toolbox(self, filter_service=None):
        """
        Display a table showing the content of the toolbox.
        """

        data = list()
        columns = [
            'Name',
            'Service',
            'Status',
            'Last Update',
            'Description',
        ]

        for tool in self.tools:

            # Install status format style
            if tool.installed:
                status = Output.colored('OK |',
                color='green')
            else:
                status = Output.colored('Not installed',  color='red')

            # Add line for the tool
            data.append([
                tool.name,
                tool.target_service,
                status,
                tool.last_update,
                StringUtils.wrap(tool.description, 120), # Max line length
            ])

        # Output.title1('Toolbox content - {filter}'.format(
        #     filter='all services' if filter_service is None \
        #            else 'service ' + filter_service))

        Output.table(columns, data, hrules=False)

    #------------------------------------------------------------------------------------