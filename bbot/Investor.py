#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.InvestmentParser import InvestmentParser

S = SPACE_REGEX
N = NUM_REGEX

TWOBIL = 2000000000
HUNMIL = 100000000

class Investor(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.has_full_inv = False
        self.ip = InvestmentParser()
        self.day = 2

    def on_bank_menu(self):
        # we are not going to invest until the bank is full, its rate is always
        #   higher.  Well should be higher, we have the data to check. but in
        #   15 years of playing I never saw the invest rate higher than the
        #   bank rate.

        # also make sure we have a decent ammoutn of cash on hand
        if self.data.realm.bank.gold < TWOBIL or self.data.realm.gold < HUNMIL:
            return

        # list the investments, and parse them
        self.app.send("l")
        buf = self.app.read()
        self.data.realm.bank.investments = []
        self.ip.parse(buf)


        while self.data.realm.gold < HUNMIL and self.day <= 10:
            self.app.send_seq(['i',self.day,'\r','>'])

            buf = self.app.read()
            if "Accept? (Y/n)" in buf:
                self.app.send_seq('y'   )
            # TODO, figure out sequence

            return









