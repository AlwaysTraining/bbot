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

valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits) 

class App:

    def get_data_dir(self):
        return "."

    def get_tag_str(self,joiner='_'):
        s = joiner.join([
                "bbot",
                self.get_app_value('address'),
                self.get_app_value('game'),
                self.get_app_value('realm')])
       
        s2 = []
        for c in s:
            if c in valid_chars:
                s2.append(c)
            else:
                s2.append('_')
        s = ''.join(s2)

#       Just remove chars
#        s = ''.join(c for c in s if c in valid_chars)
       
        return s

    def file_roll(self,suffix):

        name = self.get_tag_str() + '_' + suffix + ".txt"
        logfile = os.path.join(self.get_data_dir(), name)

        if os.path.exists(logfile):
            name = self.get_tag_str() + suffix + ".txt"
            logdir = os.path.join(self.get_data_dir(),'old')

            if not os.path.exists(logdir):
                os.makedirs(logdir)

            oldname = (self.get_tag_str() + '_' +  
                    str(Utils.modification_date(logfile)) + '_'
                        + suffix + ".txt")

            oldlogfile = os.path.join(logdir, oldname)

            os.rename(logfile,oldlogfile)

        return logfile

    def __init__(self, options, query_func, secret_query_func):
        self.options = options
        self.query_func = query_func
        self.secret_query_func = secret_query_func
        self.data = Data.Data()
        self.cur_strategy = None
        self.cur_state = None

        level=botlog.DEBUG
        self.logfile=None
        self.tracefile=None
        debug=True
        if not self.get_app_value('debug'):
            level=botlog.INFO
            self.logfile = self.file_roll('log')
            self.tracefile = self.file_roll('out')
            debug=False
            
        botlog.configure(
                msglevel=level,
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
        if environkey in os.environ and os.environ[environkey] != '':
            if not secret:
                botlog.debug( 'reading application value [environment] '+ environkey + ' : ' + os.environ[environkey])
            return os.environ[environkey]
        
        # otherwise call query function, or secretquery Func
        if secret:
            return self.secret_query_func('Please enter ' + key)

        return self.query_func(key)

    def get_close_float(self,x):
        return random.uniform(x*0.75,x*1.25)

    def wait_for_prompt(self):
        gotprompt = 0
        while not gotprompt:
            #TODO forever guard
            gotprompt = self.telnet.expect([".", pexpect.TIMEOUT], timeout=1)

    def send(self, msg, eol=False, sleep=1.5):
        """
        Send a message to the client use some rudemantry random delay to 
        semi similate a human's typing
        """

        if msg is not None and len(msg) > 0:
            botlog.info('Sending {' + msg + '}')
            for c in msg:
               #if sleep > 0:
               #    self.wait_for_prompt()
                self.telnet.delaybeforesend=self.get_close_float(sleep)
                if 1 != self.telnet.send(c):
                    raise Exception ("1 char not sent")

        if eol:
            botlog.info('Sending {\\r}')
            self.telnet.delaybeforesend=self.get_close_float(sleep)
           #if sleep > 0:
           #    self.wait_for_prompt()
            if 1 != self.telnet.send('\r'):
                raise Exception ("1 char not sent")

    def sendl(self,msg='',sleep=0.5):
        self.send(msg,eol=True,sleep=sleep)

    def get_num(self, matchIndex=0):
        """
        Get a number from the current matchign regex group
        """
        n = Utils.ToNum(self.telnet.match.groups()[matchIndex])
        # botlog.debug("Read Number: " + str(n))
        return n

    def get_str(self, matchIndex=0):
        """
        Get a number from the current matchign regex group
        """
        return self.telnet.match.groups()[matchIndex]
   
    def run_loop(self):


        # begin the telnet session

        self.telnet = pexpect.spawn('rtelnet ' + self.get_app_value('address'), 
                logfile=botlog.tracefile,
                maxread=1)

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

        # union with the default strategy handlers
        default=['Session', 'Common', 'Messages', 'Diplomacy', 'Main', 'Stats', 
            'Maintenance', 'Food','Bank','Spending','Attack', 'Trading', 
            'EndTurn', 'Industry']
        strats = list (set(strats) |  set(default))

        # compile the strategies into indicators sorted by priority
        strategies = Strategy.Strategies(self, strats)

        # repeat forever or until we think of something better to do
        running = True
        strat = None
        laststrat = None
        dbgmode = self.get_app_value('debug')
        while running:

            # expect the unified list of all possible indicators
            # print '\n\n', 'EXPECTING', keys,'\n\n'

            keyIndex = self.telnet.expect(strategies.get_keys())

            botlog.debug( 'Matched: ' + strategies.get_key(keyIndex))

            for rec in strategies.enumerate_matches(keyIndex):

                botlog.cur_strat = rec.strategy.get_name()
                botlog.cur_state = str(rec.state)
                
                # Provide a decent user experience for watching progress
                if not dbgmode:
                    if botlog.cur_strat == "Stats" or botlog.cur_strat == laststrat:
                        sys.stdout.write('.')
                        sys.stdout.flush()
                    else:
                        laststrat = botlog.cur_strat
                        sys.stdout.write( '\n' + botlog.cur_strat)
                
                action = rec.strategy.base_on_indicator(rec.state)

                botlog.cur_strat = None
                botlog.cur_state = None

                if action == Strategy.TERMINATE:
                    self.telnet.close()
                    running = False
                    break
                elif action == Strategy.CONSUMED:
                    break


    def send_notification(self, game_exception):
        if (self.get_app_value('debug')):
            botlog.debug("No notification email is sent in debug mode")
            return

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
        body = str(self.data) 
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
        
