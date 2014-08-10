#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

from bbot.Utils import *
from bbot.Data import *
from bbot.Strategy import Strategy
from bbot.SpendingParser import SpendingParser
from bbot.MetaData import MetaData


class RegionBuy(Strategy):

    def __init__(self, app, num_regions=None, region_ratio=None,
                 enter_region_menu=False):
        Strategy.__init__(self, app)
        self.data = self.app.data
        self.realm = self.app.data.realm
        self.regions = self.app.data.realm.regions
        self.sp = SpendingParser()
        enter_to_exit = False

        if enter_region_menu == True:
            # enter region buying menu
            self.app.send('6',comment="Entering region buy menu")
            # the number of regions we can afford
            buf = self.app.read()
            self.sp.parse(self.app, buf)
            if '-=<Paused>=-' in buf:
                self.app.sendl(comment="continue from region menu")
            elif 'No land is available at this time.' in buf:
                botlog.warn("No more land available to buy")
                return


        # we should be at the region menu here loaded into the current buffer

        # the number of regions we can afforAd
        self.sp.parse(self.app, self.app.buf)
        if (num_regions is None and
            self.app.data.realm.regions.number_affordable == 0):
            botlog.info("Can not afford any regions")
            return

        self.a = num_regions
        if num_regions is None:
            self.a = self.app.data.realm.regions.number_affordable


        if self.a is None:
            raise Exception("Not known how many regions there are")

        wartime = self.app.has_strategy("War") and self.app.data.has_enemy()

        # we could call buy_ag_regions multiple times per turn, but there is usually no
        #   point to doing it, it takes a lot of time when debugging.  If it is ever
        #   shown necessarry, just call it every time (in non debug mode)
        # it has been shown necessary in war time, something with how the
        #   advisor calculates the deficit when there are a lot of waste
        #   regions
        if (wartime or 
            app.metadata.last_ag_buy_turn is None or (
                app.metadata.last_ag_buy_turn !=
                self.data.realm.turns.current)):
            # buy just enough ag, this sends us back to the spending menu
            self.buy_ag_regions()
            app.metadata.last_ag_buy_turn = self.data.realm.turns.current

            self.sp.parse(self.app, self.app.read())

            # we can't afford any more regions after buying ag, this exits
            # back to wherver we came from (menu or turnflow wise)
            if self.a == 0:
                botlog.info("Bought all ag regions, should be back at "
                            "spending menu")
                if 'Your choice?' in self.app.buf or enter_to_exit:
                    app.sendl(comment='leaving ag menu, we bought the limit')

                return


        # in a nuke or victory region allocation, we must allocate, in these
        #   situations, we pass in the number of regions to allocate


        must_allocate = num_regions is not None

        if not must_allocate:
            # if we are very low on regions, buy some
            if (self.data.realm.regions.number is not None and
                    self.data.realm.regions.number < 500):
                if 500 < self.a:
                    enter_to_exit = True
                    self.a = 500

            # during wartime we do not but regions unless in danger of bank
            # overflow, and then we will only buy 1/8th of what we can afford
            elif wartime:
                if self.data.realm.gold > 0.75 * TWOBIL:
                    botlog.info("buying some regions in wartime so we don't "
                                "overflow our cash")

                    self.a = int(math.ceil(self.a * 0.75))
                else:
                    botlog.info("Not buying any regions in wartime")
                    self.a = 0
                enter_to_exit = True
            # We want some money for investments, but only out of protection
            elif (self.app.has_strategy("Investor") and
                    self.data.is_oop() and
                    not self.data.has_full_investments()):
                self.a = int(math.ceil(self.a * 0.125))
                enter_to_exit = True




        if self.a == 0:
            botlog.info("not buying any regions")
            app.sendl(
                comment="leaving buy region menu, we don't want any")
            return

        if region_ratio is None:
            r = self.app.metadata.get_region_ratio_func(
                    self.app,
                    self.app.metadata.get_region_ratio_context)

            # in case of emergency use the default region ratio
            if self.app.metadata.low_cash or self.app.metadata.low_food:
                botlog.warn("Using emergency region ratio")
                r = self.app.metadata.default_region_ratio_func(
                        self.app, None)
        else:
            r = region_ratio

        # botlog.debug("ratio: " + str(r))

        # the regions to buy
        r.ratio_to_buy(self.a)
        # botlog.debug("to buy: " + str(r))

        # maps menu option to number of regions
        r = r.get_menu_number_dict()
        # botlog.debug("buy dict: " + str(r))

        # Sequence for buying regions, return to buy menu
        seq = []
        for menu_option, ammount in r.items():
            seq.append(str(menu_option))
            seq.append(str(ammount))
            seq.append('\r')

        # buy the regions
        self.app.send_seq(seq)

        # re parse region menu/buy menu
        self.sp.parse(self.app, self.app.read())


        # return to the spending menu
        # because we bought all the regions we could afford
        # it automatically gets out of region menu
        # unless we didn't
        if enter_to_exit:
            self.app.sendl(comment="Exiting region menu even though we could "
                                   "buy more")
            # back in spending menu, give it a good parse
            buf = self.app.read()
            self.sp.parse(self.app, buf)

    def buy_ag_regions(self):
        # we start at the region menu

        advisors = self.data.realm.advisors

        num_to_buy = self.app.metadata.last_ag_buy
        wartime = self.app.has_strategy("War") and self.app.data.has_enemy()

        # visit civilian advisor and buy ag regions until he is happy
        limit = 20
        while True:
            limit -= 1
            if limit < 0:
                raise Exception("Possible infinate loop in agriculutre buy")

            self.app.read()

            # cap the number of regions to buy at the limit we can afford
            if num_to_buy is None:
                num_to_buy = 1
            elif num_to_buy > self.a:
                num_to_buy = self.a
            elif num_to_buy < 1:
                num_to_buy = 1

            # visit the ag  minister
            self.app.send('*')
            self.app.read()
            self.app.send(1)
            advisors.reset_advisor(1)
            buf = self.app.read_until("-=<Paused>=-")
            self.sp.parse(self.app, buf)
            self.app.sendl()
            self.app.read()

            needed_years_survival = 2
            needed_surplus = self.app.data.try_get_needed_surplus()
            if wartime:
                needed_years_survival *= 3
                needed_surplus *=3

            # no_deficit = advisors.civilian.food_deficit is None
            deficit_but_ok = (advisors.civilian.years_survival is not None and
                              advisors.civilian.years_survival >
                              needed_years_survival)
            big_enough_surplus = (advisors.civilian.food_surplus >=
                                  needed_surplus)
            not_enough_regions = (
                self.a is None or
                self.a <= 0)

            # if we no longer are able to buy regions, or have enough food
            if (    not_enough_regions or
                        deficit_but_ok or
                        big_enough_surplus):
                # this returns us to the buy region menu
                self.app.send('0')
                break

            # TODO, in some kind of o shit situation we might not be able to buy 
            #   this small ammount of regions

            int_num_to_buy = int(round(num_to_buy))
            if int_num_to_buy > self.a:
                int_num_to_buy = self.a

            self.app.send_seq(['0', 'a', str(int_num_to_buy), '\r'])

            self.a = ( self.a - int_num_to_buy)
            self.app.metadata.last_ag_buy = int_num_to_buy
            if self.a <= 0:
                break

            # for ultimate efficiny you could just always buy one region and
            #   until the adviso says it is okay.  This makes the logs a pain
            #   to read.
            num_to_buy = num_to_buy * 2

        # next time we have to buy ag regions
        #   we will start buying the number we
        #   ended up having to buy this time



