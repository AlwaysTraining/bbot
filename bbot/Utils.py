#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import imp
import os, sys
import botlog
from datetime import datetime

bbot_TOOL_VERSION = "0.1"
ENVIRON_PREFIX = "bbot_"

NUM_REGEX = '([0-9][,0-9]*)'
SPACE_REGEX = '[ \t]+'
STR_REGEX = '(.+)'

VERYHIGH_PRIORITY = 100 * 6
HIGH_PRIORITY = 100 * 5
MED_PRIORITY = 100 * 4
LOW_PRIORITY = 100 * 3
VERYLOW_PRIORITY = 100 * 2
NO_PRIORITY = 100 * 1

TWOBIL = 2000000000
HUNMIL = 100000000

END_OF_DAY_TURNS = 3


def load_modules(
        modulePaths  # list of paths to python modules
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
        mod_name, file_ext = os.path.splitext(os.path.split(modulePath)[-1])

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

    # botlog.debug(dir(py_mod))

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
    strNum = str(strNum)
    strNum = strNum.replace(',', '')
    strNum = strNum.replace('k', '000')
    strNum = strNum.replace('m', '000000')
    return int(strNum)


import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders


def send_mail(to, subject, text, _from="", files=[], cc=[], bcc=[],
              server="smtp.gmail.com", port=587, server_user=None,
              server_user_pass=None,preformatted=True):
    assert type(to) == list
    assert type(files) == list
    assert type(cc) == list
    assert type(bcc) == list

    message = MIMEMultipart()
    message['From'] = _from
    message['To'] = COMMASPACE.join(to)
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = subject
    message['Cc'] = COMMASPACE.join(cc)

    if preformatted:
        text = "<html><body><pre>" + text + "</html></body></pre>"

    message.attach(MIMEText(text, 'html'))

    for f in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(f))
        message.attach(part)

    addresses = []
    for x in to:
        addresses.append(x)
    for x in cc:
        addresses.append(x)
    for x in bcc:
        addresses.append(x)

    smtp = smtplib.SMTP(server, port)
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

        return output

    except Exception, e:
        botlog.exception(e)
        botlog.warn("Could not git changes")

        return "Could not get recent source code changes"

def _basenum(num,factor):
    fnum = float(num)
    fnum /= factor
    rnum = round(fnum,1)

    if (abs(rnum - fnum) < 0.1):
        rnum = int(rnum)

    return str(rnum)



def readable_num(num):
    if num == 0:
        return "0"
    num = float(num)
    if num > 1000000000:
        s = _basenum(num, 1000000000) + "b"
    elif num > 1000000:
        s = _basenum(num, 1000000) + "m"
    elif num > 1000:
        s = _basenum(num, 1000) + "k"
    else:
        s = _basenum(num,1)

    return s


def split_list(terms, bins):
    numcreds = bins
    termsPerCred = len(terms) / (numcreds)
    if termsPerCred * numcreds < len(terms):
        termsPerCred = termsPerCred + 1
    splitterms = [terms[x:x + termsPerCred] for x in
                  xrange(0, len(terms), termsPerCred)]
    return splitterms

def make_string_list(items):

    if items is None:
        raise Exception("No items provided")

    if isinstance(items, basestring):
        if ',' in items:
            items = [x.strip() for x in items.split(',')]
        else:
            items = [items]
    else:
        # case for one number as a list
        items = [items]

    return items

#coppied and pasted time functionality to bbot s WebData, maintain in both
# places

TIME_FORMAT_STR = "%a %b %d %H:%M:%S %Y"


def string_to_date(s):
    return datetime.strptime(s, TIME_FORMAT_STR)


def date_to_string(d):
    return d.strftime(TIME_FORMAT_STR)


def is_date(s):
    if s is None:
        return False

    try:
        string_to_date(s)
        return True
    except:
        return False


def string_to_bool(s):
    ls = s.lower()
    if ls == 'true':
        return True
    if ls == 'false':
        return False

    raise Exception("String is not a bool: " + str(s))
