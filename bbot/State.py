#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import re
import botlog
import pprint
from bbot.Utils import *
from bbot.BaseStates import *
from bbot.Data import *
from bbot.Data import *
from bbot.RegionBuy import RegionBuy
from bbot.Strategy import Strategy


#rom BaseStates.State import State
#rom BaseStates.StatsState import StatsState
#rom BaseStates.BailOut import BailOut

S = SPACE_REGEX
N = NUM_REGEX

TNSOA_MAIN_REGEX = re.compile(
    '. Main . [0-9:]+ \[[0-9]+\] Main \[[0-9]+\] Notices:')
SHENKS_MAIN_REGEX = re.compile('.+fidonet.+AFTERSHOCK:')
XBIT_MAIN_REGEX = re.compile(
    '. Main .* Xbit Local Echo \[[0-9]+\] InterBBS FE:')
NER_MAIN_REGEX = re.compile(
    '. Main . [0-9:]+ \[[0-9]+\] Local \[[0-9]+\] Notices:')

MAIN_MENUS = [TNSOA_MAIN_REGEX, SHENKS_MAIN_REGEX, XBIT_MAIN_REGEX]


class LogOff(State):
    def transition(self, app, buf):
        # for the looney bin
        if 'PLEASE MAKE A SELECTION OR "Q" = EXIT' in buf:
            app.send_seq(['q','o','y'],comment="Logoff Sequence")
            app.read()
            return BailOut()
        # logoff sequence for battlestar bbs
        elif 'Battlenet :' in buf and 'Which door number or (Q)uit:' in buf:
            app.send_seq(['q','q','o','y'],comment="Logoff sequence")
            app.read()
            return BailOut()
        elif ('Which, (Q)uit or [1]:' in buf or 
                'Trans-Canada Doors Menu' in buf or
                'Q) Quit back to Main Menu' in buf or
                'Which door number or (Q)uit:' in buf):
            app.send_seq(['q', 'o', 'y'],comment="Logoff sequence")

            app.read()
            return BailOut()
        elif 'Which or (Q)uit:' in buf:
            app.send('q')


class ExitGame(State):
    def transition(self, app, buf):
        if '(1) Play Game' in buf:
            app.send('0')
            return LogOff()
        elif '-=<Paused>=-' in buf:
            app.sendl(comment='continuing from paused prompt before exiting')


from bbot.EndTurnParser import EndTurnParser


class EndTurn(StatsState):
    def __init__(self):
        StatsState.__init__(self, statsParser=EndTurnParser())


    def transition(self, app, buf):

        # i guess this is a good place to reset the emergency vars
        app.metadata.low_cash = False
        app.metadata.low_food = False

        self.parse(app, buf)
        if '[Attack Menu]' in buf:
            ret = app.on_attack_menu()
            # I havn't tested every attack, but, in pirate attack, win or loose
            #   the attack menu is automatically exited from afterwards, and
            #   pirate attack is the only one implmented right now
            if ret == Strategy.UNHANDLED:
                app.send('0', comment='Exiting attack menu')
            else:
                app.skip_next_read = True

        if '[Trading]' in buf:
            app.on_trading_menu()
            app.send('0', comment='Exiting Trading menu')
        elif 'Do you wish to send a message? (y/N)' in buf:
            app.send('n', comment='Not sending a message')
        elif 'Do you wish to attack a Gooie Kablooie? (y/N)' in buf:
            app.send('n', comment='Not attacking gooie')
        elif '[InterPlanetary Operations]' in buf:

            # in case diplomacy changed we will parse any planet realms that
            # we now have a new relationship with that we previously didn't
            _parse_other_realms(app)

            app.on_interplanetary_menu()

            app.send('0', comment='Exiting Inter Planetary menu')
        elif 'Do you wish to continue? (Y/n)' in buf:

            # print out current parsed data state
            botlog.info(str(app.data))

            if (app.data.realm.turns is not None and
                        app.data.realm.turns.current is not None and
                        app.data.realm.turns.remaining is not None and
                        app.metadata.first_played_turn is not None):

                if app.has_app_value("turnsplit"):

                    # TODO, think about randomizing turnsplit, +/- 1
                    turnsplit = ToNum(app.get_app_value("turnsplit"))
                    remaining = app.data.realm.turns.remaining
                    turns_remaining_for_exit = (
                        app.metadata.first_played_turn - turnsplit)

                    if remaining <= turns_remaining_for_exit:
                        botlog.note("We are turnsplitting every " +
                                    str(turnsplit) + " turns, exiting with " +
                                    str(app.data.realm.turns.remaining) +
                                    " turns remaining")
                        app.send('n',
                                 comment='No, not continuing, we are '
                                         'turnsplitting')
                        return MainMenu(should_exit=True)

            else:
                botlog.warn("Not known what turn we are on when exiting the "
                            "turn, did the turn start in mid turn?")

            app.send('y', comment='Yes I wish to continue')

            return TurnStats()


