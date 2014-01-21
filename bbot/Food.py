#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Utils import *
from bbot.Strategy import Strategy

"""
[Food Unlimited]
(B) Buy Food    (S) Sell Food   (V) Visit Bank  (0) Quit        

You have 49,325 gold and 1979 units of food.
Choice> Quit
"""

class Food(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
'\[Food Unlimited\]' : 10,
'You have ' + NUM_REGEX + ' gold and ' + NUM_REGEX + ' units of food.' : 20,
}


    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass
        elif lastState == 10 and state == 20:

            self.app.data.set("Current Gold on Hand", self.app.get_num(0))
            self.app.data.set("Current Food", self.app.get_num(1))
            self.app.sendl()

        else:
            return Strategy.UNHANDLED


