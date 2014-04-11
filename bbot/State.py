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
        if 'Which or (Q)uit:' in buf:
            app.send('q')
        elif 'Which, (Q)uit or [1]:' in buf or 'Trans-Canada Doors Menu' in buf:
            app.send_seq(['q', 'o', 'y'],comment="Logoff sequence")
            app.read()
            return BailOut()


class ExitGame(State):
    def transition(self, app, buf):
        if '(1) Play Game' in buf:
            app.send('0')
            return LogOff()
        elif '-=<Paused>=-' in buf:
            app.sendl()


from bbot.EndTurnParser import EndTurnParser


class EndTurn(StatsState):
    def __init__(self):
        StatsState.__init__(self, statsParser=EndTurnParser())

    def transition(self, app, buf):

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
            app.on_interplanetary_menu()
            app.send('0', comment='Exiting Inter Planetary menu')
        elif 'Do you wish to continue? (Y/n)' in buf:
            app.send('y', comment='Yes I wish to continue')
            botlog.info(str(app.data))
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

        # commentin out this because we don't really need it until we heavily start to mine data

        #       # if game setup has not been read, # parse it
        #       if app.data.setup is None:
        #           app.data.setup=Setup()
        #           app.send_seq(['*','g'])
        #           buf = app.read()
        #           self.parse(app,buf)
        #           if '-=<Paused>=-' in buf:
        #               app.sendl()
        #               buf = app.read()
        #           app.send('0')
        #           buf = app.read()
        #           self.parse(app,buf)

        #       # parse the information from the advisors
        #       app.send_seq(['*','a'])
        #       for advisor in range(1,5):
        #           app.data.realm.advisors.reset_advisor(advisor)
        #           app.send(advisor)
        #           buf = app.read()
        #           self.parse(app,buf)
        #           if '-=<Paused>=-' in buf:
        #               app.sendl()
        #               buf = app.read()

        #       # return to the buy menu and parse it again for good measure
        #       app.send_seq(['0','0'])
        #       buf = app.read()
        #       self.parse(app,buf)


        # based on the strategies registered with the app we do differnt
        #   things, tell the app we are ready for the strategies to act
        app.on_spending_menu()

        # any strategy is required to leave the state back in the buy menu
        #   so the current app's buf should be the most recent buy data
        app.data.spendtext = app.buf

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
                if withdraw > app.data.realm.bank.gold:
                    withdraw = app.data.realm.bank.gold

                # withdraw the money and get back to the maintenance sequence
                app.send_seq(['y', 'w', str(withdraw), '\r', '0'])

                self.money_reconsider_turn = app.data.realm.turns.current

        elif self.which_maint == 'Food' and 'Would you like to reconsider? (Y/n)' in buf:
            if self.food_reconsider_turn == app.data.realm.turns.current:
                botlog.warn("Unable to prevent not feeding realm")
                app.send('n')
            else:
                botlog.warn("Turn food production was not enough to feed empire")
                app.send_seq(['y', 'b', '\r', '0'])
                self.food_reconsider_turn = app.data.realm.turns.current


from bbot.TurnStatsParser import TurnStatsParser


class TurnStats(StatsState):
    def __init__(self):
        StatsState.__init__(self, statsParser=TurnStatsParser())
        self.reset_statstext = True

    def append_stats_text(self, app, buf):
        if self.reset_statstext:
            self.reset_statstext = False
            app.data.statstext = ''
        app.data.statstext += "\n" + buf + "\n"

    def transition(self, app, buf):


        self.parse(app, buf)

        if 'Sorry, you have used all of your turns today.' in buf:
            app.data.planettext += "\n" + buf + "\n"
            app.sendl()
            return ExitGame()
        elif '-=<Paused>=-' in buf:
            self.append_stats_text(app, buf)
            app.sendl()
        elif 'Do you wish to accept? [Yes, No, or Ignore for now]' in buf:
            app.send('y', comment="accepting mid day trade deal")
        elif 'Do you wish to accept?' in buf:
            # TODO check what the text really is when a trade deal for ignore shows up
            app.send('i', comment="ignoring mid day trade deal")
        elif 'of your freedom.' in buf or 'Years of Protection Left.' in buf:
            # this buffer also contains the do you want to visit the bank
            #   question which is handled by the Maint state.  we must skip
            #   the next read, as the line would be eaten with noone to hanlde
            #   it
            self.append_stats_text(app, buf)
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
                return ExitGame()

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

        # another hanger
        elif '[Spending Menu]' in buf:
            app.skip_next_read = True
            return Spending()


from bbot.PlanetParser import PlanetParser


class MainMenu(StatsState):
    def __init__(self):
        StatsState.__init__(self, statsParser=PlanetParser())

    def transition(self, app, buf):


        if "Choice> Quit" in buf:
            # we have already played today, don't send emails
            botlog.warn("We already played today")
            # The server should not be playing multiple times, so we need to know if it is
            # app.no_email_reason = "We already played today"
            app.skip_next_read = True
            return ExitGame()
        else:
            # in the main menu, check the scores
            app.send(3, comment="Checking scores")
            buf = app.read()
            app.data.planet = Planet()
            # read in the scores and stats of all the realms
            self.parse(app, buf)
            if '-=<Paused>=-' in buf:
                app.sendl()
            buf = app.read()

            # in the main menu, check the empire status
            app.send(2, comment="Checking status")
            buf = app.read()
            TurnStatsParser().parse(app,buf)
            if '-=<Paused>=-' in buf:
                app.sendl()
            buf = app.read()

            app.send(1, comment="Commencing to play the game")
            return PreTurns()


class NewRealm(State):
    def transition(self, app, buf):
        app.send_seq([app.get_app_value('realm') + "\r", 'y', 'n'])
        return MainMenu()


class StartGame(State):
    def transition(self, app, buf):
        if '<Paused>' in buf or '>Paused<' in buf:
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


class Password(State):
    def transition(self, app, buf):
        if "Password:" in buf:
            app.sendl(app.get_app_value('password'))
            buf = app.read_until("[Hit a key]")
            app.sendl(comment="Is this the any key?")
            return BBSMenus()


class Login(State):
    def transition(self, app, buf):
        if "Login:" in buf:
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