from bbot.SpendingParser import SpendingParser


class Spending(StatsState):
    def __init__(self):
        StatsState.__init__(self, statsParser=SpendingParser())

    def transition(self, app, buf):
        # store the spending menu as we can include it in a status email
        app.data.spendtext = app.buf

        # parse the buy menu
        self.parse(app, buf)

        # if game setup has not been read, # parse it
        if app.data.setup is None:

            app.data.setup = Setup()
            app.send_seq(['*', 'g'])
            buf = app.read()
            self.parse(app, buf)
            if '-=<Paused>=-' in buf:
                app.sendl()
                buf = app.read()

            if ('Coordinator Vote' in buf and
                    app.has_app_value('coordinator_vote')):
                app.send(5,comment='Voting for coordinator')
                buf = app.read()
                coord_name = app.get_app_value('coordinator_vote')
                coord_realm = app.data.get_realm_by_name(
                    coord_name)
                coord_menu_option = coord_realm.menu_option
                app.send(coord_menu_option,
                         comment='Placing vote for ' + coord_name)
                buf = app.read()

            if ('Coordinator Menu' in buf and
                    (   app.has_app_value('enemy_planets') or
                        app.has_app_value('peace_planets') or
                        app.has_app_value('allied_planets') or
                        app.has_app_value('no_relation_planets')
                    )
                ):

                relation_dict = {
                    'enemy_planets': 'w',
                    'peace_planets': 'p',
                    'allied_planets': 'a',
                    'no_relation_planets': 'n'}
                relations = {}

                relation_name_option_dict = {
                    'Enemy': 'w',
                    'Peace': 'p',
                    'Allied': 'a',
                    'None': 'n'
                }

                botlog.debug("iterating relation types")

                for relation in relation_dict.keys():
                    if not app.has_app_value(relation):
                        botlog.debug('No ' + str(relation) +
                                     " planets set in options")
                        continue
                    botlog.debug('processing ' + relation + ' relations')
                    planets = make_string_list(app.get_app_value(relation))
                    botlog.debug(str(planets) + 'being set as ' + relation)
                    for planet_name in planets:
                        relations[planet_name] = relation_dict[relation]

                botlog.debug('Intermediate relation dict is:\n' +
                             str(relations))

                changed_relations = {}
                botlog.debug('Iterating all planets to compare old and new '
                             'relations')
                for planet in app.data.league.planets:
                    planet_name = planet.name
                    botlog.debug('Processing planet ' +
                                 str(planet_name) +
                                 ', looking for a similar name')

                    matched_name = None
                    for new_planet_name in relations.keys():
                        if new_planet_name.lower() in planet_name.lower():
                            matched_name = new_planet_name
                            break

                    if matched_name is None:
                        botlog.debug('Could not match planet ' +
                                     str(planet_name))
                        continue

                    relation_changed = (
                        relation_name_option_dict[planet.relation] !=
                        relations[matched_name])
                    botlog.debug('planet ' + str(planet_name) + ', matches ' +
                                 str(matched_name) + ', did relation change?' +
                                 str(relation_changed))

                    if not relation_changed:
                        continue

                    changed_relations[planet_name] = relations[matched_name]

                botlog.debug("The following relations have changed:\n" +
                             str(changed_relations))

                if len(changed_relations) > 0:
                    app.send('*', comment="Entering coordinator menu")
                    app.read()

                    app.send(2, comment='Modifying diplomacy')
                    app.read()

                    for planet_name in changed_relations.keys():

                        app.sendl(planet_name, comment="Entering planet name")
                        app.read()

                        app.send(changed_relations[planet_name],
                                 comment='Changing disposition to ' +
                                 planet_name)
                        app.read()

                    app.sendl(comment="Leaving modify diplomacy menu")
                    app.read()

                    _parse_diplomacy_list(app, '4', '[Coordinator Ops]')

                    app.sendl(comment="exiting coordinator menu")
                    app.read()


            # parse the information from the advisors, we are only doing this
            # on the first turn, even though this could change every turn, that
            # would be TMI
            app.send('a')
            for advisor in range(1, 5):
                app.data.realm.advisors.reset_advisor(advisor)
                app.send(advisor)
                buf = app.read()
                self.parse(app, buf)
                if '-=<Paused>=-' in buf:
                    app.sendl()
                    buf = app.read()

            # return to the buy menu and parse it again for good measure
            app.send_seq(['0', '0'])
            buf = app.read()
            self.parse(app, buf)


        # TODO write a function to determine when we are almost out of
        # protection, then only start headquarters at that time
        if (app.data.is_oop() and 
                app.data.realm.army.headquarters.number == 0):
            app.send(5, comment="Starting construction on headquarters")
            app.buf = app.read()
            self.parse(app, buf)

        # based on the strategies registered with the app we do differnt
        #   things, tell the app we are ready for the strategies to act
        app.on_spending_menu()

        # any strategy is required to leave the state back in the buy menu
        #   so the current app's buf should be the most recent buy data
        app.data.spendtext = app.buf
        self.parse(app, app.buf)

        buf = app.read()
        if len(buf) > 0:
            app.data.spendtext = app.buf
            # parse the buy menu
            self.parse(app, buf)


        # exit buy menu
        app.sendl()
        return EndTurn()


