#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import botlog
from Data import *


def default_region_ratio(app, context):
    r = Regions()
    r.desert.number = 1
    return r


class MetaData(dict):
    def __init__(self, data):
        self.data = data
        self.get_region_ratio_func = default_region_ratio
        self.waiting_to_record_first_turn_number = None
        self.first_played_turn = None
        self.used_all_turns = False









        
        
 



