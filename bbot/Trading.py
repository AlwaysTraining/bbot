#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Utils import *
from bbot.Strategy import Strategy

"""
[Trading]
(1) Trading         
(2) Trading Market  
(V) Visit Bank      
(0) Quit            

Choice> 
"""

class Trading(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
'\[Trading\]' : 10,
'\(2\) Trading Market' : 20
}


    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass
        elif lastState == 10 and state == 20:
            self.app.sendl()
        else:
            return Strategy.UNHANDLED