def list_investments(app, maintParser):
    app.send("l", comment="Checking investments")
    buf = app.read()
    app.data.investmentstext = buf
    app.data.realm.bank.investments = []
    maintParser.parse(app, buf)
    botlog.info("Current Investments : $" +
                str(sum(app.data.realm.bank.investments)) +
                "\n" +
                pprint.pformat(app.data.realm.bank.investments))


from bbot.MaintParser import MaintParser


class Maint(StatsState):
    def __init__(self):
        StatsState.__init__(self, statsParser=MaintParser())
        self.money_reconsider_turn = None
        self.food_reconsider_turn = None
        self.which_maint = None


    def transition(self, app, buf):

        self.parse(app, buf)

        if 'Do you wish to visit the Bank? (y/N)' in buf:
            self.which_maint = "Money"
            app.send('n')
        elif 'How much will you give?' in buf:
            app.sendl()
        elif '[Food Unlimited]' in buf:
            self.which_maint = "Food"
            app.send('0')
        elif '[Covert Operations]' in buf:
            app.send('0')
        elif '[Crazy Gold Bank]' in buf:
            # list the investments, and parse them
            if not app.data.has_full_investments():
                list_investments(app, self.statsParse)
            else:
                botlog.info("Not listing investments, we already know they "
                            "are full")
            if app.on_bank_menu() != Strategy.UNHANDLED:
                list_investments(app, self.statsParse)

            app.send('0')
            return Spending()
        elif ' Regions left] Your choice?' in buf:
            RegionBuy(app, app.data.realm.regions.waste.number)
            app.skip_next_read = True
        elif self.which_maint == 'Money' and 'Would you like to reconsider? (Y/n)' in buf:
            if self.money_reconsider_turn == app.data.realm.turns.current:
                botlog.warn("Unable to prevent not paying bills")
                app.send('n')
                app.metadata.low_cash = True
            else:
                app.send('y')
                botlog.warn("Turn income was not enough to pay bills")
                buf = app.read_until('Do you wish to visit the Bank? (y/N)')

                # maint cost
                maintcost = app.data.get_maint_cost()
                # maint minus current cold is ammount to withdraw
                withdraw = maintcost - app.data.realm.gold
                # don't try to withdraw more than we have or it will take
                #   two enter's to get through the prompt
                if withdraw > app.data.realm.bank.gold or withdraw < 0:
                    withdraw = app.data.realm.bank.gold

                # withdraw the money and get back to the maintenance sequence
                app.send_seq(['y', 'w', str(withdraw), '\r', '0'])

                self.money_reconsider_turn = app.data.realm.turns.current

        elif self.which_maint == 'Food' and 'Would you like to reconsider? (Y/n)' in buf:
            if self.food_reconsider_turn == app.data.realm.turns.current:
                botlog.warn("Unable to prevent not feeding realm")
                app.send('n')
                app.metadata.low_food = True
            else:
                botlog.warn(
                    "Turn food production was not enough to feed empire")
                app.send_seq(['y', 'b', '\r', '0'])
                self.food_reconsider_turn = app.data.realm.turns.current


