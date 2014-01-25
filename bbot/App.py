#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import Constants
import os,sys
import pexpect
import random
import time
import botlog
import Utils
import Data
import Strategy
from bbot import *
import botlog
import string

valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits) 

class App:

    def get_data_dir(self):
        return "."

    def get_tag_str(self,joiner='_'):
        s = joiner.join([
                "bbot",
                self.get_app_value('address'),
                self.get_app_value('game'),
                self.get_app_value('realm')])
       
        s = ''.join(c for c in s if c in valid_chars)
       
        return s

    def file_roll(self,suffix):
        logfile = os.path.join(self.get_data_dir(),
                self.get_tag_str() + suffix)
        if os.path.exists(logfile):
            oldlogfile = logfile + "." + str(Utils.modification_date(logfile))
            os.rename(logfile,oldlogfile)
        return logfile

    def __init__(self, options, query_func, secret_query_func):
        self.options = options
        self.query_func = query_func
        self.secret_query_func = secret_query_func
        self.data = Data.Data()

        level=botlog.DEBUG
        self.logfile=None
        self.tracefile=None
        debug=True
        if not self.get_app_value('debug'):
            level=botlog.INFO
            self.logfile = self.file_roll('.log')
            self.tracefile = self.file_roll('.out')
            debug=False
            
        botlog.configure(
                level=level,
                format='\n%(asctime)s:%(levelname)s::%(message)s',
                logpath=self.logfile,
                tracepath=self.tracefile)


    def get_app_value(self, key, secret=False):
        # Check if value is in options
        if key in self.options and self.options[key] is not None:
            if not secret:
                botlog.debug( 'reading application value [options] '+ key+' : '+str(self.options[key]))
            return self.options[key]

        environkey = Constants.ENVIRON_PREFIX + key
        # otherwise check if value is in environment
        if environkey in os.environ and self.options[key] != '':
            if not secret:
                botlog.debug( 'reading application value [environment] '+ environkey + ' : ' + os.environ[environkey])
            return os.environ[environkey]
        
        # otherwise call query function, or secretquery Func
        if secret:
            return self.secret_query_func('Please enter ' + key)

        return self.query_func(key)

    def get_close_float(self,x):
        return random.uniform(x*0.75,x*1.25)

    def send(self, msg, eol=False, sleep=1.5):
        """
        Send a message to the client use some rudemantry random delay to semi similate a human's typing
        """

        if msg is not None:
            for c in msg:
                time.sleep(selg.get_close_float(sleep))
                self.telnet.send(c)

        if eol:
            time.sleep(selg.get_close_float(sleep))
            self.telnet.sendline('\r')

    def sendl(self,msg='',sleep=0.5):
        self.send(msg,eol=True,sleep=sleep)

    def get_num(self, matchIndex=0):
        """
        Get a number from the current matchign regex group
        """
        return Utils.ToNum(self.telnet.match.groups()[matchIndex])

   
    def run_loop(self):


        # begin the telnet session

        self.telnet = pexpect.spawn('telnet ' + self.get_app_value('address'), 
                logfile=botlog.tracefile)

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

            botlog.debug( 'Matched: ' + keys[key])

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


    def send_notification(self, game_exception):
        if "notify" not in self.options or self.options['notify'] is None:
            botlog.info("No notification email address provided")
            return

        to = self.get_app_value('notify')
        if isinstance(to, basestring):
            to = [to]


        botlog.info("Sending Notification emails to " + str(to))

        files = []
        if self.logfile is not None:
            # close the logger
            files.append(self.logfile)
        if self.tracefile is not None:
            files.append(self.tracefile)

        subject = "Success"
        body = "TODO, Fancy Summary"
        if game_exception is not None:
            subject = "Failure"
            body = str(game_exception)


        Utils.send_mail(
            to,
            '[' + self.get_tag_str(' ') + '] ' + subject,
            body,
            _from='bbot@' + self.get_app_value('address'),
            files=files,
            server=self.get_app_value('smtp_server'),
            port=self.get_app_value('smtp_port'),
            server_user=self.get_app_value('smtp_user'),
            server_user_pass=self.get_app_value('smtp_password',secret=True))
            

    def run(self):
        
        game_exception = None
        try:
            botlog.info("bbot has begun")

            self.run_loop()

            botlog.info("bbot has completed")
        except Exception, e:
            botlog.exception(e)
            game_exception = e

        

        self.send_notification(game_exception)
        
