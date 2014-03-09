#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.MaintParser import MaintParser

S = SPACE_REGEX
N = NUM_REGEX




class Investor(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.has_full_inv = False
        self.ip = MaintParser()
        self.day = 2

    def on_bank_menu(self):
        # we are not going to invest until the bank is full, its rate is always
        #   higher.  Well should be higher, we have the data to check. but in
        #   15 years of playing I never saw the invest rate higher than the
        #   bank rate.

        # also make sure we have a decent ammoutn of cash on hand, and we
        # are not fully invested
        if (self.data.realm.bank.gold < TWOBIL or
            self.data.realm.gold < HUNMIL or
            self.data.has_full_investments()):
            return

        max_iters = 11

        while (self.data.realm.gold < HUNMIL and
                       self.day <= 10 and
                       max_iters > 0):
            self.app.send_seq(['i', self.day, '\r', '>'],
                              comment="investing " + str(
                                  self.day) + " days out")

            buf = self.app.read()
            self.data.realm.bank.approx_return = None
            self.ip.parse(buf)
            if "Accept? (Y/n)" in buf:
                self.app.send('y', comment='Accepting investment')

            buf = self.app.read()
            self.ip.parse(buf)
            botlog.info("After investing, " +
                        str(self.data.realm.gold) +
                        " gold remains")

            # if the day  is fully invested, go to next day
            if TWOBIL - data.realm.bank.approx_return <= 1:
                self.day = self.day + 1
            max_iters = max_iters - 1

        if max_iters == 0:
            raise Exception("Spent too many iterations trying to invest")