from bbot.TurnStatsParser import TurnStatsParser


class TurnStats(StatsState):
    def __init__(self):
        StatsState.__init__(self, statsParser=TurnStatsParser())
        self.reset_earntext = True

    def append_stats_text(self, app, buf):
        if self.reset_earntext:
            self.reset_earntext = False
            app.data.earntext = ''
        app.data.earntext += "\n" + buf + "\n"

    def transition(self, app, buf):


        self.parse(app, buf)

        # if we just started playing, record what turn we started at
        if app.metadata.waiting_to_record_first_turn_number is None:
            raise Exception("We should know at this point that we are " +
                            "waiting to record which turn we are playing")
        elif app.metadata.waiting_to_record_first_turn_number:
            app.metadata.first_played_turn = app.data.realm.turns.current
            app.metadata.waiting_to_record_first_turn_number = False

        if 'Sorry, you have used all of your turns today.' in buf:
            app.sendl(comment="Can not start next turn, we used them all, "
                              "going to main menu")
            return MainMenu(should_exit=True)
        elif '-=<Paused>=-' in buf:
            self.append_stats_text(app, buf)
            app.sendl(comment="Continuing from pause after stats display")
        elif 'Do you wish to accept? [Yes, No, or Ignore for now]' in buf:
            r = app.data.realm.turns.remaining
            if r is None:
                r = "an unknown number of"

            botlog.note("Accepting trade deal with " + str(r) +
                        "turns remaining:\n\n" + buf)
            app.send('y', comment="accepting mid day trade deal")
        elif 'Do you wish to accept?' in buf:

            r = app.data.realm.turns.remaining
            if r is None:
                r = "an unknown number of"

            botlog.note("Ignoring trade deal with " + str(r) +
                        "turns remaining:\n\n" + buf)

            # TODO check what the text really is when a trade deal for ignore shows up
            app.send('i', comment="ignoring mid day trade deal")

        elif 'of your freedom.' in buf or 'Years of Protection Left.' in buf:

            # do not append earn text here, this is a status page, we get this
            #   from the main menu for the email

            # this buffer also contains the do you want to visit the bank
            #   question which is handled by the Maint state.  we must skip
            #   the next read, as the line would be eaten with noone to hanlde
            #   it
            app.skip_next_read = True
            return Maint()
        else:
            self.append_stats_text(app, buf)

            #TODO river producing food


from bbot.PreTurnsParser import PreTurnsParser


