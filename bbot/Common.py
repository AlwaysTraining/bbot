#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import Constants
import os
import Strategy

class Common(Strategy.Strategy):

    def __init__(self, app):
        Strategy.Strategy.__init__(self, app)

    def get_indicators(self):
        return {
                'Do you want ANSI Graphics' :   1,
                'Name your Realm'   : 2
                }

    def on_indicator(self, state):
        if self.lastState is None and state == 1:

            self.app.send('n')

        elif self.lastState == 1 and state == 2:

            self.app.sendl('Randyland')
            self.app.telnet.interact()


