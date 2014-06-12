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
            '\([ 0-9]+\) ' + S + " (Enemy|None|Peace|Allied)" : 5532
        }


    def on_match(self, app, line, which):

        league = app.data.league

        if which == 5532:
            if league is None:
                app.data.league = League()
                league = app.data.league

            planet_name = self.get_str(0).strip()
            relation = self.get_str(1).strip()

            planet = None
            for cur_planet in league.planets:
                if cur_planet.name == planet_name:
                    planet = cur_planet
                    break
            if planet is None:
                planet = Planet()
                planet.name = planet_name
                league.planets.append(planet)

            planet.relation = relation
            botlog.debug("Diplomacy parser setting " + planet_name + " to " +
                str(relation))






