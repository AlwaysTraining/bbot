#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import Constants
import os
import botlog
import Utils

UNHANDLED="bbot_UNHANDLED"
TERMINATE="bbot_TERMINATE"
CONSUMED="bbot_CONSUMED"

class Strategy:

    UNHANDLED="bbot_UNHANDLED"
    TERMINATE="bbot_TERMINATE"
    CONSUMED="bbot_CONSUMED"


    def __init__(self, app):
        self.app = app
        self.lastState = None
        
    def get_indicators(self):
        return {}


    def get_priority(self,state):
        return Utils.NO_PRIORITY


    def base_on_indicator(self, state):
        botlog.debug(self.get_name() + " handling state " + str(state) + 
                ', lastState ' + str(self.lastState))
        s = self.on_indicator(self.lastState, state)
        if s != UNHANDLED:
            self.lastState = state
        else:
            botlog.debug(self.get_name() + " state " + str(state) + " was unhandled")

        return s
        

    def on_indicator(self, lastState, state):
        return UNHANDLED

    def get_name(self):
        return self.__class__.__name__


class Strategies :

    name_to_strat_map = {}
    indicator_to_records_map = {}

    class Record:
        strategy=None
        indicator=None
        priority=None
        state=None

    
    def __init__(self, app, strats):
        # shouldn't happen with cmd line checking


        if strats is None:
            raise Exception("No Strategies provided")

        # dynamically load all strategies given form the command line
        for strstrat in strats:
            codepath = os.path.join(os.path.dirname(__file__),strstrat + ".py")
            strat = Utils.create_instance(codepath, strstrat,app=app)

            self.name_to_strat_map[strat.get_name()] = strat

        
        # iterate through all the strategies collecting all of the indicators
        for sname,s in self.name_to_strat_map.items():
            # get the indicators for the current stratefy
            stateindicators = s.get_indicators()
            for indicator,state in stateindicators.items():


                # Get the record for all occurances of this indicator if it exists
                if indicator in self.indicator_to_records_map:
                    records = self.indicator_to_records_map[indicator]
                else:
                    records = []
                    self.indicator_to_records_map[indicator] = records

                # add in this indicator a record for the state value
                rec = Strategies.Record()
                rec.strategy = s
                rec.indicator = indicator
                rec.state = state
                rec.priority = s.get_priority(state)


                records.append(rec)

        # sort records in order of priority
        for recordLists in self.indicator_to_records_map.values():
            recordLists.sort(key=lambda record: record.priority, reverse = True)

    def get_keys(self):
        return self.indicator_to_records_map.keys()

    def get_key(self, keyIndex):
        return self.get_keys()[keyIndex]

    def enumerate_matches(self, keyIndex):
        key = self.get_key(keyIndex)
        recordList = self.indicator_to_records_map[key]
        for record in recordList:
            yield record




    
