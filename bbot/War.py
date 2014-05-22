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

    def get_strength(self):
        return (self.troopers + (self.jets * 2) +
         (self.tanks * 4))

    def is_filled(self):
        return self.get_strength() >= (self.realm.networth * ATCK_SURP_RATIO)

    def needed_strength(self, group_attacks, base=False):

        # base needed strength
        base = (self.realm.networth * ATCK_SURP_RATIO)

        if group_attacks is None:
            if  not base:
                return int(math.ceil(base) - self.get_strength())
            else:
                return int(math.ceil(base))

        # reduce needed stringth by some ratio for each loaded attack facing
        # the same realm
        reducer = 1.0
        num_reduces = 1
        for ga in group_attacks:

            # stop iterating when we get to this attack
            if ga.id == self.id:
                break
            if ga.leave > self.leave:
                botlog.warn("Itterating to many GA's, are they sorted?")
                continue

            if (ga.realm.name == self.realm.name and
                ga.planet.name == self.planet.name):

                if self.get_strength() >= base:
                    base *= MULTIPLE_ATTACK_REDUCER
                    num_reduces += 1

        if num_reduces > 0:
            botlog.debug("Multiple Ga's have reduced needed strength " + str(
                num_reduces) + " times")

        if not base:
            return int(math.ceil(base)) - self.get_strength()
        else:
            return int(math.ceil(base))






    def __str__(self):
        return _printvisitor(self, 0)

