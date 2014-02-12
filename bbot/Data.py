#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import botlog
import math

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

class Units(object):
    def __init__(self):
        self.number=None
        self.price=None
        self.sellprice=None
class ArmyUnits(Units):
    def __init__(self):
        Units.__init__(self)
        self.allocation=None
        self.production=None
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
    def __init__(self):
        self.troopers=Troopers()
        self.turrets=Turrets()
        self.jets=Jets()
        self.tanks=Tanks()
        self.bombers=Bombers()
        self.carriers=Carriers()

class Army(ManufacturedArmy):
    def __init__(self):
        ManufacturedArmy.__init__(self)
        self.agents=Agents()
        self.headquarters=Headquarters()
        self.maintenance = None
        self.food = None
        self.sdi = None
    
    

class Region(object):
    def __init__(self):
        self.number=None

class Industrial(Region):
    menu_option='i'
    def __init__(self):
        Region.__init__(self)
        self.zonemanufacturing=ManufacturedArmy()

class Agricultural(Region):
    menu_option='a'
    def __init__(self):
        Region.__init__(self)
        self.foodyield=None

class Earner(Region):
    def __init__(self):
        Region.__init__(self)
        self.earnings=None

class Desert(Earner):
    menu_option='d'
    
class Coastal(Earner):
    menu_option='c'

class Mountain(Earner):
    menu_option='m'

class Urban(Region):
    menu_option='u'

class Technology(Region):
    menu_option='t'

class River(Agricultural,Earner):
    menu_option='r'

class Regions(object):
    menu_option='6'
    def __init__(self):
        self.coastal=Earner()
        self.river=River()
        self.agricultural=Agricultural()
        self.desert=Earner()
        self.industrial=Industrial()
        self.urban=Urban()
        self.mountain=Earner()
        self.technology=Technology()

        self.number_affordable=None
        self.price=None
        self.number=None
        self.maintenance=None

    def __str__(self):
        return _printvisitor(self,0)

    def normalize(self):
        length = 0
        if self.coastal.number is not None: 
            length = length + self.coastal.number 
        if self.river.number is not None: 
            length = length + self.river.number 
        if self.agricultural.number is not None: 
            length = length + self.agricultural.number
        if self.desert.number is not None: 
            length = length + self.desert.number
        if self.industrial.number is not None: 
            length = length + self.industrial.number
        if self.urban.number is not None: 
            length = length + self.urban.number
        if self.mountain.number is not None: 
            length = length + self.mountain.number
        if self.technology.number is not None: 
            length = length + self.technology.number

        self.multiply(1.0/length)

    def multiply(self,length):
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

    def ratio_to_buy(self, length):

        self.normalize()

        t = 0
        m = None
        ma = -1
        if self.coastal.number is not None: 
            self.coastal.number = int(self.coastal.number * length)
            if self.coastal.number > ma:
                ma = self.coastal.number
                m = self.coastal
            t = t + self.coastal.number
        if self.river.number is not None: 
            self.river.number = int(self.river.number * length)
            if self.river.number > ma:
                ma = self.river.number
                m = self.river
            t = t + self.river.number
        if self.agricultural.number is not None: 
            self.agricultural.number = int(self.agricultural.number * length)
            if self.agricultural.number > ma:
                ma = self.agricultural.number
                m = self.agricultural
            t = t + self.agricultural.number
        if self.desert.number is not None: 
            self.desert.number = int(self.desert.number * length)
            if self.desert.number > ma:
                ma = self.desert.number
                m = self.desert
            t = t + self.desert.number
        if self.industrial.number is not None: 
            self.industrial.number = int(self.industrial.number * length)
            if self.industrial.number > ma:
                ma = self.industrial.number
                m = self.industrial
            t = t + self.industrial.number
        if self.urban.number is not None: 
            self.urban.number = int(self.urban.number * length)
            if self.urban.number > ma:
                ma = self.industrial.number
                m = self.industrial
            t = t + self.urban.number
        if self.mountain.number is not None: 
            self.mountain.number = int(self.mountain.number * length)
            if self.mountain.number > ma:
                ma = self.mountain.number
                m = self.mountain
            t = t + self.mountain.number
        if self.technology.number is not None: 
            self.technology.number = int(self.technology.number * length)
            if self.technology.number > ma:
                ma = self.technology.number
                m = self.technology
            t = t + self.technology.number
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
        self.taxearnings=None
        self.growth=None
        self.food = None
        self.pop_support_bribe = None
        self.pop_support = None
        self.rate = None
    

