#!/usr/bin/env python


# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified


import sys,os
from argparse import ArgumentParser
from bbot import App
import getpass
import pprint

import signal

app=None
def signal_handler(signal, frame):
    code = 1
    try:
        if app is not None:
            if 'smtp_password' in app.options or 'bbot_smtp_password' in os.environ:
                app.send_notification(KeyboardInterrupt('ctrl-c triggered an interrupt'))
            else:
                print >> sys.stderr, "Not sending notification emails because smtp_password is not set"

    except Exception as e:
        print >> sys.stderr, "Failed when sending email upon interupt: ", str(e)
        code = len(str(e)) + 2

    sys.exit(code)
       

    

signal.signal(signal.SIGINT, signal_handler)

parser = ArgumentParser(usage="Wikicnt Command Line App")
parser.add_argument("-u", "--username",
                  action="store", 
                  help="Your BBS username.", 
                  default='Randy32')
parser.add_argument("-p", "--password",
                  action="store", 
                  help="Your BBS password.",
                  default='RANDYPAS')
parser.add_argument("-a", "--address",
                  action="store", 
                  help="BBS address",
                  default='shenks.synchro.net')
parser.add_argument("-r", "--realm",
                  action="store", 
                  help="name of realm",
                  default='Randyland')
parser.add_argument("-g", "--game",
                  action="store", 
                  help="menu number for the game",
                  default='10')
parser.add_argument("--smtp-server",
                  action="store", 
                  default='smtp.gmail.com',
                  help="Outgoing Mail Server address ")
parser.add_argument("--smtp-port",
                  action="store", 
                  default=587,
                  help="Outgoing Mail Server port")
parser.add_argument("--smtp-user",
                  action="store", 
                  help="Outgoing Mail Server user name",
                  default="derrick.karimi")
parser.add_argument("--smtp-password",
                  action="store", 
                  help="Outgoing Mail Server user password")
parser.add_argument("-n","--notify",
                  nargs="?",
                  help="email addresses for recipiants of notifications",
                  default=["derrick.karimi@gmail.com"])
parser.add_argument("-d","--debug",
                  action="store_true",
                  help="enable debug mode",
                  default=False)



parser.add_argument("strategies", nargs='?',
                  help="list of actions to perform",
                  default=['IndMtn',]
                  )

args = parser.parse_args(sys.argv[1:])

# get all arguments in dictionary form
options = vars(args)

# build list of options set to None
noneops = [ o for o,v in options.items() if v is None]

#remove all options set to none from the options dict
for o in noneops:
    del options[o]

def query(prompt):
    return raw_input("%s: " % prompt) 

def query_secret(prompt):
    return getpass.getpass(prompt + ': ')

pprint.pprint(options)

app = App.App(options, query, query_secret)
app.run()