class PreTurns(StatsState):
    def __init__(self):
        StatsState.__init__(self, statsParser=PreTurnsParser())

    def transition(self, app, buf):

        self.parse(app, buf)

        if 'Would you like to buy a lottery ticket?' in buf:
            # play the lottery

            for i in range(7):
                i = i
                app.sendl()

        elif '-=<Paused>=-' in buf:
            app.sendl()
            if 'Sorry, you have used all of your turns today.' in buf:
                return MainMenu(should_exit=True)

        elif '[Diplomacy Menu]' in buf:
            app.on_diplomacy_menu()
            # exit the diplomicy meny
            app.send('0')

        elif 'Do you wish to accept? [Yes, No, or Ignore for now]' in buf:
            app.send('y', comment="accepting trade deal")

        elif 'Do you wish to accept?' in buf:
            #TODO this might be wronf, needd to look what it says if they send an unacceptable trade deal
            app.send('i')

        # not sure why, but in an IP game, there were sm
        elif '[R]  Reply, [D]  Delete, [I]  Ignore, or [Q]  Quit>' in buf:
            app.data.msgtext += buf + "\n"
            app.send('d', comment="Deleting received message")

        elif '[R] Reply, [D] Delete, [I] Ignore, or [Q] Quit>' in buf:
            app.data.msgtext += buf + "\n"
            app.send('d', comment="Deleting received message")

        elif 'Accept? (Y/n)' in buf:
            app.send('y', comment="Accepting offer for a treaty")

        elif '[Industrial Production]' in buf:
            app.on_industry_menu()
            app.send('n')

            return TurnStats()

        # if a game gets hung up on, you can come out into almost any arbitary
        #   state of the game, we will have to add them here one by one as we
        #   discover them
        elif '[Attack Menu]' in buf:
            app.skip_next_read = True
            return EndTurn()

        # Hung up game can emerge in bank
        elif 'Do you wish to visit the Bank? (y/N)' in buf:
            app.skip_next_read = True
            return Maint()

        # another hangup case
        elif '[Covert Operations]' in buf:
            app.skip_next_read = True
            return Maint()

        # another hanger
        elif '[Crazy Gold Bank]' in buf:
            app.skip_next_read = True
            return Maint()

        elif '[Food Unlimited]' in buf:
            app.skip_next_read = True
            return Maint()

        elif '[Spending Menu]' in buf:
            app.skip_next_read = True
            return Spending()

        elif 'Do you wish to send a message?' in buf:
            app.skip_next_read = True
            return EndTurn()

        elif '[Trading]' in buf:
            app.skip_next_read = True
            return EndTurn()

        elif ' Regions left] Your choice?' in buf:
            SpendingParser().parse(app,buf)
            botlog.info("Restarted turn on region allocate with " +
                        str(app.metadata.regions_left) + " regions")
            RegionBuy(app,num_regions=app.metadata.regions_left)
            botlog.debug("Allocated victory regions")
            app.skip_next_read = True
        
        elif '[InterPlanetary Operations]' in buf:
            app.skip_next_read = True
            return EndTurn()



from bbot.PlanetParser import PlanetParser
from bbot.WarParser import WarParser
from bbot.InterplanetaryParser import InterplanetaryParser
from bbot.OtherPlanetParser import OtherPlanetParser


def _parse_other_realm(app, cur_planet):
    app.send_seq([7, 1], comment="Fake sending a message to read "
                                      "realm stats")
    buf = app.read()
    app.sendl(cur_planet.name, comment="Fake send message to this "
                                       "enemy planet")
    buf = app.read()
    app.send('?', comment="List enemy planet realms")
    buf = app.read()
    opp = OtherPlanetParser(
        cur_planet.realms, planet_name=cur_planet.name)
    opp.parse(app, buf)

    if '-=<Paused>=-' in buf:
        app.sendl(comment="Continuing after displaying other "
                          "realms")
        buf = app.read()

    app.sendl(comment="Not sending message, returning to ip menu ")
    buf = app.read()

    return buf


def _parse_other_realms(app):
    league = app.data.league
    planets = league.planets
    buf = app.buf

    for cur_planet in planets:
        # our own relation to our own planet is None
        # our relation ship to another planet will be 'None'
        # sorry it is confusing, but thats how it works out
        if cur_planet.relation is None or cur_planet.relation == "None":
            continue

        if len(cur_planet.realms) > 0:
            botlog.debug("Not sending fake message to " +
                         cur_planet.name + ", because there are already" +
                         " realms loaded")
            continue

        buf = _parse_other_realm(app, cur_planet)

    return buf


def _parse_diplomacy_list(app, menu_option, calling_menu):
    wp = WarParser()
    app.send(menu_option, comment="Listing diplomacy")

    max_iterations = 10
    while max_iterations > 0:
        buf = app.read()
        wp.parse(app, buf)

        if '-=<Paused>=-' in buf:
            app.sendl(comment="Continuing to list diplomacy")
        elif calling_menu in buf:
            botlog.info("returned to interplanetary menu")
            break

        max_iterations -= 1

    botlog.debug("After parsing diplomacy, league is:\n" +
        str(app.data.league))

    if max_iterations <= 0:
        raise Exception("Too many iterations when listing diplomacy")


