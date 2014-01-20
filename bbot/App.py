#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import Constants
import os,sys
import pexpect
import random
import time
import logging
import Utils
from bbot import *

class App:

    def __init__(self, options, query_func, secret_query_func):
        self.options = options
        self.query_func = query_func
        self.secret_query_func = secret_query_func

    def get_app_value(self, key, secret=False):
        # Check if value is in options
        if key in self.options and self.options[key] is not None:
            if not secret:
                print '[options]', key,':',self.options[key]
            return self.options[key]

        environkey = Constants.ENVIRON_PREFIX + key
        # otherwise check if value is in environment
        if environkey in os.environ and self.options[key] != '':
            if not secret:
                print '[environment]', environkey,':',os.environ[environkey]
            return os.environ[environkey]
        
        # otherwise call query function, or secretquery Func
        if secret:
            return self.secret_query_func('Please enter ' + key)


    def send(self, msg, eol=False):
        """
        Send a message to the client use some rudemantry random delay to semi similate a human's typing
        """

        time.sleep(1)

        for c in msg:
            time.sleep(random.uniform(0.25, 0.75))
            self.telnet.send(c)

        if eol:
            time.sleep(random.uniform(0.25, 0.75))
            self.telnet.sendline('\r')

    def sendl(self,msg=''):
        self.send(msg,True)

   
    def run(self):

        # begin the telnet session
        self.telnet = pexpect.spawn('telnet ' + self.get_app_value('address'), logfile=sys.stdout)

        # get list of strategies from user
        stratgem = {}
        strats = self.get_app_value('strategies')

        # if one string is provided, someitmes they can just give it to us as one string,
        #   convert it to a list to implify 
        if isinstance(strats, basestring):
            strats = [strats]

        # shouldn't happen with cmd line checking
        if strats is None:
            raise Exception("No Strategies provided")

        # dynamically load all strategies given form the command line
        for strstrat in strats:
            codepath = os.path.join(os.path.dirname(__file__),strstrat + ".py")
            strat = Utils.create_instance(codepath, strstrat,app=self)

            stratgem[strat.get_name()] = strat


        # pull indicators out of the strategies into a collection keyed by indicator
        # each indicator correspnds to a dictionary of strategies that use that indicator
        indicators = {}
        

        # iterate through all the strategies collecting all of the indicators
        for sname,s in stratgem.items():
            # get the indicators for the current stratefy
            stateindicators = s.get_indicators()
            for indicator,state in stateindicators.items():

                # Get the record for all occurances of this indicator if it exists
                if indicator in indicators:
                    indicatorRec = indicators[indicator]
                else:
                    indicatorRec = {}
                    indicators[indicator] = indicatorRec

                # add in this indicator a record for the state value
                indicatorRec[sname] = (s,state)

        keys = indicators.keys()

        # repeat forever or until we think of something better to do
        while True:

            # expect the unified list of all possible indicators
            print '\n\n', 'EXPECTING', keys,'\n\n'

            key = self.telnet.expect(keys)

            print '\n\n', 'MATCHED', keys[key],'\n\n'

            # expect returns the index into the list, use this to locate the record 
            #   for the strategies and states tied to this keyword
            indicatorRec = indicators[keys[key]]

            # iterate each indicator
            for indicator,strategyState in indicatorRec.items():

                    s = strategyState[0]
                    state = strategyState[1]
                    s.base_on_indicator(state)



