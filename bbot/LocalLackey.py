#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.Data import *
from bbot.TreatyParser import TreatyParser
from bbot.SpendingParser import SpendingParser
from bbot.LackeyBase import LackeyBase
from math import ceil
from math import floor

class LocalLackey(LackeyBase):
    def __init__(self, app):
        LackeyBase.__init__(self, app)

        self.pp = TreatyParser()
        self.can_send_trade = True

        # get the destination realm from the application
        self.masterName = self.get_strategy_option("master")

    def get_master_name(self):
        return self.masterName

    def on_diplomacy_menu(self):
        self.app.send(9, comment="viewing the local diplomacy list")
        buf = self.app.read()

        # parse the diplomacy information
        self.pp.parse(self.app, buf)

        self.app.sendl(comment="leaving paused view of diplomacy list")
        buf = self.app.read()

        masterRealm = self.app.data.get_realm_by_name(self.masterName)

        if masterRealm is None:
            raise Exception("Could not locate master realm: " + self.masterName)

        if masterRealm.treaty == "None":
            self.app.send(2, comment="Send a protective trade agreement")
            buf = self.app.read()
            self.app.sendl(masterRealm.menu_option,
                           comment="send trade agreement to master realm")
            buf = self.app.read()
            self.app.send('N',
                          comment="not attaching message to treaty request")
            buf = self.app.read()
            self.can_send_trade = False
            self.not_trading_reason += ("we sent relations request with no " +
                                        "response yet, ")

            # we are still in diplomacy menu at this point

    def on_spending_menu(self):
        # buy carriers if needed
        LackeyBase.on_spending_menu(self)

        # we will just send the trade deal from the system menu during the
        # spending menu, this saves helps because we make trading a high
        # priority so region buying comes afterwards
        self.system_trading_menu()



    def system_trading_menu(self):

        # early in the game, we don't trade
        tradeRatio = self.get_trade_ratio()
        if not self.check_can_trade(tradeRatio):
            botlog.info(
                "Not trading this turn because: " + self.not_trading_reason)
            return

        self.app.send('*', comment="Entering System menu")
        self.app.read()
        self.app.send('t', comment="Entering trading menu")
        self.app.read()

        self.app.send(1, comment="trade with another local empire")
        buf = self.app.read()
        # we already read list of realms atbeginning of the
        # day in scores and diplomacy mwnu

        masterRealm = self.app.data.get_realm_by_name(self.masterName)

        if masterRealm is None:
            raise Exception("Could not locate master realm: " + self.masterName)

        self.app.send(masterRealm.menu_option,
                      comment="trade with master realm")
        buf = self.app.read()

        if "You do not have relations with that realm." in buf:
            botlog.warn("Could not trade with master realm")
            self.can_send_trade = False
            self.not_trading_reason = (self.get_master_name() +
                                       " has not yet accepted treaty")
        else:
            traded = self.fill_trade_deal(tradeRatio)
            if traded:
                self.can_send_trade = False
                self.not_trading_reason = "Already sent trade deal today, "

            buf = self.app.read()

        self.app.send_seq([0, 0], comment="Exit from trading menu to buy menu")

        # we are now back at the spending menu, parse it
        SpendingParser().parse(self.app, self.app.read())





