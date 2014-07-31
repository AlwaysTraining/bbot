#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.MainStrategy import MainStrategy
from bbot.Data import *

S = SPACE_REGEX
N = NUM_REGEX


def get_region_ratio(app, context):
    r = Regions()
    r.coastal.number = 0
    r.river.number = 0
    r.agricultural.number = None
    r.desert.number = 0
    r.industrial.number = 0
    r.urban.number = 0
    r.mountain.number = 0
    r.technology.number = 0

    if not app.data.is_oop():
        r.mountain.number = 1
        r.industrial.number = 5
    else:
        r.mountain.number = 1
        r.technology.number = 1
        r.industrial.number = 5
    return r


class IndMtn(MainStrategy):
    def __init__(self, app):
        MainStrategy.__init__(self, app)
        self.app.metadata.get_region_ratio_func = get_region_ratio

    def on_industry_menu(self):

        if "Specialized" not in self.app.buf:
            self.do_specialize = True

        if self.data.realm.regions.industrial.zonemanufacturing.tanks.allocation == 100:
            return

        # set industries
        self.app.send('y')
        # troopers, jets, turret, bombers at 0
        for i in range(4):
            i = i
            self.app.sendl()
        # tanks at 100%
        self.app.sendl('>')
        # carreirs at 0
        self.app.sendl()


    def get_specialize_seq(self):
        return ['*', 3, 5, 0]

    def get_buy_unit_types(self):
        return ['Tanks']

    def get_sell_unit_types(self):

        if self.data.is_oop():
            sellItems = ["Tanks"]
        else:
            sellItems = [
                "Troopers",
                "Turrets",
                "Jets",
                "Tanks",
                "Bombers",
                "Carriers"
            ]
        return sellItems

