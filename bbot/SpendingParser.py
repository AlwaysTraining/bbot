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
STR = STR_REGEX


class SpendingParser(StatsParser):
    def __init__(self):
        StatsParser.__init__(self)
        self.buymenu = True

    def get_patterns(self):
        return {
            re.escape('[Spending Menu]'): 0,
            re.escape('[Sell Menu]'): 1,
            "You can afford " + N + ' regions\.': 50,
            "\(C\) Coastal[ \t]+" + N: 70,
            "\(R\) River[ \t]+" + N: 80,
            "\(A\) Agricultural[ \t]+" + N: 90,
            "\(D\) Desert[ \t]+" + N: 100,
            "\(I\) Industrial[ \t]+" + N: 110,
            "\(U\) Urban[ \t]+" + N: 120,
            "\(M\) Mountain[ \t]+" + N: 130,
            "\(T\) Technology[ \t]+" + N: 140,

            "\(1\) Troopers" + S + N + S + N: 810,
            "\(2\) Jets" + S + N + S + N: 820,
            "\(3\) Turrets" + S + N + S + N: 830,
            "\(4\) Bombers" + S + N + S + N: 840,
            "\(5\) HeadQuarters" + S + N + S + N: 850,
            "\(6\) Regions" + S + N + S + N: 860,
            "\(7\) Covert Agents" + S + N + S + N: 870,
            "\(8\) Tanks" + S + N + S + N: 880,
            "\(9\) Carriers" + S + N + S + N: 890,
            "You have " + N + " gold and " + N + " turns\.": 900,

            "Game Started:" + S + STR: 1800,
            "Turns per day:" + S + N: 1810,
            "Protection Turns:" + S + N: 1820,
            "Daily Land Creation:" + S + N: 1830,
            "Planetary Tax Rate:" + S + N + "\%": 1840,
            "Maximum Players:" + S + N: 1850,
            "Bank Interest Rate:" + S + N + "\%": 1860,
            "Maintenance Costs:" + S + STR + S + "Region Cost Change:" + S + STR: 1870,
            "Trade Deal Costs:" + S + STR + S + "Attack Damage:" + S + STR: 1880,
            "Attack Rewards:" + S + STR: 1890,
            "Military purchasing:" + S + STR: 1900,
            "This game is setup for Local mode only\.": 1910,
            "This game is setup in InterBBS mode with " + N + " boards in the game\.": 1920,
            "Attack Costs:" + S + STR + S + "Terrorism Costs:" + S + STR: 1930,
            "Maximum Individual Attacks Per Day:" + S + N: 1940,
            "Maximum Group Attacks Per Day:" + S + N: 1950,
            "Maximum Terrorist Ops Per Day:" + S + N: 1960,
            "Maximum Bombing Operations Per Day:" + S + N: 1970,
            "Days before \"lost\" forces returned:" + S + N: 1980,
            "Gooie Kablooies:" + S + STR + S + "Bombing Ops:" + S + STR + S + "Missile Ops:" + S + STR: 1990,

            "We occasionally produce an additional " + N + " units from rivers\.": 2500,
            "The empire consumes " + N + " units of food yearly\.": 2510,
            "This gives the empire a minimum food surplus of " + N + " units per year\.": 2520,
            "This gives the empire a maximum food deficit of " + N + " units per year\.": 2523,
            "At our current population, we can survive for at least " + N + " years\.": 2527,

            "Your yearly income was " + N + " Gold, " + N + "\% of the world total\.": 2530,
            "Your barony's efficiency is approximately " + N + " Gold per Region\.": 2540,
            "The global average is approximately " + N + " Gold per Region\.": 2550,

            "Our military forces are functioning at " + N + "\% strength.": 2560,
            "Our gold producing regions are at " + N + "\% of normal production.": 2570,
            "Our food production techniques increased efficiency to " + N + "\%.": 2580,
            "Our industries are running at " + N + "\% efficiency.": 2590,
            "Our maintenance costs have been reduced to " + N + "\% of standard costs.": 2600,
            "Our SDI yearly funding needs have been lowered to " + N + "\% normal expenses.": 2610,
            "Food decay is at " + N + "\% of standard levels.": 2620,
            "Sell how many " + STR + "\? \(0\; " + N + "\)": 2701,
            "Buy how many " + STR + "\? \(0\; " + N + "\)": 2702,

            '\[' + N + ' Regions left\] Your choice\?': 2703,

        }

    def on_match(self, app, line, which):
        realm = app.data.realm
        army = realm.army
        regions = realm.regions
        setup = app.data.setup
        advisors = realm.advisors

        if which == 0:
            self.buymenu = True
        elif which == 0:
            self.buymenu = False
        elif which == 50:
            regions.number_affordable = self.get_num()
        elif which == 70:
            regions.coastal.number = self.get_num()
        elif which == 80:
            regions.river.number = self.get_num()
        elif which == 90:
            regions.agricultural.number = self.get_num()
        elif which == 100:
            regions.desert.number = self.get_num()
        elif which == 110:
            regions.industrial.number = self.get_num()
        elif which == 120:
            regions.urban.number = self.get_num()
        elif which == 130:
            regions.mountain.number = self.get_num()
        elif which == 140:
            regions.technology.number = self.get_num()
        elif which == 810:
            if self.buymenu: army.troopers.price = self.get_num(0)
            if not self.buymenu: army.troopers.sellprice = self.get_num(0)
            army.troopers.number = self.get_num(1)
        elif which == 820:
            if self.buymenu: army.jets.price = self.get_num(0)
            if not self.buymenu: army.jets.sellprice = self.get_num(0)
            army.jets.number = self.get_num(1)
        elif which == 830:
            if self.buymenu: army.turrets.price = self.get_num(0)
            if not self.buymenu: army.turrets.sellprice = self.get_num(0)
            army.turrets.number = self.get_num(1)
        elif which == 840:
            if self.buymenu: army.bombers.price = self.get_num(0)
            if not self.buymenu: army.bombers.sellprice = self.get_num(0)
            army.bombers.number = self.get_num(1)
        elif which == 850:
            if self.buymenu: army.headquarters.price = self.get_num(0)
            if not self.buymenu: army.headquarters.sellprice = self.get_num(0)
            army.headquarters.number = self.get_num(1)
        elif which == 860:
            if self.buymenu: regions.price = self.get_num(0)
            if not self.buymenu: regions.sellprice = self.get_num(0)
            regions.number = self.get_num(1)
        elif which == 870:
            if self.buymenu: army.agents.price = self.get_num(0)
            if not self.buymenu: army.agents.sellprice = self.get_num(0)
            army.agents.number = self.get_num(1)
        elif which == 880:
            if self.buymenu: army.tanks.price = self.get_num(0)
            if not self.buymenu: army.tanks.sellprice = self.get_num(0)
            army.tanks.number = self.get_num(1)
        elif which == 890:
            if self.buymenu: army.carriers.price = self.get_num(0)
            if not self.buymenu: army.carriers.sellprice = self.get_num(0)
            army.carriers.number = self.get_num(1)
        elif which == 900:
            realm.gold = self.get_num(0)
            realm.turns.remaining = self.get_num(1)

        elif which == 1800:
            setup.game_start_date = self.get_str()
        elif which == 1810:
            setup.turns_per_day = self.get_num()
        elif which == 1820:
            setup.protection_turns = self.get_num()
        elif which == 1830:
            setup.daily_land_creation = self.get_num()
        elif which == 1840:
            setup.planetary_tax_rate = self.get_num()
        elif which == 1850:
            setup.max_players = self.get_num()
        elif which == 1860:
            setup.interest_rate = self.get_num()
        elif which == 1870:
            setup.maint_costs = self.get_str()
            setup.region_cost = self.get_str(1)
        elif which == 1880:
            setup.trade_cost = self.get_str()
            setup.attack_damage = self.get_str(1)
        elif which == 1890:
            setup.attack_rewards = self.get_str()
        elif which == 1900:
            setup.army_purchase = self.get_str() == "Enabled"
        elif which == 1910:
            setup.local_game = True
        elif which == 1920:
            setup.interbbs_game = True
            setup.num_boards = self.get_num()
        elif which == 1930:
            setup.attack_cost = self.get_str()
            setup.terror_cost = self.get_str(1)
        elif which == 1940:
            setup.num_indie_attacks = self.get_num()
        elif which == 1950:
            setup.num_group_attacks = self.get_num()
        elif which == 1960:
            setup.num_tops = self.get_num()
        elif which == 1970:
            setup.num_bops = self.get_num()
        elif which == 1980:
            setup.days_for_mit = self.get_num()
        elif which == 1990:
            setup.gooies = self.get_str() == "Enabled"
            setup.bombing_ops = self.get_str(1) == "Enabled"
            setup.missle_ops = self.get_str(2) == "Enabled"

        elif which == 2500:
            advisors.civilian.river_food_production = self.get_num()
        elif which == 2510:
            advisors.civilian.food_consumption = self.get_num()
        elif which == 2520:
            advisors.civilian.food_surplus = self.get_num()
        elif which == 2523:
            advisors.civilian.food_deficit = self.get_num()
        elif which == 2527:
            advisors.civilian.years_survival = self.get_num()
        elif which == 2530:
            advisors.economic.income = self.get_num()
            advisors.economic.world_income_ratio = self.get_num(1)
        elif which == 2540:
            advisors.economic.efficiency = self.get_num()
        elif which == 2550:
            advisors.economic.global_avg_efficiency = self.get_num()
        elif which == 2560:
            advisors.technology.mil_tech = self.get_num()
        elif which == 2570:
            advisors.technology.gold_tech = self.get_num()
        elif which == 2580:
            advisors.technology.food_tech = self.get_num()
        elif which == 2590:
            advisors.technology.industry_tech = self.get_num()
        elif which == 2600:
            advisors.technology.maint_tech = self.get_num()
        elif which == 2610:
            advisors.technology.sdi_tech = self.get_num()
        elif which == 2620:
            advisors.technology.food_decay_tech = self.get_num()
        elif which == 2701 or which == 2702:
            app.metadata.max_ammount = self.get_num(1)
            botlog.debug("Set max ammount to " + str(app.metadata.max_ammount))
        elif which == 2703:
            app.metadata.regions_left = self.get_num()
