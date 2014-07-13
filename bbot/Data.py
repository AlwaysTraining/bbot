#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import botlog
import math
import random
from bbot.Utils import readable_num

def _indent(d):
    s = '\n'
    for i in range(d):
        if i == len(range(d)) - 1:
            s += '  +- '
        else:
            s += '  |  '
    return s


def enumerate_attribs(obj):
    for attr in dir(obj):
        if not callable(getattr(obj, attr)) and not attr.startswith("__"):
            yield attr, getattr(obj, attr)


def _dictvisitor(o, basename, curdict,allow_null):
    t = ''

    for n, v in enumerate_attribs(o):

        if basename != '':
            elementname = basename + '_' + n
        else:
            elementname = n


        if not allow_null and v is None:
            continue

        if (isinstance(v, basestring) or isinstance(v, int) or
                isinstance(v, float) or isinstance(v, bool) or
                isinstance(v, list)) or v is None:

            curdict[elementname] = v
        else:
            _dictvisitor(v, elementname, curdict, allow_null)


def _printvisitor(o, d):
    indent = _indent(d)
    t = ''

    for n, v in enumerate_attribs(o):

        if v is None:
            continue

        if (isinstance(v, basestring) or isinstance(v, int) or
                isinstance(v,float) or isinstance(v, bool)):
            t += indent + n + ": " + str(v)
        elif isinstance(v, list):
            t += indent + n + "[" + str(len(v)) + "]:"
            for i in range(len(v)):
                t += indent + str(i) + ")" + _printvisitor(v[i], d + 1)



        else:
            t += indent + n + ":" + _printvisitor(v, d + 1)
    return t


class Units(object):
    def __init__(self):
        self.number = None
        self.price = None
        self.sellprice = None


class ArmyUnits(Units):
    def __init__(self):
        Units.__init__(self)
        self.allocation = None
        self.production = None


class Troopers(ArmyUnits):
    menu_option = '1'
    num_per_carrier = 1000


class Turrets(ArmyUnits):
    menu_option = '3'
    num_per_carrier = 1000


class Jets(ArmyUnits):
    menu_option = '2'
    num_per_carrier = 100


class Tanks(ArmyUnits):
    menu_option = '8'
    num_per_carrier = 5000


class Bombers(ArmyUnits):
    menu_option = '4'
    num_per_carrier = None


class Carriers(ArmyUnits):
    menu_option = '9'
    num_per_carrier = None


class Agents(Units):
    menu_option = '7'
    num_per_carrier = None


class Headquarters(Units):
    menu_option = '5'


class ManufacturedArmy(object):
    def __init__(self):
        self.troopers = Troopers()
        self.turrets = Turrets()
        self.jets = Jets()
        self.tanks = Tanks()
        self.bombers = Bombers()
        self.carriers = Carriers()


class Army(ManufacturedArmy):
    def __init__(self):
        ManufacturedArmy.__init__(self)
        self.agents = Agents()
        self.headquarters = Headquarters()
        self.maintenance = None
        self.morale_bribe = None
        self.food = None
        self.sdi = None

    def __str__(self):
        return _printvisitor(self, 0)


class Region(object):
    def __init__(self):
        self.number = None


class Industrial(Region):
    menu_option = 'i'

    def __init__(self):
        Region.__init__(self)
        self.zonemanufacturing = ManufacturedArmy()


class Agricultural(Region):
    menu_option = 'a'

    def __init__(self):
        Region.__init__(self)
        self.foodyield = None


class Earner(Region):
    def __init__(self):
        Region.__init__(self)
        self.earnings = None


class Desert(Earner):
    menu_option = 'd'


class Coastal(Earner):
    menu_option = 'c'


class Mountain(Earner):
    menu_option = 'm'


class Urban(Region):
    menu_option = 'u'


class Technology(Region):
    menu_option = 't'


class River(Agricultural, Earner):
    menu_option = 'r'


