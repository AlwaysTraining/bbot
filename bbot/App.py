#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import Constants
import os, sys
import pexpect
import random
import time
import botlog
import Utils
import Data
import MetaData
import Strategy
from bbot import *
import botlog
import string
import State
import re


class App:
    def get_data_dir(self):
        data_dir = self.get_app_value("data_dir")
        data_dir = os.path.expandvars(data_dir)
        return data_dir


    def get_tag_str(self, joiner='_'):
        a = self.get_app_value('address')
        a = a.split('.')
        a = a[0]
        s = joiner.join([
            str(a),
            str(self.get_app_value('game')),
            str(self.get_app_value('realm'))])

        return s

    def file_roll(self, suffix):

        name = self.get_tag_str() + '_' + suffix + ".txt"
        name = Utils.clean_string(name)
        logfile = os.path.join(self.get_data_dir(), name)

        if os.path.exists(logfile):
            name = self.get_tag_str() + suffix + ".txt"
            name = Utils.clean_string(name)
            logdir = os.path.join(self.get_data_dir(), 'old')

            if not os.path.exists(logdir):
                os.makedirs(logdir)

            moddate = Utils.get_file_date_string(logfile)

            oldname = (self.get_tag_str() + '_' + moddate + '_'
                       + suffix + ".txt")
            oldname = Utils.clean_string(oldname)

            oldlogfile = os.path.join(logdir, oldname)

            os.rename(logfile, oldlogfile)

        return logfile

    def __init__(self, options, query_func, secret_query_func):
        self.debug = True
        self.options = options
        self.query_func = query_func
        self.secret_query_func = secret_query_func
        self.data = Data.Data()
        self.metadata = MetaData.MetaData(self.data)
        self.cur_state = None
        self.match = None
        self.match_index = None
        self.match_re = None
        self.wait_time = 0
        self.telnet = None
        self.strategies = None
        self.EOF = False
        self.adaptive_timeout = 2.5
        self.timeout_alpha = 0.1
        self.min_timeout = self.adaptive_timeout
        self.max_timeout = 10.0
        self.no_email_reason = None
        self.last_full_buf = None
        self.last_buf = None
        self.buf = ''

        level = botlog.DEBUG
        self.logfile = None
        self.tracefile = self.file_roll('out')
        debug = True
        if not self.get_app_value('debug'):
            level = botlog.INFO
            self.logfile = self.file_roll('log')
            debug = False

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
                botlog.debug(
                    'reading application value [options] ' + key + ' : ' + str(
                        self.options[key]))
            return self.options[key]

        environkey = Constants.ENVIRON_PREFIX + key
        # otherwise check if value is in environment
        if environkey in os.environ and os.environ[environkey] != '':
            if not secret:
                botlog.debug(
                    'reading application value [environment] ' + environkey + ' : ' +
                    os.environ[environkey])
            return os.environ[environkey]

        # otherwise call query function, or secretquery Func
        if secret:
            if not self.debug: raise Exception(
                "can not use query function in non debug mode, must provide value for: " + key)
            return self.secret_query_func('Please enter ' + key)

        if not self.debug: raise Exception(
            "can not use query function in non debug mode, must provide value for: " + key)
        return self.query_func(key)

    def get_close_float(self, x):
        return random.uniform(x * 0.9, x * 1.1)

    def read_until(self, stop_text, timeout=-1, maxwait=20):
        return self.read_until_any([stop_text], timeout=timeout,
                                   maxwait=maxwait)

    def read_until_any(self, stop_text_list, timeout=-1, maxwait=20):

        stop_patterns = []

        for t in stop_text_list:
            stop_patterns.append(re.compile('.*' + re.escape(t) + '.*'))

        while True:
            b = self.read(timeout, stop_patterns=stop_patterns)

            if self.match_re is not None:
                return b

            if self.wait_time > maxwait:
                raise Exception("Could not read any of " + str(
                    stop_text_list) + " in " + str(maxwait) + " seconds")


    def read(self, timeout=-1, stop_patterns=None):
        txt = []
        self.match = None
        self.match_index = None
        self.match_re = None

        adaptive = False
        if timeout < -0:
            timeout = self.adaptive_timeout
            adaptive = True

        timeout = self.get_close_float(timeout)

        botlog.debug(
            "Reading with " + str(round(timeout, 1)) + " second timeout...")

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
                    buf = ''.join(txt)
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

        newbuf = ''.join(txt)
        if len(newbuf) > 0:
            self.wait_time = 0
            if adaptive:
                self.adaptive_timeout = (
                                            1 - self.timeout_alpha / 2.0) * self.adaptive_timeout
                if self.adaptive_timeout < self.min_timeout: self.adaptive_timeout = self.min_timeout
        else:
            self.wait_time = self.wait_time + timeout
            if adaptive:
                self.adaptive_timeout = (
                                            1 + self.timeout_alpha * 2.0) * self.adaptive_timeout
                if self.adaptive_timeout > self.max_timeout: self.adaptive_timeout = self.max_timeout

        self.last_buf = self.buf
        if len(self.last_buf) > 0:
            self.last_full_buf = self.last_buf
        self.buf = newbuf

        return self.buf


    def send(self, msg, eol=False, sleep=0.5, comment=''):
        """
        Send a message to the client use some rudemantry random delay to 
        semi similate a human's typing
        """

        msg = str(msg)

        if msg is not None and len(msg) > 0:
            botlog.info('Sending {' + msg + '} # ' + str(comment))
            for c in msg:
                if sleep > 0:
                    sleep = self.get_close_float(sleep)
                    time.sleep(sleep)
                if 1 != self.telnet.send(c):
                    raise Exception("1 char not sent")

        if eol:
            botlog.info('Sending {\\r} # ' + str(comment))
            if sleep > 0:
                sleep = self.get_close_float(sleep)
                time.sleep(sleep)
            if 1 != self.telnet.send('\r'):
                raise Exception("1 char not sent")

    def sendl(self, msg='', sleep=0.5, comment=''):
        self.send(msg, eol=True, sleep=sleep, comment=comment)

    def send_seq(self, seq, comment=''):
        botlog.debug("Begin Macro: " + str(seq))
        for i in range(len(seq)):
            msg = seq[i]
            newcomment = comment + " (" + str(i + 1) + " of " + str(
                len(seq)) + ")"
            if msg == '\r':
                self.sendl(comment=newcomment)
            else:
                self.send(msg, comment=newcomment)

            # do not read after the last char in the sequence
            if i < len(seq) - 1:

                # the sequencing is problematic, because the programmer isn't 
                #   explicitly waiting to be sure he is at a prompt, he is 
                #   just sending seperate chars and blindly reading for some
                #   time in between.  We try to be smart and read until we get
                #   something
                while not self.EOF:
                    # do not allow sequence to manipulate the adaptive timing
                    #   because it is a wierd case and can throw it off. we do
                    #   however use the time as a good default timeout to use
                    b = self.read(timeout=self.adaptive_timeout)
                    if self.wait_time > 20:
                        botlog.warn(
                            "Last full buffer:\n" + str(self.last_full_buf))
                        raise Exception(
                            "Waited for about 20 seconds when sending macro and nothing happened")

                    if len(b) > 0:
                        break

        botlog.debug("End Macro: " + str(seq))
        return self.buf

    def has_strategy(self, strategy_name):
        for s in self.strategies:
            if strategy_name == s.get_name():
                return True
        return False

    def call_strategies(self, func_name):
        ret = Strategy.UNHANDLED
        for s in self.strategies:
            botlog.cur_strat = s.get_name()
            curret = eval("s." + func_name + "()")
            if curret != Strategy.UNHANDLED:
                ret = curret
        botlog.cur_strat = ''
        return ret


    def on_bank_menu(self):
        return self.call_strategies("on_bank_menu")

    def on_attack_menu(self):
        return self.call_strategies("on_attack_menu")

    def on_spending_menu(self):
        return self.call_strategies("on_spending_menu")

    def on_industry_menu(self):
        return self.call_strategies("on_industry_menu")

    def on_trading_menu(self):
        return self.call_strategies("on_trading_menu")

    def on_diplomacy_menu(self):
        return self.call_strategies("on_diplomacy_menu")

    def on_interplanetary_menu(self):
        return self.call_strategies("on_interplanetary_menu")


    def run_loop(self):


        # begin the telnet session

        self.telnet = pexpect.spawn('telnet ' + self.get_app_value('address'),
                                    logfile=botlog.tracefile,
                                    maxread=1)

        strats = self.get_app_value('strategies')

        # if one string is provided, someitmes they can just give it to us as one string,
        #   convert it to a list to implify 
        if isinstance(strats, basestring):
            if ',' in strats:
                strats = [x.strip() for x in strats.split(',')]
            else:
                strats = [strats]

        # shouldn't happen with cmd line checking
        if strats is None:
            raise Exception("No Strategies provided")

        # union with the default strategy handlers
        default = []
        strats = list(set(strats) | set(default))

        # compile the strategies into indicators sorted by priority
        self.strategies = Strategy.Strategies(self, strats)

        exitState = State.BailOut().get_name()

        state = State.Login()
        botlog.cur_state = state.get_name()

        self.skip_next_read = False

        while state.get_name() != exitState and not self.EOF:

            if self.skip_next_read:
                self.skip_next_read = False
            else:
                self.read()

            if self.wait_time > 20:
                botlog.warn("Last full buffer:\n" + str(self.last_full_buf))
                raise Exception(
                    "Waited for about 20 seconds in main loop and nothing happened")

            if not self.debug:
                if random.random() < 0.05:
                    rpause = random.random() * 30
                    botlog.info("Random human pause for " +
                                str(round(rpause, 0)) + " seconds")
                    time.sleep(rpause)
            nextstate = state.transition(self, self.buf)

            transitioned = nextstate is not None and nextstate != state

            if transitioned:
                state = nextstate
                botlog.cur_state = state.get_name()

        if not self.EOF:
            botlog.debug("Performing final read")
            self.read()

        if state.get_name() != exitState:
            raise Exception("Unexpected end of session in state: " +
                            state.get_name())


    def send_notification(self, game_exception):

        if self.no_email_reason is not None and self.no_email_reason != '':
            botlog.info(
                "No notification email sent because: " + self.no_email_reason)
            return

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
        if game_exception is not None:
            subject = "Failure : " + str(game_exception)

        changes = Utils.try_get_recent_changes()
        body = (
            self.data.planettext + "\n\n" +
            self.data.msgtext + "\n\n" +
            self.data.statstext + "\n\n" +
            self.data.spendtext + "\n\n" +
            changes )

        Utils.send_mail(
            to,
            '[bbot] ' + self.get_tag_str(' ') + ' ' + subject,
            body,
            _from='bbot@' + self.get_app_value('address'),
            files=files,
            server=self.get_app_value('smtp_server'),
            port=self.get_app_value('smtp_port'),
            server_user=self.get_app_value('smtp_user'),
            server_user_pass=self.get_app_value('smtp_password', secret=True))


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

        if game_exception is not None:
            raise game_exception
        
