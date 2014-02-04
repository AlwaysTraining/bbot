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
                app.send('o')
                app.send_seq(['o','y'])
                return BailOut()


class ExitGame(State):
    def transition(self,app,buf):
        if '(6) Read Messages         (0) Quit' in buf:
            app.send('0')
            return LogOff()
        elif '-=<Paused>=-' in buf:
            app.sendl()


class EndTurn(StatsState):
    def get_patterns(self):
        return {
            'Your dominion gained '+NUM_REGEX+' million people\.' : 1610,
            'Your dominion lost '+NUM_REGEX+' million people\.' :   1620,
            NUM_REGEX + ' units of food spoiled\.' : 1630,
            NUM_REGEX + ' units of food has been eaten by a hungry user\.'  : 1640
            }

    def transition(self,app,buf):

        lines = buf.splitlines()

        for line in lines:
            state = self.get_match(line)
            if state == 1610:
                app.data.realm.population.growth = self.get_num(0)
            elif state == 1620:
                app.data.realm.population.growth = -self.get_num(0)
            elif state == 1630:
                app.data.realm.food.spoilage = self.get_num(0)
            elif state == 1640:
                app.data.realm.food.randomly_eaten = self.get_num(0)

        if '[Attack Menu]' in buf or '[Trading]' in buf:
            app.send('0')
        elif 'Do you wish to send a message? (y/N)' in buf:
            app.send('n')
        elif 'Do you wish to continue? (Y/n)' in buf:
            app.send('y')
            botlog.info(str(app.data))
            return TurnStats() 

class Spending(StatsState):

    def __init__(self):
        StatsState.__init__(self)
        self.buymenu=None

    def get_patterns(self):
        return {
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

    
    def transition(self,app,buf):
        lines = buf.splitlines()
        realm=app.data.realm
        army=realm.army
        regions=realm.regions
        if '[Spending Menu]' in buf: self.buymenu = True
        elif '[Sell Menu]' in buf: self.buymenu = False


        for line in lines:
            state = self.get_match(line)

            if state == 810 : 
                if self.buymenu: army.troopers.price = self.get_num(0)
                if not self.buymenu: army.troopers.sellprice = self.get_num(0)
                army.troopers.number = self.get_num(1)
            elif state == 820 : 
                if self.buymenu: army.jets.price = self.get_num(0)
                if not self.buymenu: army.jets.sellprice = self.get_num(0)
                army.jets.number = self.get_num(1)
            elif state == 830 : 
                if self.buymenu: army.turrets.price = self.get_num(0)
                if not self.buymenu: army.turrets.sellprice = self.get_num(0)
                army.turrets.number = self.get_num(1)
            elif state == 840 : 
                if self.buymenu: army.bombers.price = self.get_num(0)
                if not self.buymenu: army.bombers.sellprice = self.get_num(0)
                army.bombers.number = self.get_num(1)
            elif state == 850 : 
                if self.buymenu: army.headquarters.price = self.get_num(0)
                if not self.buymenu: army.headquarters.sellprice = self.get_num(0)
                army.headquarters.number = self.get_num(1)
            elif state == 860 : 
                if self.buymenu: regions.price = self.get_num(0)
                if not self.buymenu: regions.sellprice = self.get_num(0)
                regions.number = self.get_num(1)
            elif state == 870 : 
                if self.buymenu: army.agents.price = self.get_num(0)
                if not self.buymenu: army.agents.sellprice = self.get_num(0)
                army.agents.number = self.get_num(1)
            elif state == 880 : 
                if self.buymenu: army.tanks.price = self.get_num(0)
                if not self.buymenu: army.tanks.sellprice = self.get_num(0)
                army.tanks.number = self.get_num(1)
            elif state == 890 : 
                if self.buymenu: army.carriers.price = self.get_num(0)
                if not self.buymenu: army.carriers.sellprice = self.get_num(0)
                army.carriers.number = self.get_num(1)
            elif state == 900 :
                realm.gold = self.get_num(0)
                realm.turns.remaining = self.get_num(1)
                
                app.OnSpendingMenu()
                app.sendl()
                return EndTurn()


class Maint(StatsState):

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
            }
    def transition(self,app,buf):
        lines = buf.splitlines()
        realm=app.data.realm
        army=realm.army
        regions=realm.regions


        for line in lines:
            state = self.get_match(line)
            if state == 1700:
                army.maintenance = self.get_num(0)
            elif state == 1710:
                regions.maintenance = self.get_num(0)
            elif state == 1720:
                realm.queen_taxes = self.get_num(0)
            elif state == 1730:
                realm.population.food = self.get_num(0)
            elif state == 1740:
                army.food = self.get_num(0)
            elif state == 1750:
                realm.pop_support_bribe = self.get_num(0)
            elif state == 1900:
                realm.gold = self.get_num(0)
                realm.food.units = self.get_num(1)
            elif state == 1510 : 
                realm.gold = self.get_num(0)
                realm.bank.gold = self.get_num(1)

        if 'Do you wish to visit the Bank? (y/N)' in buf:
            app.send('n')
        elif 'How much will you give?' in buf:
            app.sendl()
        elif '[Food Unlimited]' in buf:
            app.send('0')
        elif 'Crazy Gold Bank]' in buf:
            app.send('0')
            return Spending()


