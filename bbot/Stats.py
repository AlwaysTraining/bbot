#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

"""


5183 gold was earned in taxes.
18,130 gold was produced from the Ore Mines.
12,951 gold was earned in Tourism.
20,030 gold was earned by Solar Power Generators.
600 Food units were grown.

-=<Paused>=-




-*shenks.synchro.net*-
Turns: 12
Score: 213
Gold: 1,056,294
Population: 100 Million (Tax Rate: 15%)
Popular Support: 100%
Food: 1600
Military: [100 Troopers] 
          [100% Morale]
Regions:  [2 Agricultural] [5 Desert] [5 Mountains] [3 Coastal] 
You have 100 Years of Protection Left.



"""
import os
from bbot.Utils import *
from bbot.Strategy import Strategy


class Stats(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    
    def get_indicators(self):
        return {
            NUM_REGEX+' gold was earned in taxes\.'  :   10,
            "gold was produced from the Ore Mines"  :   20,
            "gold was earned in Tourism"    : 30,
            "gold was earned by Solar Power Generators" :   40,
            "Food units were grown" :   50
        }


    def on_indicator(self, lastState, state):
        if state == 10:
            self.app.data.set("Turn Tax Revenue", self.app.get_num(0))


        else:
            return Strategy.UNHANDLED


