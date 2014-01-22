#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Utils import *
from bbot.Strategy import Strategy

"""

                                                   01/22/2014  05:27:24    
  Message From: Here We Go Again...
  Message To  : B
                                        
  Interesting Realm name.....
[R] Reply, [D] Delete, [I] Ignore, or [Q] Quit>

"""

class Messages(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
                'Message From:' : 10,
                'Message To  :' : 20,
                '\[R\] Reply, \[D\] Delete, \[I\] Ignore, or \[Q\] Quit>' : 30,
                }


    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass
        elif lastState == 10 and state == 20:
            pass
        elif lastState == 20 and state == 30:
            self.app.send('i')  # ignore all messages
        else:
            return Strategy.UNHANDLED


