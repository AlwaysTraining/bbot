#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import Constants
import os
import botlog
import Utils
import math

from bbot.SpendingParser import SpendingParser

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

    def on_main_menu(self):
        return UNHANDLED

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

    def has_strategy_option(self, name):
        option = self.get_name() + "_" + name
        return self.app.has_app_value(option)

    def get_strategy_option(self, name):
        option = self.get_name() + "_" + name
        return self.app.get_app_value(option)

    def try_get_strategy_option(self, name, default):
        option = self.get_name() + "_" + name
        return self.app.try_get_app_value(option,default)

    def buy_army_units(self, unit_types, buyratio=None, desired_ammount=None):

        if ((buyratio is None and desired_ammount is None) or
                (buyratio is not None and desired_ammount is not None)):
            raise Exception("Must use either a buyratio or desired_ammount")

        botlog.debug("Requested buy with buyratio: " + str(buyratio))
        botlog.debug("Requested buy with desired_ammount: " + str(
            desired_ammount))

        sp = SpendingParser()

        if isinstance(unit_types, basestring):
            unit_types = Utils.make_string_list(unit_types)

        if unit_types is None or len(unit_types) == 0:
            raise Exception("No unit_types provided")
        tot_ammount = 0

        for unit_type in unit_types:
            # Assume at buy menu
            item = self.app.data.get_menu_option(unit_type)
            ammount = desired_ammount

            # determine number to buy
            price = self.app.data.get_price(item)
            if buyratio is not None:
                gold = self.data.realm.gold * buyratio
                ammount = gold / price
            elif ammount is None:
                raise Exception("Did not specify ratio or ammount of " + str(
                    unit_type) + " to buy")

            ammount = int(math.floor(ammount))

            if ammount <= 0:
                botlog.info("Could not afford even 1 " + unit_type)
            else:
                self.app.send(item, comment="buying " + unit_type)

                self.app.metadata.max_ammount = -1
                sp.parse(self.app, self.app.read())

                if self.app.metadata.max_ammount == -1:
                    raise Exception("Unable to read max buy amount")

                # if amount for buy is more than possible
                if self.app.metadata.max_ammount < ammount:
                    # cap off how much we are buying
                    ammount = self.app.metadata.max_ammount
                    botlog.debug("Capping max buy to " + str(ammount))

                # buy the items
                self.app.sendl(ammount,
                               comment="Buying " + str(
                                   ammount) + " " + unit_type)
                sp.parse(self.app, self.app.read())
                tot_ammount += ammount

        return tot_ammount


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





    
