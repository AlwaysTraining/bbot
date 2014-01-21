#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Utils import *
from bbot.Strategy import Strategy

"""
[Crazy Gold Bank]
(C) Cash Relief / Loans       (L) List Investments / Loans  
(D) Deposit Funds             (V) View Bank Rates           
(W) Withdraw Funds            (0) Quit                      
(I) Investments               

You have 49,325 gold in hand and 1,066,043 gold in the bank.
Choice> Quit
"""

class Bank(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
'\[Crazy Gold Bank\]' : 10,
'You have '+NUM_REGEX+' gold in hand and '+NUM_REGEX+' gold in the bank.' : 20
}


    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass
        elif lastState == 10 and state == 20:

            self.app.data.set("Current Gold on Hand", self.app.get_num(0))
            self.app.data.set("Current Gold in Bank", self.app.get_num(1))
            self.app.sendl()

        else:
            return Strategy.UNHANDLED


