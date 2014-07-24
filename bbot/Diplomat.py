#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.Data import *
from bbot.OtherPlanetParser import OtherPlanetParser

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
        for key in self.app.options:
            if not key.startswith(self.get_name()):
                continue

            parts = key.split("_")
            # botlog.debug("Found parts: " + str(parts))
            # remove the diplomat name

            if len(parts) != 4:
                botlog.warn("Diplomat parameter (" + str(key) + ") is not " +
                            "of correct format, it needs 4 parts")
                continue
            if parts[2] != "msg":
                botlog.warn("Diplomat parameter (" + str(key) + ") is not " +
                            "of correct format, 3rd part thould be 'msg'")
                continue

            if not self.app.has_app_value(key):
                continue


            if parts[1] not in msgdict:
                msgdict[parts[1]] = Message()

            msg = msgdict[parts[1]]
            msg.option_name = parts[1]
            if parts[3] == "destplanets":
                msg.destplanets = self.app.get_app_value(key)
            elif parts[3] == "destrealms":
                msg.destrealms = self.app.get_app_value(key)
            elif parts[3] == "sendafter":
                msg.sendafter = self.app.get_app_value(key)
            elif parts[3] == "send":
                msg.send = self.app.get_app_value(key)
            elif parts[3] == "text":
                msg.text = self.app.get_app_value(key)

            botlog.debug('Found message option: ' + str(eval("msg." + parts[3])))

        now = datetime.now()

        for msgname, msg in msgdict.items():
            if (
                    msg.destplanets is None or
                    msg.sendafter is None or
                    msg.send is None or
                    msg.send is False or
                    msg.text is None or
                    msg.text == "" or
                    msg.option_name is None):
                botlog.debug("Missing some parameter(s) for message: " +
                             str(msgname))
                continue
            
                    
            if now < msg.sendafter or not msg.send:
                botlog.debug("Not sending message: " + str(msgname))

            planetnames = make_string_list(msg.destplanets)
            if msg.destrealms is not None:
                msg.destrealms = make_string_list(msg.destrealms)

            if msg.destrealms is not None and len(planetnames) > 1:
                msg.destrealms = None
                botlog.warn("More than one planet specified, ignoring "
                            "individual realms listed for message: " + msgname)

            for planetname in planetnames:
                msg.destplanets = [planetname]
                buf = self.send_msg(msgname, msg)

        self.messages_processed = True


    def maybe_parse_realms(self, buf, msg):
        if 'Enter Planet Name or Number (? for list):' not in buf:
            raise Exception("Unexpected text when messaging")
        planet = self.data.find_planet(msg.destplanets[0])
        if planet is None:
            raise Exception("Could not find planet: " + str(msg.destplanets[0]))
        self.app.sendl(planet.name,
                       comment="Sending planet name for message")
        buf = self.app.read()
        if '(A-Y,Z=All,?=List) Send to:' not in buf:
            raise Exception("Unexpected text when entering planet name " +
                            " for single message")
        if len(planet.realms) == 0 and msg.destrealms is not None:
            self.app.send('?', comment="Listing planets to send a message")
            buf = self.app.read()

            opp = OtherPlanetParser(
                planet.realms, planet_name=planet.name)
            opp.parse(self.app, buf)

            if '-=<Paused>=-' in buf:
                self.app.sendl(
                    comment="Continuing after displaying other realms")
                buf = self.app.read()
        return buf

    def send_msg(self, msgname, msg):
        botlog.debug("Sending message: " + str(msgname))

        self.app.send(9, comment='Entering IP menu to send messages')
        buf = self.app.read()

        self.app.send(7, comment='Sending message menu')
        buf = self.app.read()

        if len(msg.destplanets) == 1:
            self.app.send(1,comment="Messaging single planet: " + str(
                msg.destplanets[0]))
            buf = self.app.read()
            buf = self.maybe_parse_realms(buf, msg)
        else:
            botlog.warn("Not able to send message to: " +
                        str(len(msg.destplanets)) + " planets")
            botlog.send(0, comment="Exiting message menu")

        realmletters = ""
        if msg.destrealms is None or len(msg.destrealms) == 0:
            realmletters = "z"
        else:
            realmletters = ""
            planet = self.app.data.find_planet(msg.destplanets[0])
            if planet is None:
                raise Exception("Could not find planet: " + str(msg.destplanets[0]))
            for realmname in msg.destrealms:
                for realm in planet.realms:
                    if realmname.lower() in realm.name.lower():
                        if realm.menu_option not in realmletters:
                            realmletters += realm.menu_option

        self.app.sendl(realmletters,comment="Sending message to these realms")
        buf = self.app.read()

        self.app.sendl(msg.text,comment="Writing message body")
        buf = self.app.read()

        self.app.send("/s",comment="Sending message")
        buf = self.app.read()
        if 'Saving...' not in buf:
            raise Exception("Message was unxepectedly not sent")

        # reccord that the message was sent in app options, by saying don't
        # send it next time
        optionname = '_'.join([self.get_name(), msgname, "msg", "send"])
        self.app.options[optionname] = False
        botlog.debug("Now set to not send message again: " +
                     optionname + " = " +
                     str(self.app.get_app_value(optionname)))

        # we should be back on IP menu now, one more exit will pop us back to
        #  main menu

        self.app.sendl(comment="Returning from IP to main menu after sending "
                               "messages")
        buf = self.app.read()

        return buf