class TurnStats(StatsState):
                
    def get_patterns(self):
        return {
        re.escape('-=<Paused>=-')    :   0,
        re.escape('Sorry, you have used all of your turns today.')  :   1,
        N+' gold was earned in taxes.'  :   500,
        N+' gold was produced from the Ore Mines.'  :   510,
        N+' gold was earned in Tourism.'    :   520,
        N+' gold was earned by Solar Power Generators.' :   530,
        N+' gold was created by Hydropower.'    :   540,
        N+' Food units were grown.' :   550,

        N+' Troopers were manufactured by Industrial Zones.'    :   560,
        N+' Turrets were manufactured by Industrial Zones.' :   570,
        N+' Jets were manufactured by Industrial Zones.'    :   580,
        N+' Carriers were manufactured by Industrial Zones.'    :   590,
        N+' Bombers were manufactured by Industrial Zones.' :   600,
        N+' Tanks were manufactured by Industrial Zones.'   :   610,
        N+' gold was earned from investment returns.'   :   620,
        "\-\*(.+)\*\-"  :   200,
        "Turns: "+N :   210,
        "Score: "+N :   220,
        "Gold: "+N  :   230,
        "Bank: "+N  :   240,
        "Population: "+N+" Million \(Tax Rate: "+N+"\%" :   250,
        "Popular Support: "+N+"\%"  :   260,
        "Food: "+N  :   270,
        "Agents: "+N    :   280,
        "Headquarters: "+N+"\% Complete"    :   290,
        "SDI Strength: "+N+"\%" :   300,
        "This is year "+N+" of your freedom."   :   310,
        "You have "+N+" Years of Protection Left."  :   320,
        }


    def transition(self,app,buf):
        lines = buf.splitlines()
        realm=app.data.realm
        army=realm.army
        regions=realm.regions

        
        for line in lines:
            state = self.get_match(line)
            
            if state == 200 : realm.name=self.get_str()
            elif state == 210: realm.turns.current = self.get_num()
            elif state == 220: realm.turns.score = self.get_num()
            elif state == 230: realm.turns.gold = self.get_num()
            elif state == 240: realm.bank.gold = self.get_num()
            elif state == 250:
                realm.population.size = self.get_num(0)
                realm.population.rate = self.get_num(1)
            elif state == 260: realm.population.pop_support = self.get_num()
            elif state == 270: realm.food.units = self.get_num()
            elif state == 280: army.agents.number = self.get_num()
            elif state == 290: army.headquarters.number = self.get_num()
            elif state == 300: army.sdi = self.get_num()
            elif state == 500: realm.population.taxearnings = self.get_num()
            elif state == 510: regions.mountain.earnings = self.get_num()
            elif state == 520: regions.coastal.earnings = self.get_num()
            elif state == 530: regions.desert.earnings = self.get_num()
            elif state == 540: regions.river.earnings = self.get_num()
            elif state == 550: regions.agricultural.foodyield = self.get_num()
            elif state == 0: app.sendl()
            elif state == 1: 
                app.sendl()
                return ExitGame()
            elif state == 310: 
                army.years_freedom = self.get_num()
                return Maint()
            elif state == 320: 
                army.years_protection = self.get_num()
                return Maint()

        #TODO river producing food

class PreTurns(State):
    
    def transition(self,app,buf):

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

            
        
    
MENU_REGEX = re.compile('.*'+re.escape('(1) Play Game             (7) Send Messages')+'.*')
NEW_EMPIRE_REGEX = re.compile('.*'+re.escape('Name your Realm')+'.*')

class StartGame(State):
    def transition(self,app,buf):
        if '<Paused>' in buf or '>Paused<' in buf:
            app.sendl()
        elif 'Do you want ANSI Graphics? (Y/n)' in buf:
            app.send('n')
            buf = app.read(stop_patterns=[MENU_REGEX,NEW_EMPIRE_REGEX])        

            if 'Continue? (Y/n)' in buf:
                app.send('y')
                buf = app.read(stop_patterns=[MENU_REGEX,NEW_EMPIRE_REGEX])        
            
            if app.match_re == NEW_EMPIRE_REGEX:
                return NewRealm()
            elif app.match_re == MENU_REGEX:
                return MainMenu()



        




class BBSMenus(State):
    def transition(self,app,buf):


        if "Enter number of bulletin to view or press (ENTER) to continue:" in buf:
            app.sendl()
            buf = app.read_until('Last few callers:')
            buf = app.read()

        if '[+] Read your mail now?' in buf:
            app.send('n')
            buf = app.read(stop_patterns=MAIN_MENUS)
        if 'Search all groups for new messages' in buf:
            app.send('n')
            buf = app.read(stop_patterns=MAIN_MENUS)
        if 'Search all groups for un-read messages to you' in buf:
            app.send('n')
            buf = app.read(stop_patterns=MAIN_MENUS)
        
        botlog.debug("Checking for main")
        #match_re = None
        if app.match:
            #match_re = app.match_re
            botlog.debug("Found Main")
            app.send('x')
            buf = app.read()

        if '2: Games' in buf:
            app.send('2')
            buf = app.read()

        app.send(app.get_app_value('game'))
        buf = app.read()

        return StartGame()
        
        
        

        
        

class Password(State):
    def transition(self,app,buf):
        if "Password:" in buf:
            app.sendl(app.get_app_value('password'))
            buf = app.read_until("[Hit a key]")
        if "[Hit a key]" in buf:
            app.sendl()
        return BBSMenus()
    
class Login(State):
    def transition(self,app,buf):
        if "Login:" in buf:
            app.sendl(app.get_app_value('username'))
            return Password()
            
        