class Regions(object):
    menu_option = '6'

    def __init__(self):
        self.coastal = Earner()
        self.river = River()
        self.agricultural = Agricultural()
        self.desert = Earner()
        self.industrial = Industrial()
        self.urban = Urban()
        self.mountain = Earner()
        self.technology = Technology()
        self.waste = Region()

        self.number_affordable = None
        self.price = None
        self.number = None
        self.maintenance = None

    def clone(self):
        r = Regions()

        r.coastal.number = self.coastal.number
        r.river.number = self.river.number
        r.agricultural.number = self.agricultural.number
        r.desert.number = self.desert.number
        r.industrial.number = self.industrial.number
        r.urban.number = self.urban.number
        r.mountain.number = self.mountain.number
        r.technology.number = self.technology.number
        r.waste.number = self.waste.number
        r.number_affordable = self.number_affordable
        r.price = self.price
        r.number = self.number
        r.maintenance = self.maintenance

        return r


    def __str__(self):
        return _printvisitor(self, 0)

    def normalize(self):
        length = 0
        if self.coastal.number is not None:
            length += self.coastal.number
        if self.river.number is not None:
            length += self.river.number
        if self.agricultural.number is not None:
            length += self.agricultural.number
        if self.desert.number is not None:
            length += self.desert.number
        if self.industrial.number is not None:
            length += self.industrial.number
        if self.urban.number is not None:
            length += self.urban.number
        if self.mountain.number is not None:
            length += self.mountain.number
        if self.technology.number is not None:
            length += self.technology.number

        self.multiply(1.0 / length)

    def multiply(self, length):
        """
        Multiply each region type by a constant
        :rtype : Regions
        """
        if self.coastal.number is not None:
            self.coastal.number = self.coastal.number * length
        if self.river.number is not None:
            self.river.number = self.river.number * length
        if self.agricultural.number is not None:
            self.agricultural.number = self.agricultural.number * length
        if self.desert.number is not None:
            self.desert.number = self.desert.number * length
        if self.industrial.number is not None:
            self.industrial.number = self.industrial.number * length
        if self.urban.number is not None:
            self.urban.number = self.urban.number * length
        if self.mountain.number is not None:
            self.mountain.number = self.mountain.number * length
        if self.technology.number is not None:
            self.technology.number = self.technology.number * length



    def buy_helper(self, r, m, mra, t, length):

        if r.number is None:
            return (m, mra, t)

        ra = r.number * length
        ia = int(ra)

        # randomly choose greather than or greatherthan or equal
        if random.choice([True,False]):
            newmax = ra >= mra
        else:
            newmax = ra > mra

        if newmax:
            mra = ra
            m = r

        r.number = ia
        t += r.number

        return (m, mra, t)

    def ratio_to_buy(self, length):

        self.normalize()

        t = 0
        m = None
        mra = -1

        (m, mra, t) = self.buy_helper(self.coastal, m, mra, t, length)
        (m, mra, t) = self.buy_helper(self.river, m, mra, t, length)
        (m, mra, t) = self.buy_helper(self.agricultural, m, mra, t, length)
        (m, mra, t) = self.buy_helper(self.desert, m, mra, t, length)
        (m, mra, t) = self.buy_helper(self.industrial, m, mra, t, length)
        (m, mra, t) = self.buy_helper(self.urban, m, mra, t, length)
        (m, mra, t) = self.buy_helper(self.mountain, m, mra, t, length)
        (m, mra, t) = self.buy_helper(self.technology, m, mra, t, length)

        d = length - t
        if (d > 0):
            m.number = m.number + d

    def get_menu_number_dict(self):
        d = {}

        if self.coastal.number is not None and self.coastal.number > 0:
            d[Coastal.menu_option] = self.coastal.number
        if self.river.number is not None and self.river.number > 0:
            d[River.menu_option] = self.river.number
        if self.agricultural.number is not None and self.agricultural.number > 0:
            d[Agricultural.menu_option] = self.agricultural.number
        if self.desert.number is not None and self.desert.number > 0:
            d[Desert.menu_option] = self.desert.number
        if self.industrial.number is not None and self.industrial.number > 0:
            d[Industrial.menu_option] = self.industrial.number
        if self.urban.number is not None and self.urban.number > 0:
            d[Urban.menu_option] = self.urban.number
        if self.mountain.number is not None and self.mountain.number > 0:
            d[Mountain.menu_option] = self.mountain.number
        if self.technology.number is not None and self.technology.number > 0:
            d[Technology.menu_option] = self.technology.number

        return d


