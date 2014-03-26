#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import Constants
import os
import botlog
import Utils

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





    