class War(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.army = self.app.data.realm.army
        self.wp = WarParser()
        self.sent_tops = False
        self.sent_sops = False
        self.sop_bombs = [5,7,6]
        self.possible_tops = [2,3,4,9]
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

    def select_highest_regions_enemy_realm(
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
        
    def select_indie_attack_enemy_realm(
            self,
            context,
            selectedrealms,
            planet,
            realm):

        atkstrength = self.app.data.get_attack_strength()
        defstrength = (realm.networth * ATCK_SURP_RATIO)

        # if an attack on the realm is winable
        if atkstrength >= defstrength:
            # add the realm, and sort it in descending order of regions
            selectedrealms.append(realm)
            selectedrealms.sort(key=lambda x: x.regions, reversed=True)


        # we always return false, because we handle maintenance of the
        # selected realms list
        return False

    def can_send_indie(self):
        target = self.select_enemy_realms(
            None,
            self.select_indie_attack_enemy_realm)
        return len(target) > 0

    def get_indie_targets(self):
        targets = self.select_enemy_realms(
            None,
            self.select_indie_attack_enemy_realm)
        return targets

    def get_estimated_attack_cost(self, realm=None):
        # this will take some work to reverse engineer the formular for
        # low/med/high
        return 200000000

    def get_estimated_top_cost(self,realm=None):
        return 10000000

    def can_join_ga(self):
        if self.group_attacks is None:
            return True

        #TODO parse ga's
        return True

    def get_ga_target(self):
        # TODO parse ga's

        if self.group_attacks is None:
            return None
        return None

    def make_initial_wishes(self):
        setup = self.app.data.setup
        wishlist = self.app.metadata.wishlist

        #TODO decide if we are going to try to keep wishlist
        for top in range(setup.num_tops):
            wish = CashWish(
                name="terror_wish",
                ammount=self.get_estimated_top_cost())
            wishlist.append(wish)

        if self.can_join_ga():
            wish = CashWish("ga_wish", self.get_estimated_attack_cost())
            wishlist.append(wish)

        if self.can_send_indie():
            wish = CashWish("indie_wish", self.get_estimated_attack_cost())
            wishlist.append(wish)

        for bop in range(setup.num_bops):
            wish = CashWish(name="undermine_wish",ammount=75000000)
            wishlist.append(wish)




    def on_spending_menu(self):

        if self.first_turn:

            # record the ammount of money we might need to spend in wishlist
            self.first_turn = False
            self.make_initial_wishes()

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
                    "bombers",
                    buyratio=None,
                    ammount=ammount)

            


    def get_highest_networth_enemy_realm(self):
        realms = self.select_enemy_realms(
            None,
            self.select_highest_networth_enemy_realm)
        if len(realms) == 0:
            raise Exception("No realms found when looking for highest "
                            "networth")

        return realms[0]

    def get_highest_regions_enemy_realm(self):
        realms = self.select_enemy_realms(
            None,
            self.select_highest_regions_enemy_realm)
        if len(realms) == 0:
            raise Exception("No realms found when looking for highest "
                            "regions")

        return realms[0]


    def send_sops(self, target_realm):

        if (len(self.sop_bombs) > 0 or not self.all_undermines_sent):
            self.app.send(8,comment="Entering s-op menu")
            self.app.read()

            target_realm = self.get_highest_regions_enemy_realm()

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

            target_realm = self.get_highest_networth_enemy_realm()

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

    def send_tops(self, top_target = None):

        if self.sent_tops:
            return

        # our default top target will be high networth realm

        target = top_target
        if target is None:
            target = self.get_highest_networth_enemy_realm()

        self.app.send(2, comment="Entering t-op menu")
        buf = self.app.read()
        if "Enter Planet Name or Number" not in buf:
            botlog.warn("Unable to choose t-op target planet")
            return

        self.app.sendl(target.planet_name)

        buf = self.app.read()
        if "[Terrorist Ops]" not in buf:
            botlog.warn("Could not get to t-op menu")
            return

        while(len(self.tops) > 0):
            self.app.send(self.tops[0])
            buf = self.app.read()

            if 'Choose a target' not in buf:
                botlog.warn("Unable to choose t-op target realm")
                return

            self.app.send(
                target.menu_option,
                comment="Sending t-op to " + target.name)
            buf = self.app.read()

            if 'Send how many?' not in buf:
                botlog.warn("Not able to send t-op")
                return

            self.app.sendl(1,comment="Sending one t-op")
            buf = self.app.read()
            if '1 agent sent out.' not in buf:
                botlog.warn("Agent not sent out")
                return

            self.tops.pop()

            # TODO confirm the text on the last t-op
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
            lines = buf.split(os.linesep)


            #TODO get training text for multipage list
            #TODO check text for no GA's
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
        self.app.send_seq([0,0,0,0],comment="Not joining GA, just reading "
                                            "list of current ga's")
        buf = self.app.read()
        if "[InterPlanetary Operations]" not in buf:
            raise Exception("Not back at ip menu after parsing group attacks")




    def sort_group_attacks(self):
        self.group_attacks.sort(key=lambda x:x.leave)


    def send_attack(self, attack, needed_strength):
        # determing the number of troops to put in.  Only put in what is needed
        # to win, otherwise, go all in.
        # TODO implement some way to enforce leaving troops at home to defend
        army = self.data.realm.army
        numjets = 0
        power = 2
        if army.jets.number > 0:
            jetsstrength = army.jets.number * power
            if jetsstrength > needed_strength:
                numjets = int(math.ceil(needed_strength / float(power)))
            else:
                numjets = army.jets.number
            needed_strength -= numjets * power
        numtanks = 0
        power = 4
        if army.tanks.number > 0:
            tanksstrength = army.tanks.number * power
            if tanksstrength > needed_strength:
                numtanks = int(math.ceil(needed_strength / float(power)))
            else:
                numtanks = army.tanks.number
            needed_strength -= numtanks * power
        numtroopers = 0
        power = 1
        if army.troopers.number > 0:
            troopersstrength = army.troopers.number * power
            if troopersstrength > needed_strength:
                numtroopers = int(math.ceil(needed_strength / float(power)))
            else:
                numtroopers = army.troopers.number
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
            [attack.id, numtroopers, '\r', numjets, '\r', numtanks,
             '\r', numbombers, '\r'])
        # if all went according to plan this should be asking us to be sure
        buf = self.app.read()
        ret_val = False
        if 'Send this Attack? (Y/n)' not in buf:
            botlog.warn("Not able to send out attack to " + attack.planet
                        .name + " : " + attack.realm.name)
        else:
            self.app.send('y', comment="yes, join the attack")

            # reduce the inventory of the army by what was just sent
            army.jets.number -= numjets
            army.tanks.number -= numtanks
            army.troopers.number -= numtroopers
            army.bombers.number -= numbombers

            buf = self.app.read()
            ret_val = True

        # double check we are back at the interplanetary menu
        if '[InterPlanetary Operations]' not in buf:
            raise Exception("Not back at the interplanetary menu after "
                            "sending Attack")

        # TODO i was going bbot_TOOL_VERSION return something like
        # needed_strength added
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

        # get how much is needed to put into this attack to make it win
        needed_strength = attack.needed_strength(self.group_attacks)

        ret_val = self.send_attack(attack, needed_strength)

        return ret_val

    def create_group_attack(self, attack, needed_strength):

        # check that this is a group attack
        if attack.planet.name is None or attack.planet.name == '':
            botlog.warn('Can not send group attack, no planet specified')

        #TODO I did this sequence blind, verify with real text
        self.app.send(4, comment="Enter group attack menu to create global")
        buf = self.app.read()
        if 'TODO' not in buf:
            botlog.warn("Unable to enter Create Group Attack menu")
            return 0

        self.app.send(attack.planet.name,comment="Attacking this planet with "
                                                 "GA")
        buf = self.app.read()
        if 'TODO' not in buf:
            botlog.warn("Unable to specify planet for group attack")
            return 0

        if attack.realm == None:
            self.app.send('a',comment="Creating a global group attack")
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
                        str(attack.realm.name) )

        return self.send_attack(attack, needed_strength)












    def maybe_join_winning_group_attacks(self):

        # if we can top off any GA that leaves soon, lets do it

        first_target = None

        njoined = 0
        for ga in self.group_attacks:
            # ignore any attack already filled.
            if ga.is_filled():
                continue

            # ga's are sorted, stop iterating after we are past 24 hours,
            # we won't fill these
            if ga.leave > 24:
                break

            needed_strength_to_win_ga = ga.needed_strength(self.group_attacks)
            if self.data.get_attack_strength() >= needed_strength_to_win_ga:
                joined = self.join_group_attack(ga)
                if joined:
                    self.attacked_targets.append(ga.realm)
                    njoined += 1

        return njoined

    def send_indie_attack(self, target):
        self.app.send(6, comment="Enter send indie attack menu")
        buf = self.app.read()
        if 'Enter Planet Name or Number' not in buf:
            botlog.warn("Could not send indie attack")
            return False

        self.app.sendl(target.planet_name,"Comment enter planet name for "
                                          "indie attack")
        buf = self.app.read()
        if 'Our current relations with Prison Board BBS: Enemy' not in buf:
            botlog.warn("Attempting to attack planet not marked as enemy")
            return False
        if 'Choose a target' not in buf:
            botlog.warn("Unable to select target for indie attack")
            return False
        self.app.send('?',comment="Listing planets for indie attack, for your pleasure")
        but = self.app.read()
        self.app.send(target.menu_option,comment="Selecting which realm to "
                                                 "indie")
        self.app.send(3,comment="Going balls deep with extended attack")

        indie = Attack()
        indie.realm = target
        indie.planet = self.data.find_planet(target.planet_name)
        indie.troopers = 0
        indie.jets = 0
        indie.tanks = 0
        indie.bombers = 0


        return self.send_attack(indie, target.networth * ATCK_SURP_RATIO)




    def maybe_send_indie_attacks(self):
        if not self.can_send_indie():
            return

        # targets are listed in order of sexyness
        targets = self.get_indie_targets()

        for target in targets:
            # send t-ops
            self.send_tops(target)
            attack_sent = self.send_indie_attacks(target)
            if not  attack_sent:
                break
            else:
                self.attacked_targets.append(target)


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

        self.create_group_attack(
            attack=global_attack,
            needed_strength=global_target_planets[0])



    def select_group_attacks(self, context, callback_func):
        result = []
        for ga in self.group_attacks:
            if callback_func(context, result, ga ):
                result.append(ga)
        return result


    def _select_group_attacks_in_window(
            self, context, selected_attacks, cur_attack):
        t1 = context[0]
        t2 = context[1]

        if cur_attack.leave >= t1 and cur_attack.leave < t2:
            return True


    def get_group_attacks_in_window(self,t1,t2):
        result = self.select_group_attacks(
            (t1,t2), self._select_group_attacks_in_window)
        return result



    def maybe_create_group_attacks(self):

        # add up what it would take to fill 24 hours worth of currently
        # created group attacks.
        for t1,t2 in zip(range(0, 24 * 5, 24), range(24, 24 * 6, 24)):
            cur_gas = self.get_group_attacks_in_window(t1,t2)

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

            # we have determined we have some strength left, let us try to
            # create some globals with it
            newly_commited_strength = self.maybe_create_global_ga(
                our_strength - total_base_needed_strength,
                leave=t2)

            #TODO stopped here










    def on_interplanetary_menu(self):

        if self.group_attacks is None:
            self.parse_group_attacks()
            self.sort_group_attacks()
            botlog.debug("Parsed ga's:\n" +  str(self.group_attacks))


        # join short term GA's that we would cap off to assure victory
        self.maybe_join_winning_group_attacks()

        # send indie
        self.maybe_send_indie_attacks()


        # send s-ops
        self.send_sops()

        # send t-ops
        self.send_tops()

        # join partial ga's

        # create GA's
        self.maybe_create_group_attacks()

















