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
    r.coastal.number=0
    r.river.number=0
    r.agricultural.number=None
    r.desert.number=0
    r.industrial.number=0
    r.urban.number=0
    r.mountain.number=0
    r.technology.number=0

    if app.data.realm.regions.number < 250:
        r.desert.number=1
    elif app.data.realm.regions.number < 500:
        r.desert.number=1
        r.mountain.number=1
    elif app.data.realm.regions.number < 1000:
        r.mountain.number=1
        r.industrial.number=1
    elif app.data.realm.regions.number < 2000:
        r.mountain.number=1
        r.industrial.number=2
    elif app.data.realm.regions.number < 3000:
        r.mountain.number=1
        r.industrial.number=3
        r.technology.number=1
    elif app.data.realm.regions.number < 4000:
        r.mountain.number=1
        r.industrial.number=4
        r.technology.number=1
    else:
        r.mountain.number= 1
        r.industrial.number=app.data.realm.regions.number / 1000.0
        r.technology.number=1
    return r


class IndMtn(Strategy):
    def __init__(self,app):
        Strategy.__init__(self,app)
        self.data = self.app.data
        self.app.metadata.get_region_ratio_func = get_region_ratio
        self.sp = SpendingParser()

    def on_industry_menu(self):

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
            return 1.0

        # When there are less than 1k regions, concectrate
        #   on liquidating army
        if self.data.realm.regions.number < 1000:
            return 0.75

        # If investments are not full, we will sell a portion
        if not self.data.has_full_investments:
            return 0.5

        # in general, we will sell a small portion of our army to suppliment 
        #   region growth
        return 0.025  

    def sell(self, sellItems, sellRatio):

        # we start at the buy menu
        in_buy=True


        # sell all the items specified
        for saleItem in sellItems:
            if str(saleItem) != '6':

                ammount = self.data.get_number(saleItem)

                if ammount == 0:
                    continue
                if sellRatio >= 1.0:
                    ammount = '>'
                else:
                    ammount = int(round(ammount * sellRatio,0))
                    ammount = str(ammount)
                
                if in_buy:
                    # sell all tanks and return to buy menu
                    self.app.send('s')
                    # perform a read and through a spending state to parse all the data
                    self.sp.parse(self.app, self.app.read())
                    in_buy = False
                self.app.send_seq( [ str(saleItem),ammount,'\r' ] )

            else:
                raise Exception("Do not know how to drop regions yet")

        # return to buy menu
        if not in_buy:
            self.app.send('b')
            self.sp.parse(self.app, self.app.read())

            




    def on_spending_menu(self):


        # Sell items         
        
        sell_ratio = self.get_army_sell_ratio()
        sellItems = [
            Troopers.menu_option,
            Turrets.menu_option,
            Jets.menu_option,
            Tanks.menu_option,
            Bombers.menu_option,
            Carriers.menu_option]

        self.sell(sellItems, sell_ratio)
        self.sp.parse(self.app, self.app.read())

        RegionBuy(self.app)

        # we should still be at buy menu

