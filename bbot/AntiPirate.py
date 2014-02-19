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
from bbot.AutoTuner import AutoTuner

S = SPACE_REGEX
N = NUM_REGEX


class AntiPirate(Strategy):
    def __init__(self,app):
        Strategy.__init__(self,app)
        self.data = self.app.data
        self.attack_tuner=AutoTuner(True,0.25,0.0001,0.5)
        self.pp=PirateParser()
        self.last_result = None

    def on_attack_menu(self):

        self.data.realm.reset_pirates()

        self.app.send('p',comment='go from attack menu to pirate menu')

        buf = self.app.read()

        self.app.send(randint(1,9),comment='from pirate menu to randomly chosen pirate')
        buf = self.app.read()

        ratio = self.attack_tuner.get_next_value(self.last_result)

        troopers = int(self.app.data.realm.army.troopers.number * ratio)

        self.app.sendl(troopers,comment='troopers for pirate attack')
        buf = self.app.read()

        jets = int(self.app.data.realm.army.jets.number * ratio)

        self.app.sendl(jets,comment='jets for pirate attack')
        buf = self.app.read()

        tanks = int(self.app.data.realm.army.tanks.number * ratio)

        self.app.sendl(tanks,comment='tanks for pirate attack')

        buf = self.app.read()
        self.pp.parse(self.app, buf)

        if 'You could not successfully raid' in buf:
            self.last_result = False
        elif 'have brought you success' in buf:
            self.last_result = True

        botlog.info("Pirate record: " + str(self.attack_tuner))

        if ' Regions left] Your choice?' in buf:
            RegionBuy(self.app,self.app.data.realm.pirates.regions)
            

        # self.sp.parse(self.app, self.app.read())

        # no need to 
        # return to the spending menu
        # because we bought all the regions we could afford
        # it automatically gets back to the buy menu

        
        


