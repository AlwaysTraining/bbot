#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Utils import *
from bbot.Strategy import Strategy

"""
Do you wish to send a message? (y/N)

End of Turn Statistics

Your people have great faith in you as an excellent ruler!

Your dominion gained 1 million people.
91 units of food spoiled.

Do you wish to continue? (Y/n) 

"""

class EndTurn(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
'Do you wish to send a message\? \(y/N\) ' : 10,
'End of Turn Statistics' : 20,
'Your dominion gained '+NUM_REGEX+' million people\.' : 30,
'Your dominion lost '+NUM_REGEX+' million people\.' :35,
NUM_REGEX + ' units of food spoiled.' : 40,
'Do you wish to continue\? \(Y/n\)' : 50
}


    def on_indicator(self, lastState, state):
            
        if state == 10:
            self.app.send('n')
        elif state == 20:
            pass
        elif lastState == 20 and state == 30:
            self.app.data.set("Turn Population Gain", self.app.get_num(0))
        elif lastState == 20 and state == 35:
            self.app.data.set("Turn Population Gain", -self.app.get_num(0))
        elif (lastState == 30 or lastState == 35) and state == 40:
            self.app.data.set("Turn Food Spoilage", self.app.get_num(0))
        elif state == 50:
            self.app.sendl()
        else:
            return Strategy.UNHANDLED


