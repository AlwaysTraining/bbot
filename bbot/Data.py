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
    pass
class Troopers(ArmyUnits):
    pass
class Turrets(ArmyUnits):
    pass
class Jets(ArmyUnits):
    pass
class Tanks(ArmyUnits):
    pass
class Bombers(ArmyUnits):
    pass
class Carriers(ArmyUnits):
    pass
class Agents(Units):
    pass
class Headquarters(Units):
    pass

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
    years_protection = None
    years_freedom = None
    
    

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

class Food(object):
    spoilage=None
    units=None

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
 