class MainMenu(StatsState):
    def __init__(self, should_exit=False):
        StatsState.__init__(self, statsParser=PlanetParser())
        self.should_exit = should_exit
        self.cur_score_list = None
        self.app = None

    def set_interplanetary_score(self, context, planet, num):
        # botlog.debug("Setting " + self.cur_score_list +
        #              " for: " + str(planet.name) + " to " + str(num))
        if self.cur_score_list == "score":
            planet.score = num
        elif self.cur_score_list == "networth":
            planet.networth = num
        elif self.cur_score_list == "regions":
            planet.regions = num
        elif self.cur_score_list == "nwdensity":
            planet.nwdensity = num
        else:
            raise Exception("Unexpected score list: " +
                            str(self.cur_score_list))




    def parse_interplanetary_data(self, app):
        app.data.league = League()
        app.send(9, comment="Entering IP menu to parse scores and dip list")
        app.read()
        app.send(1, comment="Entering IP scores menu")
        app.read()
        # construct parser for interplanetary stats
        ipp = InterplanetaryParser(
            context=None,
            score_callback_func=self.set_interplanetary_score)
        # the score options to parse
        scoredict = {1: 'score', 2: 'networth', 3: 'regions',
                     4: 'nwdensity'}
        app.data.ipscorestext = ''
        # parse each of the score lists
        for menu_option, score_list in scoredict.items():
            app.send(menu_option, comment="Reading stats by planet")
            self.cur_score_list = score_list
            max_iteration = 10

            # keep reading while there are more scores
            while max_iteration > 0:

                app.buf = app.read()
                ipp.parse(app, app.buf)

                lines = app.buf.splitlines()
                for line in lines:
                # remove all zero score planets from the message test
                    if (" 0" in line or
                # remove this filler line
                            "Planetary Post" in line or
                # remove all empty lines
                            "" == line.strip()):
                        continue
                    app.data.ipscorestext += line + "\n"

                max_iteration -= 1

                if 'Continue? (Y/n)' in app.buf:
                    app.send('y', comment="Continuing to display "
                                          "scores")
                elif '-=<Paused>=-' in app.buf:
                    app.sendl(
                        comment="Leaving paused prompt after displaying scores")
                    app.buf = app.read()
                    break

            if max_iteration <= 0:
                raise Exception(
                    "Too many iterations when displaying scores")

        app.send(0, comment='Leaving scores menu')
        app.read()
        self.cur_score_list = None

        _parse_diplomacy_list(app, 'd', '[InterPlanetary Operations]')

        _parse_other_realms(app)

        app.send(0, comment="going back to main game menu")
        app.read()

    def parse_info(self, app):
        self.app = app

        # in the main menu, check the scores
        app.send(3, comment="Checking scores")
        buf = app.read()
        app.data.planet = Planet()
        # read in the scores and stats of all the realms
        self.parse(app, buf)
        app.data.planettext = buf
        if '-=<Paused>=-' in buf:
            app.sendl()
        buf = app.read()

        # in the main menu, check the empire status
        app.send(2, comment="Checking status")
        buf = app.read()
        app.data.statstext = buf
        TurnStatsParser().parse(app, buf)
        if '-=<Paused>=-' in buf:
            app.sendl()
        buf = app.read()

        # in the main menu, check the history
        app.send(5, comment="Checking yesterday's news")
        buf = app.read()
        app.data.yesterdaynewstext = buf
        while 'Continue? (Y/n)' in buf:
            app.send('y', comment="Continue reading yesterday's news")
            buf = app.read()
            app.data.yesterdaynewstext += "\n" + buf
        if '-=<Paused>=-' in buf:
            app.sendl()
        buf = app.read()

        # in the main menu, check the history
        app.send(4, comment="Checking today's news")
        buf = app.read()
        app.data.todaynewstext = buf
        while 'Continue? (Y/n)' in buf:
            app.send('y', comment="Continue reading today's news")
            buf = app.read()
            app.data.todaynewstext += "\n" + buf
        if '-=<Paused>=-' in buf:
            app.sendl()
        buf = app.read()

        # if we have not read in league scores, and if
        # this is an IP game
        if app.data.league is None and '(9)' in buf:
            self.parse_interplanetary_data(app)

        return buf


    def transition(self, app, buf):


        if '-=<Paused>=-' in buf:
            app.sendl(comment="Leaving paused prompt in main menu")
        elif self.should_exit or "Choice> Quit" in buf:

            if "Choice> Quit" in buf:
                app.metadata.used_all_turns = True

            buf = self.parse_info(app)

            # The server should not be playing multiple times, so we need to know if it is
            app.skip_next_read = True
            return ExitGame()

        else:
            self.parse_info(app)

            app.send(1, comment="Commencing to play the game")
            app.metadata.waiting_to_record_first_turn_number = True
            return PreTurns()


