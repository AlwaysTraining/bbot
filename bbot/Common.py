#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Strategy import Strategy

class Common(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
                'Do you want ANSI Graphics' :   1,
                'Name your Realm'   : 2
                }

    def on_indicator(self, state):
        if self.lastState is None and state == 1:

            self.app.send('n')

        elif self.lastState == 1 and state == 2:

            self.app.sendl(self.app.get_app_value('realm'))
            self.app.telnet.interact()


