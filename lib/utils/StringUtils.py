#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### Utils > StringUtils
###
import colored
import re
import textwrap


class StringUtils:
    @staticmethod
    def wrap(string, maxlength):
        """
        Wrap a string on multilines.

        :param str string: String to wrap
        :param int maxlength: Maximum length for each line        
        """
        if not string:
            return ''
        else:
            return '\n'.join(textwrap.wrap(string, maxlength))