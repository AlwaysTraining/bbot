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
        realm=app.data.realm
        menu_option = self.get_str(0)
        r = app.data.planet.realms.find(lambda x: x.menu_option == menu_option)
        if r is None: 
            r = RealmStats()
            app.data.planet.realms.append(r)

        r.name = self.get_str(1).strip()
        r.treaty = self.get_str(2).strip()



