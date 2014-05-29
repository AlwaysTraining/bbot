#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import Constants
import os
import botlog
import Utils
import math

UNHANDLED = "bbot_UNHANDLED"
TERMINATE = "bbot_TERMINATE"
CONSUMED = "bbot_CONSUMED"


class Strategy:
    UNHANDLED = "bbot_UNHANDLED"
    TERMINATE = "bbot_TERMINATE"
    CONSUMED = "bbot_CONSUMED"


    def __init__(self, app):
        self.app = app

    def get_priority(self):
        return Utils.NO_PRIORITY

    def get_name(self):
        return self.__class__.__name__

    def on_spending_menu(self):
        return UNHANDLED

    def on_industry_menu(self):
        return UNHANDLED

    def on_attack_menu(self):
        return UNHANDLED

    def on_trading_menu(self):
        return UNHANDLED

    def on_diplomacy_menu(self):
        return UNHANDLED

    def on_bank_menu(self):
        return UNHANDLED

    def on_interplanetary_menu(self):
        return UNHANDLED


    def get_strategy_option(self, name):
        option = self.get_name() + "_" + name
        return self.app.get_app_value(option)

    def buy_army_units(self, unit_types, buyratio, ammount = None):

        if isinstance(unit_types, basestring):
            if ',' in unit_types:
                unit_types = [x.strip() for x in unit_types.split(',')]
            else:
                unit_types = [unit_types]

        if unit_types is None:
            raise Exception("No unit_types provided")


        if isinstance(unit_types, basestring):
            unit_types = [unit_types]


        for unit_type in unit_types:
            # Assume at buy menu
            item = self.app.data.get_menu_option(unit_type)

            # determine number to buy
            price = self.app.data.get_price(item)
            if buyratio is not None:
                gold = self.data.realm.gold * buyratio
                ammount = gold / price
            elif ammount is None:
                raise Exception("Did not specify ratio or ammount of " + str(
                    unit_type) + " to buy")

            ammount = int(math.floor(ammount))

            if ammount == 0:
                botlog.info("Could not afford even 1 " + unit_type)
            else:
                self.app.send(item, comment="buying " + unit_type)
                self.sp.parse(self.app, self.app.read())

                # if max ammoutn for buy is more than possible
                if self.app.metadata.max_ammount > ammount:
                    # cap off how much we are buying
                    ammount = self.app.metadata.max_ammount

                # buy the items
                self.app.sendl(ammount,
                               comment="Buying " + str(ammount) + " " + unit_type)

        return ammount


class Strategies(list):
    def __init__(self, app, strats):
        # shouldn't happen with cmd line checking

        list.__init__(self)

        if strats is None:
            raise Exception("No Strategies provided")


        # dynamically load all strategies given form the command line
        for strstrat in strats:
            codepath = os.path.join(os.path.dirname(__file__), strstrat + ".py")
            strat = Utils.create_instance(codepath, strstrat, app=app)

            self.append(strat)

        # sort strategies in desending order of priority
        self.sort(key=lambda s: s.get_priority(), reverse=True)





    
