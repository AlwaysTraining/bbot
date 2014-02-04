
import logging
import sys

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN

level = WARN

tracefile=sys.stdout

traceid=0

cur_state=None
cur_prefix=None

def formattrace(msg):
    global traceid
    traceid = traceid + 1

    s = "<"+str(traceid)
    if cur_prefix is not None:
        s+=":"+cur_prefix
    if cur_state is not None:
        s+=":"+cur_state
    s+=">  " + str(msg)
    return s

def trace(msg):
    tracefile.write("\n" + msg + "\n")
    
def info(msg):
    global level
    msg = formattrace(msg)
    logging.info(msg)
    #print 'info message',traceid,'going to log',level
    if level <= INFO:
        #print 'info message',traceid,'going to trace',level,'vs',INFO
        trace(msg)
def debug(msg):
    global level
    msg = formattrace(msg)
    logging.debug(msg)
    #print 'debug message',traceid,'going to log',level
    if level <= DEBUG:
        #print 'debug message',traceid,'going to trace',level,'vs',DEBUG
        trace(msg)
def warn(msg):
    global level
    msg = formattrace(msg)
    logging.warn(msg)
    if level <= WARN:
        trace(msg)

def exception(msg):
    trace(formattrace(str(msg)))
    logging.exception(msg)

def configure(msglevel,format,logpath,tracepath):
    global tracefile
    global level
    level = msglevel
    logging.getLogger('').handlers = []

    if logpath is not None:
        # when logging to file always go full debug
        logmsglevel=DEBUG
    else:
        logmsglevel = msglevel

    logging.basicConfig(level=logmsglevel,format=format,filename=logpath)

    if tracepath is None:
        tracefile = sys.stdout
    else:
        tracefile = file(tracepath,'w')



        

