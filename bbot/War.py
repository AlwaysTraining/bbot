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

# % of attack strength compared to target networth
ATCK_SURP_RATIO = 1.125
MULTIPLE_ATTACK_REDUCER = 0.9

# what portion of troops stay home
# TODO use this
DEFENSIIVE_RESERVE_RATIO = 0.1


class Attack(object):
    def __init__(self):
        self.id = None
        self.by = None
        self.planet = None
        self.realm = None
        self.troopers = None
        self.jets = None
        self.tanks = None
        self.bombers = None
        self.leave = None

    def __str__(self):

        msg = ""
        msg += "Target: "
        msg += self.planet.name
        if self.realm is not None:
            msg += " (" + self.realm.name + ")"

        if self.troopers is not None and self.troopers > 0:
            msg += ", Troopers: " + readable_num(self.troopers)

        if self.jets is not None and self.jets > 0:
            msg += ", Jets: " + readable_num(self.jets)

        if self.tanks is not None and self.tanks > 0:
            msg += ", Tanks: " + readable_num(self.tanks)

        if self.bombers is not None and self.bombers > 0:
            msg += ", Bombers: " + readable_num(self.bombers)

        return msg

    def get_strength(self):
        return (self.troopers + (self.jets * 2) +
                (self.tanks * 4))

    def get_target_strength(self):
        # for attack on one realm
        target_strength = self.planet.networth

        if self.realm is not None:
            # for planetary attack
            target_strength = self.realm.networth

        return  target_strength

    def is_filled(self, num_reduces=0):

        # for attack on one realm
        target_strength = self.get_target_strength()

        win_strength = target_strength * ATCK_SURP_RATIO

        for i in range(num_reduces):
            win_strength *= MULTIPLE_ATTACK_REDUCER

        return (self.get_strength() >= win_strength)


    def is_global(self):
        return self.realm is None

    def needed_strength(self, group_attacks, base=False):

        # base needed strength
        base = (self.get_target_strength() * ATCK_SURP_RATIO)

        if group_attacks is None:
            if not base:
                return int(math.ceil(base) - self.get_strength())
            else:
                return int(math.ceil(base))

        # reduce needed stringth by some ratio for each loaded attack facing
        # the same realm
        reducer = 1.0
        num_reduces = 0
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

            reduce_strength = False

            if self.is_global():
                if ga.is_global():
                    reduce_strength = ga.is_filled(num_reduces)
                else:
                    # if this is a global, and the considered GA is a non
                    # global, we will not consider any strength reduction.
                    # this will be conservative
                    continue
            else:
                if ga.is_global():
                    # this attack is non global, but considered GA is global.
                    # In this case a filled GA should give us a reduction
                    reduce_strength = ga.is_filled(num_reduces)
                else:
                    # both attacks are non global, reduce if same realm is
                    # being attacked, and attack is filled
                    reduce_strength = (self.realm.name == self.realm.name and
                                       ga.is_filled(num_reduces))

            if reduce_strength:
                # reduce the needed ratio
                base *= MULTIPLE_ATTACK_REDUCER
                num_reduces += 1

        if num_reduces > 0:
            botlog.debug("Multiple Ga's have reduced needed strength " + str(
                num_reduces) + " times")

        return math.max(0, int(math.ceil(base)) - self.get_strength())

