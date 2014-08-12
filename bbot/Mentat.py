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
        botlog.debug("Determining if it is the end of the day")
        end_of_day = False
        confidence = 0.0
        realm = self.data.realm
        if realm.turns.remaining is not None:
            botlog.debug("Turns remaining is set and is: " +
                         str(realm.turns.remaining))
            confidence = 1.0
            end_of_day = realm.turns.remaining <= END_OF_DAY_TURNS
        elif realm.turns.current is not None:
            maxturns = 8
            if self.data.setup is not None and self.data.setup.turns_per_day is not None:
                maxturns = self.data.setup.turns_per_day

                botlog.debug("Turns remaining not set, but max turns is: " +
                             str(maxturns))

                confidence = 1.0
            else:
                confidence = 0.5
                botlog.debug("Turns remaining not set, but max turns blindly "
                             "assumed at: " + str(maxturns))
            end_of_day = maxturns - realm.turns.current <= END_OF_DAY_TURNS
            botlog.debug("Turns remaining calculated to probably be: " +
                         str(realm.turns.remaining))

        return PrimeProjection(
            answer=end_of_day,
            confidence=confidence)
