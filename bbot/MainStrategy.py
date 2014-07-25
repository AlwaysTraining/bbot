__author__ = 'dhkarimi'

from bbot.Utils import *
from bbot.Strategy import Strategy

class MainStrategy(Strategy):
    def __init__(self, app):
        Strategy.__init__(self, app)

        self.protection_sell_ratio = self.get_app_value(
            "protection_sell_ratio")
        self.investing_sell_ratio = self.get_app_value(
            "investing_sell_ratio")
        self.normal_sell_ratio = self.get_app_value(
            "normal_sell_ratio")

        self.protection_buy_ratio = self.get_app_value(
            "protection_buy_ratio")
        self.investing_buy_ratio = self.get_app_value(
            "investing_buy_ratio")
        self.normal_buy_ratio = self.get_app_value(
            "normal_buy_ratio")

    def get_army_sell_ratio(self):

        # from the beginning of the game to the first
        # total day out of protection, we will always
        #   sell 100% of regions
        if not self.data.is_oop():
            return self.protection_sell_ratio

        if (self.app.has_strategy("Investor") and
                    (self.data.realm.bank.investments) > 0 and  # TODO a better way to learn if investments are unparsed, or try to garantee that they are parsed before calling this funciton
                not self.data.has_full_investments(days_missing=2)):
            # if only missing one day of investments, this is normal, don't
            # sell anything, otherwise sell a chunk
            return self.investing_sell_ratio

        # in general, we will sell a small portion of our army to suppliment
        #   region growth
        return self.normal_sell_ratio

    def buy_army_units(self, unit_types, buyratio=None,
                       desired_ammount=None):

        if ((buyratio is None and desired_ammount is None) or
                (buyratio is not None and desired_ammount is not None)):
            raise Exception("Must use either a buyratio or desired_ammount")

        botlog.debug("Requested buy with buyratio: " + str(buyratio))
        botlog.debug("Requested buy with desired_ammount: " + str(
            desired_ammount))

        unit_types = Utils.make_string_list(unit_types)

        sp = SpendingParser()

        if isinstance(unit_types, basestring):
            unit_types = [unit_types]

        if unit_types is None or len(unit_types) == 0:
            raise Exception("No unit_types provided")
        tot_ammount = 0

        for unit_type in unit_types:
            # Assume at buy menu
            item = self.app.data.get_menu_option(unit_type)
            ammount = desired_ammount

            # determine number to buy
            price = self.app.data.get_price(item)
            if buyratio is not None:
                gold = self.data.realm.gold * buyratio
                ammount = gold / price
            elif ammount is None:
                raise Exception(
                    "Did not specify ratio or ammount of " + str(
                        unit_type) + " to buy")

            ammount = int(math.floor(ammount))

            if ammount <= 0:
                botlog.info("Could not afford even 1 " + unit_type)
            else:
                self.app.send(item, comment="buying " + unit_type)

                self.app.metadata.max_ammount = -1
                sp.parse(self.app, self.app.read())

                if self.app.metadata.max_ammount == -1:
                    raise Exception("Unable to read max buy amount")

                # if amount for buy is more than possible
                if self.app.metadata.max_ammount < ammount:
                    # cap off how much we are buying
                    ammount = self.app.metadata.max_ammount
                    botlog.debug("Capping max buy to " + str(ammount))

                # buy the items
                self.app.sendl(ammount,
                               comment="Buying " + str(
                                   ammount) + " " + unit_type)
                sp.parse(self.app, self.app.read())
                tot_ammount += ammount

        return tot_ammount


    def get_army_buy_ratio(self):

        # if we are going to try to trade, don't buy anything
        will_attempt_to_trade = False
        if self.app.has_strategy("LocalLackey"):
            lackey = self.app.get_strategy(
                "LocalLackey")
            will_attempt_to_trade = lackey.check_can_trade(
                lackey.get_trade_ratio())

        if self.app.has_strategy("Lackey"):
            lackey = self.app.get_strategy(
                "Lackey")
            will_attempt_to_trade = lackey.check_can_trade(
                lackey.get_trade_ratio())

        if will_attempt_to_trade:
            botlog.info("We may trade this round, do not buying anything")
            return 0

        if not self.data.is_oop():
            return self.protection_buy_ratio

        if (self.app.has_strategy("Investor") and (
                self.data.realm.bank.investments) > 0 and  # TODO a better way to learn if investments are unparsed, or try to garantee that they are parsed before calling this funciton
                not self.data.has_full_investments(days_missing=2)):
            # if only missing one day of investments, this is normal, don't
            # buy anything, otherwise buy a chunk
            return self.investing_buy_ratio

        # in general, we will buy a to suppliment
        # industry
        return self.normal_buy_ratio


    def sell(self, sellItems, sellRatio):
        # we start at the buy menu
        in_buy = True

        if self.visited_sell_menu and sellRatio <= 0:
            return

        # sell all the items specified
        for saleItem in sellItems:
            if str(saleItem) != '6':

                ammount = self.data.get_number(saleItem)

                if ammount is None:
                    botlog.warn('can not sell item, ' +
                                'ammount has not been parsed')
                    continue

                if ammount == 0:
                    continue

                ammount = int(round(ammount * sellRatio, 0))

                if in_buy:
                    # sell all tanks and return to buy menu
                    self.app.send('s')
                    self.visited_sell_menu = True
                    # perform a read and through a spending state to parse all the data
                    self.sp.parse(self.app, self.app.read())
                    in_buy = False

                if ammount > 0:

                    # sell the item
                    self.app.send(saleItem,
                                  comment="selling item " + str(saleItem))

                    # read max ammount for sale
                    self.app.metadata.max_ammount = -1
                    self.sp.parse(self.app, self.app.read())
                    if self.app.metadata.max_ammount == -1:
                        raise Exception("Unable to read max sale amount")

                    botlog.info("Max sale amount is " +
                                str(self.app.metadata.max_ammount) +
                                " desired sale ammount is " +
                                str(ammount) + ", t1 is " +
                                str(type(self.app.metadata.max_ammount)) +
                                " and t2 is " + str(type(ammount)) +
                                ", too much? " +
                                str(self.app.metadata.max_ammount <
                                    ammount))

                    # if max ammoutn for sale is less than what we are selling
                    if self.app.metadata.max_ammount < ammount:
                        # cap off how much we are selling
                        ammount = self.app.metadata.max_ammount

                    # send the number we are selling
                    self.app.sendl(ammount, comment="Selling this many")
                    self.sp.parse(self.app, self.app.read())

            else:
                raise Exception("Do not know how to drop regions yet")

        # return to buy menu
        if not in_buy:
            self.app.send('b')
            self.sp.parse(self.app, self.app.read())

    def sell(self, sellItems, sellRatio):

        # we start at the buy menu
        in_buy = True

        if self.visited_sell_menu and sellRatio <= 0:
            return

        # sell all the items specified
        for saleItem in sellItems:
            if str(saleItem) != '6':

                ammount = self.data.get_number(saleItem)

                if ammount is None:
                    botlog.warn('can not sell item, ' +
                                'ammount has not been parsed')
                    continue

                if ammount == 0:
                    continue

                ammount = int(round(ammount * sellRatio, 0))

                if in_buy:
                    # sell all tanks and return to buy menu
                    self.app.send('s')
                    self.visited_sell_menu = True
                    # perform a read and through a spending state to parse all the data
                    self.sp.parse(self.app, self.app.read())
                    in_buy = False

                if ammount > 0:

                    # sell the item
                    self.app.send(saleItem,
                                  comment="selling item " + str(saleItem))

                    # read max ammount for sale
                    self.app.metadata.max_ammount = -1
                    self.sp.parse(self.app, self.app.read())
                    if self.app.metadata.max_ammount == -1:
                        raise Exception("Unable to read max sale amount")

                    botlog.info("Max sale amount is " +
                                str(self.app.metadata.max_ammount) +
                                " desired sale ammount is " +
                                str(ammount) + ", t1 is " +
                                str(type(self.app.metadata.max_ammount)) +
                                " and t2 is " + str(type(ammount)) +
                                ", too much? " +
                                str(self.app.metadata.max_ammount <
                                    ammount))

                    # if max ammoutn for sale is less than what we are selling
                    if self.app.metadata.max_ammount < ammount:
                        # cap off how much we are selling
                        ammount = self.app.metadata.max_ammount

                    # send the number we are selling
                    self.app.sendl(ammount, comment="Selling this many")
                    self.sp.parse(self.app, self.app.read())

            else:
                raise Exception("Do not know how to drop regions yet")

        # return to buy menu
        if not in_buy:
            self.app.send('b')
            self.sp.parse(self.app, self.app.read())
