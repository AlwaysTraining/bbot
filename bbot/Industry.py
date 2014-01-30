#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Utils import *
from bbot.Strategy import Strategy

"""

[Industrial Production]
Troopers        :  15%       (0 per year)
Jets            :  15%       (0 per year)
Turrets         :  15%       (0 per year)
Bombers         :  15%       (0 per year)
Tanks           :  15%       (0 per year)
Carriers        :  15%       (0 per year)

Change Production? (y/N) 
"""

class Industry(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return { "\[Industrial Production\]"    :   10,
                "Change Production\? \(y/N\)"   :   20,
                }


    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass
        elif lastState == 10 and state == 20:

            self.app.sendl()

        else:
            return Strategy.UNHANDLED


