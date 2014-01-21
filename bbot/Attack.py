#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Utils import *
from bbot.Strategy import Strategy

"""
[Attack Menu]
(R) Regular Attack     
(N) Nuclear Attack     
(C) Chemical Attack    
(B) Biological Attack  
(P) Attack Pirates     
(A) Alliance Strength  
(V) Visit Bank         
(?) Help               
(0) Quit               

Choice> 
"""

class Attack(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
'\[Attack Menu\]' : 10,
'\(A\) Alliance Strength' : 20
}


    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass
        elif lastState == 10 and state == 20:
            self.app.sendl()
        else:
            return Strategy.UNHANDLED


