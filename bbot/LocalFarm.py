#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.Data import *
from bbot.PlanetParser import PlanetParser

S = SPACE_REGEX
N = NUM_REGEX


class LocalTrader(Strategy):
    def __init__(self,app):
        Strategy.__init__(self,app)
        self.data = self.app.data
        self.ratio = 0.02
        self.pp=PlanetParser()
        # get the destination realm from the application
        destRealmName = self.get_strategy_option("

    def on_diplomacy_menu(self):
        self.app.send(9,comment="viewing the local diplomacy list")
        buf = self.app.read()
        
        # parse the diplomacy information
        self.pp.parse(buf)

        if '-=<Paused>=-' in buf:
            app.sendl(comment="leaving paused view of diplomacy list")






    def on_trading_menu(self):
        self.app.send(1,comment="trade with another local empire")
        # read the list of realms
        self.pp.parse(self, self.app.read())



