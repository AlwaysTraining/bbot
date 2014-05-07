#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import re
import botlog
from bbot.Utils import *
from bbot.Data import *
from bbot.StatsParser import StatsParser

S = STR_REGEX
N = NUM_REGEX
W = SPACE_REGEX


class WarParser(StatsParser):
    def __init__(self):
        StatsParser.__init__(self)

    def get_patterns(self):
        return {
            # note if someone puts five spaces in thier realm name, it will break this
            "\[([A-Z])\]  " + S + "     " + S: 5532
        }


    def on_match(self, app, line, which):

        if which == 5532:
            pass



