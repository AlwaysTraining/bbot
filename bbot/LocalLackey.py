#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.Data import *
from bbot.TreatyParser import TreatyParser
from bbot.SpendingParser import SpendingParser
from math import ceil
from math import floor

S = SPACE_REGEX
N = NUM_REGEX


class LocalLackey(Strategy):
    def __init__(self,app):
        Strategy.__init__(self,app)
        self.data = self.app.data
        self.tradeItems = [1,2,3,4,6,7,8,9]
        self.pp=TreatyParser()
        self.can_send_trade = True
        # get the destination realm from the application
        self.masterName = self.get_strategy_option("master")
        self.notTradingReason=''

    def get_priority(self):
        return HIGH_PRIORITY

    def on_diplomacy_menu(self):
        self.app.send(9,comment="viewing the local diplomacy list")
        buf = self.app.read()
        
        # parse the diplomacy information
        self.pp.parse(self.app, buf)

        self.app.sendl(comment="leaving paused view of diplomacy list")
        buf = self.app.read()

        masterRealm = self.app.data.get_realm_by_name(self.masterName)

        if masterRealm is None:
            raise Exception("Could not locate master realm: " + self.masterName)

        if masterRealm.treaty == "None":
            self.app.send(2,comment="Send a protective trade agreement")
            buf = self.app.read()
            self.app.sendl(masterRealm.menu_option,
                    comment="send trade agreement to master realm")
            buf = self.app.read()
            self.app.send('N',comment="not attaching message to treaty request")
            buf = self.app.read()
            self.can_send_trade = False
            self.notTradingReason = "we sent relations request with no response yet"

        # we are still in diplomacy menu at this point

    def get_num_carriers_needed(self, item, ammount):
        if ammount is None or ammount == 0:
            return 0

        num_per_carrier=float(self.app.data.get_num_per_carrier(
                item))
        if num_per_carrier is None:
            return 0
        
        needed = ceil(ammount/num_per_carrier)
        return needed

    def get_trade_ratio(self):

        # from the beginning of the game to the first
        #   total day out of protection, we will always
        #   sell 100% of regions
        if not self.data.is_oop():
            self.notTradingReason += "Empire is still in protection,"
            return 0.0

        # grow fat before giving up the goods
        if self.data.realm.regions.number < 1000:
            self.notTradingReason += "Empire has too few regions,"
            return 0.0

        # If investments are not full, we will will focus on that
        if not self.data.has_full_investments:
            self.notTradingReason += "Empire does not have full investments,"
            return 0.0

        # in general we will give up a small portion to the master
        #   each turn
        return 0.025

    def on_spending_menu(self):
        army = self.app.data.realm.army
        tradeRatio = self.get_trade_ratio()
        if tradeRatio <= 0.0 or self.can_send_trade == False:
            botlog.info("We are not trading this turn: " + self.notTradingReason)
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
                        self.masterName + " his goods")
                return
            else:
                self.app.send_seq([Carriers.menu_option, 
                    str(int(num_to_buy)), '\r'],
                    comment="Buying carriers to send " + self.masterName + " a trade deal")

        self.system_trading_menu()



    
    def system_trading_menu(self):

        # early in the game, we don't trade
        tradeRatio = self.get_trade_ratio()
        if tradeRatio <= 0.0:
            self.can_send_trade = False

        if not self.can_send_trade:
            botlog.info("Not trading this turn because: " + self.notTradingReason)
            return

        self.app.send('*',comment="Entering System menu")
        self.app.read()
        self.app.send('t',comment="Entering trading menu")
        self.app.read()

        self.app.send(1,comment="trade with another local empire")
        buf = self.app.read()
        # we already read list of realms atbeginning of the
        # day in scores and diplomacy mwnu

        masterRealm = self.app.data.get_realm_by_name(self.masterName)

        if masterRealm is None:
            raise Exception("Could not locate master realm: " + self.masterName)
        
        self.app.send(masterRealm.menu_option,comment="trade with master realm")
        buf = self.app.read()

        if "You do not have relations with that realm." in buf:
            botlog.warn("Could not trade with master realm")
        else:
            seq=[]
            for item in self.tradeItems:
                
                ammount = self.app.data.get_number(item)

                if ammount == 0:
                    continue
                if tradeRatio >= 1.0:
                    ammount = '>'
                else:
                    ammount = int(round(ammount * tradeRatio,0))
                    ammount = str(ammount)
                
                seq = seq + [ item, ammount, '\r' ]

            buf = self.app.send_seq(seq, "Loading up trade deal")

            if "WARNING: You do not have enough carriers." in buf:
                # our logic and math should gaurantee we bought enough carriers
                #   however, shit happens, if this becomes an issue we can deal with
                #   it.
                botlog.warn("Did not buy enough carriers")

            self.app.send_seq(["\r","\r",'y',2,"\r"], comment="Send the deal out")

        self.app.send_seq([0,0],comment="Exit from trading menu to buy menu")

        # we are now back at the spending menu, parse it
        SpendingParser().parse(self.app, self.app.read())





