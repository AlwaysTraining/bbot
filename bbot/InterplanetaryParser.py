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


class InterplanetaryParser(StatsParser):
    def __init__(self, score_callback_func, context):
        StatsParser.__init__(self)
        self.context = context
        self.score_callback_func = score_callback_func

    def get_patterns(self):
        return {

            # TODO get correct string
            STR_REGEX + SPACE_REGEX + NUM_REGEX : 26184

        }


    def on_match(self, app, line, which):

        if which == 26184:
            planet_name = self.get_str(0)

            planet = None
            for cur_planet in app.data.league.planets:
                if cur_planet.name == planet_name:
                    planet = cur_planet
                    break
            if planet is None:
                planet = Planet()
                planet.name = planet_name

            num = self.get_num(1)

            self.score_callback_func(self.context, planet, num)

