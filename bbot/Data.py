#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import logging

class Data(dict):

    def set(self, key, value):
        logging.debug("recording " + str(key) + " = " + str(value))
        self[key] = value



