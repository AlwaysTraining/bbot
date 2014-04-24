#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import re
import botlog
from bbot.Utils import *
from bbot.StatsParser import StatsParser

S = SPACE_REGEX
N = NUM_REGEX


class TurnStatsParser(StatsParser):
    def __init__(self):
        StatsParser.__init__(self)
        self.buymenu = True

    def get_patterns(self):
        return {

            N + ' gold was earned in taxes.': 500,
            N + ' gold was produced from the Ore Mines.': 510,
            N + ' gold was earned in Tourism.': 520,
            N + ' gold was earned by Solar Power Generators.': 530,
            N + ' gold was created by Hydropower.': 540,
            N + ' Food units were grown.': 550,

            N + ' Troopers were manufactured by Industrial Zones.': 560,
            N + ' Turrets were manufactured by Industrial Zones.': 570,
            N + ' Jets were manufactured by Industrial Zones.': 580,
            N + ' Carriers were manufactured by Industrial Zones.': 590,
            N + ' Bombers were manufactured by Industrial Zones.': 600,
            N + ' Tanks were manufactured by Industrial Zones.': 610,
            N + ' gold was earned from investment returns.': 620,
            "\-\*(.+)\*\-": 200,
            "Turns: " + N: 210,
            "Score: " + N: 220,
            "Gold: " + N: 230,
            "Bank: " + N: 240,
            "Population: " + N + " Million \(Tax Rate: " + N + "\%": 250,
            "Popular Support: " + N + "\%": 260,
            "Food: " + N: 270,
            "Agents: " + N: 280,
            "Headquarters: " + N + "\% Complete": 290,
            "SDI Strength: " + N + "\%": 300,
            "This is year " + N + " of your freedom.": 310,
            "You have " + N + " Years of Protection Left.": 320,
        }


    def on_match(self, app, line, which):
        realm = app.data.realm
        army = realm.army
        regions = realm.regions

        if which == 200:
            realm.name = self.get_str()
        elif which == 210:
            realm.turns.current = self.get_num()
        elif which == 220:
            realm.score = self.get_num()
        elif which == 230:
            realm.gold = self.get_num()
        elif which == 240:
            realm.bank.gold = self.get_num()
        elif which == 250:
            realm.population.size = self.get_num(0)
            realm.population.rate = self.get_num(1)
        elif which == 260:
            realm.population.pop_support = self.get_num()
        elif which == 270:
            realm.food.units = self.get_num()
        elif which == 280:
            army.agents.number = self.get_num()
        elif which == 290:
            army.headquarters.number = self.get_num()
        elif which == 300:
            army.sdi = self.get_num()
        elif which == 500:
            realm.population.taxearnings = self.get_num()
        elif which == 510:
            regions.mountain.earnings = self.get_num()
        elif which == 520:
            regions.coastal.earnings = self.get_num()
        elif which == 530:
            regions.desert.earnings = self.get_num()
        elif which == 540:
            regions.river.earnings = self.get_num()
        elif which == 550:
            regions.agricultural.foodyield = self.get_num()
        elif which == 310:
            realm.turns.years_freedom = self.get_num()
            realm.turns.years_protection = None
        elif which == 320:
            realm.turns.years_protection = self.get_num()
            realm.turns.years_freedom = None
        elif which == 560:
            manufacture.troopers.production = self.get_num()
        elif which == 580:
            manufacture.jets.production = self.get_num()
        elif which == 570:
            manufacture.turrets.production = self.get_num()
        elif which == 600:
            manufacture.bombers.production = self.get_num()
        elif which == 610:
            manufacture.tanks.production = self.get_num()
        elif which == 590:
            manufacture.carriers.production = self.get_num()



