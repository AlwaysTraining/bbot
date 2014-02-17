#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.Data import *
from bbot.PirateParser import PirateParser
from random import randint
from bbot.RegionBuy import RegionBuy

S = SPACE_REGEX
N = NUM_REGEX


class AntiPirate(Strategy):
    def __init__(self,app):
        Strategy.__init__(self,app)
        self.data = self.app.data
        self.attack_ratio=0.5
        self.pirateloss=0
        self.piratewins=0
        self.piratebattles=0
        self.pp=PirateParser()

    def on_attack_menu(self):

        self.data.realm.reset_pirates()

        self.app.send('p',comment='go from attack menu to pirate menu')

        buf = self.app.read()

        self.app.send(randint(1,9),comment='from pirate menu to randomly chosen pirate')
        buf = self.app.read()

        troopers = int(self.app.data.realm.army.troopers.number * self.attack_ratio)

        self.app.sendl(troopers,comment='troopers for pirate attack')
        buf = self.app.read()

        jets = int(self.app.data.realm.army.jets.number * self.attack_ratio)

        self.app.sendl(jets,comment='jets for pirate attack')
        buf = self.app.read()

        tanks = int(self.app.data.realm.army.tanks.number * self.attack_ratio)

        self.app.sendl(tanks,comment='tanks for pirate attack')

        buf = self.app.read()
        self.pp.parse(self.app, buf)

        self.piratebattles = self.piratebattles + 1
        if 'You could not successfully raid' in buf:
            self.attack_ratio = self.attack_ratio * 2
            self.pirateloss = self.pirateloss + 1
        elif 'have brought you success' in buf:
            self.attack_ratio = self.attack_ratio / 4
            self.piratewins = self.piratewins + 1

        botlog.info("Pirate record: " + 
                str(round(self.piratewins/self.piratebattles,1))+"% "+
                str(self.piratewins)+"-"+
                str(self.pirateloss)+"-"+
                str(self.piratebattles-(self.piratewins+self.pirateloss)))

        if ' Regions left] Your choice?' in buf:
            RegionBuy(self.app,self.app.data.realm.pirates.regions)
            

        # self.sp.parse(self.app, self.app.read())

        # no need to 
        # return to the spending menu
        # because we bought all the regions we could afford
        # it automatically gets back to the buy menu

        
        


