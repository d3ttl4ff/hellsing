#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### Output > Command-Line Output
###
import os
import re
import sys
from colored import *
import prettytable
import humanfriendly.prompts

from lib.output.Logger import logger

class Output(object):

    @staticmethod
    def print(string, color=None, highlight=None, attrs=None):
        """Print string with styles"""
        print(Output.colored(string, color, highlight, attrs))

    @staticmethod
    def colored(string, color=None, highlight=None, attrs=None):
        """Apply styles to a given string"""
        # Colors list: https://pypi.org/project/colored/
        return colored.stylize(string, (colored.fg(color) if color else '') + \
                                       (colored.bg(highlight) if highlight else '') + \
                                       (colored.attr(attrs) if attrs else ''))
    
    @staticmethod
    def bold(string):
        """Print string in bold"""
        return colored.stylize(string, colored.attr('bold'))
    
    @staticmethod
    def print_title(title: str) -> None:
        title_len = len(title) + 2  # Adding 2 for the spaces around the title
        max_title_len = 67
        rest_len = (max_title_len - title_len) // 2 - 2  # Adjusted for the border characters
        
        title_color = '6'
        border_color = '10'

        print()
        # Top border
        top_border = ' ' * rest_len + '╔' + '═' * (title_len) + '╗'
        Output.print(top_border, color=border_color, attrs='bold')

        # Title row
        title_part = Output.colored(' ' + title + ' ', color=title_color)
        # For the title row, since it combines different colors, print parts separately
        left_border = Output.colored('═' * rest_len + '╣', color=border_color, attrs='bold')
        right_border = Output.colored('╠' + '═' * rest_len, color=border_color, attrs='bold')
        print(left_border + title_part + right_border)

        # Bottom border
        bottom_border = ' ' * rest_len + '╚' + '═' * (title_len) + '╝'
        Output.print(bottom_border, color=border_color, attrs='bold')
        # print()
        
    @staticmethod
    def print_subtitle(subtitle: str, subtool: str, subcommand: str) -> None:
        subtitle_color = 'black'
        subtitle_highlight = '226'
        subtool_color = 'black'
        subtool_highlight = 'turquoise_2'
        subcommand_color = 'turquoise_2'
        subcommand_highlight = '234'
        border_color = '10'

        # Subtitle, subtool and subcommand 
        subtitle_part = Output.colored(' ' + subtitle + ' ', color=subtitle_color, highlight=subtitle_highlight, attrs='bold')
        subtool_part = Output.colored(' ' + subtool + ' ', color=subtool_color, highlight=subtool_highlight, attrs='bold')
        subcommand_part = Output.colored(' ' + subcommand + ' ', color=subcommand_color, attrs='bold')
        check_part = Output.colored(' check ', color='black', highlight=border_color, attrs='bold')
        
        # top_border = Output.colored('╔═════════check═╣ ', color=border_color, attrs='bold')
        top_border = Output.colored('╔════════', color=border_color, attrs='bold')
        bottom_border = Output.colored('╚═', color=border_color)
        buttom_cmd = Output.colored('$', color=border_color, attrs='bold')
        subtitle_connector = Output.colored('▒', color=subtitle_highlight, attrs='bold')
        subtool_connector = Output.colored('▒', color=subtool_highlight, attrs='bold')
        check_connector = Output.colored('▒', color=border_color, attrs='bold')
        
        print(top_border + check_part + check_connector + subtitle_connector + subtitle_part + subtitle_connector + subtool_connector + subtool_part)
        print(bottom_border + buttom_cmd + subcommand_part)
        print()
        
    @staticmethod
    def print_neon_title(title: str) -> None:
        title_len = len(title) + 2  # Adding 2 for the spaces around the title
        # rest_len = (title_len) // 2 - 2  # Adjusted for the border characters
        
        title_color = '105'
        border_color = 'white'
        
        top_border = ' ' * 0 + '₋' * (title_len + 4)
        Output.print(top_border, color=border_color, attrs='bold')

        left_border = Output.colored('┃⥏', color=border_color, attrs='bold')
        title_part = Output.colored(' ' + title + ' ', color=title_color, attrs='bold')
        right_border = Output.colored('⥑┃', color=border_color, attrs='bold')
        print(left_border + title_part + right_border)

        bottom_border = ' ' * 0 + 'ˉ' * (title_len + 4)
        Output.print(bottom_border, color=border_color)
        # print()
        
    @staticmethod
    def print_neon_colored(title: str) -> None:
        title_len = len(title) + 2  # Adding 2 for the spaces around the title
        
        title_color = '6'
        border_color = '10'
        
        left_border = Output.colored('┃⥏', color=border_color, attrs='bold')
        title_part = Output.colored(' ' + title, color=title_color, attrs='bold')
        y = Output.colored(left_border + title_part )
        
        return y
    
    @staticmethod
    def print_sub_scoreboard(total_game_played: str, total_game_count: str, subtitle_highlight="226") -> None:
        game_count_length = len(total_game_count)
        score_board_rest_len = (game_count_length) // 2
        
        total_game_played_part_color = 'black'
        # subtitle_highlight = '226'
        subtool_color = 'black'
        border_color = '10'
        total_game_played_part_highlight = 'green'

        total_game_played_part = Output.colored(' ' + total_game_played + ' ', color=total_game_played_part_color, highlight=total_game_played_part_highlight, attrs='bold')

        left_border = Output.colored('┃⥏ ' * 1, color=border_color, attrs='bold')
        total_game_played_score_connector = Output.colored('▒', color=subtitle_highlight, attrs='bold')
        total_game_played_part_connector = Output.colored('▒', color=border_color, attrs='bold')
        score_connector = Output.colored('░', color=border_color, attrs='bold')
        
        left_highlight = Output.colored(' ', highlight=subtitle_highlight, attrs='bold')
        right_highlight = Output.colored(' ', highlight=subtitle_highlight, attrs='bold')
        score_count_part = Output.colored(total_game_count, color=subtool_color, highlight=subtitle_highlight, attrs='bold')
        final_score_count_part = left_highlight + score_count_part + right_highlight

        print(left_border + total_game_played_part + total_game_played_part_connector + score_connector + total_game_played_score_connector + final_score_count_part + total_game_played_score_connector)
        # print("")
        
    @staticmethod
    def print_banner_grabbing(description: str, target_mode: str, action: str) -> None:
        description_color = 'black'
        description_highlight = '135'
        target_mode_color = 'black'
        target_mode_highlight = '111'
        action_color = 'turquoise_2'
        action_highlight = '234'
        border_color = '10'

        # action, target_mode and subcommand 
        description_part = Output.colored(' ' + description + ' ', color=description_color, highlight=description_highlight, attrs='bold')
        target_mode_part = Output.colored(' ' + target_mode + ' ', color=target_mode_color, highlight=target_mode_highlight, attrs='bold')
        action_part = Output.colored(' ' + action + ' ', color=action_color, attrs='bold')
        identify_part = Output.colored(' identify ', color='black', highlight=border_color, attrs='bold')
        
        # top_border = Output.colored('╔═════════check═╣ ', color=border_color, attrs='bold')
        top_border = Output.colored('╔═══════╣', color=border_color, attrs='bold')
        bottom_border = Output.colored('╚═', color=border_color)
        buttom_cmd = Output.colored('$', color=border_color, attrs='bold')
        description_connector = Output.colored('▒', color=description_highlight, attrs='bold')
        target_mode_connector = Output.colored('▒', color=target_mode_highlight, attrs='bold')
        identify_connector = Output.colored('▒', color=border_color, attrs='bold')
        
        print(top_border + identify_part + identify_connector + description_connector + description_part + description_connector + target_mode_connector + target_mode_part)
        print(bottom_border + buttom_cmd + action_part)
        print()

    @staticmethod
    def print_with_tabs(string, color=None, highlight=None, attrs=None):
        """Print string prefixed by a tabulation"""
        Output.print('         '+string, color, highlight, attrs)

    @staticmethod
    def print_inline(string):
        """Print at the same location (erase and print)"""
        sys.stdout.write('\033[1K')
        sys.stdout.write('\033[0G')
        sys.stdout.write(string)
        sys.stdout.flush()


    @staticmethod
    def banner(banner):
        """Print banner"""
        Output.print(banner, color='light_green', attrs='bold')


    @staticmethod
    def title1(title):
        """Print title level 1"""
        msg  = '\n'
        msg += '-'*80 + '\n'
        msg += ' {title}\n'.format(title=title)
        msg += '-'*80 + '\n'
        Output.print(msg, color='light_green', attrs='bold')


    @staticmethod
    def title2(title):
        """Print title level 2"""
        Output.print('[>] ' + title, color='light_yellow', attrs='bold')


    @staticmethod
    def title3(title):
        """Print title level 3"""
        Output.print('[>] ' + title, attrs='bold')


    @staticmethod
    def begin_cmd(cmd):
        """Print command-line and beginning delimiter for output"""
        # If command-line starts with "cd" command, remove it for better readability
        if cmd.startswith("cd"):
            cmd = cmd[cmd.index(";") + 1 :].strip()
        col = None
        try:
            _, col = (lambda x: (int(x[0]), int(x[1])))(
                os.popen("stty size 2>/dev/null", "r").read().split()
            )
        except Exception as e:
            col = col if col is not None else 80
        msg = "\n"
        msg += " " * col + "\n"
        msg += " command> {cmd}".format(cmd=cmd) + " " * (col - (len(cmd) + 5) % col)
        Output.print(msg, color="161", highlight="234", attrs="bold")
        Output.print("")

    @staticmethod
    def delimiter():
        """Print ending delimiter for command output"""
        col = None
        try:
            _, col = (lambda x: (int(x[0]), int(x[1])))(
                os.popen("stty size 2>/dev/null", "r").read().split()
            )
        except Exception as e:
            col = col if col is not None else 80
        msg = "\n"
        msg += " " * col + "\n"
        Output.print(msg, color="white", highlight="grey_19", attrs="bold")

    @staticmethod
    def prompt_confirm(question, default=None):
        """
        Prompt for confirmation.
        :param str question: Question to print
        :param str default: Default answer
        """
        return humanfriendly.prompts.prompt_for_confirmation(
            colored.stylize('[?] ', colored.fg('cyan')+colored.attr('bold'))+question,
            default=default, padding=False)


    @staticmethod
    def prompt_choice(question, choices, default=None):
        """
        Prompt choice.
        :param str question: Question to print
        :param dict choices: Possible choices
            Example: {'y': 'Yes', 'n': 'No', 'q': 'Quit'}
        :param str default: Default answer
        """
        while True:
            ret = humanfriendly.prompts.prompt_for_input(
                colored.stylize('\b[?] ', colored.fg('cyan')+colored.attr('bold')) \
                    + question, default=default)

            if ret.lower() in choices: return ret.lower()
            else:
                valid = ' / '.join('{} = {}'.format(key,val) \
                    for key,val in choices.items())
                logger.warning('Invalid value. Valid values are: ' + valid)
        return default


    @staticmethod
    def prompt_choice_range(question, mini, maxi, default):
        """
        Prompt choice in a range [mini-maxi].
        :param str question: Question to print
        :param int mini: Minimum number in range
        :param int maxi: Maximum number in range
        :param int default: Default answer
        """
        while True:
            try:
                ret = int(humanfriendly.prompts.prompt_for_input(
                    colored.stylize('\b[?] ', colored.fg('cyan')+colored.attr('bold'))+ \
                    question, default=default))
            except ValueError:
                continue
            if mini <= ret <= maxi: 
                return ret
            else:
                logger.warning('Invalid value. Valid values are in range ' \
                    '[{mini}-{maxi}]'.format(mini=mini, maxi=maxi))
        return default


    @staticmethod
    def prompt_choice_verbose(choices, default=None):
        """Prompt choice in verbose mode"""
        return humanfriendly.prompts.prompt_for_choice(choices, 
            default=default, padding=False)


    @staticmethod
    def table(columns, data, hrules=True, borders=True):
        """
        Print a table. Supports multi-row cells.
        :param columns: An iterable of column names (strings)
        :param data: An iterable containing the data of the table
        :param hrules: Boolean for horizontal rules
        """
        columns = map(lambda x:Output.colored(x, attrs='bold'), columns)
        table = prettytable.PrettyTable(
            hrules=prettytable.ALL if hrules else prettytable.FRAME, 
            field_names=columns)
        for row in data:
            table.add_row(row)
        table.align = 'l'
        if not borders:
            table.border = False
            
        print(table)
        
    @staticmethod
    def report_table(columns, data, hrules=True, borders=True, use_ansi=True):
        """
        Print a table. Supports multi-row cells.
        :param columns: An iterable of column names (strings)
        :param data: An iterable containing the data of the table
        :param hrules: Boolean for horizontal rules
        """
        if use_ansi:
            columns = [Output.colored(x, attrs='bold') for x in columns]
        table = prettytable.PrettyTable(field_names=columns)
        for row in data:
            table.add_row(row)
        table.align = 'l'
        if not borders:
            table.border = False
        if hrules:
            table.hrules = prettytable.ALL
        return table.get_string()

    @staticmethod
    def input_exit_choice(title: str) -> None:
        title_len = len(title) + 2  # Adding 2 for the spaces around the title
        
        title_color = '135'
        border_color = 'turquoise_2'
        
        left_border = Output.colored('⬤', color=border_color, attrs='bold')
        title_part = Output.colored(' ' + title, color=title_color, attrs='bold')
        y = Output.colored(left_border + title_part)
        
        return y
    