class Population(object):
    def __init__(self):
        self.taxearnings = None
        self.growth = None
        self.food = None
        self.pop_support_bribe = None
        self.pop_support = None
        self.rate = None
        self.size = None


class Gold(object):
    menu_option = '6'
    num_per_carrier = 100000


class Bank(object):
    def __init__(self):
        self.gold = None
        self.investments = []
        self.approx_return = None


class Turns(object):
    def __init__(self):
        self.remaining = None
        self.current = None
        self.years_protection = None
        self.years_freedom = None


class Food(object):
    menu_option = '5'
    num_per_carrier = None

    def __init__(self):
        self.spoilage = None
        self.units = None
        self.randomly_eaten = None


class Setup(object):
    def __init__(self):
        self.game_start_date = None
        self.turns_per_day = None
        self.protection_turns = None
        self.daily_land_creation = None
        self.planetary_tax_rate = None
        self.max_players = None
        self.interest_rate = None
        self.maint_costs = None
        self.region_cost = None
        self.trade_cost = None
        self.attack_damage = None
        self.attack_rewards = None
        self.army_purchase = None
        self.local_game = None
        self.interbbs_game = None
        self.num_boards = None
        self.attack_cost = None
        self.terror_cost = None
        self.num_indie_attacks = None
        self.num_group_attacks = None
        self.num_tops = None
        self.num_bops = None
        self.days_for_mit = None
        self.gooies = None
        self.bombing_ops = None
        self.missle_ops = None


class Advisor(object):
    pass


class CivilianAdvisor(Advisor):
    menu_option = '1'

    def __init__(self):
        Advisor.__init__(self)
        self.river_food_production = None
        self.food_consumption = None
        self.food_surplus = None
        self.food_deficit = None
        self.years_survival = None


class EconomicAdvisor(Advisor):
    menu_option = '2'

    def __init__(self):
        Advisor.__init__(self)
        self.income = None
        self.world_income_ratio = None
        self.efficiency = None
        self.global_avg_efficiency = None


class MilitaryAdvisor(Advisor):
    menu_option = '3'

    def __init__(self):
        Advisor.__init__(self)


class TechnologyAdvisor(Advisor):
    menu_option = '4'

    def __init__(self):
        Advisor.__init__(self)
        self.mil_tech = None
        self.gold_tech = None
        self.food_tech = None
        self.industry_tech = None
        self.maint_tech = None
        self.sdi_tech = None
        self.food_decay_tech = None


class Advisors(object):
    def __init__(self):
        self.civilian = CivilianAdvisor()
        self.economic = EconomicAdvisor()
        self.military = MilitaryAdvisor()
        self.technology = TechnologyAdvisor()

    def get_advisor(self, menu_option):
        if CivilianAdvisor.menu_option == str(menu_option):
            return self.civilian
        elif EconomicAdvisor.menu_option == str(menu_option):
            return self.economic
        elif MilitaryAdvisor.menu_option == str(menu_option):
            return self.military
        elif TechnologyAdvisor.menu_option == str(menu_option):
            return self.technology
        else:
            raise Exception("Unkown menu options for advisor")

    def reset_advisor(self, menu_option):
        if CivilianAdvisor.menu_option == str(menu_option):
            self.civilian = CivilianAdvisor()
        elif EconomicAdvisor.menu_option == str(menu_option):
            self.economic = EconomicAdvisor()
        elif MilitaryAdvisor.menu_option == str(menu_option):
            self.military = MilitaryAdvisor()
        elif TechnologyAdvisor.menu_option == str(menu_option):
            self.technology = TechnologyAdvisor()
        else:
            raise Exception("Unkown menu options for advisor")


class Pirates(object):
    def __init__(self):
        self.regions = None


class Event:
    def __init__(self):
        self.number = None
        self.time = None

class Realm(object):
    def __init__(self):
        self.regions = Regions()
        self.population = Population()
        self.army = Army()
        self.name = None
        self.gold = None
        self.bank = Bank()
        self.turns = Turns()
        self.food = Food()
        self.queen_taxes = None
        self.score = None
        self.networth = None
        self.advisors = Advisors()
        self.pirates = Pirates()
        self.events = []

    def reset_pirates(self):
        self.pirates = Pirates()


