#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import botlog

class Units(object):
    number=None
    price=None
class ArmyUnits(Units):
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
class Army(object):
    troopers=Troopers()
    turrets=Turrets()
    jets=Jets()
    tanks=Tanks()
    bombers=Bombers()
    carriers=Carriers()
    agents=Agents()
    headquarters=Headquarters()

class Region(object):
    number=None

class Industrial(Region):
    zonemanufacturing=Army()
    

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


    
class Population(object):
    taxearnings=None

class Bank(object):
    gold=None

class Turns(object):
    remaining=None

class Realm(object):
    regions=Regions()
    population=Population()
    army=Army()
    name=''
    gold=None
    bank=Bank()
    turns=Turns()

class Data(dict):

    realm=Realm()

    def _indent(d):
        s='\n'
        for i in range(d):
            s+='\t'
            
    def _printvisitor(o,d):
        indent=_indent(d)
        t = ''
        for n,v in o.__dict__.items():
            if v is None or isinstance(v, basestring) or isinstance(v, int) or isinstance(v, float) or isinstance(v,bool):
                t += indent + n + "\t:\t" + str(v)
            else:
                t += indent + n + "\t:\n" + _printvisitor(v,d+1)

                


        

    def __str__(self):
        return _printvisitor(self.realm)


    def set(self, key, value):
        botlog.debug("recording " + str(key) + " = " + str(value))
        self[key] = value



