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

S = SPACE_REGEX
N = NUM_REGEX

class IndMtn(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_priority(self):
        return MED_PRIORITY

    def on_spending_menu(self):

        return Strategy.UNHANDLED

