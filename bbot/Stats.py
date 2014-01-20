#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Strategy import Strategy

class Common(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
            "gold was earned in taxes"  :   10,
            "gold was produced from the Ore Mines"  :   20,
            "gold was earned in Tourism"    : 30,
            "gold was earned by Solar Power Generators" :   40,
            "Food units were grown" :   50
}

"""
Turns: 10
Score: 213
Gold: 1,048,281
Population: 100 Million (Tax Rate: 15%)
Popular Support: 100%
Food: 1600
Military: [100 Troopers] 
          [100% Morale]
Regions:  [2 Agricultural] [5 Desert] [5 Mountains] [3 Coastal] 
You have 100 Years of Protection Left.
���������������������������������������������������������������������
"""

    def on_indicator(self, state):
        if self.lastState is None and state == 1:

            # no ansi graphics
            self.app.send('n')

        elif state == 2:
    
            # yes at continue prompt
            self.app.send('y')

        elif (self.lastState == 1 or self.lastState == 2) and state == 2:

            # name the realm
            self.app.sendl(self.app.get_app_value('realm'))

        elif self.lastState == 3 and state == 4:

            # confirm that is the name you wanted for the realm
            self.app.send('y')

        elif self.lastState == 4 and state == 5:

            # No I don't want any directions
            self.app.send('n')

        elif state == 6:

            # Paused, press enter
            self.app.sendl()

        elif state == 7:
            # first menu option seen
            pass
        elif self.lastState == 7 and state == 8:
            # second menu option seen
            pass
        elif self.lastState == 8 and state == 9:
            # thid menu option seen, this is probably the menu
            # press enter to start play
            self.sendl()
        elif self.lastState == 9 and state == 10:
            # play the lottery
            for i in range(7):
                self.sendl()
            # exit the diplomicy meny
            self.sendl()
            # set industries
            self.send('y')
            # troopers, jets, turret, bombers at 0
            for i in range(4):
                self.sendl()
            # tanks at 100%
            self.sendl('>')
            # carreirs at 0
            self.sendl()
            




        else:
            return Strategy.UNHANDLED


