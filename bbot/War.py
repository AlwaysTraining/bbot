#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.WarParser import WarParser
from bbot.Data import *
import math

S = SPACE_REGEX
N = NUM_REGEX


class War(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.army = self.app.data.realm.army
        self.wp = WarParser()
        self.sent_tops = False
        self.sent_sops = False
        self.sop_bombs = {5,7,6}
        self.all_undermines_sent = False




    def on_spending_menu(self):
        #TODO group agent pool feature


        # buy some of the stuff we need

        if self.army.agents is None or self.army.agents.number is None:
            botlog.warn("Not known how many agents there are")

        # buy agents if neccessary
        elif self.army.agents.number < 1000:
            botlog.warn("Very low agents, buying enough to send tops")
            self.buy_army_units(
                "agents",
                buyratio=None,
                ammount=1000 - self.army.agents.number )
            if self.army.agents.number < 1000:
                botlog.warn("Could not buy 1k agents")

        if self.army.bombers is None or self.army.bombers.number is None:
            botlog.warn("Not known how many agents there are")

        # buy bombers if necessarry
        elif self.army.bombers.number < 10000:
            self.buy_army_units(
                "agents",
                buyratio=None,
                ammount=1000 - self.army.bombers.number)
            if self.army.agents.number < 10000:
                botlog.warn("Could not buy 10k bombers")

        # buy carriers if we don't have enough to send jets
        if (self.army.jets is None or self.army.jets.number is None or
            self.army.carriers is None or self.army.carriers.number is None):
            botlog.warn("Not known how many jets or carriers there are")
        else:
            jets_per_carrier = self.app.data.get_num_per_carrier(
                Jets.menu_option)
            needed_carriers = int(
                math.ceil(self.army.jets.number / float(jets_per_carrier)))
            ammount = needed_carriers - self.army.carriers.number
            if ammount > 0:
                self.buy_army_units(
                    "carriers",
                    buyratio=None,
                    ammount=ammount)


    def select_enemy_realms(self,context, select_func):

        league = self.app.data.league
        if league is None:
            raise Exception("League scores have not been read")
        planets = league.planets

        selected_realms = []

        for p in league.planets:
            if p.relation != "Enemy":
                continue
            for r in p.realms:
                if select_func(context, selected_realms, p, r):
                    selected_realms.append(r)

        return selected_realms


    def select_highest_networth_enemy_realm(
            self,
            context,
            selectedrealms,
            planet,
            realm):


        if len(selectedrealms) == 0:
            return True

        if realm.networth > selectedrealms[0].networth:
            selectedrealms.pop()
            return True

        return False



    def get_highest_networth_enemy_realm(self):
        realms = self.select_enemy_realms(
            None,
            self.select_highest_networth_enemy_realm)
        if len(realms) == 0:
            raise Exception("No realms found when looking for highest "
                            "networth")

        return realms[0]




    def send_sops(self, target_realm):

        if (len(self.sop_bombs) > 0 or not self.all_undermines_sent):
            self.app.send(8,comment="Entering s-op menu")
            self.app.read()


        # send s-op missles
        while len(self.sop_bombs) > 0:
            self.app.send(self.sop_bombs[0],comment="Sending bomb")
            buf = self.app.read()
            if "Enter Planet Name or Number" not in buf:
                botlog.warn("Not able to send missle s-op")
                break
            self.app.sendl(target_realm.planet_name)
            self.app.read()
            self.app.send('?',comment="Displaying realms at missle s-op menu")
            self.app.read()
            self.app.send(target_realm.menu_option)
            buf = self.app.read()
            if "Would you like to prepare the attack? (Y/n)" not in buf:
                botlog.warn("Unable to send sop:\n" + buf)
                break
            self.app.send('y',comment="Yes i will send the s-op")

            buf = self.app.read()
            if "Attack Launched." not in buf:
                botlog.warn("s-op missle was not sent")
                break

            self.sop_bombs.pop(0)


        # send s-op undermines
        if not self.all_undermines_sent:
            max_iterations = 20
            while max_iterations > 0:
                self.app.send("4",comment="Undermining Investments")
                buf = self.app.read()
                if "Enter Planet Name or Number" not in buf:
                    botlog.warn("Not able to send undermine s-op: \n" + buf)
                    break

                # note if attacking multiple planets, this may not be the high NW
                #  planet
                self.app.sendl(target_realm.planet_name)

                buf = self.app.read()
                if "Send a bomb to" not in buf:
                    botlog.warn("Not able to send undermine to enemy planet")
                    break

                self.app.send('y')
                buf = self.app.read()
                if "Mission Specialists sent out." not in buf:
                    botlog.warn("Could not send undermine to enemy planet")
                    break

                if 'You have 0 bombing ops left today' in buf:
                    self.all_undermines_sent = True
                    break

                max_iterations -= 1

            if max_iterations <= 0:
                raise Exception("Tried too many times to send bombs")



    def on_interplanetary_menu(self):


        # send t-ops


        # send s-ops
        sop_target = self.get_highest_networth_enemy_realm()
        self.send_sops(sop_target)

        # join short term GA's

        # send indie

        # create short term GA

















