#!/usr/bin/env python


"""

Do you wish to visit the Bank? (y/N)

Your Armed Forces Require 10 gold.
How much will you give? (10; 10)


4565 gold is required to maintain your regions.

4496 gold is requested to boost popular support.
How much will you give? (4496; 6744)

The Queen Royale requires 3197 gold for Taxes.

Your People Need 151 units of food






Choice> Quit

Your People Need 2163 units of food
<2596:Maintenance:40>  Sending {\r}


How much will you give? (1063; 1063) 1063

Your Armed Forces Require 125 units of food
<2600:Maintenance:50>  Sending {\r}


How much will you give? (0; 0) 0

Your actions may lead to DISASTEROUS results.
Would you like to reconsider? (Y/n) 
"""
import os
from bbot.Utils import *
from bbot.Strategy import Strategy


class Maintenance(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)
        self.substate = 0
        self.substate2 = 0
        self.turn = None
        self.turn2 = None

    def get_priority(self,state):
        return HIGH_PRIORITY
    
    def get_indicators(self):
        return {
            'Do you wish to visit the Bank\? \(y/N\)'  :   5,
            'Your Armed Forces Require '+NUM_REGEX+' gold\.'  :   10,
            NUM_REGEX + ' gold is required to maintain your regions\.'   :   20,
            'The Queen Royale requires '+NUM_REGEX+' gold for Taxes\.' : 30,
            'Your People Need '+NUM_REGEX+' units of food'    :   40,
            'Your Armed Forces Require '+NUM_REGEX+' units of food'   :   50,
            NUM_REGEX + ' gold is requested to boost popular support\.' :   60,
            # TODO Morale
            'Your actions may lead to DISASTEROUS results\.'    :   70,
            'Would you like to reconsider\? \(Y/n\)'   :   75,
            'You have ' + NUM_REGEX + ' gold and ' + NUM_REGEX + ' units of food\.' : 80,
            'How much food do you wish to buy\? \(.*\)' :   90,
            '\[Crazy Gold Bank\]' : 95,
            'You have '+NUM_REGEX+' gold in hand and '+NUM_REGEX+' gold in the bank.' : 100,
            'Withdraw how many gold\? \(.*\)'  :   110,
        }


    def on_indicator(self, lastState, state):
        if state == 5 and self.substate2 != 2:
            self.app.sendl()
        elif state == 10:
            self.app.sendl()
        elif state == 20:
            self.app.sendl()
        elif state == 30:
            self.app.sendl()
        elif state == 40:
            self.app.sendl()
        elif state == 50:
            self.app.sendl()
        elif state == 60:
            self.app.sendl()
        # sequence for buying food then you don't have enough
        elif lastState == 50 and state == 70 and self.substate == 0:
            self.substate = 1
        elif lastState == 70 and state == 75 and self.substate == 1:
            self.substate = 2
            turn = self.app.data.realm.turns.current

            botlog.debug("!self turn: " + str(self.turn) + " turn: " + str(turn))

            if self.turn == turn:
                botlog.warn("Unable to avoid food shortage")
                self.app.send('n')
                self.substate = 0
            else:
                self.app.send('y')
                self.turn = turn

            return Strategy.CONSUMED
        elif lastState == 70 and state == 80 and self.substate == 2:
            self.substate = 3
            self.app.send('b')
            return Strategy.CONSUMED
        elif lastState == 80 and state == 90 and self.substate == 3:
            self.substate = 0
            self.app.sendl()
            return Strategy.CONSUMED

        # sequence for visiting bank to afford maintenance
        elif lastState == 30 and state == 70 and self.substate2 == 0:
            self.substate2 = 1
            return Strategy.CONSUMED
        elif lastState == 70 and state == 75 and self.substate2 == 1:
            self.substate2 = 2
            turn2 = self.app.data.realm.turns.current

            botlog.debug("!self turn2: " + str(self.turn2) + " turn2: " + str(turn2))

            if self.turn2 == turn2:
                botlog.warn("Unable to avoid money shortage")
                self.app.send('n')
                self.substate2 = 0
            else:
                self.app.send('y')
                self.turn2 = turn2

            return Strategy.CONSUMED

        elif lastState == 75 and state == 5 and self.substate2 == 2:
            self.substate2 = 3
            self.app.send('y')
            return Strategy.CONSUMED
        elif lastState == 5 and state == 95 and self.substate2 == 3:
            self.substate2 = 4
            return Strategy.CONSUMED
        elif lastState == 95 and state == 100 and self.substate2 == 4:
            self.substate2 = 5
            self.app.send('w')
            return Strategy.CONSUMED
        elif lastState == 100 and state == 110 and self.substate2 == 5:
            self.substate2 = 6
            # maint cost
            maintcost = self.app.data.get_maint_cost()
            # maint minus current cold is ammount to withdraw
            withdraw = maintcost - self.app.data.realm.gold 
            # don't try to withdraw more than we have or it will take 
            #   two enter's to get through the prompt
            if withdraw > self.app.data.realm.bank.gold:
                withdraw = self.app.data.realm.bank.gold
            # withdraw ammount
            self.app.sendl(str(withdraw))
            
            return Strategy.CONSUMED
            
        elif lastState == 110 and state == 100 and self.substate2 == 6:
            self.substate2 = 0
            self.app.sendl()
            # should then retart the maintenance sequence
            return Strategy.CONSUMED

            
        
        
            
            



        else:
            return Strategy.UNHANDLED


