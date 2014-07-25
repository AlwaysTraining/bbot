#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.SpendingParser import SpendingParser
from bbot.Data import *
from bbot.RegionBuy import RegionBuy
from bbot.SpendingParser import SpendingParser
from bbot.Data import *

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


class AgentRecruiter(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.app.metadata.get_region_ratio_func = get_region_ratio
        self.sp = SpendingParser()
        self.do_specialize = False


    def on_industry_menu(self):

        if "Specialized" not in self.app.buf:
            self.do_specialize = True

        if self.data.realm.regions.industrial.zonemanufacturing.turrets.allocation == 100:
            return

        # set to 100% turret production
        self.app.send_seq(['y', '\r', '\r', '>\r', '\r', '\r', '\r'])


    def on_spending_menu(self):

        # specialize if we have not yet
        if self.do_specialize:
            # TODO check that 3 is turrets
            self.app.send_seq(['*', 3, 3, 0],
                              comment="Specializing industry on turrets")
            self.do_specialize = False

        sellItems = [
                Troopers.menu_option,
                Turrets.menu_option,
                Jets.menu_option,
                Tanks.menu_option,
                Bombers.menu_option,
                Carriers.menu_option
            ]

        botlog.info("Selling " + str(round(sell_ratio * 100, 1)) +
                    "% of " + str(sellItems))

        self.sell(sellItems, sell_ratio)
        self.sp.parse(self.app, self.app.read())

        ratio = self.get_army_buy_ratio()
        if ratio == 0:
            botlog.info("Not spending any money today, probably in protection")

        else:
            self.buy_army_units([Agents.menu_option],buyratio=ratio)


        # enter region buying menu
        RegionBuy(self.app, enter_region_menu=True)


        # we should still be at buy menu