class Bank(object):
    def __init__(self):
        self.gold=None

class Turns(object):
    def __init__(self):
        self.remaining=None
        self.current=None
        self.years_protection = None
        self.years_freedom = None

class Food(object):
    def __init__(self):
        self.spoilage=None
        self.units=None
        self.randomly_eaten=None

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

class Advisor(object):
    pass

class CivilianAdvisor(Advisor):
    menu_option='1'
    def __init__(self):
        Advisor.__init__(self)
        self.river_food_production=None
        self.food_consumption=None
        self.food_surplus=None
        self.food_deficit=None
        self.years_survival=None
class EconomicAdvisor(Advisor):
    menu_option='2'
    def __init__(self):
        Advisor.__init__(self)
        self.income=None
        self.world_income_ratio=None
        self.efficiency=None
        self.global_avg_efficiency=None
class MilitaryAdvisor(Advisor):
    menu_option='3'
    def __init__(self):
        Advisor.__init__(self)
class TechnologyAdvisor(Advisor):
    menu_option='4'
    def __init__(self):
        Advisor.__init__(self)
        self.mil_tech=None
        self.gold_tech=None
        self.food_tech=None
        self.industry_tech=None
        self.maint_tech=None
        self.sdi_tech=None
        self.food_decay_tech=None
class Advisors(object):
    def __init__(self):
        self.civilian=CivilianAdvisor()
        self.economic=EconomicAdvisor()
        self.military=MilitaryAdvisor()
        self.technology=TechnologyAdvisor()
    def get_advisor(self, menu_option):
        if CivilianAdvisor.menu_option == str(menu_option): return self.civilian
        elif EconomicAdvisor.menu_option == str(menu_option): return self.economic
        elif MilitaryAdvisor.menu_option == str(menu_option): return self.military
        elif TechnologyAdvisor.menu_option == str(menu_option): return self.technology
        else: raise Exception("Unkown menu options for advisor")
    def reset_advisor(self, menu_option):
        if CivilianAdvisor.menu_option == str(menu_option): self.civilian = CivilianAdvisor()
        elif EconomicAdvisor.menu_option == str(menu_option): self.economic = EconomicAdvisor()
        elif MilitaryAdvisor.menu_option == str(menu_option): self.military = MilitaryAdvisor()
        elif TechnologyAdvisor.menu_option == str(menu_option): self.technology = TechnologyAdvisor()
        else: raise Exception("Unkown menu options for advisor")
    

class Realm(object):
    def __init__(self):
        self.regions=Regions()
        self.population=Population()
        self.army=Army()
        self.name=None
        self.gold=None
        self.bank=Bank()
        self.turns=Turns()
        self.food=Food()
        self.queen_taxes=None
        self.score=None
        self.advisors=Advisors()


class Data(dict):

    realm=Realm()
    setup=None
    statstext=''
    spendtext=''
    msgtext=''
    planettext=''


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

    def is_oop(self):
        return self.realm.turns.years_freedom is None

    def has_full_investments(self):
        return True

    def get_number(self, item):
        army = self.realm.army
        item = str(item)
        if item == Troopers.menu_option: return army.troopers.number
        if item == Turrets.menu_option: return army.turrets.number
        if item == Jets.menu_option: return army.jets.number
        if item == Tanks.menu_option: return army.tanks.number
        if item == Bombers.menu_option: return army.bombers.number
        if item == Carriers.menu_option: return army.carriers.number
        raise Exception("I don't know about option " + str(item))
        
        
 



