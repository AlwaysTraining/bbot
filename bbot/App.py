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
import Data
import Strategy
from bbot import *

class App:

    def __init__(self, options, query_func, secret_query_func):
        self.options = options
        self.query_func = query_func
        self.secret_query_func = secret_query_func
        self.data = Data.Data()

    def get_app_value(self, key, secret=False):
        # Check if value is in options
        if key in self.options and self.options[key] is not None:
            if not secret:
                logging.debug( 'reading application value [options] '+ key+' : '+str(self.options[key]))
            return self.options[key]

        environkey = Constants.ENVIRON_PREFIX + key
        # otherwise check if value is in environment
        if environkey in os.environ and self.options[key] != '':
            if not secret:
                logging.debug( 'reading application value [environment] '+ environkey + ' : ' + os.environ[environkey])
            return os.environ[environkey]
        
        # otherwise call query function, or secretquery Func
        if secret:
            return self.secret_query_func('Please enter ' + key)

        return self.query_func(key)


    def send(self, msg, eol=False, sleep=(1,2)):
        """
        Send a message to the client use some rudemantry random delay to semi similate a human's typing
        """

        if msg is not None:
            for c in msg:
                time.sleep(random.uniform(sleep[0],sleep[1]))
                self.telnet.send(c)

        if eol:
            time.sleep(random.uniform(sleep[0],sleep[1]))
            self.telnet.sendline('\r')

    def sendl(self,msg=''):
        self.send(msg,True)

    def get_num(self, matchIndex=0):
        """
        Get a number from the current matchign regex group
        """
        return Utils.ToNum(self.telnet.match.groups()[matchIndex])

   
    def run(self):

        logging.info("bbot has begun")

        # begin the telnet session
        # fout = file('mylog.txt','w')
        fout = sys.stdout
        self.telnet = pexpect.spawn('telnet ' + self.get_app_value('address'), logfile=fout)

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
        running = True
        while running:

            # expect the unified list of all possible indicators
            # print '\n\n', 'EXPECTING', keys,'\n\n'

            key = self.telnet.expect(keys)

            logging.debug( 'Matched: ' + keys[key])

            # expect returns the index into the list, use this to locate the record 
            #   for the strategies and states tied to this keyword
            indicatorRec = indicators[keys[key]]

            # iterate each indicator
            for indicator,strategyState in indicatorRec.items():

                s = strategyState[0]
                state = strategyState[1]
                action = s.base_on_indicator(state)
                if action == Strategy.TERMINATE:
                    self.telnet.close()
                    running = False
                    break

        logging.info("bbot has completed")


