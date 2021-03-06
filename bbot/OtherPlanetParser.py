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


class OtherPlanetParser(StatsParser):
    def __init__(self, realms=None, planet_name=None):
        StatsParser.__init__(self)
        if realms is None:
            realms = []
        self.realms = realms
        self.planet_name = planet_name

#   (A)  Bonk                                    16,761     33k       743k

    def get_patterns(self):
        return {
            # '\(([A-Z])\)  (.+  )[ ]+([0-9,km].*) +([0-9,km].*)[ ]+(.,km+)':
            '\(([A-Z])\)  (.+) ([0-9,km]+)[ ]+([0-9,km]+)[ ]+([0-9,km]+)':
                9091
        }


    def on_match(self, app, line, which):

        if which == 9091:
            menu_option = self.get_str(0)
            r = None
            for x in self.realms:
                if x.menu_option == menu_option:
                    r = x
                    break

            if r is None:
                r = RealmStats()
                self.realms.append(r)

            r.menu_option = menu_option
            r.name = self.get_str(1).strip()
            r.regions = self.get_num(2)
            r.score = self.get_num(3)
            r.networth = self.get_num(4)
            r.planet_name = self.planet_name
