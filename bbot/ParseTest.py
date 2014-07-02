#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
import re
import bbot.botlog
from bbot.PreTurnsParser import PreTurnsParser
import os


class ParseTest:
    def __init__(self, app):
        self.data_dir = app.get_data_dir()

    def t01_ParseTest(self, app):
        datafile = os.path.join(self.data_dir,"t01_ParseTest_in.txt.txt")
        botlog.debug("Testing events parsing on")

        parser = PreTurnsParser()

        for line in file(datafile):
            parser.parse(app,line)

        event = app.data.realm.events[0]

    def test(self, app):

        self.t01_ParseTest(app)



