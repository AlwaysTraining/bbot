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
import Mentat
import Strategy
from bbot import *
import botlog
import string
import State
import re
import json
from datetime import datetime

MAXWAIT = 60

class App:
    def get_data_dir(self):
        data_dir = self.get_app_value("data_dir")
        data_dir = os.path.expandvars(data_dir)
        return data_dir


    def get_tag_str(self, joiner='_'):
        if self.has_app_value('id'):
            a = self.get_app_value('id')
        else:
            a = self.get_app_value('address')
            a = a.split('.')
            a = a[0]
        s = joiner.join([
            str(a),
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

    class ArgsEncoder(json.JSONEncoder):

        def default(self, obj):
            if isinstance(obj, datetime):
                return Utils.date_to_string(obj)

            return json.JSONEncoder.default(self, obj)

    def write_options_dict(self):

        argfile = self.file_roll("arg")
        with open(argfile, 'w') as outfile:
            json.dump(self.options, outfile, cls=App.ArgsEncoder, indent=3,
                      sort_keys=True)

    def __init__(self, options, query_func, secret_query_func):
        self.debug = False
        self.options = options

        # if reading options from file, dates will still be strings
        for key, value in options.items():
            if Utils.is_date(value):
                options[key] = Utils.string_to_date(value)

        self.query_func = query_func
        self.secret_query_func = secret_query_func
        self.data = Data.Data()
        self.metadata = MetaData.MetaData(self)
        self.mentat = Mentat.Mentat(self)
        self.cur_state = None
        self.match = None
        self.match_index = None
        self.match_re = None
        self.wait_time = 0
        self.telnet = None
        self.strategies = None
        self.EOF = False
        self.adaptive_timeout = self.get_app_value('human_delay')
        self.timeout_alpha = 0.1
        self.min_timeout = self.adaptive_timeout
        self.max_timeout = 20.0
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
        self.human_pause_ratio = self.get_app_value('human_pause_ratio')

        botlog.configure(
            msglevel=level,
            format='\n%(asctime)s:%(levelname)s::%(message)s',
            logpath=self.logfile,
            tracepath=self.tracefile)

        self.write_options_dict()

    def has_app_value(self, key):
        if key in self.options and self.options[key] is not None:
            return True
        environkey = Constants.ENVIRON_PREFIX + key
        # otherwise check if value is in environment
        if environkey in os.environ and os.environ[environkey] != '':
            return True

    def try_get_app_value(self, key, secret=False, default=None):
        if not self.has_app_value(key):
            botlog.debug("reading application value [default] " + 
                    key + ' : ' + str(default))
            return default
        return self.get_app_value(key, secret)

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
            return self.secret_query_func('Please enter ' + key)

        return self.query_func(key)

    def get_close_float(self, x):
        return random.uniform(x * 0.9, x * 1.1)

    def read_until_full_buffer(self,timeout=-1):
        buf = ""
        max_iterations = 10
        while buf == "" and max_iterations >= 0:
            buf = self.read(timeout=timeout)
        if buf == "":
            raise Exception("Could not read full buffer")
        return buf

    def read_until(self, stop_text, timeout=-1, maxwait=MAXWAIT):
        return self.read_until_any([stop_text], timeout=timeout,
                                   maxwait=maxwait)

    def read_until_any(self, stop_text_list, timeout=-1, maxwait=MAXWAIT):

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
                    if self.wait_time > MAXWAIT:
                        botlog.warn(
                            "Last full buffer:\n" + str(self.last_full_buf))
                        raise Exception(
                            "Waited for about " + str(MAXWAIT) + " seconds when sending macro and nothing happened")

                    if len(b) > 0:
                        break

        botlog.debug("End Macro: " + str(seq))
        return self.buf

    def has_strategy(self, strategy_name):
        for s in self.strategies:
            if strategy_name == s.get_name():
                return True
        return False

    def get_strategy(self, strategy_name):
        for s in self.strategies:
            if strategy_name == s.get_name():
                return s
        raise Exception("No strategy named: " + str(strategy_name))

    def call_strategies(self, func_name):
        ret = Strategy.UNHANDLED
        for s in self.strategies:
            botlog.cur_strat = s.get_name()
            curret = eval("s." + func_name + "()")
            if curret != Strategy.UNHANDLED:
                ret = curret
        botlog.cur_strat = ''
        return ret

    def on_main_menu(self):
        return self.call_strategies("on_main_menu")

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


    def init_strategies(self):

        strats = []
        if self.has_app_value('strategies'):
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

    def run_loop(self):
        exitState = State.BailOut().get_name()

        while self.state.get_name() != exitState and not self.EOF:

            if self.skip_next_read:
                self.skip_next_read = False
            else:
                self.read()

            if self.wait_time > MAXWAIT:
                botlog.warn("Last full buffer:\n" + str(self.last_full_buf))
                raise Exception(
                    "Waited for about " + str(
                        MAXWAIT) + " seconds in main loop and nothing happened")

            if not self.debug:
                if random.random() < self.human_pause_ratio:
                    rpause = random.random() * 30
                    botlog.info("Random human pause for " +
                                str(round(rpause, 0)) + " seconds")
                    time.sleep(rpause)
            nextstate = self.state.transition(self, self.buf)

            transitioned = nextstate is not None and nextstate != self.state

            if transitioned:
                self.state = nextstate
                botlog.cur_state = self.state.get_name()

        if not self.EOF:
            botlog.debug("Performing final read")
            self.read()

        if self.state.get_name() != exitState:
            raise Exception("Unexpected end of session in state: " +
                            self.state.get_name())

    def run_init(self):


        # begin the telnet session

        self.telnet = pexpect.spawn('telnet ' + self.get_app_value('address'),
                                    logfile=botlog.tracefile,
                                    maxread=1)

        self.init_strategies()


        self.state = State.Login()
        botlog.cur_state = self.state.get_name()

        self.skip_next_read = False
        self.run_loop()

        self.write_options_dict()



    def format_msgmap_text(self, msgmap):
        warntext = ""
        for warning,count in sorted(msgmap.items(), key=lambda x: x[0]):
            warntext += str(warning)
            if count > 1:
                warntext += " (x" + str(count) + ")"
            warntext += "\n"
        return warntext

    def maybe_append_section(self, body, section_title, section):
        section = section.strip()
        if len(section) > 0:
            titleline = "----==== " + section_title + " ====----"
            spacer = '-' * len(titleline)
            body += ("\n\n\n" +
                    spacer + "\n" +
                    titleline + "\n" +
                    spacer +"\n\n" + 
                    section)

        return body

    def send_notification(self, game_exception):

        if self.no_email_reason is not None and self.no_email_reason != '':
            botlog.info(
                "No notification email sent because: " + self.no_email_reason)
            return

        if (self.debug):
            botlog.debug("No notification email is sent in debug mode")
            return

        if "notify" not in self.options or self.options['notify'] is None:
            botlog.info("No notification email address provided")
            return

        to = self.get_app_value('notify')
        to = Utils.make_string_list(to)

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

        changetext = Utils.try_get_recent_changes()
        warntext = self.format_msgmap_text(botlog.warnings)
        errortext = self.format_msgmap_text(botlog.errors)
        notetext = self.format_msgmap_text(botlog.notes)

        body = ""


        body = self.maybe_append_section(body, "Errors", errortext)
        body = self.maybe_append_section(body, "Warnings", warntext)
        body = self.maybe_append_section(body, "Notes", notetext)
        body = self.maybe_append_section(body, "Events", self.data.eventtext)
        body = self.maybe_append_section(body, "Messages`", self.data.msgtext)
        body = self.maybe_append_section(body, "IP Scores",self.data.ipscorestext)
        body = self.maybe_append_section(body, "Scores", self.data.planettext)
        body = self.maybe_append_section(body, "Other Realms", self.data.otherrealmscores)
        body = self.maybe_append_section(body, "Group Attacks", self.data.gatext)
        body = self.maybe_append_section(body, "Income", self.data.earntext)
        body = self.maybe_append_section(body, "Status", self.data.statstext)
        body = self.maybe_append_section(body, "Inventory", self.data.spendtext)
        body = self.maybe_append_section(body, "Investments", self.data.investmentstext)
        body = self.maybe_append_section(body, "Recent Source Code Changes", changetext)
        body = self.maybe_append_section(body, "Today's News", self.data.todaynewstext)
        body = self.maybe_append_section(body, "Yesterday's News",self.data.yesterdaynewstext)
        body = body.strip()

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


    def interact(self):
        try:

            botlog.debug("Exception occured in debug, going to " +
                         "interactive mode. Use 'ESC' to attempt to " +
                         "return to bot control, last buffer was:\n" +
                         self.buf)

            self.telnet.interact(escape_character='\x1b')
            botlog.debug("Interactive mode has ended, returning to game "
                         "loop")

            self.state = State.PreTurns()
            self.skip_next_read = True

            self.run_loop()

        except Exception, e:
            botlog.exception(e)

    def run(self):

        game_exception = None
        try:
            botlog.info("bbot has begun")

            self.run_init()

            botlog.info("bbot has completed")
        except Exception, e:
            botlog.exception(e)
            game_exception = e

        if self.debug and game_exception is not None:
            self.interact()



        self.send_notification(game_exception)

        if game_exception is not None:
            raise game_exception
        
