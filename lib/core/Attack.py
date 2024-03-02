import configparser
from datetime import datetime
import os
import subprocess
import sys
import shutil

from lib.core.Config import *
from lib.output import Output
from lib.output.Logger import logger
from lib.utils.StringUtils import StringUtils

class Attack:
    def __init__ (self, settings):
        """
        Construct the Toolbox object.

        :param Settings settings: Settings from config file
        """
        self.settings = settings
        self.config = configparser.ConfigParser()
        self.config.read(HTTP_CONF_FILE + CONF_EXT)
        self.tools = self.config.sections()

    #------------------------------------------------------------------------------------
    
    # Attack methods
    
    def 