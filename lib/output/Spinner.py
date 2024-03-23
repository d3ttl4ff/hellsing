import itertools
import threading
import time
import sys
import random
import subprocess
from colored import fg, bg, attr

# Initializing the color module class
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    BADFAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    BG_ERR_TXT  = '\033[41m' # For critical errors and crashes
    BG_HEAD_TXT = '\033[100m'
    BG_ENDL_TXT = '\033[46m'
    BG_CRIT_TXT = '\033[45m'
    BG_HIGH_TXT = '\033[41m'
    BG_MED_TXT  = '\033[43m'
    BG_LOW_TXT  = '\033[44m'
    BG_INFO_TXT = '\033[42m'

    BG_SCAN_TXT_START = '\x1b[6;30;42m'
    BG_SCAN_TXT_END   = '\x1b[0m'

def terminal_size():
    try:
        rows, columns = subprocess.check_output(['stty', 'size']).split()
        return int(columns)
    except subprocess.CalledProcessError as e:
        return int(20)
    
class Spinner:
    busy = False
    delay = 0.005 # 0.05

    @staticmethod
    def spinning_cursor():
        while 1:
            #for cursor in '|/-\\/': yield cursor #←↑↓→
            #for cursor in '←↑↓→': yield cursor
            #for cursor in '....scanning...please..wait....': yield cursor
            for cursor in '░': yield cursor
    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay
        self.disabled = False
        self.colors = [10, 16]

    def spinner_task(self):
        inc = 0
        try:
            while self.busy:
                if not self.disabled:
                    # x = bcolors.BG_SCAN_TXT_START+next(self.spinner_generator)+bcolors.BG_SCAN_TXT_END
                    # inc = inc + 1
                    # print(x,end='')
                    
                    # if inc>random.uniform(0,terminal_size()): #30 init
                    #     print(end="\r")
                    #     bcolors.BG_SCAN_TXT_START = '\x1b[6;30;'+str(round(random.uniform(40,47)))+'m'
                    #     inc = 0
                    
                    current_color = random.choice(self.colors) # Randomly choose a color
                    x = fg('white') + bg(current_color) + next(self.spinner_generator) + attr('reset')
                    inc = inc + 1
                    print(x, end='')
                    
                    if inc > random.uniform(0, terminal_size()):
                        print(end="\r")
                        inc = 0
                        
                    sys.stdout.flush()
                    
                time.sleep(self.delay)
                
                if not self.disabled:
                    sys.stdout.flush()

        except (KeyboardInterrupt, SystemExit):
            # print("\n\t"+ bcolors.BG_ERR_TXT+"Terminating..." +bcolors.ENDC)
            sys.exit(1)

    def start(self):
        self.busy = True
        try:
            threading.Thread(target=self.spinner_task).start()
        except Exception as e:
            print("\n")
        
    def stop(self):
        try:
            self.busy = False
            time.sleep(self.delay)
        except (KeyboardInterrupt, SystemExit):
            # print("\n\t"+ bcolors.BG_ERR_TXT+"Terminating..." +bcolors.ENDC)
            sys.exit(1)
            
