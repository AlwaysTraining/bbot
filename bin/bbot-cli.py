#!/usr/bin/env python


# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified
import logging
logging.basicConfig(
        level=logging.DEBUG,format='%(asctime)s:%(levelname)s:%(message)s')

# logging.getLogger('suds.client').setLevel(logging.CRITICAL)


import sys
from argparse import ArgumentParser
from bbot import App
import getpass

parser = ArgumentParser(usage="Wikicnt Command Line App")
parser.add_argument("-u", "--username",
                  action="store", 
                  help="Your BBS username.", 
                  default='Randy32')
parser.add_argument("-p", "--password",
                  action="store", 
                  help="Your BBS password.",
                  )
parser.add_argument("-a", "--address",
                  action="store", 
                  help="BBS address",
                  default='shenks.synchro.net')
parser.add_argument("-r", "--realm",
                  action="store", 
                  help="name of realm",
                  default='shenks.synchro.net')
parser.add_argument("strategies", nargs='+',
                  help="list of actions to perform")

args = parser.parse_args(sys.argv[1:])

# get all arguments in dictionary form
options = vars(args)

# build list of options set to None
noneops = [ o for o,v in options.items() if v is None]

#remove all options set to none from the options dict
for o in noneops:
    del options[o]

logging.debug("opts from args: " + str(options))


def query(prompt):
    return raw_input("%s: " % prompt) 

def query_secret(prompt):
    return getpass.getpass(prompt + ': ')

app = App.App(options, query, query_secret)
app.run()



