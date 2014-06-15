#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.Data import *

S = SPACE_REGEX
N = NUM_REGEX




class Diplomat(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data

    def on_main_menu(self):

        for key in self.app.options:
            if not key.startswith(self.get_name()):
                continue
            option = key[len(self.get_name())+1:]

            if not option.starts_with('msg'):
                continue

            if not self.app.has_app_value(key):
                continue




