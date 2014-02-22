#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.Data import *
from bbot.TreatyParser import TreatyParser

S = SPACE_REGEX
N = NUM_REGEX


class LocalLackey(Strategy):
    def __init__(self,app):
        Strategy.__init__(self,app)
        self.data = self.app.data
        self.ratio = 0.5
        self.tradeItems = [1,2,3,4,6,7,8,9]
        self.pp=TreatyParser()

        # get the destination realm from the application
        self.masterName = self.get_strategy_option("master")
    def on_diplomacy_menu(self):
        self.app.send(9,comment="viewing the local diplomacy list")
        buf = self.app.read()
        
        # parse the diplomacy information
        self.pp.parse(self.app, buf)

        if '-=<Paused>=-' in buf:
            self.app.sendl(comment="leaving paused view of diplomacy list")
            buf = self.app.read()

        masterRealm = self.app.data.get_realm_by_name(self.masterName)

        if masterRealm is None:
            raise Exception("Could not locate master realm: " + self.masterName)

        if masterRealm.treaty == "None":
            self.app.send(2,comment="Send a protective trade agreement")
            buf = self.app.read()
            self.app.sendl(masterRealm.menu_option,comment="send trade agreement to master realm")
            buf = self.app.read()
            self.app.sendl('N',comment="not attaching message to treaty request")
            buf = self.app.read()

        # we are still in diplomacy menu at this point


    def on_spending_menu(self):
        army = self.app.data.realm.army

        for item in self.tradeItems:




    def on_trading_menu(self):
        self.app.send(1,comment="trade with another local empire")
        buf = self.app.read()
        # we already read list of realms atbeginning of the
        # day in scores and diplomacy mwnu

        masterRealm = self.app.data.get_realm_by_name(self.masterName)

        if masterRealm is None:
            raise Exception("Could not locate master realm: " + self.masterName)
        
        self.app.send(masterRealm.menu_option,comment="trade with master realm")

# 1k troopers
# 100 jets
# 1k turrets
# 100k gold
# 5k tanks



