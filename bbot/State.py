#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Strategy import Strategy
import re
import botlog
from bbot.Utils import *

S = SPACE_REGEX
N = NUM_REGEX

class State(object):
    def transition(self,app,buf):
        pass
    def get_name(self):
        return self.__class__.__name__

class BailOut(State):
    pass

class StatsState(State):
    def __init__(self):
        self.regexs = None
        self.match = None
    
    def get_patterns(self):
        return {}

    def get_regexs(self):
    
        if self.regexs is None:
            self.regexs={}
            patterns = self.get_patterns()
            for pattern,id in patterns.items():
                self.regexs[id]=re.compile(pattern)
        return self.regexs

    def get_match(self,line):
        
        regexs = self.get_regexs()
        for rid,regex in regexs.items():
            m = regex.match(line)
            if m is not None:
                self.match = m
                return rid

    def get_num(self, matchIndex=0):
        n = ToNum(self.match.groups()[matchIndex])
        
    def get_str(self,matchIndex=0):
        """
        Get a number from the current matchign regex group
        """
        return self.match.groups()[matchIndex]
    
            

class Maint(StatsState):
    pass

class TurnStats(StatsState):
                
    def get_patterns(self):
        return {
        re.escape('-=<Paused>=-')    :   0,
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
                app.sendl()

        elif '-=<Paused>=-' in buf:
            app.sendl()

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
        else:
            return BailOut()

        


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



        



TNSOA_MAIN_REGEX = re.compile('. Main . [0-9:]+ \[[0-9]+\] Main \[[0-9]+\] Notices:')
SHENKS_MAIN_REGEX = re.compile('.+fidonet.+AFTERSHOCK:')
XBIT_MAIN_REGEX = re.compile('. Main .* Xbit Local Echo \[[0-9]+\] InterBBS FE:')

MAIN_MENUS = [TNSOA_MAIN_REGEX,SHENKS_MAIN_REGEX,XBIT_MAIN_REGEX]

class BBSMenus(State):
    def transition(self,app,buf):


        if "Enter number of bulletin to view or press (ENTER) to continue:" in buf:
            app.sendl()
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
        match_re = None
        if app.match:
            match_re = app.match_re
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
            
        
