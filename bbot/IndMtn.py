#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.SpendingParser import SpendingParser

S = SPACE_REGEX
N = NUM_REGEX


class IndMtn(Strategy):
    def __init__(self,app):
        Strategy.__init__(self,app)

    def on_spending_menu(self):
        # sell all tanks and return to buy menu
        self.app.send('s')
        # perform a read and through a spending state to parse all the data
        sp = SpendingParser()
        sp.parse(self.app, self.app.read())

        sellItems = ['8']
        # sell all the items specified
        for saleItem in sellItems:
            if str(saleItem) != '6':
                self.app.send_seq( [ str(saleItem),'>','\r' ] )
            else:
                raise Exception("Do not know how to drop regions yet")

        # return to buy menu
        self.app.send('b')
        sp.parse(self.app, self.app.read())
        
        # enter region buying menu
        self.app.send('6')
        sp.parse(self.app, self.app.read())

        a = self.app.data.realm.regions.number_affordable
        # 5:1:1 is 5+1+1 = 7 is 5/7,1/7,1/7
        r = int(a/7)
        # Sequence for buying regions, return to buy menu
        self.app.send_seq(['t',r,'m',r,'i','>','\r'])
        sp.parse(self.app, self.app.read())
        



        


