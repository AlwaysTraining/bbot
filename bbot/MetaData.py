#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import botlog
from Data import *
from bbot.Wishlist import Wishlist


def default_region_ratio(app, context):
    r = Regions()

    emergency = False

    # take care of emergency situations

    if app.metadata.low_cash:
        r.desert.number = 1
        emergency = True

    if app.metadata.low_food:
        r.agricultural.number = 1
        emergency = True

    if not emergency:
        r.desert.number = 1

    return r

class MetaData(dict):
    def __init__(self, app):
        self.data = app.data
        self.default_region_ratio_func = default_region_ratio
        self.get_region_ratio_func = default_region_ratio
        self.get_region_ratio_context = None
        self.waiting_to_record_first_turn_number = None
        self.first_played_turn = None
        self.used_all_turns = False
        self.last_ag_buy = None
        self.last_ag_buy_turn = None
        self.max_ammount = None
        self.wishlist = Wishlist(app)
        self.regions_left = None
        self.low_cash = False
        self.low_food = False







        
        
 



