#!/usr/bin/env python


# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified


import sys, os
from argparse import ArgumentParser
from bbot import App
import getpass
import pprint

import signal

app = None


def signal_handler(signal, frame):
    code = 1
    try:
        if app is not None:
            if 'smtp_password' in app.options or 'bbot_smtp_password' in os.environ:
                app.send_notification(
                    KeyboardInterrupt('ctrl-c triggered an interrupt'))
            else:
                print >> sys.stderr, "Not sending notification emails because smtp_password is not set"

    except Exception as e:
        print >> sys.stderr, "Failed when sending email upon interupt: ", str(e)
        code = len(str(e)) + 2

    sys.exit(code)


signal.signal(signal.SIGINT, signal_handler)

defaults = {

    'tnsoa': {
        'username': 'Randy32',
        'password': 'RANDYPAS',
        'address': 'tnsoa.strangled.net',
        'realm': 'Randyland',
        'game': '6',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': 'derrick.karimi',
        'notify': 'derrick.karimi@gmail.com',
        'debug': False,
        'strategies': ['IndMtn', ],
        'data_dir': '.',
    },

    'tnsoa3': {
        'username': 'Tester0',
        'password': 'RANDYPAS',
        'address': 'tnsoa.strangled.net',
        'realm': 'Funkshak',
        'game': '6',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': 'derrick.karimi',
        'notify': 'derrick.karimi@gmail.com',
        'debug': False,
        'strategies': ['IndMtn', ],
        'data_dir': '.',
    },

    'tnsoa4': {
        'username': 'Tester1',
        'password': 'RANDYPAS',
        'address': 'tnsoa.strangled.net',
        'realm': 'Crankles',
        'game': '6',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': 'derrick.karimi',
        'notify': 'derrick.karimi@gmail.com',
        'debug': False,
        'strategies': ['IndMtn', ],
        'data_dir': '.',
    },

    'tnsoa5': {
        'username': 'Tester2',
        'password': 'RANDYPAS',
        'address': 'tnsoa.strangled.net',
        'realm': 'IlDuche',
        'game': '6',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': 'derrick.karimi',
        'notify': 'derrick.karimi@gmail.com',
        'debug': False,
        'strategies': ['IndMtn', 'AntiPirate', 'LocalLackey'],
        'LocalLackey_master': 'Funkshak',
        'LocalLackey_trade_items': ['Troopers', 'Turrets', 'Jets',
                                    'Tanks', 'Bombers', 'Agents',
                                    'Gold'],
        'LocalLackey_regions_required': 3000,
        'LocalLackey_tribute_ratio': 0.25,
        'data_dir': '.',
    },
}


def get_default(key):
    superkey = 'tnsoa5'
    ans = None
    if superkey in defaults:
        d = defaults[superkey]
        if key in d:
            ans = d[key]
    return ans


parser = ArgumentParser(usage="Wikicnt Command Line App")
parser.add_argument("-u", "--username",
                    action="store",
                    help="Your BBS username.",
                    default=get_default('username'))
parser.add_argument("-p", "--password",
                    action="store",
                    help="Your BBS password.",
                    default=get_default('password'))
parser.add_argument("-a", "--address",
                    action="store",
                    help="BBS address",
                    default=get_default('address'))
parser.add_argument("-r", "--realm",
                    action="store",
                    help="name of realm",
                    default=get_default('realm'))
parser.add_argument("-g", "--game",
                    action="store",
                    help="menu number for the game",
                    default=get_default('game'))
parser.add_argument("--smtp-server",
                    action="store",
                    default=get_default('smtp_server'),
                    help="Outgoing Mail Server address ")
parser.add_argument("--smtp-port",
                    action="store",
                    default=get_default('smtp_port'),
                    help="Outgoing Mail Server port")
parser.add_argument("--smtp-user",
                    action="store",
                    help="Outgoing Mail Server user name",
                    default=get_default("smtp_user"))
parser.add_argument("--smtp-password",
                    action="store",
                    help="Outgoing Mail Server user password",
                    default=get_default('smtp_password'))
parser.add_argument("-n", "--notify", action='append',
                    help="comma separated email addresses for recipients of "
                         "notifications")

parser.add_argument("--LocalLackey-master",
                    action="store",
                    help="Name of the realm who a LocalLackey will send trade deals to",
                    default=get_default('LocalLackey_master'))
parser.add_argument("--LocalLackey-trade-items",
                    nargs="*",
                    help="Items to include in trade deal: [ Troopers. "
                         "Turrets, Jets, Tanks, Bombers, Carriers, Agents, "
                         "Food, Gold ]",
                    default=get_default('LocalLackey_trade_items'))
parser.add_argument("--LocalLackey-regions-required",
                    action="store",
                    help="The number of regions required before sending out "
                         "trade deals",
                    default=get_default('LocalLackey_regions_required'))
parser.add_argument("--LocalLackey-tribute-ratio",
                    action="store",
                    help="The ratio of owned resources to give in tribute to "
                         "the master realm each day: [0.0 - 1.0]",
                    default=get_default('LocalLackey_tribute_ratio'))

parser.add_argument("-d", "--debug",
                    action="store_true",
                    help="enable debug mode",
                    default=get_default('debug'))

parser.add_argument("--data-dir",
                    action="store",
                    help="Set the directory used to store log files",
                    default=get_default('data_dir'))

parser.add_argument("strategies", nargs='*',
                    help="a list of strategies to govern gameplay",
                    default=get_default('strategies')
)

args = parser.parse_args(sys.argv[1:])

# get all arguments in dictionary form
options = vars(args)

# build list of options set to None
noneops = [o for o, v in options.items() if v is None]

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



