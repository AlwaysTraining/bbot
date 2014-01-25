
import logging
import sys

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN

level = WARN

tracefile=sys.stdout

traceid=0

def formattrace(msg):
    global traceid
    traceid = traceid + 1
    return "<"+str(traceid)+"> " + str(msg)

def trace(msg):
    tracefile.write("\n" + msg + "\n")
    
def info(msg):
    global level
    if level < INFO:
        return
    msg = formattrace(msg)
    trace(msg)
    logging.info(msg)
def debug(msg):
    global level
    if level < DEBUG:
        return
    msg = formattrace(msg)
    trace(msg)
    logging.debug(msg)
def warn(msg):
    global level
    if level < WARN:
        return
    msg = formattrace(msg)
    trace(msg)
    logging.warn(msg)

def exception(msg):
    trace(formattrace(str(msg)))
    logging.exception(msg)

def configure(level,format,logpath,tracepath):
    global tracefile
    logging.getLogger('').handlers = []
    if logpath is not None:
        logging.basicConfig(level=level,format=format,filename=logpath)
    if tracepath is None:
        tracefile = sys.stdout
    else:
        tracefile = file(tracepath,'w')


        

