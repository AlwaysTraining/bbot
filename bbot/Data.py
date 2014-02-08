#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import botlog

class Units(object):
    number=None
    price=None
    sellprice=None
class ArmyUnits(Units):
    allocation=None
    production=None
class Troopers(ArmyUnits):
    menu_option='1'
class Turrets(ArmyUnits):
    menu_option='2'
class Jets(ArmyUnits):
    menu_option='3'
class Tanks(ArmyUnits):
    menu_option='8'
class Bombers(ArmyUnits):
    menu_option='4'
class Carriers(ArmyUnits):
    menu_option='9'
class Agents(Units):
    menu_option='7'
class Headquarters(Units):
    menu_option='5'

class ManufacturedArmy(object):
    troopers=Troopers()
    turrets=Turrets()
    jets=Jets()
    tanks=Tanks()
    bombers=Bombers()
    carriers=Carriers()

class Army(ManufacturedArmy):
    agents=Agents()
    headquarters=Headquarters()
    maintenance = None
    food = None
    sdi = None
    
    

class Region(object):
    number=None

class Industrial(Region):
    zonemanufacturing=ManufacturedArmy()

class Agricultural(Region):
    foodyield=None

class Earner(Region):
    earnings=None
    
class Urban(Region):
    pass

class Technology(Region):
    pass

class River(Agricultural,Earner):
    pass

class Regions(object):
    coastal=Earner()
    river=River()
    agricultural=Agricultural()
    desert=Earner()
    industrial=Industrial()
    urban=Urban()
    mountain=Earner()
    technology=Technology()

    number_affordable=None
    price=None
    number=None
    maintenance=None

    menu_option='6'

    
class Population(object):
    taxearnings=None
    growth=None
    food = None
    pop_support_bribe = None
    pop_support = None
    rate = None
    

class Bank(object):
    gold=None

class Turns(object):
    remaining=None
    current=None
    years_protection = None
    years_freedom = None

class Food(object):
    spoilage=None
    units=None
    randomly_eaten=None

class Setup(object):
    game_start_date=None
    turns_per_day=None
    protection_turns = None
    daily_land_creation=None
    planetary_tax_rate=None
    max_players=None
    interest_rate=None
    maint_costs=None
    region_cost=None
    trade_cost=None
    attack_damage=None
    attack_rewards=None
    army_purchase=None
    local_game=None
    interbbs_game=None
    num_boards=None
    attack_cost=None
    terror_cost=None
    num_indie_attacks=None
    num_group_attacks=None
    num_tops=None
    num_bops=None
    days_for_mit=None
    gooies=None
    bombing_ops=None
    missle_ops=None

class Realm(object):
    regions=Regions()
    population=Population()
    army=Army()
    name=None
    gold=None
    bank=Bank()
    turns=Turns()
    food=Food()
    queen_taxes=None
    score=None

def _indent(d):
    s='\n'
    for i in range(d):
        if i == len(range(d)) -1:
            s+='  +- '
        else:
            s+='  |  '
    return s
        
def enumerate_attribs(obj):
    for attr in dir(obj):
        if not callable(getattr(obj,attr)) and not attr.startswith("__"):
            yield attr,getattr(obj,attr)

def _printvisitor(o,d):
    indent=_indent(d)
    t = ''

    for n,v in enumerate_attribs(o):

        if v is None:
            continue

        if isinstance(v, basestring) or isinstance(v, int) or isinstance(v, float) or isinstance(v,bool):
            t += indent + n + ": " + str(v)
        else:
            t += indent + n + ":" + _printvisitor(v,d+1)
    return t

class Data(dict):

    realm=Realm()
    setup=None


    def __str__(self):
        return _printvisitor(self.realm,0)


    def set(self, key, value):
        botlog.debug("recording " + str(key) + " = " + str(value))
        self[key] = value

    def get_maint_cost(self):
        c = 0
        realm = self.realm
        if realm.army.maintenance is not None: c = c + realm.army.maintenance
        if realm.regions.maintenance is not None: c = c + realm.regions.maintenance
        if realm.queen_taxes is not None: c = c + realm.queen_taxes
        if realm.population.pop_support_bribe is not None: c = c + realm.population.pop_support_bribe
        # TODO Morale cost

        return c

    def oop(self):
        return realm.turns.years_freedom is not None
 



