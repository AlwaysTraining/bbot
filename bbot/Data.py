#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import botlog

class Data(dict):

    def set(self, key, value):
        botlog.debug("recording " + str(key) + " = " + str(value))
        self[key] = value



