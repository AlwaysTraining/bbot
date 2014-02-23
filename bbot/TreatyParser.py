#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import re
import botlog
from bbot.Utils import *
from bbot.Data import *
from bbot.StatsParser import StatsParser

S = STR_REGEX
N = NUM_REGEX
W = SPACE_REGEX

class TreatyParser(StatsParser):

    def __init__(self):
        StatsParser.__init__(self)
        self.buymenu=True
        self.myrealm = None

    def get_patterns(self):
        return {
                # note if someone puts five spaces in thier realm name, it will break this
                "\[([A-Z])\]  "+S+"     "+S : 832
            }

    
    def on_match(self,app,line,which):

        if which == 832:
            menu_option = self.get_str(0)
            r = None
            for x in app.data.planet.realms:
                if x.menu_option == menu_option:
                    r = x
                    break
            if r is None: 
                r = RealmStats()
                app.data.planet.realms.append(r)

            r.name = self.get_str(1).strip()
            r.treaty = self.get_str(2).strip()



