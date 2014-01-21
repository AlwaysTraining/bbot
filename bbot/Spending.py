#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Utils import *
from bbot.Strategy import Strategy

"""
[Spending Menu]
Key Item                 Price       # Owned
(*) System Menu                             
(1) Troopers              271           100 
(2) Jets                  330             0 
(3) Turrets               383             0 
(4) Bombers              3138             0 
(5) HeadQuarters         5277             0 
(6) Regions              1412            15 
(7) Covert Agents         725             0 
(8) Tanks                1735             0 
(9) Carriers             5269             0 
(S) Sell                                    
(V) Visit Bank                              
(?) Help                                    
(0) Quit                                    

You have 49,325 gold and 10 turns.
Choice> 
"""

class Spending(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
'\[Spending Menu\]' : 10,
'You have '+NUM_REGEX+' gold and '+NUM_REGEX+' turns.' : 20
}


    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass
        elif lastState == 10 and state == 20:

            self.app.data.set("Current Gold on Hand", self.app.get_num(0))
            self.app.data.set("Remaining Turns", self.app.get_num(1))
            self.app.sendl()

        else:
            return Strategy.UNHANDLED


