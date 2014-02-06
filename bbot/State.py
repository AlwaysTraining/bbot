#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import re
import botlog
from bbot.Utils import *
from bbot.BaseStates import *

#rom BaseStates.State import State
#rom BaseStates.StatsState import StatsState
#rom BaseStates.BailOut import BailOut

S = SPACE_REGEX
N = NUM_REGEX

TNSOA_MAIN_REGEX = re.compile('. Main . [0-9:]+ \[[0-9]+\] Main \[[0-9]+\] Notices:')
SHENKS_MAIN_REGEX = re.compile('.+fidonet.+AFTERSHOCK:')
XBIT_MAIN_REGEX = re.compile('. Main .* Xbit Local Echo \[[0-9]+\] InterBBS FE:')

MAIN_MENUS = [TNSOA_MAIN_REGEX,SHENKS_MAIN_REGEX,XBIT_MAIN_REGEX]

class LogOff(State):
    def transition(self,app,buf):
        if 'Which or (Q)uit:' in buf:
            app.send('q')
        if 'Which, (Q)uit or [1]:' in buf:
            app.send('q')
            buf = app.read(stop_patterns=MAIN_MENUS)
            if app.match_re != None:
                app.send_seq(['o','y'])
                return BailOut()


class ExitGame(State):
    def transition(self,app,buf):
        if '(6) Read Messages         (0) Quit' in buf:
            app.send('0')
            return LogOff()
        elif '-=<Paused>=-' in buf:
            app.sendl()

from bbot.EndTurnParser import EndTurnParser
class EndTurn(StatsState):

    def __init__(self):
        StatsState.__init__(self,statsParser=EndTurnParser())
    
    def transition(self,app,buf):
        
        self.parse(app,buf)
        if '[Attack Menu]' in buf or '[Trading]' in buf:
            app.send('0')
        elif 'Do you wish to send a message? (y/N)' in buf:
            app.send('n')
        elif 'Do you wish to continue? (Y/n)' in buf:
            app.send('y')
            botlog.info(str(app.data))
            return TurnStats() 

from bbot.SpendingParser import SpendingParser
class Spending(StatsState):

    def __init__(self):
        StatsState.__init__(self,statsParser=SpendingParser())
    
    def transition(self,app,buf):
        
        self.parse(app,buf)

        app.on_spending_menu()
        app.sendl()
        return EndTurn()


from bbot.MaintParser import MaintParser
class Maint(StatsState):

    def __init__(self):
        StatsState.__init__(self,statsParser=MaintParser())
        self.money_reconsider_turn = None
        self.food_reconsider_turn = None
        self.which_maint = None
        

    def transition(self,app,buf):

        self.parse(app,buf)

        if 'Do you wish to visit the Bank? (y/N)' in buf:
            self.which_maint = "Money"
            app.send('n')
        elif 'How much will you give?' in buf:
            app.sendl()
        elif '[Food Unlimited]' in buf:
            self.which_maint = "Food"
            app.send('0')
        elif '[Crazy Gold Bank]' in buf:
            app.send('0')
            return Spending()
        elif self.which_maint == 'Money' and 'Would you like to reconsider? (Y/n)' in buf:
            if self.money_reconsider_turn == app.data.realm.turns.current:
                botlog.warn("Unable to prevent not paying bills")
                app.send('n')
            else:
                app.send('y')
                buf = app.read()
                if 'Do you wish to visit the Bank? (y/N)' in buf:

                    # maint cost
                    maintcost = app.data.get_maint_cost()
                    # maint minus current cold is ammount to withdraw
                    withdraw = maintcost - app.data.realm.gold 
                    # don't try to withdraw more than we have or it will take 
                    #   two enter's to get through the prompt
                    if withdraw > app.data.realm.bank.gold:
                        withdraw = app.data.realm.bank.gold

                    # withdraw the money and get back to the maintenance sequence
                    app.send_seq(['y','w',str(withdraw),'\r','0'])

                    self.money_reconsider_turn = app.data.realm.turns.current
                    
        elif self.which_maint == 'Food' and 'Would you like to reconsider? (Y/n)' in buf:
            if self.food_reconsider_turn == app.data.realm.turns.current:
                botlog.warn("Unable to prevent not feeding realm")
                app.send('n')
            else:
                app.send_seq(['y','b','\r','0'])
                self.food_reconsider_turn =  app.data.realm.turns.current



