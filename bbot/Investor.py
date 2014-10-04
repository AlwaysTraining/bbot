#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
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
        self.first_turn = True

    def on_bank_menu(self):
        # we are not going to invest until the bank is full, its rate is always
        #   higher.  Well should be higher, we have the data to check. but in
        #   15 years of playing I never saw the invest rate higher than the
        #   bank rate.

        # also make sure we have a decent ammount of cash on hand, and we
        # are not fully invested
        realm = self.data.realm
        setup = self.data.setup

        first_turn = self.first_turn
        self.first_turn = False
        full_bank = realm.bank.gold >= 0.95 * TWOBIL
        high_cash = realm.gold >= 0.75 * TWOBIL
        low_cash = realm.gold <= HUNMIL
        war_time = self.app.has_strategy("War") and self.app.data.has_enemy()
        full_investments = self.data.has_full_investments()
        mostly_full_investments = self.data.has_full_investments(days_missing=2)
        # can't rely on parsed turns remaining, because that won't happen yet

        # default end of day to be true so we ar emore conservative, if there
        # are parsing problems or restarts it may not be absolutely determinable
        # if this end of the day
        end_of_day = self.app.mentat.is_end_of_day()
        if not end_of_day.is_certain():
            end_of_day = True
        else:
            end_of_day = end_of_day.answer

        botlog.debug("full_bank? " + str(full_bank) + ", " +
                     "high_cash? " + str(high_cash) + ", " +
                     "low_cash? " + str(low_cash) + ", " +
                     "war_time? " + str(war_time) + ", " +
                     "full_investments? " + str(full_investments) + ", " +
                     "mostly_full_investments? " + str(mostly_full_investments) + ", " +
                     "end_of_day? " + str(end_of_day) +", " +
                     "first_turn? " + str(first_turn))

        if first_turn:
            botlog.info("Not investing because this is the first turn")
            return Strategy.UNHANDLED

        if full_investments:
            botlog.info("Not investing because investments are fill")
            return Strategy.UNHANDLED

        if not full_bank:
            botlog.info("Not investing because there is less than 2 Bil in "
                        "the bank")
            return Strategy.UNHANDLED

        if low_cash:
            botlog.info("Not investing because there is less than 100 Mil on "
                        "hand")
            return Strategy.UNHANDLED

        if war_time and not high_cash and not end_of_day:
            botlog.info("Not investing because it is wartime and we " +
                        "are not in danger of overflowing cash, and " +
                        "it is not the end of the day")
            return Strategy.UNHANDLED

        if mostly_full_investments and not high_cash and not end_of_day:
            botlog.info("No need to invest now, investments are mostly full, "
                        "it is early in the day, and we are not in danger of "
                        "overflowing cash")
            return Strategy.UNHANDLED

        max_iters = 12

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
                        readable_num(realm.gold) +
                        " gold remains onhand")

            # if the day  is fully invested, go to next day
            approx_ret = realm.bank.approx_return
            if approx_ret is None or TWOBIL - approx_ret <= 1:
                self.day += 1
            max_iters -= 1

        if max_iters == 0:
            botlog.warn("Spent too many iterations trying to invest")












