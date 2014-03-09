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

class MaintParser(StatsParser):

    def __init__(self):
        StatsParser.__init__(self)
        self.buymenu=True

    def get_patterns(self):
        return {

            'Your Armed Forces Require '+NUM_REGEX+' gold\.'  :   1700,
            NUM_REGEX + ' gold is required to maintain your regions\.'   :   1710,
            'The Queen Royale requires '+NUM_REGEX+' gold for Taxes\.' : 1720,
            'Your People Need '+NUM_REGEX+' units of food'    :   1730,
            'Your Armed Forces Require '+NUM_REGEX+' units of food'   :   1740,
            NUM_REGEX + ' gold is requested to boost popular support\.' :   1750,
            'You have ' + NUM_REGEX + ' gold and ' + NUM_REGEX + ' units of food.' : 1900,
            'You have '+NUM_REGEX+' gold in hand and '+NUM_REGEX+' gold in the bank.' : 1510,
            '\['+N+' Regions left\] Your choice\?'  :   521,
            N + "/" + N + "/" + N + S + "\$" + N: 3254,
            ('Returns expected to be approximately ' + N +' gold\.  Accept\? \(Y/n\) '): 3264,
            'You have ' + NUM_REGEX + ' gold in hand and ' + NUM_REGEX + ' gold in the bank.': 1510,
            }

    
    def on_match(self,app,line,which):
        realm=app.data.realm
        army=realm.army
        regions=realm.regions

        if which == 1700: army.maintenance = self.get_num(0)
        elif which == 1710: regions.maintenance = self.get_num(0)
        elif which == 1720: realm.queen_taxes = self.get_num(0)
        elif which == 1730: realm.population.food = self.get_num(0)
        elif which == 1740: army.food = self.get_num(0)
        elif which == 1750: realm.pop_support_bribe = self.get_num(0)
        elif which == 1900:
            realm.gold = self.get_num(0)
            realm.food.units = self.get_num(1)
        elif which == 1510 : 
            realm.gold = self.get_num(0)
            realm.bank.gold = self.get_num(1)
        elif which == 521: realm.regions.waste.number = self.get_num(0)
        elif which == 3254:
            bank.investments.append(self.get_num(3))
        elif which == 3256:
            bank.investments.approx_return = self.get_num(1)




