#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.SpendingParser import SpendingParser
from bbot.Data import *

S = SPACE_REGEX
N = NUM_REGEX


class IndMtn(Strategy):
    def __init__(self,app):
        Strategy.__init__(self,app)
        self.data = self.app.data
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
        if self.data.regions.number < 1000:
            return 0.75

        # If investments are not full, we will sell a portion
        if not self.data.has_full_investments:
            return 0.5

        # in general, we will sell a small portion of our army to suppliment 
        #   region growth
        return 0.025  

    def sell(self, sellItems, sellRatio):

        # we start at the buy menu

        # sell all tanks and return to buy menu
        self.app.send('s')
        # perform a read and through a spending state to parse all the data
        self.sp.parse(self.app, self.app.read())

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
                
                self.app.send_seq( [ str(saleItem),ammount,'\r' ] )

            else:
                raise Exception("Do not know how to drop regions yet")

        # return to buy menu
        self.app.send('b')
        self.sp.parse(self.app, self.app.read())

            
    def buy_ag_regions(self):
        # we start at the region menu

        regions = self.data.realm.regions
        

        num_to_buy = 1.0
        # visit civilian advisor and buy ag regions until he is happy
        while True:
            self.app.send('*')
            self.app.read()
            self.app.send(1)
            self.data.realm.advisors.reset_advisor(1)
            buf = self.app.read()
            self.sp.parse(self.app, buf)
            if '-=<Paused>=-' in buf:
                self.app.sendl()
                self.app.read()

            # if we no longer have a deficit we have bought enough ag
            if self.data.realm.advisors.civilian.food_deficit is None:
                # this returns us to the buy region menu
                self.app.send('0')
                break

            self.app.send_seq(['0','a',str(int(round(num_to_buy))),'0'])
            num_to_buy = num_to_buy * 1.25
        



    def get_region_ratio(self):
        
        r = Regions()
        r.coastal.number=0
        r.river.number=0
        r.agricultural.number=None
        r.desert.number=0
        r.industrial.number=0
        r.urban.number=0
        r.mountain.number=0
        r.technology.number=0

        if self.data.realm.regions.number < 250:
            r.desert.number=1
        elif self.data.realm.regions.number < 500:
            r.desert.number=1
            r.mountain.number=1
        elif self.data.realm.regions.number < 1000:
            r.mountain.number=1
            r.industrial.number=1
        elif self.data.realm.regions.number < 2000:
            r.mountain.number=2
            r.industrial.number=1
        elif self.data.realm.regions.number < 3000:
            r.mountain.number=3
            r.industrial.number=1
            r.technology.number=1
        elif self.data.realm.regions.number < 4000:
            r.mountain.number=4
            r.industrial.number=1
            r.technology.number=1
        else:
            r.mountain.number=self.data.realm.regions.number / 1000.0
            r.industrial.number=1
            r.technology.number=1


        return r




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


        # enter region buying menu
        self.app.send('6')
        self.sp.parse(self.app, self.app.read())

        # buy just enough ag
        self.buy_ag_regions()
        self.sp.parse(self.app, self.app.read())

        # determine the proper region ratio for buy
        r = self.get_region_ratio()
        # botlog.debug("ratio: " + str(r))
        
        self.sp.parse(self.app, self.app.read())
        # the number of regions we can afford
        a = self.data.realm.regions.number_affordable

        if a is None:
            raise Exception("Not known how many regions there are")

        # the regions to buy
        r.ratio_to_buy(a)
        # botlog.debug("to buy: " + str(r))

        # maps menu option to number of regions
        r = r.get_menu_number_dict()
        # botlog.debug("buy dict: " + str(r))

        # Sequence for buying regions, return to buy menu
        seq = []
        for menu_option, ammount in r.items():
            seq.append(str(menu_option))
            seq.append(str(ammount))
            seq.append('\r')

        # buy the regions
        self.app.send_seq(seq)

        # re parse region menu/buy meny
        self.sp.parse(self.app, self.app.read())

        # no need to 
        # return to the spending menu
        # because we bought all the regions we could afford
        # it automatically gets back to the buy menu

        
        


