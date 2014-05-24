#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
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


class IndMtn(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.app.metadata.get_region_ratio_func = get_region_ratio
        self.sp = SpendingParser()
        self.do_specialize = False
        self.protection_sell_ratio = self.get_strategy_option(
            "protection_sell_ratio")
        self.investing_sell_ratio = self.get_strategy_option(
            "investing_sell_ratio")
        self.normal_sell_ratio = self.get_strategy_option(
            "normal_sell_ratio")

        self.protection_buy_ratio = self.get_strategy_option(
            "protection_buy_ratio")
        self.investing_buy_ratio = self.get_strategy_option(
            "investing_buy_ratio")
        self.normal_buy_ratio = self.get_strategy_option(
            "normal_buy_ratio")
        self.visited_sell_menu = False

        if self.normal_sell_ratio * self.normal_buy_ratio != 0:
            botlog.warn("buy ratio of " + str(self.normal_buy_ratio) +
                " and sell ratio of " + str(self.normal_sell_ratio) +
                " are self conflicting")

    def get_priority(self):
        return MED_PRIORITY

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


    def get_army_sell_ratio(self):

        # from the beginning of the game to the first
        #   total day out of protection, we will always
        #   sell 100% of regions
        if not self.data.is_oop():
            return self.protection_sell_ratio

        if (self.app.has_strategy("Investor") and
            (self.data.realm.bank.investments) > 0 and  # TODO a better way to learn if investments are unparsed, or try to garantee that they are parsed before calling this funciton
            not self.data.has_full_investments(days_missing=2)):
            # if only missing one day of investments, this is normal, don't
            # sell anything, otherwise sell a chunk
            return self.investing_sell_ratio

        # in general, we will sell a small portion of our army to suppliment
        #   region growth
        return self.normal_sell_ratio

    def get_army_buy_ratio(self):

        # if we are going to try to trade, don't buy anything
        will_attempt_to_trade = False
        if self.app.has_strategy("LocalLackey"):
            lackey = self.app.get_strategy(
                    "LocalLackey")
            will_attempt_to_trade = lackey.check_can_trade(
                    lackey.get_trade_ratio())

        if self.app.has_strategy("Lackey"):
            lackey = self.app.get_strategy(
                    "Lackey")
            will_attempt_to_trade = lackey.check_can_trade(
                    lackey.get_trade_ratio())

        if will_attempt_to_trade:
            botlog.info("We may trade this round, do not buyi anything")
            return 0


        if not self.data.is_oop():
            return self.protection_buy_ratio

        if (self.app.has_strategy("Investor") and
                    (
                            self.data.realm.bank.investments) > 0 and  # TODO a better way to learn if investments are unparsed, or try to garantee that they are parsed before calling this funciton
                not self.data.has_full_investments(days_missing=2)):
            # if only missing one day of investments, this is normal, don't
            # buy anything, otherwise buy a chunk
            return self.investing_buy_ratio

        # in general, we will buy a to suppliment
        #   industry
        return self.normal_buy_ratio


    def sell(self, sellItems, sellRatio):

        # we start at the buy menu
        in_buy = True

        if self.visited_sell_menu and sellRatio <= 0:
            return

        # sell all the items specified
        for saleItem in sellItems:
            if str(saleItem) != '6':

                ammount = self.data.get_number(saleItem)

                if ammount is None:
                    botlog.warn('can not sell item, ' + 
                            'ammount has not been parsed')
                    continue

                if ammount == 0:
                    continue

                ammount = int(round(ammount * sellRatio, 0))

                if in_buy:
                    # sell all tanks and return to buy menu
                    self.app.send('s')
                    self.visited_sell_menu = True
                    # perform a read and through a spending state to parse all the data
                    self.sp.parse(self.app, self.app.read())
                    in_buy = False

                if ammount > 0:

                    # sell the item
                    self.app.send(saleItem,
                                  comment="selling item " + str(saleItem))

                    # read max ammount for sale
                    self.sp.parse(self.app, self.app.read())

                    botlog.info("Max sale amount is " +
                                str(self.app.metadata.max_sale_ammount) +
                                " desired sale ammount is " +
                                str(ammount) + ", t1 is " +
                                str(type(self.app.metadata.max_sale_ammount)) +
                                " and t2 is " + str(type(ammount)) +
                                ", too much? " +
                                str(self.app.metadata.max_sale_ammount <
                                    ammount))

                    # if max ammoutn for sale is less than what we are selling
                    if self.app.metadata.max_sale_ammount < ammount:
                        # cap off how much we are selling
                        ammount = self.app.metadata.max_sale_ammount

                    # send the number we are selling
                    self.app.sendl(ammount, comment="Selling this many")
                    self.sp.parse(self.app, self.app.read())

            else:
                raise Exception("Do not know how to drop regions yet")

        # return to buy menu
        if not in_buy:
            self.app.send('b')
            self.sp.parse(self.app, self.app.read())


    def on_spending_menu(self):

        # specialize if we have not hyet
        if self.do_specialize:
            self.app.send_seq(['*', 3, 5, 0],
                              comment="Specializing industry on tanks")
            self.do_specialize = False

        # Sell items

        sell_ratio = self.get_army_sell_ratio()

        sellItems = [
            Troopers.menu_option,
            Turrets.menu_option,
            Jets.menu_option,
            Tanks.menu_option,
            Bombers.menu_option,
            Carriers.menu_option
        ]

        # don't bother selling rinky dink pirate winnings if we arn't going
        # whole hog liquidate
        if sell_ratio < 0.5:
            sellItems = [Tanks.menu_option]

        botlog.info("Selling " + str(round(sell_ratio * 100, 1)) +
                    "% of " + str(sellItems))

        self.sell(sellItems, sell_ratio)
        self.sp.parse(self.app, self.app.read())

        # buy tanks
        buy_ratio = self.get_army_buy_ratio()
        if buy_ratio > 0:
            self.buy_army_units("Tanks", buy_ratio)

        # enter region buying menu
        RegionBuy(self.app, enter_region_menu=True)

        # we should still be at buy menu

