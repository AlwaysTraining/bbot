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
from bbot.OtherPlanetParser import OtherPlanetParser
from math import ceil
from math import floor

class Lackey(LackyBase):
    def __init__(self, app):
        LackeyBase.__init__(self, app)

        self.pp = TreatyParser()
        self.can_send_trade = True
        # get the destination realm from the application
        self.masterPlanet = self.get_strategy_option("master_planet")
        self.masterRealm = self.get_strategy_option("master_realm")

    def on_spending_menu(self):
        # buy carriers if needed
        LackeyBase.on_spending_menu()

        # we will just send the trade deal from the system menu during the
        # spending menu, this saves helps because we make trading a high
        # priority so region buying comes afterwards
        self.system_trading_menu()


    def on_interplanetary_menu(self):

        # early in the game, we don't trade
        tradeRatio = self.get_trade_ratio()
        if not self.check_can_trade(tradeRatio):
            return

        self.app.send('3', comment="Sending trade deal")
        self.app.read()
        self.app.sendl(self.masterPlanet, comment="entering name of master "
                                                  "planet")

        # get and parse the list of realms on this planet
        buf = self.app.read()
        self.app.send('?', comment="Getting list of realm names")
        buf = self.app.read()
        opp = OtherPlanetParser()
        opp.parse(self.app, buf)

        master = self.app.data.get_realm_by_name(self.masterName,
                                                 realms=opp.realms)

        if master is None:
            raise Exception("Could not locate master realm: " +
                            str(self.masterName) + " on " +
                            str(self.masterPlanet))

        self.app.send(master.menu_option,
                      comment="trade with master realm")
        buf = self.app.read()

        traded = self.fill_trade_deal(tradeRatio, oneway=True)
        if traded:
            self.can_send_trade = False
            self.not_trading_reason = "Already sent trade deal today, "

            buf = self.app.read()

        # TODO we should be back
        botlog.info("Exiting Lackey, should be at IP menu")






