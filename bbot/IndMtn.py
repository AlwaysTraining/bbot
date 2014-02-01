#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Utils import *
from bbot.Strategy import Strategy

"""
[Spending Menu]
Key Item                 Price       # Owned
(*) System Menu                             
(1) Troopers              271           100 
(2) Jets                  330             0 
(3) Turrets               383             0 
(4) Bombers              3138             0 
(5) HeadQuarters         5277             0 
(6) Regions              1412            15 
(7) Covert Agents         725             0 
(8) Tanks                1735             0 
(9) Carriers             5269             0 
(S) Sell                                    
(V) Visit Bank                              
(?) Help                                    
(0) Quit                                    

You have 49,325 gold and 10 turns.
Choice> 
"""

S = SPACE_REGEX
N = NUM_REGEX

class IndMtn(Strategy):

    ind_to_mtn_and_tech_ratio = 5

    def __init__(self, app):
        Strategy.__init__(self, app)
        self.turn = None
        self.soldturn = None
        self.curTankAlloc = None
        self.substate=0

    def get_indicators(self):
        return {
            '\[Spending Menu\]' : 10,
            "\[Sell Menu\]"   : 15,
            'You have '+NUM_REGEX+' gold and '+NUM_REGEX+' turns.' : 20,
            'Sell how many Tanks\? \(.*\)'  :   25,
            "\(T\) Technology[ \t]+"+NUM_REGEX      :   30,
            "Buy how many Industrial regions\?"     :   40,
            "Buy how many Mountain regions\?"       :   50,
            "Buy how many Technology regions\?"     :   60,
            "\[Industrial Production\]" :   70,               
            'Tanks'+S+':'+S+N+'\%'+S+'\('+N+' per year\)'     :   80,
            "Change Production\? \(y/N\)"   :   90,
            }

    def get_priority(self,state):
        return MED_PRIORITY

    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass

        # buy menu state
        elif lastState == 10 and state == 20:

            turn = self.app.get_num(1)
            soldturn = self.app.get_num(1)

            # make sure buy logic is only applied once
            if self.soldturn != soldturn and self.substate == 0:
                self.soldturn = soldturn
                self.substate = 1
                self.app.send('s')
                return Strategy.CONSUMED 
            else:
                self.substate = 0

            # make sure buy logic is only applied once
            if self.turn != turn:
                self.app.send('6')
                self.turn = turn
                return Strategy.CONSUMED # stop other strategies from doing buy menu stuff

        # Sequence for selling tanks
        elif lastState == 20 and state == 15 and self.substate == 1:
            self.substate = 2
            return Strategy.CONSUMED
        elif lastState == 15 and state == 20 and self.substate == 2:
            self.substate = 3
            self.app.send('8')
            return Strategy.CONSUMED
        elif lastState == 20 and state == 25 and self.substate == 3:
            self.substate = 4
            self.app.sendl('>')
            return Strategy.CONSUMED
        elif lastState == 25 and state == 15 and self.substate == 4:
            self.substate = 5
            self.substate = False
            return Strategy.CONSUMED
        elif lastState == 15 and state == 20 and not self.substate == 5:
            self.substate = 0
            self.app.send('b')
            return Strategy.CONSUMED
        # Sequence for selling tanks, returns to buy menu
            
            
        # Sequence for buing regions
        elif lastState == 20 and state == 30:
            self.app.send('t')
        elif lastState == 30 and state == 60:
            self.a = self.app.data.realm.regions.number_affordable
            # 5:1:1 is 5+1+1 = 7 is 5/7,1/7,1/7
            self.t = int(self.a/7)
            self.app.sendl(str(self.t))
            self.app.send('m')
        elif lastState == 60 and state == 50:
            self.app.sendl(str(self.t))
            self.app.send('i')
        elif lastState == 50 and state == 40:
            self.app.sendl('>')
            self.app.sendl()
        # Sequence for buying regions, return to buy menu


        elif state == 70:
            pass
        elif lastState == 70 and state == 80:
            self.curTankAlloc = self.app.get_num(0)
        elif lastState == 80 and state == 90:
            # if tank production not at 100%, reset industry
            botlog.debug("Current tank allocation 2 is " + str(self.curTankAlloc))
            if self.curTankAlloc < 100:
                self.app.send('y')
                self.app.sendl('0')
                self.app.sendl('0')
                self.app.sendl('0')
                self.app.sendl('0')
                self.app.sendl('100')
                self.app.sendl('0')
                
                
                return Strategy.CONSUMED
        # Sequence for buing regions, returns to buy menu

        else:
            return Strategy.UNHANDLED


