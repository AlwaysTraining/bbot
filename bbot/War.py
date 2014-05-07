#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.WarParser import WarParser

S = SPACE_REGEX
N = NUM_REGEX


class War(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.wp = WarParser()

    def on_interplanetary_menu(self):
        # send t-ops

        # send s-ops

        # join short term GA's

        # send indie

        # create short term GA

















