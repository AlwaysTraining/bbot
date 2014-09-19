#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Strategy import Strategy
from bbot.WarParser import WarParser
from bbot.Data import *
from bbot.Wishlist import *

import math

S = SPACE_REGEX
N = NUM_REGEX

# % of attack strength compared to target strength

MULTIPLE_ATTACK_REDUCER = 0.9

# what portion of troops stay home
# TODO use this
DEFENSIIVE_RESERVE_RATIO = 0.1


def _realm_in_protection(app, r):
    if app.try_get_app_value("War_attack_protected_realms",False):
        return False
    return app.mentat.score_indicates_realm_in_protection(realm=r).answer


def _networth_to_strength(net):
    return net * 4

def _unprotected_planet_networth(app, realms):
    unprotected_networth = 0
    for r in realms:
        if not realm_in_protection(app, r):
            unprotected_networth += r.networth
    return unprotected_networth


def _planet_strength(app, realms):
    return _networth_to_strength(
        _unprotected_planet_networth(app, realms))



class Attack(object):
    def __init__(self, war):
        self.war = war
        self.attack_surp_ratio = war.get_attack_surp_ratio()
        self.id = None
        self.by = None
        self.planet = None
        self.realm = None
        self.troopers = None
        self.jets = None
        self.tanks = None
        self.bombers = None
        self.leave = None

    def get_attack_surp_ratio(self):
        return self.attack_surp_ratio

    def __str__(self):

        msg = ""
        msg += "Attack " + str(self.id) + " to "
        if self.planet is not None:
            msg += str(self.planet.name)
        if self.realm is not None:
            msg += " : " + self.realm.name

        astrength = self.get_strength()
        nstrength = self.needed_strength(self.war.group_attacks)

        if nstrength > 0:
            fullness = astrength / float(nstrength) * 100.0
            fullness = int(round(fullness))
        else:
            fullness = 0

        msg += ", Tanks: " + readable_num(astrength/4.0)
        msg += ", Fill: " + str(fullness) + "%"

        if self.leave is not None:
            msg += ", Leaves: " + str(self.leave) + "h"

        return msg

    def get_strength(self):
        strength = 0
        if self.troopers is not None:
            strength += self.troopers

        if self.jets is not None:
            strength += self.jets * 2

        if self.tanks is not None:
            strength += self.tanks * 4

        return strength

    def get_target_strength(self):
        # for attack on one realm
        if self.realm is None:
            return _planet_strength(self.war.app, self.planet.realms)

        # for planetary attack
        if _realm_in_protection(self.war.app, self.realm):
            target_strength = 0
        else:
            target_strength = self.realm.networth

        return _networth_to_strength(target_strength)

    def is_filled(self, num_reduces=0):

        # for attack on one realm
        target_strength = self.get_target_strength()

        win_strength = target_strength * self.get_attack_surp_ratio()

        for i in range(num_reduces):
            win_strength *= MULTIPLE_ATTACK_REDUCER

        return (self.get_strength() >= win_strength)


    def is_global(self):
        return self.realm is None

    def needed_strength(self, group_attacks, base=False):

        # note, __str__ now uses this function, don't try to call __str__
        # from this function (like with logging) or it will infinatly recurse

        botlog.debug("Determining needed strength for attack: " +
                     str(self.id))

        # TODO, the base parameter is being ignored, have to look in to this
        # are we getting expected behavior?
        # base needed strength
        base = (self.get_target_strength() * self.get_attack_surp_ratio())

        botlog.debug("The base needed strength is " + readable_num(base))

        if group_attacks is None:
            strength = max(0, int(math.ceil(base)) - self.get_strength())
            botlog.debug("No group attacks specified, not attempting to " +
                         "reduce attack strength requirement, strength " +
                         "needed is: " + str(strength))

            return strength

        # reduce needed strength by some ratio for each loaded attack facing
        # the same realm
        reducer = 1.0
        num_reduces = 0
        botlog.debug("Iterating group attacks to potentially reduce needed "
                     "strength")
        for ga in group_attacks:

            # group attacks should always be in order of leaving
            # stop iterating when we get later than this attack
            if ga.leave > self.leave:
                break
            # skip this attack
            if self.id == ga.id:
                continue

            # skip attacks to a differnt planet
            same_planet = self.planet.name == ga.planet.name
            if not same_planet:
                continue

            botlog.debug("group attack ID: " + str(ga.id) + " could affect" +
                         " the needed strength for this attack")

            reduce_strength = False

            if self.is_global():
                if ga.is_global():
                    reduce_strength = ga.is_filled(num_reduces)
                    botlog.debug("group attack ID: " + str(ga.id) +
                                 " is filled")
                else:
                    # if this is a global, and the considered GA is a non
                    # global, we will not consider any strength reduction.
                    # this will be conservative
                    botlog.debug("We won't reduce for this attack because " +
                                 "this attack is global and GA ID: " +
                                 str(ga.id) + " is non global")
                    continue
            else:
                if ga.is_global():
                    # this attack is non global, but considered GA is global.
                    # In this case a filled GA should give us a reduction
                    reduce_strength = ga.is_filled(num_reduces)
                    botlog.debug("global group attack ID: " + str(ga.id) +
                                 " is filled")
                else:
                    # both attacks are non global, reduce if same realm is
                    # being attacked, and attack is filled
                    reduce_strength = (self.realm.name == self.realm.name and
                                       ga.is_filled(num_reduces))
                    if reduce_strength:
                        botlog.debug("Reducing strength needed for this GA")

            if reduce_strength:
                # reduce the needed ratio
                base *= MULTIPLE_ATTACK_REDUCER
                num_reduces += 1
                botlog.debug("New base needed strength is " + readable_num(base) +
                             " after " + str(num_reduces) + " reduces")

        if num_reduces > 0:
            botlog.debug("Multiple Ga's have reduced needed strength " + str(
                num_reduces) + " times")

        strength = max(0, int(math.ceil(base)) - self.get_strength())
        botlog.debug("Determined remaining needed strength in ga: " +
                     str(self.id) + " is " + str(strength))

        return strength


