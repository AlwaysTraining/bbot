import logging
import sys
import traceback

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN

level = WARN

tracefile = sys.stdout
tracefilepath = None

logfile = sys.stderr
logfilepath = None

traceid = 0

cur_state = None
cur_strat = None

errors = {}
warnings = {}
notes = {}

def formattrace(msg):
    global traceid
    traceid = traceid + 1

    s = "<" + str(traceid)
    if cur_strat is not None:
        s += ":" + cur_strat
    if cur_state is not None:
        s += ":" + cur_state
    s += ">  " + str(msg)
    return s

class Log:
    def info(self, msg):
        logfile.write("INFO  : " + msg + "\n")
        logfile.flush()
    def debug(self, msg):
        logfile.write("DEBUG : " + msg + "\n")
        logfile.flush()
    def warn(self, msg):
        logfile.write("WARN  : " + msg + "\n")
        logfile.flush()
    def exception(self, msg):
        logfile.write("EXCEPTION: " + str(type(msg)) + " : " + str(msg) + "\n")
        logfile.write(traceback.format_exc())
        logfile.flush()
log = Log()


def trace(msg):
    tracefile.write("\n" + msg + "\n")
    tracefile.flush()


def info(msg):
    global level
    global log
    msg = formattrace(msg)
    log.info(msg)
    #print 'info message',traceid,'going to log',level
    if level <= INFO:
        #print 'info message',traceid,'going to trace',level,'vs',INFO
        trace(msg)

def note(msg):
    global notes
    global log
    _update_msg_map(notes,msg)
    info("NOTE: " + msg)

def _update_msg_map(msgmap, msg):
    if msg in msgmap:
        msgmap[msg] += 1
    else:
        msgmap[msg] = 1

def debug(msg):
    global level
    global log
    msg = formattrace(msg)
    log.debug(msg)
    #print 'debug message',traceid,'going to log',level
    if level <= DEBUG:
        #print 'debug message',traceid,'going to trace',level,'vs',DEBUG
        trace(msg)

def warn(msg):
    global level
    global log
    global warnings
    _update_msg_map(warnings,msg)

    msg = formattrace(msg)
    
    log.warn(msg)
    if level <= WARN:
        trace(msg)


def exception(msg):
    global errors
    global log
    _update_msg_map(errors,msg)
    trace(formattrace(str(msg)))
    log.exception(msg)


def configure(msglevel, format, logpath, tracepath):
    global tracefile
    global log
    global tracefilepath
    global logfile
    global logfilepath
    global level
    global warnings
    global errors
    global notes

    warnings = {}
    errors = {}
    notes = {}

    level = msglevel

    if logpath is not None:
        # when logging to file always go full debug
        logmsglevel = DEBUG
    else:
        logmsglevel = msglevel

    if logpath is None:
        logfile = sys.stderr
    else:
        logfile = file(logpath, 'w')
    logfilepath = logpath

    if tracepath is None:
        tracefile = sys.stdout
    else:
        tracefile = file(tracepath, 'w')
    tracefilepath = tracepath



        

