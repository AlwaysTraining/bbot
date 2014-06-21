#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.Data import *

S = SPACE_REGEX
N = NUM_REGEX


class Message:
    def __init__(self):
        self.destplanets = None
        self.destrealms = None
        self.sendafter = None
        self.send = None
        self.text = None
        self.option_name = None

class Diplomat(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.messages_processed = False



    def on_main_menu(self):

        if self.messages_processed:
            botlog.debug("Messsages have already been processed today")
            return


        # parameters of format Diplomat_peace_msg_body

        botlog.debug("Iterating messages in options")

        msgdict = {}
        msgopts = []
        for key in self.app.options:
            if not key.startswith(self.get_name()):
                continue

            parts = "_".split(key)
            # remove the diplomat name

            if len(parts) != 4:
                botlog.warn("Diplomat parameter (" + str(key) + ") is not" +
                            "of correct format, it needs 4 parts")
                continue
            if parts[2] != "msg":
                botlog.warn("Diplomat parameter (" + str(key) + ") is not" +
                            "of correct format, 3rd part thould be 'msg'")
                continue

            if not self.app.has_app_value(key):
                continue


            if parts[1] not in msgdict:
                msgdict[parts[1]] = Message()

            msg = msgdict[parts[1]]
            msg.option_name = parts[1]
            codestr = ("msg." + parts[3] +
                       " = self.app.get_app_value(key)")
            eval(codestr)


            botlog.debug("Found message option: " + str(key))
            msgopts.append(parts)

        now = datetime.now()

        for msgname, msg in msgdict.items():
            if (
                    msg.destplanets is None or
                    msg.destrealms is None or
                    msg.sendafter is None or
                    msg.send is None or
                    msg.text is None or
                    msg.option_name is None):
                botlog.debug("Missing some parameter(s) for message: " +
                             str(msgname))
                continue
            
                    
            if now < msg.sendafter or not msg.send:
                botlog.debug("Not sending message: " + str(msgname))

        self.app.send(9,'Entering IP menu to send messages')
        buf = self.app.read()

        self.app.send(7,'Sending message menu')
        buf = self.app.read()

        # TODO get send message training text

        self.app.sendl(comment="Returning from IP to main menu after sending "
                               "messages")
        buf = self.app.read()















