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

class IndMtn(Strategy):

    ind_to_mtn_and_tech_ratio = 5

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
            '\[Spending Menu\]' : 10,
            'You have '+NUM_REGEX+' gold and '+NUM_REGEX+' turns.' : 20,
            "\(T\) Technology[ \t]+"+NUM_REGEX      :   30,
            "Buy how many Industrial regions\?"     :   40,
            "Buy how many Mountain regions\?"       :   50,
            "Buy how many Technology regions\?"     :   60,
            }

    def get_priority(self,state):
        return MED_PRIORITY

    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass
        elif lastState == 10 and state == 20:
            self.app.send('6')
        elif lastState == 20 and state == 30:
            self.app.send('t')
        elif lastState == 30 and state == 60:
            self.a = self.app.data.realm.regions.number_affordable
            # 5:1:1 is 5+1+1 = 7 is 5/7,1/7,1/7
            self.t = int(a/7)
            self.app.sendl(str(t))
            self.app.send('m')
        elif lastState == 60 and state == 50:
            self.app.sendl(str(t))
            self.app.send('i')
        elif lastState == 50 and state == 40:
            self.app.sendl('>')
            self.app.sendl()

        else:
            return Strategy.UNHANDLED