from bbot.TurnStatsParser import TurnStatsParser
class TurnStats(StatsState):
                
    def __init__(self):
        StatsState.__init__(self,statsParser=TurnStatsParser())

    def transition(self,app,buf):

        self.parse(app,buf)

        if 'Sorry, you have used all of your turns today.' in buf: 
            app.sendl()
            return ExitGame()
        elif '-=<Paused>=-' in buf:
            app.sendl()
        elif 'of your freedom.' in buf or 'Years of Protection Left.' in buf: 
            # this buffer also contains the do you want to visit the bank
            #   question which is handled by the Maint state.  we must skip
            #   the next read, as the line would be eaten with noone to hanlde
            #   it
            app.skip_next_read = True
            return Maint()

        #TODO river producing food

from bbot.PreTurnsParser import PreTurnsParser
class PreTurns(StatsState):
                
    def __init__(self):
        StatsState.__init__(self,statsParser=PreTurnsParser())

    def transition(self,app,buf):

        self.parse(app,buf)

        if 'Would you like to buy a lottery ticket?' in buf:
            # play the lottery

            for i in range(7):
                i=i
                app.sendl()

        elif '-=<Paused>=-' in buf:
            app.sendl()
            if 'Sorry, you have used all of your turns today.' in buf:
                return ExitGame()

        elif '[Diplomacy Menu]' in buf:
            # exit the diplomicy meny
            app.send('0')

        elif 'Do you wish to accept?' in buf:
            app.send('i')

        elif '[R] Reply, [D] Delete, [I] Ignore, or [Q] Quit>' in buf:
            app.send('i')

        elif '[Industrial Production]' in buf:
            app.on_industry_menu()
            app.send('n')

            return TurnStats()

        


class MainMenu(State):
        
    playing = False

    def transition(self,app,buf):
        if not MainMenu.playing:
            MainMenu.playing = True
            app.send(1)
            return PreTurns()
        else:
            app.send(0)
        
        return BailOut()

class NewRealm(State):
    def transition(self,app,buf):
        app.send_seq( [ app.get_app_value('realm')+"\r", 'y','n' ] )
        return MainMenu()

            

class StartGame(State):
    def transition(self,app,buf):
        if '<Paused>' in buf or '>Paused<' in buf:
            app.sendl()
        elif 'Do you want ANSI Graphics? (Y/n)' in buf:
            app.send('n')
        elif 'Continue? (Y/n)' in buf:
            app.send('y')
        elif 'Name your Realm' in buf:
            return NewRealm()
        elif '(1) Play Game             (7) Send Messages' in buf:
            return MainMenu()


class BBSMenus(State):
    def transition(self,app,buf):


        looking_for_main = False
        if "Enter number of bulletin to view or press (ENTER) to continue:" in buf:
            app.sendl()
            # there is a decent pause here sometimes, so just use the read until
            # function

        elif '[+] Read your mail now?' in buf:
            app.send('n')
            looking_for_main = True
            
        elif 'Search all groups for new messages' in buf:
            app.send('n')

        elif 'Search all groups for un-read messages to you' in buf:
            app.send('n')

        elif 'TNSOA' in buf and " Main " in buf and " Notices:" in buf:
            app.send_seq(['x','2',app.get_app_value('game')])
            return StartGame()
 

        
        
        

        
        

class Password(State):
    def transition(self,app,buf):
        if "Password:" in buf:
            app.sendl(app.get_app_value('password'))
            buf = app.read_until("[Hit a key]")
            app.sendl()
            return BBSMenus()
       #elif "[Hit a key]" in buf:
       #    app.sendl()
       #    return BBSMenus()
    
class Login(State):
    def transition(self,app,buf):
        if "Login:" in buf:
            app.sendl(app.get_app_value('username'))
            return Password()
            
        
