#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import re
from bbot.Utils import *


class StatsParser(object):
    def __init__(self, get_patterns_method=None):
        self.regexs = None
        self.match = None
        self.get_patterns_method = get_patterns_method

    def get_patterns(self):
        return {}

    def get_regexs(self):

        if self.regexs is None:
            self.regexs = {}

            # User can derive the class, or make use of the accessor method
            if self.get_patterns_method is not None:
                patterns = self.get_patterns_method()
            else:
                patterns = self.get_patterns()
            for pattern, rid in patterns.items():
                self.regexs[rid] = re.compile(pattern)
        return self.regexs

    def get_match(self, line):

        regexs = self.get_regexs()
        for rid, regex in regexs.items():
            m = regex.match(line)
            if m is not None:
                self.match = m
                return rid

    def get_num(self, matchIndex=0):
        n = ToNum(self.match.groups()[matchIndex])
        return n

    def get_str(self, matchIndex=0):
        """
        Get a number from the current matchign regex group
        """
        return self.match.groups()[matchIndex]

    def parse(self, app, buf):
        lines = buf.splitlines()
        for line in lines:
            # botlog.debug("Matching -->" + line + "<--")
            which = self.get_match(line)
            self.on_match(app, line, which)

    def on_match(self, app, line, which):
        pass