class War(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.army = self.app.data.realm.army
        self.wp = WarParser()
        self.sent_tops = False
        self.sent_sops = False
        self.sent_indies = False
        self.sop_bombs = [5, 7, 6]
        self.possible_tops = [2, 3, 4, 9]
        self.tops = []
        self.all_undermines_sent = False
        self.first_turn = True
        self.group_attacks = None
        self.attacked_targets = None


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


        defstrength = (realm.networth * ATCK_SURP_RATIO)

        # if an attack on the realm is winable
        if atkstrength >= defstrength:
            # add the realm, and sort it in descending order of regions
            selectedrealms.append(realm)
            selectedrealms.sort(key=lambda x: x.regions, reversed=True)


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


    # def get_estimated_attack_cost(self, realm=None):
    #     # this will take some work to reverse engineer the formular for
    #     # low/med/high
    #     return 200000000
    #
    # def get_estimated_top_cost(self,realm=None):
    #     return 10000000
    #


    # def make_initial_wishes(self):
    #     setup = self.app.data.setup
    #     wishlist = self.app.metadata.wishlist
    #
    #     #TODO decide if we are going to try to keep wishlist
    #     for top in range(setup.num_tops):
    #         wish = CashWish(
    #             name="terror_wish",
    #             ammount=self.get_estimated_top_cost())
    #         wishlist.append(wish)
    #
    #     if self.can_join_ga():
    #         wish = CashWish("ga_wish", self.get_estimated_attack_cost())
    #         wishlist.append(wish)
    #
    #     if self.can_send_indie():
    #         wish = CashWish("indie_wish", self.get_estimated_attack_cost())
    #         wishlist.append(wish)
    #
    #     for bop in range(setup.num_bops):
    #         wish = CashWish(name="undermine_wish",ammount=75000000)
    #         wishlist.append(wish)




    def on_spending_menu(self):

        if self.data.setup.local_game:
            botlog.warn("War Strategy is not for local games")
            return Strategy.UNHANDLED

        if self.first_turn:

            self.first_turn = False

            # record the ammount of money we might need to spend in wishlist
            # self.make_initial_wishes()

            # setup the tops we plan on sending, game setup is read by now
            for i in range(self.data.setup.num_tops):
                self.tops = random.choice(self.possible_tops)


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
            if self.army.agents.number < 1000:
                botlog.warn("Could not buy 1k agents")

        if self.army.bombers is None or self.army.bombers.number is None:
            botlog.warn("Not known how many agents there are")

        # buy bombers if necessarry
        elif self.army.bombers.number < 1000:
            self.buy_army_units(
                "agents",
                buyratio=None,
                desired_ammount=10000 - self.army.bombers.number)
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
                    "bombers",
                    buyratio=None,
                    ammount=ammount)


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
            self.sop_bombs = []
            self.all_undermines_sent = True
            return


        self.app.send(8, comment="Entering s-op menu")
        self.app.read()


        # send s-op missles
        while not self.sent_sops and len(self.sop_bombs) > 0:

            # pick the correct target for this type of missle if the user
            # has not specified a desired target
            if caller_supplied_target_realm is None:
                if self.sop_bombs[0] == 5:
                    # nuke big region target
                    target_realm = self.get_highest_regions_enemy_realm()
                elif self.sop_bombs[0] == 6:
                    # chem big region target
                    target_realm = self.get_highest_regions_enemy_realm()
                else:
                    # sabre big net target
                    target_realm = self.get_highest_networth_enemy_realm()
            else:
                target_realm = caller_supplied_target_realm

            # check if we have already sent this type of bomb
            menu_string = '(' + self.sop_bombs[0] + ')'
            if menu_string not in buf:
                # this bomb is not available, try next one
                self.sop_bombs.pop()
                continue

            self.app.send(self.sop_bombs[0], comment="Sending bomb")
            buf = self.app.read()

            if "All missiles and bombs require 500 Bombers to deliver their " \
               "payloads." in buf:
                botlog.warn("Not enough bombers to send S-op")
                self.app.sendl(comment="Returning from S-Op to interplanetary "
                                       "menu")
                buf = self.app.read()
                return

            if "Enter Planet Name or Number" not in buf:
                raise Exception("Not able to send missle s-op")

            self.app.sendl(target_realm.planet_name)
            buf = self.app.read()

            if 'Enemy' not in buf:
                raise Exception(
                    "Attempting to bomb planet not marked as enemy")

            # because this is what a human would do, and we might like to read
            # it in the log
            self.app.send('?', comment="Displaying realms at missle s-op menu")
            self.app.read()
            self.app.send(target_realm.menu_option)
            buf = self.app.read()

            if "You cannot afford it." in buf:
                botlog.warn("Could not afford to send S-Op missle/bomb")
                # though we can't afford it, we don't quit, we break,
                # which will then cause us to send undermines in the next
                # loop.

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
            # TODO verify it is always 500 bombers per sop
            self.data.realm.army.bombers -= 500




        # send s-op undermines
        if not self.all_undermines_sent:
            max_iterations = 20
            while max_iterations > 0:
                self.app.send("4", comment="Undermining Investments")
                buf = self.app.read()

                if "You can't afford that!" in buf:
                    botlog.warn("Could not afford to send undermine")
                    self.app.sendl(
                        comment="Returning from S-Op to interplanetary "
                                "menu")
                    buf = self.app.read()
                    return

                if ("All missiles and bombs require 500 Bombers to deliver "
                    "their payloads." in buf):
                    botlog.warn("Not enough bombers to send undermine")
                    self.app.sendl(
                        comment="Returning from S-Op to interplanetary "
                                "menu")
                    buf = self.app.read()
                    return

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
                    raise Exception("Not able to send undermine to enemy planet")

                self.app.send('y')
                buf = self.app.read()
                if "Mission Specialists sent out." not in buf:
                    raise Exception("Could not send undermine to enemy planet")

                self.data.realm.army.bombers -= 500

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
            botlog.warn("Unexpected exit from S-Op menu")
            self.app.sendl(
                comment="Returning from S-Op to interplanetary menu")
            buf = self.app.read()

        if '[InterPlanetary Operations]' not in buf:
            raise Exception(
                "Not returned to interplanetary menu after S-Op menu")



    def send_tops(self, top_target=None):

        if self.sent_tops:
            return

        # our default top target will be high networth realm

        target = top_target
        if target is None:
            target = self.get_highest_networth_enemy_realm()

        self.app.send(2, comment="Entering t-op menu")
        buf = self.app.read()

        if "You can't afford that!" in buf:
            botlog.warn("Can not afford to send T-Ops")
            return

        # if we have already sent the limit, lets not try to do it again
        if "Limit " in buf and " Terrorist Operations per day!" in buf:
            self.sent_tops = True
            return

        if "Enter Planet Name or Number" not in buf:
            botlog.warn("Unable to choose t-op target planet")
            return

        self.app.sendl(target.planet_name, comment="entering planet name for "
                                                   "top target")
        buf = self.app.read()

        if 'Enemy' not in buf:
            raise Exception("Attempting to terrorize planet not marked as "
                            "enemy")

        if 'Choose a target' not in buf:
            botlog.warn("Unable to choose t-op target realm")
            return

        self.app.send(
            target.menu_option,
            comment="Sending t-ops to " + target.name)
        buf = self.app.read()

        if "[Terrorist Ops]" not in buf:
            botlog.warn("Could not get to t-op menu")
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
                    self.app.sendl()
                    return
                #
                # if 'agents sent out.' not in buf:
                #     botlog.warn("Agents not sent out")
                #     return
            else:
                if '1 agent sent out.' not in buf:
                    botlog.warn("Agent not sent out")
                    return

            self.tops.pop()

            if "[InterPlanetary Operations]" in buf:
                self.tops = []
                self.sent_tops = True
                break


    def create_ga_from_tokens(self, tokens):
        t = tokens
        ga = Attack()
        i = 0
        ga.id = ToNum(t[i])
        i += 1
        ga.planet = self.data.find_planet(t[i])
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
        return ga

    def parse_group_attacks(self):
        self.group_attacks = []
        gas = self.group_attacks

        self.app.send('5')

        max_iterations = 50

        next_line_header = False
        reading_body = False

        sepchar = None

        while max_iterations > 0:
            buf = self.app.read()

            # check if there are no GA's
            if 'There are not any attack parties at this time.' in buf:
                return


            lines = buf.split(os.linesep)

            if len(lines) <= 1:
                raise Exception("Expected more lines in group attack buffer")


            #TODO get training text for multipage list
            for line in lines:
                if 'Individual Target' in line:
                    next_line_header = True
                elif next_line_header:
                    sepchar = line[0]
                    next_line_header = False
                    reading_body = True
                elif reading_body and 'Join which group?' in line:
                    reading_body = False
                    break
                elif reading_body:
                    tokens = [x.strip() for x in line.split(sepchar)]
                    ga = self.create_ga_from_tokens(tokens)
                    gas.append(ga)

                else:
                    raise Exception("Could not parse group attacks")

            max_iterations -= 1

        if max_iterations <= 0:
            raise Exception("Too many iterations when listing GA's")

        self.app.send_seq([0, 0, 0, 0], comment="Not joining GA, just reading "
                                                "list of current ga's")
        buf = self.app.read()
        if "[InterPlanetary Operations]" not in buf:
            raise Exception("Not back at ip menu after parsing group attacks")


    def sort_group_attacks(self):
        self.group_attacks.sort(key=lambda x: x.leave)


    def send_attack(self, attack, needed_strength):
        # determing the number of troops to put in.  Only put in what is needed
        # to win, otherwise, go all in.
        # TODO implement some way to enforce leaving troops at home to defend
        army = self.data.realm.army
        numjets = 0
        power = 2
        sent_strength = 0
        if army.jets.number > 0:
            jetsstrength = army.jets.number * power
            if jetsstrength > needed_strength:
                numjets = int(math.ceil(needed_strength / float(power)))
            else:
                numjets = army.jets.number
            sent_strength += numjets * power
            needed_strength -= numjets * power
        numtanks = 0
        power = 4
        if army.tanks.number > 0:
            tanksstrength = army.tanks.number * power
            if tanksstrength > needed_strength:
                numtanks = int(math.ceil(needed_strength / float(power)))
            else:
                numtanks = army.tanks.number
            sent_strength += numtanks * power
            needed_strength -= numtanks * power
        numtroopers = 0
        power = 1
        if army.troopers.number > 0:
            troopersstrength = army.troopers.number * power
            if troopersstrength > needed_strength:
                numtroopers = int(math.ceil(needed_strength / float(power)))
            else:
                numtroopers = army.troopers.number
            sent_strength += numtroopers * power
            needed_strength -= numtroopers * power

        # noone really cares about bombers, just send some portion of what
        # we have
        numbombers = int(0.25 * army.bombers.number)


        # integrety check, this should be true, we should only be sending
        # enough to win
        if needed_strength > 10 or needed_strength < -1:
            botlog.warn("Attack force too big or too small for " +
                        attack.planet.name + " : " + attack.realm.name +
                        " by: " + str(needed_strength))

        # send the sequence for joining
        self.app.send_seq(
            [numtroopers, '\r', numjets, '\r', numtanks,
             '\r', numbombers, '\r'])
        # if all went according to plan this should be asking us to be sure
        buf = self.app.read()
        ret_val = 0
        if 'Send this Attack? (Y/n)' not in buf:
            botlog.warn("Not able to send out attack to " + str(attack.planet
                        .name) + " : " + str(attack.realm.name))
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

        # double check we are back at the interplanetary menu
        if '[InterPlanetary Operations]' not in buf:
            raise Exception("Not back at the interplanetary menu after "
                            "sending Attack")

        return ret_val

    def join_group_attack(self, attack):
        self.app.send(5)

        # read all the attacks until we get to the join prompt
        max_iterations = 20
        while max_iterations > 0:
            buf = self.app.read()
            if "Join which group?" in buf:
                break
            self.app.sendl(comment="Who the fuck created so many damn GA's")
            max_iterations -= 1

        if max_iterations <= 0:
            raise Exception("too many iterations when joining GA")

        # get how much is needed to put into this attack to make it win
        needed_strength = attack.needed_strength(self.group_attacks)

        ret_val = self.send_attack(attack, needed_strength)

        return ret_val

    def create_group_attack(self, attack, needed_strength):


        self.app.send(4, comment="Enter group attack menu to create global")
        buf = self.app.read()

        if 'Enter Planet Name or Number' not in buf:
            raise Exception("Unable to enter Create Group Attack menu")

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
            if 'TODO' not in buf:
                botlog.warn("Unable to create one realm GA")
                max_ter = 10
                while "[InterPlanetary Operations]" not in buf and max_ter > 0:
                    max_ter -= 1
                    self.app.sendl(comment="trying to get back to " \
                                           "interplanetary menu")
                    buf = self.app.read()
                return 0

            self.app.send(
                attack.realm.menu_option,
                comment="creating attacking to realm: " +
                        str(attack.realm.name))
            buf = self.app.read()

        if 'Wait how many Hours (12-120)?' not in buf:
            raise Exception("Expected to enter hours before GA leaves")

        self.app.sendl(attack.leave, comment="Sending hours to wait before "
                                             "launching GA")
        buf = self.app.read()

        sent_strength = self.send_attack(attack, needed_strength)

        # if a new GA was created, add it to our list of GA's
        if sent_strength > 0:
            self.group_attacks.append(attack)
            self.sort_group_attacks()

        return sent_strength


    def maybe_join_winning_group_attacks(self):

        # if we can top off any GA that leaves soon, lets do it


        ret_val = 0
        for ga in self.group_attacks:

            # ga's are sorted, stop iterating after we are past 24 hours,
            # we won't fill these, we can do it tommorrow
            if ga.leave > 24:
                break

            needed_strength_to_win_ga = ga.needed_strength(self.group_attacks)
            if self.data.get_attack_strength() >= needed_strength_to_win_ga:
                val = self.join_group_attack(ga)
                if val > 0:
                    ret_val += val
                    self.attacked_targets.append(ga.realm)

        return ret_val


    def maybe_fill_group_attacks(self):

        # we only join Ga's at the end of our day, theory being, we have
        # already filled any ga's that will win as first priority, and
        # we have also sent any winnable indies
        if self.data.realm.turns.remaining > 3:
            return  0

        # if we have no army, don't join
        if self.data.get_attack_strength() < 1000:
            return 0

        # itterate ga's in 24 hour windows
        for t1, t2 in zip(range(0, 24 * 5, 24), range(24, 24 * 6, 24)):
            cur_gas = self.get_group_attacks_in_window(t1, t2)

            global_gas = []
            indie_gas = []

            # classify ga's into global and non global lists
            for ga in cur_gas:
                if ga.is_global():
                    global_gas.append(ga)
                else:
                    indie_gas.append(ga)

            # sort the lists by fattest targets
            global_gas.sort(key = lambda x: x.planet.regions, reverse=True)
            indie_gas.sort(key=lambda x: x.realm.regions, reverse=True)

            # recombine ga's to new prefered fill order
            # NOTE it could be posisble that an indie GA would yield more
            # regions then a global, but in generall I would rather fill
            # globals
            cur_gas = global_gas + indie_gas

            ret_val = 0

            for ga in cur_gas:

                val = self.join_group_attack(ga)
                if val > 0:
                    ret_val += val
                    self.attacked_targets.append(ga.realm)

                # if we don't have much more army, stop joining
                if self.data.get_attack_strength() < 1000:
                    break

                # if we don't have much more army, stop joining
            if self.data.get_attack_strength() < 1000:
                break

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

        self.app.sendl(target.planet_name, "Comment enter planet name for "
                                           "indie attack")
        buf = self.app.read()

        if 'Enemy' not in buf:
            raise Exception("Attempting to attack planet not marked as enemy")

        if 'Choose a target' not in buf:
            raise  Exception("Unable to select target for indie attack")

        self.app.send('?',
                      comment="Listing planets for indie attack, for your pleasure")
        buf = self.app.read()
        self.app.send(target.menu_option, comment="Selecting which realm to "
                                                  "indie")
        buf = self.app.read()
        self.app.send(3, comment="Going balls deep with extended attack")

        indie = Attack()
        indie.realm = target
        indie.planet = self.data.find_planet(target.planet_name)
        indie.troopers = 0
        indie.jets = 0
        indie.tanks = 0
        indie.bombers = 0

        ret_val = self.send_attack(indie, target.networth * ATCK_SURP_RATIO)
        if ret_val > 0:
            msg = ("Sent indie Attack:\n" + str(indie))
            botlog.note(msg)




    def maybe_send_indie_attacks(self):

        if not self.can_send_indie():
            return

        # targets are listed in order of sexyness
        targets = self.get_indie_targets()
        tot_ret = 0

        for target in targets:
            # send t-ops
            self.send_tops(target)
            ret_val = self.send_indie_attack(target)
            tot_ret += ret_val


            if ret_val == 0:

                # we do our best to ensure we are attacking targets in the right
                # order, if we couldn't attack, it is probably because we couldn't
                # afford it, lets just wait until we have more money

                # TODO on last turn, relax this rule, and allow exaustively
                #   attacking all indie targets


                break
            else:
                self.attacked_targets.append(target)

        return tot_ret


    def get_planet_strength(self):
        # get our current strength
        our_strength = 0
        for realm in self.data.planet.realms:
            our_strength += realm.networth

        return our_strength

    def maybe_create_global_ga(self, our_strength=None, leave=12):

        if our_strength is None:
            our_strength = self.get_planet_strength()

        #get list of beatable by global attack enemies
        global_target_planets = []
        for planet in self.data.league.planets:
            if planet.relation != "Enemy":
                continue
            if our_strength * ATCK_SURP_RATIO >= planet.networth:
                global_target_planets.append(planet)

        # sort beatable enemies in order of most regions
        global_target_planets.sort(key=lambda x: x.regions, reverse=True)

        # bail if no global beatable enemies
        if len(global_target_planets) == 0:
            return 0

        global_attack = Attack()
        global_attack.planet = global_target_planets[0]
        global_attack.leave = leave

        return self.create_group_attack(
            attack=global_attack,
            needed_strength=global_target_planets[0].networth * ATCK_SURP_RATIO)

    def maybe_create_ga(self, our_strength=None, leave=12):

        targets = self.get_ga_targets(max_strength=our_strength)
        if len(targets) == 0:
            return 0

        target_realm = targets[0]

        group_attack = Attack()
        group_attack.planet = self.data.find_planet(target_realm.planet_name)
        group_attack.leave = leave
        group_attack.realm = target_realm

        return self.create_group_attack(
            attack=group_attack,
            needed_strength=target_realm.networth * ATCK_SURP_RATIO)


    def maybe_create_group_attack(self, max_strength=None, leave=12,
                                  planetary_attack=False):
        if planetary_attack:
            return self.maybe_create_global_ga(
                our_strength=max_strength,
                leave=leave)
        else:
            return self.maybe_create_ga(
                our_strength=max_strength,
                leave=leave)


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


        # first try to great global ga's then one realm ga's
        for planetary_attack in [True, False]:
            # add up what it would take to fill 24 hours worth of currently
            # created group attacks, and create global GA's if we think our planet
            # is capable of filling them
            for t1, t2 in zip(range(0, 24 * 5, 24), range(24, 24 * 6, 24)):
                cur_gas = self.get_group_attacks_in_window(t1, t2)

                # calculate how much strength is needed for all of these attacks
                # to win
                total_base_needed_strength = 0
                for ga in cur_gas:
                    total_base_needed_strength += ga.needed_strength(
                        cur_gas, base=True)

                # calculate how much strength our planet has
                our_strength = self.get_planet_strength()

                # we have already created all of the GA's we can handle
                if our_strength < total_base_needed_strength:
                    continue

                # # we have determined we have some strength left, let us try to
                # # create some ga's with it
                # planetary_strength_surplus = (
                #     our_strength - total_base_needed_strength)
                #
                # # if creating a GA far in the future, don't bother fully committing
                # #   at this time
                # if t1 > 48:
                #     strength_to_commit = 10
                # else:
                #     # we know we often can't contribute the planetary ammount
                #     # ourselves, but we don't want to contribute more then that
                #     # for sure
                #     strength_to_commit = planetary_strength_surplus

                # because we have seperate functionality for filling the
                # correct GA, we just create GA with minimal ammount
                strength_to_commit = 10


                newly_commited_strength = self.maybe_create_group_attack(
                    strength_to_commit,
                    leave=t2,
                    planetary_attack=planetary_attack)


    def on_interplanetary_menu(self):

        if self.data.setup.local_game:
            raise Exception("War Strategy is not for local games, how can a "
                            "local game be in the interplanetary menu?")


        if self.group_attacks is None:
            self.parse_group_attacks()
            self.sort_group_attacks()
            botlog.debug("Parsed ga's:\n" + str(self.group_attacks))

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



