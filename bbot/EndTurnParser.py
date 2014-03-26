#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import re
import botlog
from bbot.Utils import *
from bbot.StatsParser import StatsParser

S = SPACE_REGEX
N = NUM_REGEX


class EndTurnParser(StatsParser):
    def __init__(self):
        StatsParser.__init__(self)
        self.buymenu = True

    def get_patterns(self):
        return {

            'Your dominion gained ' + NUM_REGEX + ' million people\.': 1610,
            'Your dominion lost ' + NUM_REGEX + ' million people\.': 1620,
            NUM_REGEX + ' units of food spoiled\.': 1630,
            NUM_REGEX + ' units of food has been eaten by a hungry user\.': 1640

        }


    def on_match(self, app, line, which):
        realm = app.data.realm
        army = realm.army
        regions = realm.regions

        if which == 1610:
            app.data.realm.population.growth = self.get_num(0)
        elif which == 1620:
            app.data.realm.population.growth = -self.get_num(0)
        elif which == 1630:
            app.data.realm.food.spoilage = self.get_num(0)
        elif which == 1640:
            app.data.realm.food.randomly_eaten = self.get_num(0)