class NewRealm(State):
    def transition(self, app, buf):
        app.send_seq([app.get_app_value('realm') + "\r", 'y', 'n'],
                     comment="Creating a new realm")
        return MainMenu()


class StartGame(State):
    def transition(self, app, buf):
        if '<Paused>' in buf or '>Paused<' in buf or '<MORE>' in buf:
            app.sendl()
        elif 'Do you want ANSI Graphics? (Y/n)' in buf:
            app.send('n')
        elif 'Continue? (Y/n)' in buf:
            app.send('y')
        elif 'Name your Realm' in buf:
            return NewRealm()
        elif '(1) Play Game' in buf:
            app.skip_next_read = True
            return MainMenu()


class BBSMenus(State):
    def transition(self, app, buf):


        if "Enter number of bulletin to view or press (ENTER) to continue:" in buf:
            app.sendl()
            # there is a decent pause here sometimes, so just use the read until
            # function
        elif "[Hit a key]" in buf:
            app.sendl(comment="Yet another any key")

        elif ' Read your mail now?' in buf:
            app.send('n',
                     comment="No I will not read mail, I am a fucking robot")

        elif 'Search all groups for new messages' in buf:
            app.send('n',
                     comment="No I will not search for new messages, who uses a bbs for messages?")

        elif 'Search all groups for un-read messages to you' in buf:
            app.send('n',
                     comment="No messsages, how many fucking times do I ahve to tell you")

        # sequence for TNSOA
        elif 'TNSOA' in buf and " Main " in buf and " Notices:" in buf:
            app.send_seq(['x', '2', app.get_app_value('game')])
            return StartGame()

        # sequence for shenks
        elif 'Main' in buf and 'fidonet' in buf and 'AFTERSHOCK' in buf:
            app.send_seq(['x', '2', app.get_app_value('game')])
            return StartGame()

        # sequence for xbit
        elif 'Main' in buf and ' Xbit Local Echo ' in buf:
            app.send_seq(['x', '4', app.get_app_value('game')])
            return StartGame()

        # sequence for ner
        elif 'Main' in buf and ' NER BBS ' in buf:
            app.send_seq(['x', '3', app.get_app_value('game')])
            return StartGame()

        # sequence for trans canada
        elif 'Main' in buf and ' Trans-Canada ' in buf:
            app.send_seq(['x', '7', app.get_app_value('game')])
            return StartGame()

        # sequence for Battlestar
        elif ('Main' in buf and 
                ('Battlestar BBS' in buf or 
                app.get_app_value("address") == 'battlestarbbs.dyndns.org')):
            app.send_seq(['x', '33', app.get_app_value('game')])
            return StartGame()

        # sequence for The Loonie Bin
        elif ('Main' in buf and ('The Loonie Bin' in buf or
                app.get_app_value("address") == 'thelooniebin.net')):
            # there is a "Hit a key" in there because this menu is so big
            app.send_seq(['x', '\r', app.get_app_value('game')])
            return StartGame()

        # sequence for The Section One
        elif ('Main' in buf and ('Section One BBS' in buf or
                app.get_app_value("address") == 'sectiononebbs.com')):
            # there is a "Hit a key" in there because this menu is so big
            app.send_seq(['x', '4', app.get_app_value('game')])
            return StartGame()

class Password(State):
    def transition(self, app, buf):
        if "Password:" in buf or "PW:" in buf:
            app.sendl(app.get_app_value('password'))
            buf = app.read_until("[Hit a key]")
            app.sendl(comment="Is this the any key?")
            return BBSMenus()


class Login(State):
    def transition(self, app, buf):
        if "Login:" in buf or "Enter Name, Number, 'New', or 'Guest'" in buf or 'NN:' in buf:
            app.sendl(app.get_app_value('username'))
            return Password()
        elif 'Hit a key' in buf:
            app.sendl(comment="Where is the any key?")
        elif 'Matrix Login' in buf:
            app.sendl(comment="login to login screen")
            app.read()
            app.sendl(app.get_app_value('username'))
            app.read()
            app.sendl(app.get_app_value('password'))
            return BBSMenus()


