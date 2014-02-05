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
import State
import re


class App:

    def get_data_dir(self):
        return "."

    
    def get_tag_str(self,joiner='_'):
        a = self.get_app_value('address')
        a = a.split('.')
        a = a[0]
        s = joiner.join([
                "bbot",a,
                self.get_app_value('game'),
                self.get_app_value('realm')])
        s = Utils.clean_string(s)

       
        return s

    def file_roll(self,suffix):

        name = self.get_tag_str() + '_' + suffix + ".txt"
        logfile = os.path.join(self.get_data_dir(), name)

        if os.path.exists(logfile):
            name = self.get_tag_str() + suffix + ".txt"
            logdir = os.path.join(self.get_data_dir(),'old')

            if not os.path.exists(logdir):
                os.makedirs(logdir)

            moddate = Utils.get_file_date_string(logfile)

            oldname = (self.get_tag_str() + '_' +  moddate + '_'
                        + suffix + ".txt")


            oldlogfile = os.path.join(logdir, oldname)

            os.rename(logfile,oldlogfile)

        return logfile

    def __init__(self, options, query_func, secret_query_func):
        self.options = options
        self.query_func = query_func
        self.secret_query_func = secret_query_func
        self.data = Data.Data()
        self.cur_state = None
        self.match = None
        self.match_index = None
        self.match_re = None
        self.wait_time = 0
        self.telnet = None
        self.strategies = None
        self.EOF = False

        level=botlog.DEBUG
        self.logfile=None
        self.tracefile = self.file_roll('out')
        debug=True
        if not self.get_app_value('debug'):
            level=botlog.INFO
            self.logfile = self.file_roll('log')
            debug=False

        self.debug = debug
            
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

    def read_until(self,stop_text,timeout=1,maxwait=20):
        
        while True:
            b = self.read(timeout,stop_patterns=[re.compile(
                '.*'+re.escape(stop_text)+'.*'
                )])

            if self.match_re is not None:
                return b
           
            if self.wait_time > maxwait:
                raise Exception("Could not read '" + str(stop_text) + 
                    "' in " + str(maxwait) + " seconds")

    def read(self,timeout=1,stop_patterns=None):
        botlog.debug("Reading...")
        txt=[]
        self.match = None
        self.match_index = None
        self.match_re = None
        
        while True:
            #todo infinte guard
            try:
                x = self.telnet.read_nonblocking(size=1, timeout=timeout)

                # print the read data in debug mode
                if self.debug:
                    sys.stdout.write(x)
                    sys.stdout.flush()

                txt.append(x)

                if stop_patterns is not None:
                    buf =  ''.join(txt)
                    lines = buf.splitlines()
                    line = lines[-1]

                    for i in range(len(stop_patterns)):
                        self.match = stop_patterns[i].match(line)
                        if self.match is not None:
                            self.match_index = i
                            self.match_re = stop_patterns[i]
                            break
                    
                if self.match is not None:
                    break
                
            except pexpect.TIMEOUT:
                break
            except pexpect.EOF:
                botlog.info("No more data can be read from telnet")
                self.EOF = True
                break

       
        newbuf =  ''.join(txt)
        if len(newbuf) > 0:
            self.wait_time = 0
        else:
            self.wait_time = self.wait_time + timeout

        self.buf = newbuf
        
        
        return self.buf


    def send(self, msg, eol=False, sleep=0):
        """
        Send a message to the client use some rudemantry random delay to 
        semi similate a human's typing
        """

        msg = str(msg)

        if msg is not None and len(msg) > 0:
            botlog.info('Sending {' + msg + '}')
            for c in msg:
                if sleep > 0:
                    time.sleep(sleep)
                if 1 != self.telnet.send(c):
                    raise Exception ("1 char not sent")

        if eol:
            botlog.info('Sending {\\r}')
            if sleep > 0:
                time.sleep(sleep)
            if 1 != self.telnet.send('\r'):
                raise Exception ("1 char not sent")

    def sendl(self,msg='',sleep=0.5):
        self.send(msg,eol=True,sleep=sleep)

    def send_seq(self,seq):
        for msg in seq:
            self.send(msg)
            self.read()
        return self.buf

    def on_spending_menu(self):
        for s in self.strategies:
            s.on_spending_menu()
    def on_industry_menu(self):
        for s in self.strategies:
            s.on_industry_menu()

    def run_loop(self):


        # begin the telnet session

        self.telnet = pexpect.spawn('telnet ' + self.get_app_value('address'), 
                logfile=botlog.tracefile,
                maxread=1)

        strats = self.get_app_value('strategies')

        # if one string is provided, someitmes they can just give it to us as one string,
        #   convert it to a list to implify 
        if isinstance(strats, basestring):
            strats = [strats]

        # shouldn't happen with cmd line checking
        if strats is None:
            raise Exception("No Strategies provided")

        # union with the default strategy handlers
        default=[]                                                                                                                                                                                 
        strats = list (set(strats) |  set(default))

        # compile the strategies into indicators sorted by priority
        self.strategies = Strategy.Strategies(self, strats)

        
        exitState = State.BailOut().get_name()

        state = State.Login()
        botlog.cur_state = state.get_name()

        skip_read = False

        while state.get_name() != exitState and not self.EOF:

            if skip_read:
                skip_read = False
            else:
                buf = self.read()
             

            if self.wait_time > 20:
                raise Exception("Waited for about 20 seconds and nothing happened")

            nextstate = state.transition(self,buf)
            
            transitioned = nextstate is not None and nextstate != state

            if transitioned:
                state = nextstate
                botlog.cur_state = state.get_name()
                skip_read = True

        if not self.EOF:
            botlog.debug("Performing final read")
            self.read()


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
        
