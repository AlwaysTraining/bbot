#!/usr/bin/env python


"""

Do you wish to visit the Bank? (y/N)

Your Armed Forces Require 10 gold.
How much will you give? (10; 10)


4565 gold is required to maintain your regions.

4496 gold is requested to boost popular support.
How much will you give? (4496; 6744)

The Queen Royale requires 3197 gold for Taxes.

Your People Need 151 units of food

"""
import os
from bbot.Utils import *
from bbot.Strategy import Strategy


class Maintenance(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    
    def get_indicators(self):
        return {
            'Do you wish to visit the Bank\? \(y/N\)'  :   5,
            'Your Armed Forces Require '+NUM_REGEX+' gold\.'  :   10,
            NUM_REGEX + ' gold is required to maintain your regions\.'   :   20,
            'The Queen Royale requires '+NUM_REGEX+' gold for Taxes\.' : 30,
            'Your People Need '+NUM_REGEX+' units of food'    :   40,
            'Your Armed Forces Require '+NUM_REGEX+' units of food'   :   50,
            NUM_REGEX + ' gold is requested to boost popular support\.' :   60,
        }


    def on_indicator(self, lastState, state):
        if state == 5:
            self.app.sendl()
        elif state == 10:
            self.app.sendl()
        elif state == 20:
            self.app.sendl()
        elif state == 30:
            self.app.sendl()
        elif state == 40:
            self.app.sendl()
        elif state == 50:
            self.app.sendl()
        elif state == 60:
            self.app.sendl()



        else:
            return Strategy.UNHANDLED


