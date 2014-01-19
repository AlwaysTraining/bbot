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
                  help="Your BBS username.", 
                  default='Randy32')
parser.add_option("-p", "--password",
                  action="store", type="string", dest="password",
                  help="Your BBS password.",
                  default=None)
parser.add_option("-a", "--address",
                  action="store", type="string", dest="url",
                  help="BBS address",
                  default='https://confluence.di2e.net/rpc/xmlrpc')
parser.add_option("-a", "--strategy", action="append", type="string",
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



