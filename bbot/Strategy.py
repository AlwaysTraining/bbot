#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import Constants
import os
import botlog

UNHANDLED="bbot_UNHANDLED"
TERMINATE="bbot_TERMINATE"

class Strategy:

    UNHANDLED="bbot_UNHANDLED"
    TERMINATE="bbot_TERMINATE"


    def __init__(self, app):
        self.app = app
        self.lastState = None
        
    def get_indicators(self):
        return {}


    def base_on_indicator(self, state):
        botlog.debug(self.get_name() + " handling state " + str(state) + 
                ', lastState ' + str(self.lastState))
        s = self.on_indicator(self.lastState, state)
        if s != UNHANDLED:
            self.lastState = state
        else:
            botlog.debug(self.get_name() + " state " + str(state) + " was unhandled")

        return s
        

    def on_indicator(self, lastState, state):
        return UNHANDLED

    def get_name(self):
        return self.__class__.__name__