class RealmStats(object):
    def __init__(self):
        self.menu_option = None
        self.name = None
        self.score = None
        self.regions = None
        self.networth = None
        self.treaty = None
        self.planet_name = None


class Planet(object):
    def __init__(self):
        self.realms = []
        self.name = None
        self.networth = None
        self.score = None
        self.regions = None
        self.nwdensity = None
        self.relation = None


    def __str__(self):
        return _printvisitor(self, 0)

    def find_realm(self, name):
        found = None
        for r in self.realms:
            if name in r.name:
                if found is not None:
                    raise Exception("Ambiguous planet name search")
                found = r
        return found


class League(object):
    def __init__(self):
        self.planets = []

    def __str__(self):
        return _printvisitor(self, 0)

class Data(dict):
    def __init__(self):
        self.realm = Realm()
        self.setup = None
        self.statstext = ''
        self.earntext = ''
        self.spendtext = ''
        self.investmentstext = ''
        self.msgtext = ''
        self.planettext = ''
        self.planet = None
        self.yesterdaynewstext = ''
        self.todaynewstext = ''
        self.league = None
        self.ipscorestext = ''
        self.eventtext = ''
        self.gatext = ''
        self.enemyscores = ''


    def __str__(self):
        return _printvisitor(self.realm, 0) + "\n" + _printvisitor(
                self.planet, 0) + "\n" + _printvisitor(self.league, 0)


    def set(self, key, value):
        botlog.debug("recording " + str(key) + " = " + str(value))
        self[key] = value

    def get_maint_cost(self):
        c = 0
        realm = self.realm
        if realm.army.maintenance is not None: c += realm.army.maintenance
        if realm.regions.maintenance is not None: c += realm.regions.maintenance
        if realm.queen_taxes is not None: c += realm.queen_taxes
        if realm.population.pop_support_bribe is not None: c += realm.population.pop_support_bribe
        if realm.army.morale_bribe is not None: c += realm.army.morale_bribe

        return c

    def is_oop(self):
        return self.realm.turns.years_freedom is not None

    def has_full_investments(self, days_missing=0):
        # it is common to see $1,999,999,998 investments, i
        #   so subtract 10 of those off by 2's and you get 20
        TWOBIL = 2000000000
        full = (TWOBIL * (10 - days_missing)) - 20
        botlog.debug(readable_num(full) + " needed for  full investments with " +
                str(days_missing) + " days missing")
        cur = sum(self.realm.bank.investments) 
        botlog.debug(readable_num(cur) + " Current total investments")
        is_full = cur >= full
        botlog.debug("Are investments full?: " + str(is_full))

        return is_full


    def has_full_bank(self):
        return self.realm.bank.gold >= 1999999999

    def get_number(self, item):
        army = self.realm.army
        item = str(item)
        if item == Troopers.menu_option: return army.troopers.number
        if item == Turrets.menu_option: return army.turrets.number
        if item == Jets.menu_option: return army.jets.number
        if item == Tanks.menu_option: return army.tanks.number
        if item == Bombers.menu_option: return army.bombers.number
        if item == Carriers.menu_option: return army.carriers.number
        if item == Agents.menu_option: return army.agents.number
        if item == Food.menu_option: return self.realm.food.units
        if item == Gold.menu_option: return self.realm.gold
        raise Exception("get_number() don't know about option " + str(item))


    def get_price(self, item):
        army = self.realm.army
        item = str(item)
        if item == Troopers.menu_option: return army.troopers.price
        if item == Turrets.menu_option: return army.turrets.price
        if item == Jets.menu_option: return army.jets.price
        if item == Tanks.menu_option: return army.tanks.price
        if item == Bombers.menu_option: return army.bombers.price
        if item == Carriers.menu_option: return army.carriers.price
        if item == Agents.menu_option: return army.agents.price
        raise Exception("get_price() don't know about option " + str(item))

    def get_num_per_carrier(self, item):
        # my experiements indicate:
        # 1k troopers
        # 100 jets
        # 1k turrets
        # 100k gold
        # 5k tanks
        army = self.realm.army
        item = str(item)
        if item == Troopers.menu_option: return army.troopers.num_per_carrier
        if item == Turrets.menu_option: return army.turrets.num_per_carrier
        if item == Jets.menu_option: return army.jets.num_per_carrier
        if item == Tanks.menu_option: return army.tanks.num_per_carrier
        if item == Bombers.menu_option: return army.bombers.num_per_carrier
        if item == Carriers.menu_option: return army.carriers.num_per_carrier
        if item == Agents.menu_option: return army.agents.num_per_carrier
        if item == Food.menu_option: return Food.num_per_carrier
        if item == Gold.menu_option: return Gold.num_per_carrier
        raise Exception(
            "get_num_per_carrier() don't know about option " + str(item))

    def get_menu_option(self, unit_type):
        army = self.realm.army
        if "trooper" in unit_type.lower(): return Troopers.menu_option
        if "turret" in unit_type.lower(): return Turrets.menu_option
        if "jet" in unit_type.lower(): return Jets.menu_option
        if "tank" in unit_type.lower(): return Tanks.menu_option
        if "bomber" in unit_type.lower(): return Bombers.menu_option
        if "carrier" in unit_type.lower(): return Carriers.menu_option
        if "agent" in unit_type.lower(): return Agents.menu_option

        raise Exception(
            "get_menu_option() don't know about type " + str(unit_type))


    def get_realm_by_name(self, name, realms=None):
        if realms is None:
            realms = self.planet.realms
        for r in realms:
            if r.name == name:
                return r
        return None

    def can_get_attack_strength(self):
        army = self.realm.army
        return not ( army.troopers.number is None or army.jets.number is None
                     or army.tanks.number is None)

    def get_attack_strength(self):
        army = self.realm.army
        return (army.troopers.number + (army.jets.number * 2) +
                (army.tanks.number * 4))

    def can_get_defense_strength(self):
        army = self.realm.army
        return not ( army.troopers.number is None or
                     army.turrets.number is None or army.tanks.number is None)

    def get_defense_strength(self):
        army = self.realm.army
        return (army.troopers.number + (army.turrets.number * 2) +
                (army.tanks.number * 4))

    def try_get_needed_surplus(self):
        """Guess at how much food we will need for the next turn"""

        p = self.realm.population
        a = self.realm.advisors

        if p.growth is not None and p.size is not None:
            g = p.growth / float(p.size)
            if g > 0.01:
                botlog.info("Population growth was calulated as " +
                        str(round(g,1)) + "%, that seems high, capping " +
                        " to 1%")
                g = 0.01

        else:
            g = 0.01

        r = a.civilian.food_consumption

        if r is not None:
            r = int(round(g * r, 0))
        else:
            raise Exception("Not known what current food consumption is")

        botlog.info("last population food consumption was " + 
                str(a.civilian.food_consumption) +
            ". at a " + str(round(g*100,2)) +
            "% growth rate, we should need a surplus of " +
            str(r))


        return r

