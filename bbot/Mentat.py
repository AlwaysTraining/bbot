#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import botlog
from bbot.Data import *
from bbot.Utils import *

class PrimeProjection:
    def __init__(self, answer=None, confidence=None):
        self.answer = answer
        self.confidence = confidence

    def is_low_confidence(self):
        return self.confidence is None or self.confidence < 0.5
    def is_high_confidence(self):
        return not self.is_low_confidence()
    def is_certain(self):
        return self.confidence >= 1.0

    def __str__(self):
        stringrep = str(self.answer)
        if not self.is_certain():
            stringrep += (" (confidence " +
                          str(round(self.confidence*100)) + "%")
        return stringrep

class Mentat:

    def __init__(self, app):
        self.app = app
        self.data = app.data


    def is_end_of_day(self):
        end_of_day = True
        confidence = 0.0
        realm = self.data.realm
        if realm.turns.remaining is not None:
            confidence = 1.0
            end_of_day = realm.turns.remaining <= END_OF_DAY_TURNS

        return PrimeProjection(
            answer=end_of_day,
            confidence=confidence)
