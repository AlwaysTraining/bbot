#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
import bbot.botlog
from bbot.LocalLackey import LocalLackey
import os


class LocalLackeyTest:
    def __init__(self, app):
        self.app = app
        self.data_dir = app.get_data_dir()

    def t02_calc_realm_trade_ratio_test(self, app):
        botlog.debug("Testing calc realm trade ratio parsing on")

        lackey = LocalLackey(self.app)

        testuples = [
            (100, 1.0, 1.00, 0, 1),
            (200, 1.0, 0.50, 0, 2),
            (210, 1.0, 1.00, 1, 2),
            (400, 1.0, 0.25, 0, 4),
            (410, 1.0, 1/3.0, 1, 4),
            (420, 1.0, 0.5, 2, 4),
            (430, 1.0, 1.0, 3, 4),
        ]

        for testuple in testuples:
            app.options["LocalLackey_tribute_ratio"] = testuples[1]

            if testuple[2] != lackey.calc_realm_trade_ratio(
                    testuple[1], testuple[3], testuple[4]):

                raise Exception("Error in calc realm trade ratio case: " +
                                str(testuple[0]))

        botlog.debug("Done testing trade ratio calculations")



    def test(self, app):

        self.t02_calc_realm_trade_ratio_test(app)



