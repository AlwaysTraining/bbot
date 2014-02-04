#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import re
# import botlog
from bbot.Utils import *
S = SPACE_REGEX
N = NUM_REGEX

class State(object):
    def transition(self,app,buf):
        pass
    def get_name(self):
        return self.__class__.__name__

class BailOut(State):
    pass

class StatsState(State):
    def __init__(self):
        State.__init__(self)
        self.regexs = None
        self.match = None
    
    def get_patterns(self):
        return {}

    def get_regexs(self):
    
        if self.regexs is None:
            self.regexs={}
            patterns = self.get_patterns()
            for pattern,rid in patterns.items():
                self.regexs[rid]=re.compile(pattern)
        return self.regexs

    def get_match(self,line):
        
        regexs = self.get_regexs()
        for rid,regex in regexs.items():
            m = regex.match(line)
            if m is not None:
                self.match = m
                return rid

    def get_num(self, matchIndex=0):
        n = ToNum(self.match.groups()[matchIndex])
        return n
        
    def get_str(self,matchIndex=0):
        """
        Get a number from the current matchign regex group
        """
        return self.match.groups()[matchIndex]
    
            

