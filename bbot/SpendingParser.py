#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import re
import botlog
from bbot.Utils import *
from bbot.StatsParser import StatsParser

S = SPACE_REGEX
N = NUM_REGEX

class SpendingParser(StatsParser):

    def __init__(self):
        StatsParser.__init__(self)
        self.buymenu=True

    def get_patterns(self):
        return {
            re.escape('[Spending Menu]')    :   0,
            re.escape('[Sell Menu]')        :   1,
            "You can afford "+N+' regions\.':   50,
            "\(C\) Coastal[ \t]+"+N         :   70,
            "\(R\) River[ \t]+"+N           :   80,
            "\(A\) Agricultural[ \t]+"+N    :   90,
            "\(D\) Desert[ \t]+"+N          :   100,
            "\(I\) Industrial[ \t]+"+N      :   110,
            "\(U\) Urban[ \t]+"+N           :   120,
            "\(M\) Mountain[ \t]+"+N        :   130,
            "\(T\) Technology[ \t]+"+N      :   140,

            "\(1\) Troopers"+S+N+S+N  : 810,
            "\(2\) Jets"+S+N+S+N  : 820,
            "\(3\) Turrets"+S+N+S+N  : 830,
            "\(4\) Bombers"+S+N+S+N  : 840,
            "\(5\) HeadQuarters"+S+N+S+N  : 850,
            "\(6\) Regions"+S+N+S+N  : 860,
            "\(7\) Covert Agents"+S+N+S+N  : 870,
            "\(8\) Tanks"+S+N+S+N  : 880,
            "\(9\) Carriers"+S+N+S+N  : 890,
            "You have "+N+" gold and "+N+" turns\." : 900,
            }

    
    def on_match(self,app,line,which):
        realm=app.data.realm
        army=realm.army
        regions=realm.regions

        if which == 0: self.buymenu = True
        elif which == 0: self.buymenu = False
        elif which == 50: regions.number_affordable = self.get_num()
        elif which == 70: regions.coastal.number = self.get_num()
        elif which == 80: regions.river.number = self.get_num()
        elif which == 90: regions.agricultural.number = self.get_num()
        elif which == 100: regions.desert.number = self.get_num()
        elif which == 110: regions.industrial.number = self.get_num()
        elif which == 120: regions.urban.number = self.get_num()
        elif which == 130: regions.mountain.number = self.get_num()
        elif which == 140: regions.technology.number = self.get_num()
        elif which == 810: 
            if self.buymenu: army.troopers.price = self.get_num(0)
            if not self.buymenu: army.troopers.sellprice = self.get_num(0)
            army.troopers.number = self.get_num(1)
        elif which == 820 : 
            if self.buymenu: army.jets.price = self.get_num(0)
            if not self.buymenu: army.jets.sellprice = self.get_num(0)
            army.jets.number = self.get_num(1)
        elif which == 830 : 
            if self.buymenu: army.turrets.price = self.get_num(0)
            if not self.buymenu: army.turrets.sellprice = self.get_num(0)
            army.turrets.number = self.get_num(1)
        elif which == 840 : 
            if self.buymenu: army.bombers.price = self.get_num(0)
            if not self.buymenu: army.bombers.sellprice = self.get_num(0)
            army.bombers.number = self.get_num(1)
        elif which == 850 : 
            if self.buymenu: army.headquarters.price = self.get_num(0)
            if not self.buymenu: army.headquarters.sellprice = self.get_num(0)
            army.headquarters.number = self.get_num(1)
        elif which == 860 : 
            if self.buymenu: regions.price = self.get_num(0)
            if not self.buymenu: regions.sellprice = self.get_num(0)
            regions.number = self.get_num(1)
        elif which == 870 : 
            if self.buymenu: army.agents.price = self.get_num(0)
            if not self.buymenu: army.agents.sellprice = self.get_num(0)
            army.agents.number = self.get_num(1)
        elif which == 880 : 
            if self.buymenu: army.tanks.price = self.get_num(0)
            if not self.buymenu: army.tanks.sellprice = self.get_num(0)
            army.tanks.number = self.get_num(1)
        elif which == 890 : 
            if self.buymenu: army.carriers.price = self.get_num(0)
            if not self.buymenu: army.carriers.sellprice = self.get_num(0)
            army.carriers.number = self.get_num(1)
        elif which == 900 :
            realm.gold = self.get_num(0)
            realm.turns.remaining = self.get_num(1)
            

