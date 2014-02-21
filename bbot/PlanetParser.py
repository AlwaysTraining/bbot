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

class PlanetParser(StatsParser):

    def __init__(self):
        StatsParser.__init__(self)
        self.buymenu=True
        self.myrealm = None

    def get_patterns(self):
        return {
            "\(([A-Z])\) "+S+W+N+W+N+W+N : 909
            }

    
    def on_match(self,app,line,which):
        realm=app.data.realm
        regions=realm.regions
        if self.myrealm is None:
            self.myrealm = app.get_app_value("realm")
        
        if which == 909 : 
            menu_option = self.get_str(0)
            r = app.data.planet.realms.find(lambda x: x.menu_option == menu_option)
            if r is None: 
                r = RealmStats()
                app.data.planet.realms.append(r)

            r.menu_option = menu_option
            r.name = self.get_str(1).strip()
            r.regions = self.get_num(2)
            r.score = self.get_num(3)
            r.networth = self.get_num(4)

            if r.name == self.myrealm:
                regions.number = r.regions
    



