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


class PreTurnsParser(StatsParser):
    def __init__(self):
        StatsParser.__init__(self)
        self.buymenu = True

    def get_patterns(self):
        return {
            'Troopers' + S + ':' + S + N + '\%' + S + '\(' + N + ' per year\)': 1310,
            'Jets' + S + ':' + S + N + '\%' + S + '\(' + N + ' per year\)': 1320,
            'Turrets' + S + ':' + S + N + '\%' + S + '\(' + N + ' per year\)': 1330,
            'Bombers' + S + ':' + S + N + '\%' + S + '\(' + N + ' per year\)': 1340,
            'Tanks' + S + ':' + S + N + '\%' + S + '\(' + N + ' per year\)': 1350,
            'Carriers' + S + ':' + S + N + '\%' + S + '\(' + N + ' per year\)': 1360,
        }


    def on_match(self, app, line, which):
        realm = app.data.realm
        regions = realm.regions
        manufacture = regions.industrial.zonemanufacturing

        if which == 1310:
            manufacture.troopers.allocation = self.get_num(0)
            manufacture.troopers.production = self.get_num(1)
        elif which == 1320:
            manufacture.jets.allocation = self.get_num(0)
            manufacture.jets.production = self.get_num(1)
        elif which == 1330:
            manufacture.turrets.allocation = self.get_num(0)
            manufacture.turrets.production = self.get_num(1)
        elif which == 1340:
            manufacture.bombers.allocation = self.get_num(0)
            manufacture.bombers.production = self.get_num(1)
        elif which == 1350:
            manufacture.tanks.allocation = self.get_num(0)
            manufacture.tanks.production = self.get_num(1)
        elif which == 1360:
            manufacture.carriers.allocation = self.get_num(0)
            manufacture.carriers.production = self.get_num(1)



