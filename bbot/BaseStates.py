#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

# import botlog
from bbot.Utils import *

S = SPACE_REGEX
N = NUM_REGEX
from bbot.StatsParser import StatsParser


class State(object):
    def transition(self, app, buf):
        pass

    def get_name(self):
        return self.__class__.__name__


class BailOut(State):
    pass


class StatsState(State):
    def __init__(self, statsParser=None, get_patterns_method=None):
        State.__init__(self)
        if statsParser is not None:
            self.statsParse = statsParser
            if get_patterns_method is not None:
                self.statsParse.get_patterns_method = get_patterns_method
        else:
            self.statsParse = StatsParser(
                get_patterns_method=self.get_patterns())

    def get_patterns(self):
        return {}

    def get_regexs(self):
        return self.statsParse.get_regexs()

    def get_match(self, line):
        return self.statsParse.get_match(line)

    def get_num(self, matchIndex=0):
        return self.statsParse.get_num(matchIndex)

    def get_str(self, matchIndex=0):
        return self.statsParse.get_str(matchIndex)

    def parse(self, app, buf):
        return self.statsParse.parse(app, buf)
    
            

