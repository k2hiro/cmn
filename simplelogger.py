#
#   simple logger class
#

import colorama
from colorama import Fore, Style
import threading
import datetime
import os
import inspect

colorama.init(strip=False)

LOG_DEBUG = 0
LOG_DBUG = 0
LOG_INFO = 1
LOG_WARN = 2
LOG_ERR  = 3
LOG_CRIT = 4
FMT_DEF = 0
FMT_DETAIL = 1
Level_str = ['DBUG', 'INFO', 'WARN', 'ERR ', 'CRIT']


class Simplelogger():

    def __init__(self, level=LOG_WARN):
        self.loglevel_stdout = level           # logging level for STDOUT
        self.logfile = None
        self.loglevel_file = None              # logging level for file output
        self.logformats = [
            '{date_time} [{loglevel}] <{thread:^10}> {msg}',
            '{date_time} [{loglevel}] <{thread:^10}> {codeinfo} {msg}',     # for DBUG logs
        ]

    def setloglevel(self, level):
        """
        Set log level for terminal logging
        :param level: log level
        :return:
        """
        self.loglevel_stdout = level


    def logfile(self, path, level=LOG_DEBUG, encoding='utf-8'):
        """
        Open log file. Directory will be created if specified.
        :param path: file path or basename
        :param level: log level
        :param encoding: encoding
        :return:
        """
        if self.logfile:
            self.logfile.close()
            self.logfile = None
        try:
            if '/' in path:
                dir_nam = os.path.dirname(path)
                if not os.path.exists(dir_nam):
                    os.mkdir(os.path.dirname(path))
            self.logfile = open(path, mode='w', encoding=encoding)
        except Exception as e:
            print(f"failed to create logfile '{path}' with exception {type(e).__name__}: {str(e)}")
            return False

        self.loglevel_file = level
        return True


    def format_simple(self):
        self.logformats = [
            '{date_time} [{loglevel}] {msg}',
            '{date_time} [{loglevel}] {msg}',
        ]
        return


    def debug(self, msg, fmt=1):
        self._log(msg, fmt, LOG_DEBUG, Fore.GREEN)

    def info(self, msg, fmt=0):
        self._log(msg, fmt, LOG_INFO, Fore.CYAN)

    def warn(self, msg, fmt=0):
        self._log(msg, fmt, LOG_WARN, Fore.YELLOW)

    def err(self, msg, fmt=0):
        self._log(msg, fmt, LOG_ERR, Fore.RED)

    def crit(self, msg, fmt=0):
        self._log(msg, fmt, LOG_CRIT, Fore.MAGENTA)


    # -------------------------------------

    def _log(self, msg, fmt, level, color):
        if self.loglevel_stdout > level and (self.logfile is None or self.loglevel_file > level):
            return

        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        th = threading.current_thread().name
        fn = os.path.basename(inspect.stack()[2].filename)
        cinfo = f"|{fn}:{inspect.stack()[2].lineno}:{inspect.stack()[2].function}|"
        logmsg = self.logformats[fmt].format(date_time=dt, loglevel=Level_str[level], thread=th, codeinfo=cinfo, msg=msg)

        if self.loglevel_stdout <= level:
            print(color + logmsg + Style.RESET_ALL, flush=True)
        if self.logfile and self.loglevel_file <= level:
            self.logfile.write(logmsg + '\n')
