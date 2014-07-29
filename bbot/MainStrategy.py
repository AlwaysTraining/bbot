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
    return app.metadata.default_region_ratio(app, context)


class MainStrategy(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.app.metadata.get_region_ratio_func = get_region_ratio
        self.app.metadata.get_region_ratio_context = self
        self.sp = SpendingParser()
        self.do_specialize = False
        self.protection_sell_ratio = self.app.get_app_value(
            "protection_sell_ratio")
        self.investing_sell_ratio = self.app.get_app_value(
            "investing_sell_ratio")
        self.normal_sell_ratio = self.app.get_app_value(
            "normal_sell_ratio")

        self.protection_buy_ratio = self.app.get_app_value(
            "protection_buy_ratio")
        self.investing_buy_ratio = self.app.get_app_value(
            "investing_buy_ratio")
        self.normal_buy_ratio = self.app.get_app_value(
            "normal_buy_ratio")
        self.visited_sell_menu = False

        if self.normal_sell_ratio * self.normal_buy_ratio != 0:
            botlog.warn("buy ratio of " + str(self.normal_buy_ratio) +
                        " and sell ratio of " + str(self.normal_sell_ratio) +
                        " are self conflicting")

    def get_priority(self):
        return MED_PRIORITY



    def get_army_sell_ratio(self):

        # from the beginning of the game to the first
        # total day out of protection, we will always
        #   sell 100% of regions
        if not self.data.is_oop():
            return self.protection_sell_ratio

        if (self.app.has_strategy("Investor") and
                    (
                            self.data.realm.bank.investments) > 0 and  # TODO a better way to learn if investments are unparsed, or try to garantee that they are parsed before calling this funciton
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
        # industry
        return self.normal_buy_ratio


    def sell(self, sellItems, sellRatio):

        if isinstance(sellItems, basestring):
            sellItems = make_string_list(sellItems)

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
                    self.app.metadata.max_ammount = -1
                    self.sp.parse(self.app, self.app.read())
                    if self.app.metadata.max_ammount == -1:
                        raise Exception("Unable to read max sale amount")

                    botlog.info("Max sale amount is " +
                                str(self.app.metadata.max_ammount) +
                                " desired sale ammount is " +
                                str(ammount) + ", t1 is " +
                                str(type(self.app.metadata.max_ammount)) +
                                " and t2 is " + str(type(ammount)) +
                                ", too much? " +
                                str(self.app.metadata.max_ammount <
                                    ammount))

                    # if max ammoutn for sale is less than what we are selling
                    if self.app.metadata.max_ammount < ammount:
                        # cap off how much we are selling
                        ammount = self.app.metadata.max_ammount

                    # send the number we are selling
                    self.app.sendl(ammount, comment="Selling this many")
                    self.sp.parse(self.app, self.app.read())

            else:
                raise Exception("Do not know how to drop regions yet")

        # return to buy menu
        if not in_buy:
            self.app.send('b')
            self.sp.parse(self.app, self.app.read())


    def get_specialize_sequence(self):
        return None

    def get_sell_unit_types(self):
        if self.app.has_app_value("sell_unit_types"):
            return make_string_list(
                self.app.get_app_value("sell_unit_types"))
        return None

    def get_buy_unit_types(self):
        if self.app.has_app_value("buy_unit_types"):
            return make_string_list(
                self.app.get_app_value("buy_unit_types"))
        return None

    def on_spending_menu(self):

        # specialize if we have not hyet
        if self.do_specialize:
            seq = self.get_specialize_sequence()
            if seq  is not None:
                self.app.send_seq(seq,
                              comment="Specializing industry on tanks")
                buf = self.app.read()
                self.sp.parse(buf)
            self.do_specialize = False

        # Sell items

        sell_ratio = self.get_army_sell_ratio()

        sellunits = self.get_sell_unit_types()
        sellItems = []

        for s in sellunits:
            mnuopt = self.app.data.get_menu_option(s)
            if mnuopt is not None:
                sellItems.append(mnuopt)
            else:
                botlog.warn("could not find menu option for unit: " + str(s))

        # in protection sell everything, otherwise just tanks

        if sellItems is None and len(sellItems) > 0:
            botlog.info("Selling " + str(round(sell_ratio * 100, 1)) +
                        "% of " + str(sellItems))

            self.sell(sellItems, sell_ratio)
            self.sp.parse(self.app, self.app.read())

        # buy tanks
        buy_ratio = self.get_army_buy_ratio()
        buy_items = self.get_buy_unit_types()
        if (buy_ratio > 0 and self.data.realm.gold > 0 and
            buy_items is not None and len(buy_items) > 0):
            self.buy_army_units(buy_items, buy_ratio)

        # enter region buying menu
        RegionBuy(self.app, enter_region_menu=True)

        # we should still be at buy menu

