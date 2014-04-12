#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.Data import *
from bbot.TreatyParser import TreatyParser
from bbot.SpendingParser import SpendingParser
from math import ceil
from math import floor


class LackeyBase(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.not_trading_reason = ''
        self.tribute_ratio = self.get_strategy_option("tribute_ratio")

        if self.tribute_ratio > 1.0: self.tribute_ratio = 1.0
        if self.tribute_ratio < 0.0: self.tribute_ratio = 0.0

        # determine what to trade
        tradeItemStrings = self.get_strategy_option("trade_items")
        if isinstance(tradeItemStrings, basestring):
            if ',' in tradeItemStrings:
                tradeItemStrings = [x.strip() for x in
                                    tradeItemStrings.split(',')]
            else:
                tradeItemStrings = [tradeItemStrings]
        self.tradeItemStrings = tradeItemStrings

        self.tradeItems = []
        for tradeItemString in tradeItemStrings:
            if tradeItemString == "Food":
                raise Exception(
                    "There is a bug, we can't reliably trade food at this time, fix the problem if you care")
            self.tradeItems.append(eval(tradeItemString + ".menu_option"))

        self.not_trading_reason = ''

    def get_priority(self):
        return HIGH_PRIORITY


    def get_num_carriers_needed(self, item, ammount):
        if ammount is None or ammount == 0:
            return 0

        num_per_carrier = (self.app.data.get_num_per_carrier(
            item))
        if num_per_carrier is None:
            return 0

        needed = ceil(ammount / float(num_per_carrier))
        return needed

    def get_trade_ratio(self):

        # from the beginning of the game to the first
        #   total day out of protection, we will always
        #   sell 100% of regions
        if not self.data.is_oop():
            self.not_trading_reason += "Empire is still in protection, "
            return 0.0

        # grow fat before giving up the goods
        if self.data.realm.regions.number < 1000:
            self.not_trading_reason += "Empire has too few regions, "
            return 0.0

        # in general we will give up a quarter of all assets
        #   each turn
        return self.tribute_ratio

    def get_master_name(self):
        raise Exception("Base class must provide master name")

    def on_spending_menu(self):
        army = self.app.data.realm.army
        tradeRatio = self.get_trade_ratio()
        if tradeRatio <= 0.0 or self.can_send_trade == False:
            botlog.info(
                "We are not trading this turn: " + self.not_trading_reason)
            return

        # determine the ammount of carriers needed by the trade deal we want
        #   to send
        needed_carriers = 0
        for item in self.tradeItems:
            ammount = floor(tradeRatio * self.app.data.get_number(item))
            needed_carriers = needed_carriers + self.get_num_carriers_needed(
                item, ammount)

        # if we don't already have enough carriers for the trade deal
        if needed_carriers > army.carriers.number:

            # determine if we can afford the carriers, and if so buy them

            num_to_buy = needed_carriers - army.carriers.number
            can_afford = floor(self.app.data.realm.gold / army.carriers.price)
            if num_to_buy > can_afford:
                botlog.warn("We can not afford enough carriers to send " +
                            self.get_master_name() + " his goods")
                # TODO, should we make a partial purchase here?
                return
            else:
                self.app.send_seq([Carriers.menu_option,
                                   str(int(num_to_buy)), '\r'],
                                  comment="Buying carriers to send " + self.get_master_name() + " a trade deal")


    def check_can_trade(self, tradeRatio):
        if tradeRatio <= 0.0:
            self.can_send_trade = False

        if not self.can_send_trade:
            botlog.info(
                "Not trading this turn because: " + self.not_trading_reason)

        return self.can_send_trade

    def fill_trade_deal(self, tradeRatio, oneway=False):
        seq = []
        trademap = {}
        for index in xrange(len(self.tradeItems)):
            item = self.tradeItems[index]

            ammount = self.app.data.get_number(item)
            trademap[self.tradeItemStrings[index]] = ammount
            

            if ammount == 0:
                continue
            if tradeRatio >= 1.0:
                ammount = '>'
            else:
                ammount = int(round(ammount * tradeRatio, 0))
                ammount = str(ammount)
                trademap[self.tradeItemStrings[index]] = ammount

            seq = seq + [item, ammount, '\r']
        buf = self.app.send_seq(seq, "Loading up trade deal")
        buf = self.app.read()
        if "WARNING: You do not have enough carriers." in buf:
            # our logic and math should gaurantee we bought enough carriers
            #   however, shit happens, if this becomes an issue we can deal with
            #   it.
            botlog.warn("Did not buy enough carriers")
            self.app.send_seq(["\r", "\r", 'n'],
                              comment="just quit from trade deal, not enough carriers")
            return False
        else:
            if not oneway:
                self.app.send_seq(["\r", "\r", 'y', 2, "\r"],
                                  comment="Send the deal out")
            else:
                # TODO double check this sequence for IP Trading
                self.app.send_seq(["\r", 'y'],
                                  comment="Send the deal out")

            msg = ("Traded " + str(int(round(tradeRatio * 100,0))) + 
                    "% of assets to " + self.get_master_name() + " with " +
                    str(self.app.data.realm.turns.remaining) +
                   " turns remaining:\n")
            for itemName,itemAmmount in trademap.items():
                msg += "\t" + itemName + ":\t" + readable_num(itemAmmount) +"\n"
            botlog.note(msg)




            return True