class War(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.army = self.app.data.realm.army
        self.wp = WarParser()
        self.sent_tops = False
        self.sent_sops = False
        self.sent_indies = False
        self.created_group_attacks = False
        self.sop_bombs = [5, 7, 6]

        if not self.try_get_strategy_option(
                "send_nuke", True):
            self.sop_bombs.remove(5)

        if not self.try_get_strategy_option(
                "send_chem", True):
            self.sop_bombs.remove(6)

        if not self.try_get_strategy_option(
                "send_sabre", True):
            self.sop_bombs.remove(7)

        self.possible_tops = [2, 3, 4, 9]

        user_tops = self.try_get_strategy_option(
            "possible_terrorist_ops", None)
        if user_tops is not None:
            user_tops = make_string_list(user_tops)
            if len(user_tops) > 0:
                self.possible_tops = []
                for str_top in user_tops:
                    self.possible_tops.append(int(str_top))


        self.tops = []
        self.all_undermines_sent = False

        if not self.try_get_strategy_option("send_undermines", True):
            self.all_undermines_sent = True

        self.first_turn = True
        self.group_attacks = None
        self.attacked_targets = []
        self.joined_gas = []
        self.currently_filling_ga = None
        self.at_war = None
        self.end_of_day = None

        self.attack_surp_ratio = self.try_get_strategy_option(
            "attacker_size_advantage_ratio", 1.25 )


    def get_attack_surp_ratio(self):
        return self.attack_surp_ratio

    def get_priority(self):
        return VERYHIGH_PRIORITY

    def select_enemy_realms(self, context, select_func):
        league = self.app.data.league
        if league is None:
            raise Exception("League scores have not been read")
        planets = league.planets

        selected_realms = []

        for p in planets:
            if p.relation != "Enemy":
                continue
            for r in p.realms:

                if _realm_in_protection(self.app, r):
                    botlog.debug("Realm: " + (r.name) + " may be in protection")
                    continue

                if select_func(context, selected_realms, p, r):
                    selected_realms.append(r)

        return selected_realms


    def _select_highest_networth_enemy_realm(
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

    def _select_highest_regions_enemy_realm(
            self,
            context,
            selectedrealms,
            planet,
            realm):
        if len(selectedrealms) == 0:
            return True

        if realm.regions > selectedrealms[0].regions:
            selectedrealms.pop()
            return True

        return False

    def _select_attackable_enemy_realms(
            self,
            atkstrength,
            selectedrealms,
            planet,
            realm):


        defstrength = (_networth_to_strength(realm.networth) *
                       self.get_attack_surp_ratio())

        # if an attack on the realm is winable
        if atkstrength >= defstrength:
            # add the realm, and sort it in descending order of regions
            selectedrealms.append(realm)
            selectedrealms.sort(key=lambda x: x.regions, reverse=True)


        # we always return false, because we handle maintenance of the
        # selected realms list
        return False


    def get_indie_targets(self, max_strength=None):
        if max_strength is None:
            max_strength = self.data.get_attack_strength()
        targets = self.select_enemy_realms(
            max_strength,
            self._select_attackable_enemy_realms)
        return targets

    def can_send_indie(self, max_strength=None):

        if not self.try_get_strategy_option(
                "send_indie_attacks", True):
            return False

        if self.sent_indies:
            return False

        return len(self.get_indie_targets(max_strength=max_strength)) > 0

    def get_ga_targets(self, max_strength=None):
        if max_strength is None:
            max_strength = self.get_planet_strength()
        targets = self.select_enemy_realms(
            max_strength,
            self._select_attackable_enemy_realms)
        return targets

    def can_send_ga(self, max_strength=None):
        return len(self.get_ga_targets(max_strength=max_strength)) > 0

    def return_true(self,
                    context,
                    selectedrealms,
                    planet,
                    realm):
        return True

    def get_num_enemy_realms(self):
        realms = self.select_enemy_realms(None, self.return_true)
        return len(realms)

    def get_num_enemy_planets(self):
        league = self.app.data.league
        if league is None:
            raise Exception("League scores have not been read to get number "
                            "of enemies")
        planets = league.planets

        e = 0
        for p in planets:
            if p.relation == "Enemy":
                e += 1
        return e


    def on_spending_menu(self):

        self.end_of_day = self.app.mentat.is_end_of_day()

        if self.data.setup.local_game:
            botlog.warn("War Strategy is not for local games")
            return Strategy.UNHANDLED

        if not self.data.is_oop():
            botlog.debug("We are in protection, not taking any war actions")
            return

        if self.at_war is None:
            self.at_war = self.get_num_enemy_planets() > 0
            if self.at_war:
                realms = self.select_enemy_realms(
                    None,
                    self._select_highest_networth_enemy_realm)
                if len(realms) == 0:
                    botlog.warning("There are no attackable realms")
                    self.at_war = False

            if not self.at_war:
                botlog.info("No Enemies Found")

        if not self.at_war:
            botlog.debug("We are not at war, not taking any war actions")
            return

        if self.first_turn:

            self.first_turn = False

            # setup the tops we plan on sending, game setup is read by now
            for i in range(self.data.setup.num_tops):
                self.tops.append(random.choice(self.possible_tops))


        #TODO group agent pool feature

        # buy some of the minor stuff we may need

        if self.army.agents is None or self.army.agents.number is None:
            botlog.warn("Not known how many agents there are")

        # buy agents if neccessary
        elif self.army.agents.number < 1000:
            botlog.warn("Very low agents, buying enough to send tops")
            self.buy_army_units(
                "agents",
                buyratio=None,
                desired_ammount=1000 - self.army.agents.number)
            if (self.army.agents.number < 1000 and
                        self.end_of_day.is_certain() and
                        self.end_of_day.answer):

                botlog.warn("Could not buy 1k agents")

        if self.army.bombers is None or self.army.bombers.number is None:
            botlog.warn("Not known how many agents there are")

        # buy bombers if necessarry
        elif self.army.bombers.number < 1000:
            self.buy_army_units(
                "bombers",
                buyratio=None,
                desired_ammount=10000 - self.army.bombers.number)
            if (self.army.agents.number < 10000 and
                    self.end_of_day.is_certain() and
                    self.end_of_day.answer):
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
                    desired_ammount=1 + ammount)


    def get_highest_networth_enemy_realm(self):
        realms = self.select_enemy_realms(
            None,
            self._select_highest_networth_enemy_realm)
        if len(realms) == 0:
            raise Exception("No realms found when looking for highest "
                            "networth")

        return realms[0]

    def get_highest_regions_enemy_realm(self):
        realms = self.select_enemy_realms(
            None,
            self._select_highest_regions_enemy_realm)
        if len(realms) == 0:
            raise Exception("No realms found when looking for highest "
                            "regions")

        return realms[0]


    def send_sops(self, caller_supplied_target_realm=None):

        buf = self.app.buf

        if len(self.sop_bombs) == 0 and self.all_undermines_sent:
            self.sent_sops = True

        if self.sent_sops:
            # just to enforce consistancy, make sure these are set.  There is
            # a strange case where we send all undermines and no nukes because
            # a target is too big to afford to nuke in which the sent_sops
            # will become true with elements still in the sop_bombs list

            botlog.debug("All sops have already been sent")
            self.sop_bombs = []
            self.all_undermines_sent = True
            return

        if self.data.realm.army.bombers.number < 500:
            botlog.debug("Not enough bombers to send s-ops")
            return

        self.app.send(8, comment="Entering s-op menu")
        buf = self.app.read()

        # pick the correct target for this type of missle if the user
        # has not specified a desired target
        if caller_supplied_target_realm is None:
            if len(self.sop_bombs) > 0 and self.sop_bombs[0] == 5:
                botlog.debug("Caller did not supply target realm, " +
                             "picking bug region target for nuke")
                # nuke big region target
                target_realm = self.get_highest_regions_enemy_realm()
            elif len(self.sop_bombs) > 0 and self.sop_bombs[0] == 6:
                botlog.debug("Caller did not supply target realm, " +
                             "picking big region target for chem")
                # chem big region target
                target_realm = self.get_highest_regions_enemy_realm()
            else:
                botlog.debug("Caller did not supply target realm, " +
                             "picking big networth target for sabre")
                # sabre big net target
                target_realm = self.get_highest_networth_enemy_realm()
        else:
            target_realm = caller_supplied_target_realm


        # send s-op missles
        while not self.sent_sops and len(self.sop_bombs) > 0:


            if target_realm is None:
                raise Exception("Could not find and was not supplied with a "
                                "target realm to s-op")

            botlog.debug("Target realm for s op's is: " +
                         str(target_realm.name))

            # check if we have already sent this type of bomb
            menu_string = '(' + str(self.sop_bombs[0]) + ')'
            botlog.debug("Checking if '" + menu_string + "' has been sent")
            if menu_string not in buf:
                botlog.debug("Already sent bomb: " + menu_string)
                # this bomb is not available, try next one
                self.sop_bombs.pop(0)
                continue


            self.app.send(self.sop_bombs[0], comment="Sending bomb")

            buf = self.app.read_until_full_buffer()

            if "All missiles and bombs require 500 Bombers to deliver their " \
               "payloads." in buf:

                if (self.end_of_day.is_certain() and
                        self.end_of_day.answer):
                    botlog.warn("Not enough bombers to send S-op")
                self.app.sendl(comment="Returning from S-Op to interplanetary "
                                       "menu")
                buf = self.app.read()
                return


            if "Enter Planet Name or Number" not in buf:
                return

            self.app.sendl(target_realm.planet_name)
            buf = self.app.read()

            if 'Enemy' not in buf:
                raise Exception(
                    "Attempting to bomb planet not marked as enemy")

            # because this is what a human would do, and we might like to read
            # it in the log
            self.app.send('?', comment="Displaying realms at missle s-op menu")
            buf = self.app.read()
            self.app.send(target_realm.menu_option)
            buf = self.app.read()

            if "You cannot afford it." in buf:
                if (self.end_of_day.is_certain() and self.end_of_day.answer):
                    botlog.warn("Could not afford to send S-Op missle/bomb")
                # though we can't afford it, we don't quit, we break,
                # which will then cause us to send undermines in the next
                # turn.

                # TODO If by the last turn we still can't send missles to our
                #  prefered target we should lower our sights to smaller
                # targets
                break

            if "Would you like to prepare the attack? (Y/n)" not in buf:
                raise Exception("Unable to send sop:\n" + buf)

            self.app.send('y', comment="Yes i will send the s-op")

            buf = self.app.read()
            if "Attack Launched." not in buf:
                botlog.warn("s-op missle was not sent")
                break

            self.sop_bombs.pop(0)
            self.data.realm.army.bombers.number -= 500
            botlog.note("Sent bomb to " + str(target_realm.planet_name) +
                        " : " + str(target_realm.name))
            if len(self.sop_bombs) <= 0:
                botlog.debug("Just sent the last bomb for today")
                break

        if ('(4) Undermine Investments' not in buf):
            botlog.info("We must have already sent all undermines today")
            self.all_undermines_sent = True


        # send s-op undermines
        if (not self.all_undermines_sent):

            if target_realm is None:
                raise Exception("Could not find and was not supplied with a "
                                "target realm to undermine")


            botlog.debug("I don't think I have sent all undermines yet")


            max_iterations = 20
            while max_iterations > 0:
                self.app.send("4", comment="Undermining Investments")
                buf = self.app.read()

                if "You can't afford that!" in buf:
                    if (self.end_of_day.is_certain() and self.end_of_day.answer):
                        botlog.warn("Could not afford to send undermine")
                    self.app.sendl(
                        comment="Returning from S-Op to interplanetary "
                                "menu")
                    buf = self.app.read()
                    return

                if ("All missiles and bombs require 500 Bombers to deliver "
                    "their payloads." in buf):
                    if self.end_of_day.is_certain() and self.end_of_day.answer:
                        botlog.warn("Not enough bombers to send undermine")
                    self.app.sendl(
                        comment="Returning from S-Op to interplanetary "
                                "menu")
                    buf = self.app.read()
                    return

                # TODO, check this logic against game text, in the case where
                # we are turn splitting and already sent all agents

                if "Enter Planet Name or Number" not in buf:
                    raise Exception("Not able to send undermine s-op: \n" + buf)

                # note if attacking multiple planets, this may not be the high NW
                #  planet
                self.app.sendl(target_realm.planet_name)

                buf = self.app.read()

                if 'Enemy' not in buf:
                    raise Exception(
                        "Attempting to undermine planet not marked as enemy")

                if "Send a bomb to" not in buf:
                    raise Exception(
                        "Not able to send undermine to enemy planet")

                self.app.send('y')
                buf = self.app.read()
                if "Mission Specialists sent out." not in buf:
                    raise Exception("Could not send undermine to enemy planet")

                self.data.realm.army.bombers.number -= 500
                botlog.note("Sent undermine to " +
                            str(target_realm.planet_name))

                if 'You have 0 bombing ops left today' in buf:
                    self.all_undermines_sent = True
                    self.app.sendl(
                        comment="Returning from S-Op to interplanetary "
                                "menu")
                    buf = self.app.read()
                    return

                max_iterations -= 1

            if max_iterations <= 0:
                raise Exception("Tried too many times to send bombs")

        if '[Special Operations]' in buf:
            if 'You cannot afford it.' not in buf:
                botlog.warn("Unexpected exit from S-Op menu")
            self.app.sendl(
                comment="Returning from S-Op to interplanetary menu")
            buf = self.app.read()

        if '[InterPlanetary Operations]' not in buf:
            raise Exception(
                "Not returned to interplanetary menu after S-Op menu")


    def send_tops(self, top_target=None):

        if not self.try_get_strategy_option(
                "send_terrorist_ops", True):
            return

        if self.sent_tops:
            return

        # our default top target will be high networth realm


        target = top_target
        if target is None:
            botlog.debug("No specific t-op target specified, picking high "
                         "networth enemy realm")

            target = self.get_highest_networth_enemy_realm()

        botlog.debug("Sending out tops to: " + str(target.name))

        self.app.send(2, comment="Entering t-op menu")
        buf = self.app.read()

        if "You can't afford that!" in buf:
            botlog.warn("Can not afford to send T-Ops")
            return

        # if we have already sent the limit, lets not try to do it again
        if "Limit " in buf and " Terrorist Operations per day!" in buf:
            self.sent_tops = True
            botlog.debug("Just found out the hardway we already sent out tops")
            return

        if "Enter Planet Name or Number" not in buf:
            botlog.warn("Unable to choose t-op target planet")
            # this should probably be an exception, don't know why this would
            #  happen
            return

        self.app.sendl(target.planet_name, comment="entering planet name for "
                                                   "top target")
        buf = self.app.read()

        if 'Enemy' not in buf:
            raise Exception("Attempting to terrorize planet not marked as "
                            "enemy")

        if 'Choose a target' not in buf:
            botlog.warn("Unable to choose t-op target realm")
            # this should probably be an exception, don't know why this would
            #  happen
            return

        self.app.send(
            target.menu_option,
            comment="Sending t-ops to " + str(target.name))
        buf = self.app.read()

        if "[Terrorist Ops]" not in buf:
            botlog.warn("Could not get to t-op menu")
            # this should probably be an exception, don't know why this would
            #  happen
            return

        # TODO case for running out of money/agents during send cycles

        while (len(self.tops) > 0):
            self.app.send(self.tops[0])
            buf = self.app.read()

            if 'Send how many?' not in buf:
                botlog.warn("Not able to send t-op")
                return

            self.app.sendl(1, comment="Sending one t-op")
            buf = self.app.read()

            # in my experience sending 1 top at a time it won't ask you to
            # confirm, just assure this
            if 'This will cost you' in buf and 'Accept? (Y/n)' in buf:
                botlog.warn("Unexpected confirmation message sending t-op")
                self.app.send('y', comment="Confirming t-op send")
                buf = self.app.read()
                if "[InterPlanetary Operations]" not in buf:
                    botlog.warn("Indeterminate state, not sure why we had " +
                                 "to confirm sending one agent, returning " +
                                 "to interplanetary")
                    self.app.sendl()
                    return
            else:
                if '1 agent sent out.' not in buf:
                    botlog.warn("Agent not sent out")
                    return

            self.data.realm.army.agents.number -= 1
            botlog.note("Sent t-op to " + str(target.planet_name) +
                        " : " + str(target.name))
            self.tops.pop(0)

            if "[InterPlanetary Operations]" in buf:
                self.tops = []
                self.sent_tops = True
                break


    def create_ga_from_tokens(self, tokens):

        botlog.debug("GA parsing tokens: " + ', '.join(tokens))

        t = tokens
        ga = Attack(self)
        i = 0
        ga.id = ToNum(t[i])
        i += 2 # skip who created the GA
        ga.planet = self.data.find_planet(t[i])
        if ga.planet is None:
            raise Exception("Unable to determine planet name from token: " +
                            str(t[i]))
        i += 1
        # what would happen if someone named thier realm 'ALL'
        if t[i] != 'ALL':
            ga.realm = ga.planet.find_realm(t[i])
        i += 1
        ga.troopers = ToNum(t[i])
        i += 1
        ga.jets = ToNum(t[i])
        i += 1
        ga.tanks = ToNum(t[i])
        i += 1
        ga.bombers = ToNum(t[i])
        i += 1
        ga.leave = ToNum(t[i][0:-1])

        botlog.debug("GA token string: " + ', '.join(tokens) +
                     ": yeilds attack: " + str(ga))
        return ga

    def set_ga_text(self,buf):
        self.data.gatext += (
            buf.replace(
                'Join Group Attack', '').replace(
                'Join which group?', '') + "\n")

    def parse_group_attacks(self):
        self.group_attacks = []
        gas = self.group_attacks

        self.app.send('5',comment="selected join attacks, just to list them")

        max_iterations = 50

        next_line_header = False
        reading_body = False
        done_reading = False

        sepchar = ';' #hopefully no one puts this char in their realm name

        self.data.gatext = ""
        buf = ""

        while not done_reading and max_iterations > 0:
            buf = self.app.read()

            # check if there are no GA's
            if 'There are not any attack parties at this time.' in buf:
                botlog.debug("Not parsing any ga's because there arn't any")
                return

            self.set_ga_text(buf)

            lines = buf.split(os.linesep)

            if len(lines) <= 1:
                raise Exception("Expected more lines in group attack buffer")

            # there are some strange chars in the group attack buffer.  I ended
            # up hardcoding the column widths by manually pulling char positions
            # with some debug code.  This might not work if you are not using
            # the black/white version of bre
            # breaks = [(0, 2), (5, 7), (10, 24), (27, 46), (49, 57),
            #           (60, 66), (69, 76), (79, 86), (89, 94)]
            breaks = [(0, 1), (2, 4), (5, 19), (20, 39), (40, 48),
                      (49, 55), (56, 63), (64, 71), (72, 77)]

            #TODO get training text for multipage list
            for line in lines:

                botlog.debug("Parsing Line: '" + line + "'")
                line = line.strip()
                if line == '':
                    continue

                if 'Individual Target' in line:
                    botlog.debug("next line is header")
                    next_line_header = True
                    # i = 0
                    # for c in line:
                    #     dline = str(i) + ": '" + str(c) + "'"
                    #     botlog.debug(dline)
                    #     i += 1
                elif next_line_header:
                    botlog.debug("reading body")
                    next_line_header = False
                    reading_body = True
                elif (reading_body and ('Join which group?' in line or
                        'You must play one turn per entry into the game to access this option.' in line)):
                    botlog.debug("Done reading body")
                    reading_body = False
                    done_reading = True
                    break
                elif reading_body:
                    botlog.debug("Reading body line")
                    i = 0
                    reading_id = 0
                    idtok=""
                    for c in line:
                        dline = str(i) + ": '" + str(c) + "'"
                        botlog.debug(dline)
                        i += 1
                        if reading_id == 0 and c in "0123456789":
                            idtok += c

                        elif reading_id == 0 and c not in "0123456789":
                            reading_id = 1
                            break

                    start_tok = len(idtok) - 1

                    breaks = [(0, 1 + start_tok) ,
                              (2 + start_tok, 4 + start_tok),
                              (5 + start_tok, 19 + start_tok),
                              (20 + start_tok, 39 + start_tok),
                              (40 + start_tok, 48 + start_tok),
                              (49 + start_tok, 55 + start_tok),
                              (56 + start_tok, 63 + start_tok),
                              (64 + start_tok, 71 + start_tok),
                              (72 + start_tok, 77 + start_tok)]

                    tokens = []
                    for x in breaks:
                        tokens.append(line[x[0]:x[1]].strip())
                    # botlog.debug("Tokens are: " + str(tokens))
                    ga = self.create_ga_from_tokens(tokens)
                    gas.append(ga)
                elif 'Join Group Attack' in line:
                    continue
                else:
                    botlog.warn("Unhandled line '" + line + "'")

            max_iterations -= 1

        if max_iterations <= 0:
            raise Exception("Too many iterations when listing GA's")

        # on partial restart you don't get the option to join an attack
        if ('You must play one turn per entry into the game to access this option.'
                not in buf):
            self.app.sendl(0, comment="Not joining GA, just reading list of "
                                      "current ga's")
            buf = self.app.read()

        if "[InterPlanetary Operations]" not in buf:
            raise Exception("Not back at ip menu after parsing group attacks")


    def sort_group_attacks(self):
        self.group_attacks.sort(key=lambda x: x.leave)


    def send_attack(self, attack, strength_to_commit):

        botlog.debug("Sending strength " + str(strength_to_commit) +
                     " on attack: \n" + str(attack))

        needed_strength = strength_to_commit
        # determing the number of troops to put in.  Only put in what is needed
        # to win, otherwise, go all in.
        # TODO implement some way to enforce leaving troops at home to defend
        army = self.data.realm.army
        numjets = 0
        power = 2
        sent_strength = 0
        botlog.debug("Army before sending attack:\n" +
                     str(self.data.realm.army))
        if needed_strength > 0 and army.jets.number > 0:
            jetsstrength = army.jets.number * power
            if jetsstrength > needed_strength:
                numjets = int(math.ceil(needed_strength / float(power)))
            else:
                numjets = army.jets.number
            sent_strength += numjets * power
            needed_strength -= numjets * power
        numtanks = 0
        power = 4
        if needed_strength > 0 and army.tanks.number > 0:
            tanksstrength = army.tanks.number * power
            if tanksstrength > needed_strength:
                numtanks = int(math.ceil(needed_strength / float(power)))
            else:
                numtanks = army.tanks.number
            sent_strength += numtanks * power
            needed_strength -= numtanks * power
        numtroopers = 0
        power = 1
        if needed_strength > 0 and army.troopers.number > 0:
            troopersstrength = army.troopers.number * power
            if troopersstrength > needed_strength:
                numtroopers = int(math.ceil(needed_strength / float(power)))
            else:
                numtroopers = army.troopers.number
            sent_strength += numtroopers * power
            needed_strength -= numtroopers * power


        if strength_to_commit > 10:
            # noone really cares about bombers, just send some portion of what
            # we have
            numbombers = int(0.25 * army.bombers.number)
        else:
            # we commit a small ammount when creating a GA, don't put
            # in bombers at this time
            numbombers = 0


        # Log how much we are submitting if this is not known to be a optimized
        # winning attack
        if (strength_to_commit > 10 and (
            needed_strength > 10 or needed_strength < -10)):
            rname = "ALL"
            if attack.realm is not None:
                rname = attack.realm.name
            botlog.debug("Attack to " + rname + " of " +
                        readable_num(sent_strength) +
                        " is too big or too small for target force of " +
                        readable_num(strength_to_commit) + " by " +
                        readable_num(needed_strength))

        botlog.debug("Sending attack with " + readable_num(numtroopers) +
                     " troopers, " + readable_num(numjets) + " jets, " +
                     readable_num(numtanks) + " tanks, and " +
                     readable_num(numbombers) + " bombers")

        # send the sequence for joining
        self.app.send_seq(
            [numtroopers, '\r', numjets, '\r', numtanks,
             '\r', numbombers, '\r'])
        # if all went according to plan this should be asking us to be sure
        buf = self.app.read()
        ret_val = 0
        if 'Send this Attack? (Y/n)' not in buf:
            botlog.warn("Not able to send out attack: " + str(attack))
        else:
            self.app.send('y', comment="yes, join the attack")
            buf = self.app.read()

            # reduce the inventory of the army by what was just sent
            army.jets.number -= numjets
            army.tanks.number -= numtanks
            army.troopers.number -= numtroopers
            army.bombers.number -= numbombers

            # record what was sent in the attack
            if attack.jets is None:
                attack.jets = numjets
            else:
                attack.jets += numjets
            if attack.tanks is None:
                attack.tanks = numtanks
            else:
                attack.tanks += numtanks
            if attack.troopers is None:
                attack.troopers = numtroopers
            else:
                attack.troopers += numtroopers
            if attack.bombers is None:
                attack.bombers = numbombers
            else:
                attack.bombers += numbombers

            ret_val = sent_strength

            botlog.debug("Army AFTER sending attack:\n" +
                         str(self.data.realm.army))

        # double check we are back at the interplanetary menu
        if '[InterPlanetary Operations]' not in buf:
            raise Exception("Not back at the interplanetary menu after "
                            "sending Attack")

        # botlog.debug("Sent strength: " + str(sent_strength) +
        #              " Attack now:\n" + str(attack))

        return ret_val

    def join_group_attack(self, attack):
        self.app.send(5)

        # read all the attacks until we get to the join prompt
        max_iterations = 20
        self.data.gatext = ""
        while max_iterations > 0:
            buf = self.app.read()
            self.set_ga_text(buf)
            if 'You must play one turn per entry into the game to access this option.' in buf:
                botlog.debug("Can not join GA, we need to play another turn")
                return 0
            if "Join which group?" in buf:
                break
            self.app.sendl(comment="Who the fuck created so many damn GA's")
            max_iterations -= 1

        if max_iterations <= 0:
            raise Exception("too many iterations when joining GA")

        # get how much is needed to put into this attack to make it win
        needed_strength = attack.needed_strength(self.group_attacks)

        botlog.debug("group attack ID: " + str(attack.id) + " needs: " +
                     str(needed_strength) + " strength, joining it now")

        if attack.id is None:
            raise Exception("No attack id")

        self.app.sendl(attack.id,comment="joining attack " + str(attack.id))
        buf = self.app.read()

        ret_val = self.send_attack(attack, needed_strength)

        if ret_val > 0:
            botlog.note("Joined attack: " + str(attack))
            self.joined_gas.append(attack.id)

        return ret_val

    def create_group_attack(self, attack, strength_to_commit=10):

        if self.created_group_attacks:
            return 0

        if attack.leave is None:
            raise Exception("How long to wait is not set in proposed group "
                            "attack")

        botlog.debug("Commiting strength " + str(strength_to_commit) +
                     " and creating group attack: " + str(attack))

        needed_strength = strength_to_commit

        self.app.send(4, comment="Enter group attack menu to create global")
        buf = self.app.read()

        if 'You can only create' in buf and 'Group Strike(s) per day!' in buf:
            botlog.debug("Can not create any more GA's")
            self.created_group_attacks = True
            return 0

        if 'Enter Planet Name or Number' not in buf:
            botlog.warn("Unable to enter Create Group Attack menu")
            return 0

        self.app.sendl(attack.planet.name,
                       comment="Attacking this planet with GA")
        buf = self.app.read()

        if 'Enemy' not in buf:
            raise Exception("Attempting to group attack planet not marked as "
                            "enemy")

        if 'Do you wish to target (O)ne Dominion or (A)ll' not in buf:
            raise Exception("Unable to specify planet for group attack")

        if attack.realm == None:
            self.app.send('a', comment="Creating a global group attack")
            buf = self.app.read()
        else:
            self.app.send('o', comment="Creating a one realm group attack")
            buf = self.app.read()
            if 'Choose a target' not in buf:
                raise Exception("Was not asked which target when creating GA")
            self.app.send(attack.realm.menu_option,
                          comment="create ga to this realm")
            buf = self.app.read()

        if 'Wait how many Hours (12-120)?' not in buf:
            raise Exception("Expected to enter hours before GA leaves")

        self.app.sendl(attack.leave, comment="Sending hours to wait before "
                                             "launching GA")
        buf = self.app.read()

        sent_strength = self.send_attack(attack, needed_strength)

        # if a new GA was created, add it to our list of GA's
        if sent_strength > 0:
            attack.id = len(self.group_attacks) + 1
            botlog.debug("Assigning new ID of " + str(attack.id) + " to GA")
            self.group_attacks.append(attack)
            self.sort_group_attacks()

            botlog.debug("There are now " + str(len(self.group_attacks)) +
                         " group attacks")

            botlog.note("Created group attack: " + str(attack))

        else:
            botlog.debug("For some reason or another we were unable to send "
                         "an attack with strength " + str(needed_strength))

        return sent_strength


    def check_morale_and_hq(self):
        have_tanks = self.data.realm.army.tanks.number > 5000
        low_hq = self.data.realm.army.headquarters.number < 100
        low_morale = False  # TODO, parse morale

        delay_attack = low_morale or (have_tanks and low_hq)

        if (delay_attack and
                self.end_of_day.is_certain and
                self.end_of_day.answer):
            botlog.debug("Should not attack at this time, low morale or hq")
            return False

        if delay_attack:
            botlog.warn("Considering attacking even though morale or HQ is low")

        return True

    def do_not_fill_ga(self, ga):
        # attack is filled don't join
        if ga.is_filled():
            botlog.debug("Attack: " + str(ga.id) +
                         " Is filled, not joining")
            return True

        # if we have no GA that we are currently filling
        # then we could join this one
        if self.currently_filling_ga is None:
            return False

        # if this is not the GA that we are currently filling
        # we don't want to fill it. (we probably could use reference
        # comparison here, but id comparison should be more robust)
        if self.currently_filling_ga.id != ga.id:
            return True

        # now we know this is the GA we are currently filling, we can't
        # contribute at least 10% of current atttack, strength, do not join
        if (self.data.get_attack_strength() <
            0.1 * ga.needed_strength(self.group_attacks)):
            return True

        return False

    def maybe_join_winning_group_attacks(self):

        if not self.try_get_strategy_option(
                "join_current_group_attacks", True):
            return 0


        # if we can top off any GA that leaves soon, lets do it

        botlog.debug("Checking the " + str(len(self.group_attacks)) +
                     " to see if we can cap any of them off that are leaving "
                     "soon")

        if not self.check_morale_and_hq():
            return 0

        ret_val = 0
        for ga in self.group_attacks:

            # ga's are sorted, stop iterating after we are past 24 hours,
            # we won't fill these, we can do it tommorrow
            if ga.leave > 24:
                break

            if ga.planet.relation != "Enemy":
                botlog.debug("Not joining attack to planet who is not enemy")
                continue

            botlog.debug("Group attack " + str(ga.id) + " leaves in " +
                         str(ga.leave) + " hours")

            needed_strength_to_win_ga = ga.needed_strength(self.group_attacks)

            botlog.debug("Determined that " + str(needed_strength_to_win_ga)
                         + " strength is required to win this GA")

            if (0 < needed_strength_to_win_ga <=
                    self.data.get_attack_strength()):

                botlog.debug("Joining group attack id: " + str(ga.id))
                val = self.join_group_attack(ga)
                if val > 0:
                    ret_val += val
                    self.attacked_targets.append(ga.realm)
            else:
                botlog.debug("Attack is full or We do not have enough attack "
                             "strength")

        return ret_val


    def maybe_fill_group_attacks(self):

        ret_val = 0

        if not self.try_get_strategy_option(
                "join_future_group_attacks", True):
            return 0

        # we only join Ga's at the end of our day, theory being, we have
        # already filled any ga's that will win as first priority, and
        # we have also sent any winnable indies
        if self.end_of_day.is_certain() and not self.end_of_day.answer:
            botlog.debug("Not filling GA, more than " + str(
                END_OF_DAY_TURNS) + " turns remain")
            return 0

        # if we have no army, don't join
        if self.data.get_attack_strength() < 1000:
            botlog.debug("Not filling GA, we have very low strength")
            return 0

        # is the ga we are currently filling full?
        if (    self.currently_filling_ga is not None and
                self.currently_filling_ga.is_filled()):
                # the currenty filling ga is now full, reset it
            self.currently_filling_ga = None

        # if there is a GA we are currently filling, just fill that
        if (self.currently_filling_ga is not None and
            not self.do_not_fill_ga(self.currently_filling_ga)):

            val = self.join_group_attack(self.currently_filling_ga)
            if val > 0:
                ret_val += val
                botlog.debug("Joined GA: " + str(self.currently_filling_ga.id) +
                             ", " + "with strength: " + str(val))
                self.attacked_targets.append(self.currently_filling_ga.realm)
                if self.currently_filling_ga.is_filled():
                    self.currently_filling_ga = None

        # if there is a GA that continues to need filling, don't search list
        # for new ga
        if self.currently_filling_ga is not None:
            return ret_val

        # itterate ga's in 24 hour windows
        for t1, t2 in zip(range(0, 24 * 5, 24), range(24, 24 * 6, 24)):
            botlog.debug("Filling GA's that leave in window: " + str((t1,t2)))
            cur_gas = self.get_group_attacks_in_window(t1, t2)

            botlog.debug(str(len(cur_gas)) + "ga's leave in current window")

            global_gas = []
            indie_gas = []

            # classify ga's into global and non global lists
            for ga in cur_gas:

                if ga.planet.relation != "Enemy":
                    botlog.debug(
                        "Not filling group attack to planet who is not enemy")
                    continue

                if ga.is_global():
                    global_gas.append(ga)
                else:
                    indie_gas.append(ga)

            # sort the lists by fattest targets
            global_gas.sort(key=lambda x: x.planet.regions, reverse=True)
            indie_gas.sort(key=lambda x: x.realm.regions, reverse=True)

            botlog.debug(str(len(global_gas)) +
                         "global ga's leave in current window")
            botlog.debug(str(len(indie_gas)) +
                         "indie ga's leave in current window")

            # recombine ga's to new prefered fill order
            # NOTE it could be posisble that an indie GA would yield more
            # regions then a global, (in multi planet war)
            # but in generall I would rather fill
            # globals
            cur_gas = global_gas + indie_gas



            for ga in cur_gas:
                botlog.debug("Considering GA: " + str(ga.id))

                if self.do_not_fill_ga(ga):
                    continue

                val = self.join_group_attack(ga)
                if val > 0:
                    botlog.debug("Joined GA: " + str(ga.id) + ", " +
                                 "with strength: " + str(val))
                    ret_val += val
                    self.attacked_targets.append(ga.realm)
                    # we just joined an attack, if it is not full, this is the
                    # current attack we will be joining until it gets filled
                    if not ga.is_filled():
                        self.currently_filling_ga = ga
                        break

                # if we don't have much more army, stop joining
                if self.data.get_attack_strength() < 1000:
                    botlog.debug("Army is too low, not filling any more GA's")
                    break

                    # if we don't have much more army, stop joining
            if self.data.get_attack_strength() < 1000:
                botlog.debug("Army is too low, stop joining all GA's")
                break


        botlog.debug("Filled " + str(ret_val) + " strength worth of GA's")
        return ret_val

    def send_indie_attack(self, target):

        if self.sent_indies:
            return 0

        self.app.send(6, comment="Enter send indie attack menu")
        buf = self.app.read()

        if ('You can only send' in buf and
                    'individual Strike(s) per day!' in buf):
            self.sent_indies = True
            return 0

        if 'Enter Planet Name or Number' not in buf:
            botlog.warn("Could not send indie attack")
            return 0

        self.app.sendl(target.planet_name, comment=
                "Comment enter planet name for indie attack")
        buf = self.app.read()

        if 'Enemy' not in buf:
            raise Exception("Attempting to attack planet not marked as enemy")

        if 'Choose a target' not in buf:
            raise Exception("Unable to select target for indie attack")

        self.app.send('?',
                      comment="Listing planets for indie attack, for your pleasure")
        buf = self.app.read()
        self.app.send(target.menu_option, comment="Selecting which realm to "
                                                  "indie")
        buf = self.app.read()
        self.app.send(3, comment="Going balls deep with extended attack")

        indie = Attack(self)
        indie.realm = target
        indie.planet = self.data.find_planet(target.planet_name)
        indie.troopers = 0
        indie.jets = 0
        indie.tanks = 0
        indie.bombers = 0

        ret_val = self.send_attack(
            indie,
            (_networth_to_strength(target.networth) *
                self.get_attack_surp_ratio()))
        if ret_val > 0:
            msg = ("Sent indie Attack: " + str(indie))
            botlog.note(msg)
        return ret_val


    def maybe_send_indie_attack(self, targets):

        for target in targets:

            botlog.debug("Possibly sending tops to target: " +
                         str(target.name))
            # send t-ops
            self.send_tops(target)

            botlog.debug("Sending an indie attack to target: " +
                         str(target.name))
            ret_val = self.send_indie_attack(target)

            if ret_val > 0:
                botlog.debug(
                    "Sent strength of " + readable_num(ret_val) + " to target: " +
                    str(target.name))

                return ret_val

        return 0



    def maybe_send_indie_attacks(self):

        if not self.can_send_indie():
            return 0

        if not self.check_morale_and_hq():
            return 0

        # targets are listed in order of sexyness
        botlog.debug("Getting any possible indie targets")
        targets = self.get_indie_targets()
        botlog.debug("found " + str(len(targets)) + " indie targets")
        tot_ret = 0

        # plenty of turns left, just send one attack
        if self.end_of_day.is_certain and not self.end_of_day:
            tot_ret += self.maybe_send_indie_attack(targets)
        else:
            max_iterations = len(targets)
            while self.can_send_indie() and max_iterations >= 0:
                max_iterations -= 1

                ret = self.maybe_send_indie_attack(targets)
                tot_ret += ret

                if ret == 0:
                    break

                botlog.debug("Getting new possible indie targets")
                targets = self.get_indie_targets()
                botlog.debug("found " + str(len(targets)) + " indie targets")


        return tot_ret


    def get_planet_strength(self):
        # get our current strength
        our_strength = _planet_strength(self.app, self.data.planet.realms)

        botlog.debug("Determined our planet has a combined strength of " +
                     str(our_strength))

        return our_strength

    def maybe_create_global_ga(self, our_strength=None, leave=12,
                               strength_to_commit=10):

        if our_strength is None:
            our_strength = self.get_planet_strength()

        #get list of beatable by global attack enemies
        botlog.debug("Searching for a beatable global attack target")
        global_target_planets = []
        for planet in self.data.league.planets:
            if planet.relation != "Enemy":
                continue
            if (our_strength * self.get_attack_surp_ratio() >=
                    _planet_strength(self.app, planet.realms)):
                global_target_planets.append(planet)

        # sort beatable enemies in order of most regions
        global_target_planets.sort(key=lambda x: x.regions, reverse=True)

        botlog.debug("Found global group attack targets: " +
                     str(global_target_planets))

        # bail if no global beatable enemies
        if len(global_target_planets) == 0:
            return 0

        global_attack = Attack(self)
        global_attack.planet = global_target_planets[0]
        global_attack.leave = leave

        return self.create_group_attack(
            attack=global_attack,
            strength_to_commit=strength_to_commit)

    def maybe_create_ga(self, our_strength=None, leave=12,
                        strength_to_commit=10):

        if self.created_group_attacks:
            return 0

        targets = self.get_ga_targets(max_strength=our_strength)
        if len(targets) == 0:
            return 0

        target_realm = targets[0]

        group_attack = Attack(self)
        group_attack.planet = self.data.find_planet(target_realm.planet_name)
        group_attack.leave = leave
        group_attack.realm = target_realm

        return self.create_group_attack(
            attack=group_attack,
            strength_to_commit=strength_to_commit)


    def maybe_create_group_attack(self, max_strength=None, leave=12,
                                  planetary_attack=False,
                                  strength_to_commit=10):
        if self.created_group_attacks:
            return 0

        botlog.debug("Attempting to create a planetary group attack " +
                     " with max strength: " + str(max_strength) +
                     ", leaving in: " + str(leave) + ", planetary: " +
                     str(planetary_attack) + ", strength_to_commit: " +
                     str(strength_to_commit))

        if planetary_attack:
            return self.maybe_create_global_ga(
                our_strength=max_strength,
                leave=leave,
                strength_to_commit=strength_to_commit)
        else:
            return self.maybe_create_ga(
                our_strength=max_strength,
                leave=leave,
                strength_to_commit=strength_to_commit)


    def select_group_attacks(self, context, callback_func):
        result = []
        for ga in self.group_attacks:
            if callback_func(context, result, ga):
                result.append(ga)
        return result


    def _select_group_attacks_in_window(
            self, context, selected_attacks, cur_attack):
        t1 = context[0]
        t2 = context[1]

        if cur_attack.leave >= t1 and cur_attack.leave < t2:
            return True

        return False


    def get_group_attacks_in_window(self, t1, t2):
        result = self.select_group_attacks(
            (t1, t2), self._select_group_attacks_in_window)
        return result


    def maybe_create_group_attacks(self):

        if not self.try_get_strategy_option("create_group_attacks", True):
            return 0

        if self.created_group_attacks:
            botlog.debug("All Group attacks have already been created")
            return 0

        # I am taking this out, because you may want to use GA's if you
        # have exausted your indies


        # if we are the only realm, we won't create a group attack
        # if len(self.data.planet.realms) <= 1:
        #     botlog.debug("We are the only realm, not creating GA's")
        #     return 0

        commited_strength = 0

        # first try to great global ga's then one realm ga's
        for planetary_attack in [True, False]:
            if planetary_attack:
                botlog.debug('considering creating global group attacks')
            else:
                botlog.debug('considering creating regular group attacks')

            # add up what it would take to fill 24 hours worth of currently
            # created group attacks, and create global GA's if we think our planet
            # is capable of filling them
            for t1, t2 in zip(range(0, 24 * 5, 24), range(24, 24 * 6, 24)):
                cur_gas = self.get_group_attacks_in_window(t1, t2)

                botlog.debug("Found " + str(len(cur_gas)) +
                             " leaving in a window of " + str(t1) +
                             " and " + str(t2) + " hours from now")

                # calculate how much strength is needed for all of these attacks
                # to win
                total_base_needed_strength = 0
                for ga in cur_gas:
                    total_base_needed_strength += ga.needed_strength(
                        cur_gas, base=True)

                botlog.debug("Determined the total strength needed for these "
                             "attacks to win is " +
                             str(total_base_needed_strength))

                # calculate how much strength our planet has
                our_strength = self.get_planet_strength()

                # we have already created all of the GA's we can handle
                if our_strength < total_base_needed_strength:
                    botlog.debug("We are already commited all " +
                                 "available strength to GA's no need to " +
                                 "create any in this window")
                    continue

                # we have determined we have some strength left, let us try to
                # create some ga's with it

                planetary_strength_surplus = (
                    our_strength - total_base_needed_strength)

                # because we have seperate functionality for filling the
                # correct GA, we just create GA with minimal amount.  Even
                # though the filling GA's occurs before creating GA's in the
                # War strategy sequence, this is not expected to be a
                # problem, as we can just fill it on the next turn
                strength_to_commit = 1

                botlog.debug("Continuing to attempt to create a group attack")
                newly_commited_strength = self.maybe_create_group_attack(
                    planetary_strength_surplus,
                    strength_to_commit=strength_to_commit,
                    leave=t2,
                    planetary_attack=planetary_attack)

                botlog.debug(str(newly_commited_strength) +
                             " was committed to a new group attack")

                commited_strength += newly_commited_strength

                if self.created_group_attacks:
                    break

            if self.created_group_attacks:
                break


        return commited_strength


    def on_interplanetary_menu(self):

        self.end_of_day = self.app.mentat.is_end_of_day()

        if self.data.setup is None:
            botlog.warn("Game restarted mid turn, "
                        "no war activities on first turn")
            return

        if self.data.setup.local_game:
            raise Exception("War Strategy is not for local games, how can a "
                            "local game be in the interplanetary menu?")

        if not self.data.is_oop():
            botlog.debug("We are in protection, not taking any war actions")
            return

        if not self.at_war:
            botlog.debug("We are not at war, not taking any war actions")
            return

        if self.data.realm.gold < HUNMIL:

            if (self.app.metadata.low_cash or (
                        self.end_of_day.is_certain() and
                        self.end_of_day.answer)):

                self.app.send_seq(['v','w','>','\r','\r'],
                                  comment='withdawing war funds at end of day')
                botlog.info("We are low on money "
                            "on hand, withdrawing some so we can make "
                            "something happen")
                buf = self.app.read()
                self.wp.parse(self.app, buf)
                if self.data.realm.gold < HUNMIL:
                    botlog.info("Jeeze we are really broke, no war")
                    return

            else:
                botlog.info("Skipping War operations, less than 100 mil on hand")
                return

        if self.group_attacks is None:
            self.parse_group_attacks()
            self.sort_group_attacks()
            botlog.debug("Parsed " + str(len(self.group_attacks)) + " ga's")
            for ga in self.group_attacks:
                botlog.debug(str(ga))


        botlog.debug("War phase: maybe_join_winning_group_attacks")
        # join short term GA's that we would cap off to assure victory
        self.maybe_join_winning_group_attacks()

        botlog.debug("War phase: maybe_send_indie_attacks")
        # send indie
        self.maybe_send_indie_attacks()

        botlog.debug("War phase: send_sops")
        # send s-ops
        self.send_sops()

        botlog.debug("War phase: send_tops")
        # send t-ops
        self.send_tops()

        botlog.debug("War phase: maybe_create_group_attacks")
        # create GA's
        self.maybe_create_group_attacks()

        # join partially filled GA's
        botlog.debug("War phase: maybe_fill_group_attacks")
        self.maybe_fill_group_attacks()



