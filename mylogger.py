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

LogLevel_stdout = LOG_WARN       # default log level for stdout
LogLevel_file   = LOG_DEBUG      # default log level for file
LogFile = None      # file handler


def setloglevel(level):
    """
    Set log level for terminal logging
    :param level: log level
    :return:
    """
    global LogLevel_stdout
    LogLevel_stdout = level


def logfile(path, level=LOG_DEBUG, encoding='utf-8'):
    """
    Open log file. Directory will be created if specified.
    :param path: file path or basename
    :param level: log level
    :param encoding: encoding
    :return:
    """
    global LogFile, LogLevel_file
    if LogFile:
        LogFile.close()
        LogFile = None
    try:
        if '/' in path:
            dir_nam = os.path.dirname(path)
            if not os.path.exists(dir_nam):
                os.mkdir(os.path.dirname(path))
        LogFile = open(path, mode='w', encoding=encoding)
    except Exception as e:
        print(f"failed to create logfile '{path}' with exception {type(e).__name__}: {str(e)}")
        return False

    LogLevel_file = level
    return True

def debug(msg, fmt=1):
    _log(msg, fmt, LOG_DEBUG, Fore.GREEN)

def info(msg, fmt=0):
    _log(msg, fmt, LOG_INFO, Fore.CYAN)

def warn(msg, fmt=0):
    _log(msg, fmt, LOG_WARN, Fore.YELLOW)

def err(msg, fmt=0):
    _log(msg, fmt, LOG_ERR, Fore.RED)

def crit(msg, fmt=0):
    _log(msg, fmt, LOG_CRIT, Fore.MAGENTA)


# ------------------------------------- Private functions

def _log(msg, fmt, level, color):
    global LogLevel_stdout, LogLevel_file, LogFile
    level_str = ['DBUG', 'INFO', 'WARN', 'ERR ', 'CRIT']
    log_format = [
        '{date_time} [{loglevel}] <{thread:^10}> {msg}',
        '{date_time} [{loglevel}] <{thread:^10}> {codeinfo} {msg}',
    ]

    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    th = threading.current_thread().name
    #cinfo = f"|{inspect.stack()[2].function:17}|"
    fn = os.path.basename(inspect.stack()[2].filename)
    cinfo = f"|{fn}:{inspect.stack()[2].lineno}:{inspect.stack()[2].function}|"
    logmsg = log_format[fmt].format(date_time=dt, loglevel=level_str[level], thread=th, codeinfo=cinfo, msg=msg)

    if LogLevel_stdout <= level:
        print(color + logmsg + Style.RESET_ALL, flush=True)
    if LogFile and LogLevel_file <= level:
        LogFile.write(logmsg + '\n')
