#!/usr/bin/env python


# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified
# import logging

# logging.getLogger('suds.client').setLevel(logging.CRITICAL)


import sys
from optparse import OptionParser
from bbot import App
import getpass

parser = OptionParser(usage="Wikicnt Command Line App")
parser.add_option("-u", "--username",
                  action="store", type="string", dest="username",
                  help="Your Confluence username.", 
                  default=None)
parser.add_option("-p", "--password",
                  action="store", type="string", dest="password",
                  help="Your Confluence password.",
                  default=None)
parser.add_option("-l", "--url",
                  action="store", type="string", dest="url",
                  help="Optional: a confluence XMLRPC URL. Default is to confluence,di2e",
                  default='https://confluence.di2e.net/rpc/xmlrpc')
parser.add_option("-s", "--space", action="store", type="string",
                  dest="space",
                  help="name of space",
                  default=None)
parser.add_option("-t", "--title", action="store", type="string",
                  dest="title", 
                  help="title of page",
                  default=None)
parser.add_option("-a", "--action", action="store", type="string",
                  dest="action", 
                  help="action to perform []",
                  default=None)

(options, args) = parser.parse_args(sys.argv[1:])
option_dict = vars(options)


def query(prompt):
    return raw_input("%s: " % prompt) 

def query_secret(prompt):
    return getpass.getpass(prompt + ': ')

app = App.App(option_dict, query, query_secret)
app.run()



