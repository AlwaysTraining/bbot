#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import re
import botlog
from bbot.Utils import *
from bbot.StatsParser import StatsParser

S = SPACE_REGEX
N = NUM_REGEX


class PirateParser(StatsParser):
    def __init__(self):
        StatsParser.__init__(self)
        self.buymenu = True

    def get_patterns(self):
        return {

            '\[' + N + ' Regions left\] Your choice\?': 521
        }


    def on_match(self, app, line, which):
        realm = app.data.realm

        if which == 521: realm.pirates.regions = self.get_num(0)



