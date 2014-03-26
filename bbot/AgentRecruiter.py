#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
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


    def get_buy_ratio(self):

        if not self.data.is_oop():
            return 0

        bank_full = self.data.has_full_bank()
        is_investor = self.app.has_strategy("Investor")
        inv_fill = self.data.has_full_investments()

        if not is_investor:
            if not bank_full:
                return 0.1
            else:
                return 1
        else:
            if not bank_full:
                return 0.1
            elif not inv_fill:
                return 0.2
            else:
                return 1


    def on_spending_menu(self):

        # specialize if we have not yet
        if self.do_specialize:
            # TODO check that 3 is turrets
            self.app.send_seq(['*', 3, 3, 0],
                              comment="Specializing industry on turrets")
            self.do_specialize = False

        ratio = self.get_buy_ratio()
        if ratio == 0:
            botlog.info("Not spending any money today, probably in protection")

        else:

            item = Agents.menu_option

            # determine number to buy
            price = self.data.get_price(item)
            gold = self.data.realm.gold * ratio
            ammount = int(math.floor(gold / price))

            if ammount == 0:
                botlog.info("Could not afford even 1 agent")
            else:
                # buy the items
                self.app.send_seq([item, ammount], comment="Buying " +
                                                           str(
                                                               ammount) + " agents")


        # enter region buying menu
        self.app.send('6')
        # the number of regions we can afford
        self.sp.parse(self.app, self.app.read())
        RegionBuy(self.app)


        # we should still be at buy menu

