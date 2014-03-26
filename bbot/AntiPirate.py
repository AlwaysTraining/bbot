#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
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
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.ratio = 0.02
        self.attack_tuner = AutoTuner(True, self.ratio, 0.00001, 0.25)
        self.pp = PirateParser()
        self.last_result = None

    def on_attack_menu(self):

        if not self.data.can_get_attack_strength():
            botlog.warn("Unable to determine attack strength, has spending "
                        "menu been parsed?")
            return Strategy.UNHANDLED

        # if we have no army, don't attack
        if self.data.get_attack_strength() <= 0:
            botlog.info("No army, so not attacking pirates")
            return Strategy.UNHANDLED

        self.data.realm.reset_pirates()

        self.app.send('p', comment='go from attack menu to pirate menu')

        buf = self.app.read()

        self.app.send(randint(1, 9),
                      comment='from pirate menu to randomly chosen pirate')
        buf = self.app.read()

        ratio = self.ratio
        troopers = int(self.app.data.realm.army.troopers.number * ratio)

        self.app.sendl(troopers, comment='troopers for pirate attack')
        buf = self.app.read()

        jets = int(self.app.data.realm.army.jets.number * ratio)

        self.app.sendl(jets, comment='jets for pirate attack')
        buf = self.app.read()

        tanks = int(self.app.data.realm.army.tanks.number * ratio)

        self.app.sendl(tanks, comment='tanks for pirate attack')

        # I had a bug where pirate results were not returned in time, rather
        # then resort to state based parsing, we will just wait for the results
        # to come in.  This will get annoying if we ever decide to fully parse
        # pirate attack resultsg31
        buf = self.app.read_until_any([
            'You could not successfully raid',
            'have brought you success'])
        self.pp.parse(self.app, buf)

        if self.app.match_index == 0:
            self.last_result = False
        elif self.app.match_index == 1:
            self.last_result = True
        else:
            raise Exception('Error after waiting for pirate attack results')

        self.ratio = self.attack_tuner.get_next_value(self.last_result)
        botlog.info("Pirate record: " + str(self.attack_tuner))

        # finish reading pirate results
        buf = self.app.read()
        self.pp.parse(self.app, buf)

        # [1 Regions left] Your choice?
        if ' Regions left] Your choice?' in buf:
            botlog.info("Allocating " +
                        str(self.app.data.realm.pirates.regions) +
                        " pirate booty regions")
            RegionBuy(self.app, self.app.data.realm.pirates.regions)

        botlog.info('AntiPirate strategy handler')
        # self.sp.parse(self.app, self.app.read())

        # no need to 
        # return to the spending menu
        # because we bought all the regions we could afford
        # it automatically gets back to the buy menu

        
        


