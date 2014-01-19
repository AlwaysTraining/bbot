#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import Constants
import os

UNHANDLED="bbot_UNHANDLED"

class Strategy:

    def __init__(self, app):
        self.app = app
        self.lastState = None
        
    def get_indicators(self):
        return {}


    def base_on_indicator(self, state):
        s = self.on_indicator(self.lastState, state)
        if s != UNHANDLED:
            self.lastState = state
        

    def on_indicator(self, lastState, state):
        return UNHANDLED

    def get_name(self):
        return self.__class__.__name__

