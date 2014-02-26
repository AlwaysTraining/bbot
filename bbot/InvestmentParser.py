#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import re
import botlog
from bbot.Utils import *
from bbot.StatsParser import StatsParser

S = SPACE_REGEX
N = NUM_REGEX

class InvestmentParser(StatsParser):

    def __init__(self):
        StatsParser.__init__(self)

# Date         Investments         Loans Due

03# /07/2014   $2

    def get_patterns(self):
        return {
            N+"/"+N+"/"+N+S+"\$"+N    :   3254
            }

    
    def on_match(self,app,line,which):
        realm=app.data.realm
        bank=realm.bank
        if which == 3254:
            bank.investments.append(self.get_num(3))