#       # But the time we need to buy ag, we should have paid maintenance, and
#       #   read stats, so the following should always normally happen
#       if p.size is not None and p.food is not None:
#           # determine how much food each person was eating
#           foodPerPerson = p.food/p.size

#           # default to assuming popoulation will increase 5%
#           newsize = p.size * 1.05

#           # if this is at least the second turn, we should know how many
#           #   people came or left last year, which will hopefully be similar
#           #   to this year, so use it to calculate a new size
#           if p.growth is not None:
#               newsize = p.size + p.growth

#           # use this years food per person rate to guess how much food we need
#           #   to produce next year
#           r = newsize * foodPerPerson

#       # Add in what the army ate if they ate 
#       if a.food is not None and r is not None:

#           # there is no easy way to guess how much the army grew last year
#           #   to apply to next year, we just use 5%
#           r = r + (a.food * 1.05)

    def get_realm_dict(self,allow_null=True):
        rdict = {}
        _dictvisitor(self.realm,"",rdict,allow_null)
        return rdict

    def has_enemy(self):
        if self.league is None:
            return False
        for p in self.league.planets:
            if p.relation == "Enemy":
                return True

        return False

    def find_planet(self, name):
        name = name.lower()
        found = None
        for p in self.league.planets:
            if name in p.name.lower():
                if found is not None:
                    raise Exception("Ambiguously specified planet")
                found = p

        return found






        
        
 



