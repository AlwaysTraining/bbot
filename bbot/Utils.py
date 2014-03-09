#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import imp
import os,sys
import botlog
import Strategy

bbot_TOOL_VERSION="0.1"
ENVIRON_PREFIX="bbot_"

NUM_REGEX='([0-9][,0-9]*)'
SPACE_REGEX='[ \t]+'
STR_REGEX='(.+)'

VERYHIGH_PRIORITY = 100 * 6
HIGH_PRIORITY =     100 * 5
MED_PRIORITY =      100 * 4
LOW_PRIORITY =      100 * 3
VERYLOW_PRIORITY =  100 * 2
NO_PRIORITY =       100 * 1

TWOBIL = 2000000000
HUNMIL = 100000000

def load_modules(
    modulePaths    # list of paths to python modules
    ):
    """
    Dynamically load each module path in the list modulePaths
    return a dictionary where keys are the items in modulePaths and the
    values are the corresponding loaded module object
    """

    # create empty dictionary for return from function
    modules = {}

    # iterate each path in the list of modulePaths
    for modulePath in modulePaths:

        # expand all environment variables in path with built in function
        expandedModulePath = os.path.expandvars(modulePath)

        if not os.path.exists(expandedModulePath):
            raise Exception("Module path " + str(expandedModulePath) + 
                    " was not found") 

        # split path into base path (module path) and file extension
        mod_name,file_ext = os.path.splitext(os.path.split(modulePath)[-1])

        # set loadFunction to None
        loadFunc = None

        # if file extenstion indicates python source file
        if file_ext.lower() == '.py':
            # set the loadFunction to imp.load_source
            loadFunc = imp.load_source
        # otherwise if the file extension indicates a compiled object
        elif file_ext.lower() == '.pyc':
            # set the loadFunction to imp.load_compiled
            loadFunc = imp.load_compiled

        # if loadFunction is None
        if loadFunc is None:
            # raise an exception for the unexpected path name
            raise Exception("Unable to load module: " + str(expandedModulePath))

        # set the returned python module resulting from invoking 
        #   loadFunction into returning dictionary
        botlog.debug("dynamically loding: " + expandedModulePath)
        mod = loadFunc(mod_name, expandedModulePath)
        modules[modulePath] = mod

    # return the dictinoary mapping modulePaths to loaded module objects
    return modules

def create_instance(
    modulePath,
    srcMgrTypeName,
    **kwargs
    ):
    """
    string modulePath       the path to a python module (one .py file or a
                              package directory that contains an __init__.py
                              file.  This path may contain environment
                              variables
    string srcMgrTypeN me   the name of the python class that inherits
                              from SourceManager and implements a
                              specific source manager
    **kwargs                keyworded argument list providing arguments to
                              the type's constructor
    """

    # use load_modules utility function to get dictionary mapping 
    #   modulePath to a loaded module 
    # get the loadedModule value from the modulePath key
    py_mod = load_modules([modulePath])[modulePath]

    # get the type specified by the srcMgrTypeName from the loaded module
    if not hasattr(py_mod, srcMgrTypeName):
        raise Exception("Type " + str(srcMgrTypeName) +
                " was not found in " + str(py_mod))
    type_ = getattr(py_mod, srcMgrTypeName)

    # call the tanstances constructor, unwrap the key word argument
    #   dictionary and pass parameters to the constructor
    instance = type_(**kwargs)

    return instance

def ToNum(strNum):
    strNum = strNum.replace(',','')
    return int(strNum)

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def send_mail(to, subject, text, _from="", files=[], cc=[], bcc=[],
        server="smtp.gmail.com",port=587,server_user=None, server_user_pass=None):
    assert type(to)==list
    assert type(files)==list
    assert type(cc)==list
    assert type(bcc)==list

    message = MIMEMultipart()
    message['From'] = _from
    message['To'] = COMMASPACE.join(to)
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = subject
    message['Cc'] = COMMASPACE.join(cc)
    
    html = "<html><body><pre>" + text + "</html></body></pre>"
    message.attach(MIMEText(html,'html'))
    
    for f in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        message.attach(part)
    
    addresses = []
    for x in to:
        addresses.append(x)
    for x in cc:
        addresses.append(x)
    for x in bcc:
        addresses.append(x)

    smtp =  smtplib.SMTP(server,port) 
    if server_user is not None:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(server_user, server_user_pass)

    smtp.sendmail(_from, addresses, message.as_string())
    smtp.close()


import time
def get_file_date_string(filename):
    return time.strftime("%Y_%m_%d-%H_%M_%S",
            time.gmtime(os.path.getmtime(filename)))

import string
VALID_CHARS = "-_.%s%s" % (string.ascii_letters, string.digits) 
def clean_string(s):

#       Just remove chars
#        s = ''.join(c for c in s if c in valid_chars)
    s2 = []
    for c in s:
        if c in VALID_CHARS:
            s2.append(c)
        else:
            s2.append('_')
    return ''.join(s2)
    


from subprocess import Popen
from subprocess import PIPE
def try_get_recent_changes():
    try:
        codedir = os.path.dirname(__file__)
        gitcmd = "$(which git) log --pretty=format:'%cr:  %s' --abbrev-commit --date=short --branches -n 10"
        # with author name, but really who else will work on this project?
        # gitcmd = "$(which git) log --pretty=format:'%cr:  %s <%an>%Creset' --abbrev-commit --date=short --branches -n 10"
        cmd = "cd " + codedir + " && " + gitcmd
        botlog.debug("Running: " + cmd)
        
        output = Popen(cmd, stdout=PIPE, shell=True).communicate()[0]

        return "Recent source code changes: \n" + output

    except Exception, e:
        botlog.exception(e)
        botlog.warn("Could not git changes")

        return "Could not get recent source code changes"
