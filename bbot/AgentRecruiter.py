#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.MainStrategy import MainStrategy
from bbot.SpendingParser import SpendingParser
from bbot.Data import *
from bbot.RegionBuy import RegionBuy

S = SPACE_REGEX
N = NUM_REGEX


def get_region_ratio(app, context):
    r = Regions()
    r.coastal.number = 50
    r.river.number = 0
    r.agricultural.number = None
    r.desert.number = 0
    r.industrial.number = 1
    r.urban.number = 0
    r.mountain.number = 0
    r.technology.number = 1

    return r


class AgentRecruiter(MainStrategy):
    def __init__(self, app):
        MainStrategy.__init__(self, app)
        self.app.metadata.get_region_ratio_func = get_region_ratio

    def on_industry_menu(self):

        if "Specialized" not in self.app.buf:
            self.do_specialize = True

        if self.data.realm.regions.industrial.zonemanufacturing.turrets.allocation == 100:
            return

        # set to 100% turret production
        self.app.send_seq(['y', '\r', '\r', '>\r', '\r', '\r', '\r'])

    def get_specialize_seq(self):
        return ['*', 3, 3, 0]

    def get_buy_unit_types(self):
        return ['Agents']


