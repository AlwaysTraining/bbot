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

        # also make sure we have a decent ammount of cash on hand, and we
        # are not fully invested
        realm = self.data.realm

        # returning UNHANDLED prevents investments from being re parsed when we know they didn't changed
        if realm.bank.gold < TWOBIL:
            botlog.info("Not investing because there is less than 2 Bil in "
                        "the bank")
            return Strategy.UNHANDLED
        if realm.gold < HUNMIL:
            botlog.info("Not investing because there is less than 100 Mil on "
                        "hand")
            return Strategy.UNHANDLED
        if self.data.has_full_investments():
            botlog.info("Not investing because there is are already full "
                        "investments")
            return Strategy.UNHANDLED

        max_iters = 11

        while (realm.gold > HUNMIL and
                       self.day <= 10 and
                       max_iters >= 0):
            self.app.send_seq(['i', self.day, '\r', '>', '\r'],
                              comment="investing " + str(
                                  self.day) + " days out")

            buf = self.app.read()
            realm.bank.approx_return = None
            self.ip.parse(self.app, buf)
            if "Accept? (Y/n)" in buf:
                self.app.send('y', comment='Accepting investment')

            buf = self.app.read()
            self.ip.parse(self.app, buf)
            botlog.info("After investing, " +
                        str(realm.gold) +
                        " gold remains onhand")

            # if the day  is fully invested, go to next day
            approx_ret = realm.bank.approx_return
            if approx_ret is None or TWOBIL - approx_ret <= 1:
                self.day = self.day + 1
            max_iters = max_iters - 1

        if max_iters == 0:
            raise Exception("Spent too many iterations trying to invest")












