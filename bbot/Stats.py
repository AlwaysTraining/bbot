#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

"""



14,374,607 gold was earned in taxes.
15,731,467 gold was produced from the Ore Mines.
4198 gold was earned in Tourism.
4777 gold was earned by Solar Power Generators.
5548 gold was created by Hydropower.
290,400 Food units were grown.

963,273 Jets were manufactured by Industrial Zones.
9981 Carriers were manufactured by Industrial Zones.
100,000,000 gold was earned from investment returns.


-=<Paused>=-




-*Skull House*-
Turns: 20
Score: 11,466,305
Gold: 172,033,271
Bank: 2,000,000,000
Population: 177,183 Million (Tax Rate: 30%)
Popular Support: 100%
Food: 790,325
Agents: 20,319
Headquarters: 100% Complete
Military: [49,510 Troopers] [81,041,840 Jets] [48 Turrets] 
          [4,248,488 Tanks] [14,574 Bombers] [1,034,704 Carriers] 
          [100% Morale]
SDI Strength: 4%
Regions:  [1 Rivers] [800 Agricultural] [1 Desert] [46,731 Industrial] 
          [3900 Mountains] [1 Coastal] [3900 Technology] 
This is year 887 of your freedom.

-*shenks.synchro.net*-
Turns: 12
Score: 213
Gold: 1,056,294
Population: 100 Million (Tax Rate: 15%)
Popular Support: 100%
Food: 1600
Military: [100 Troopers] 
          [100% Morale]
Regions:  [1 Rivers] [800 Agricultural] [1 Desert] [46,731 Industrial] 
          [3900 Mountains] [1 Coastal] [3900 Technology]
You have 100 Years of Protection Left.





There are 516,494 Regions available.
Note: Region prices are constantly changing.  Therefore, the region price
      shown is only the price for the first piece of territory you buy.
You can afford 500 regions.


Key Name            Owned

(C) Coastal             0
(R) River               0
(A) Agricultural      300
(D) Desert              1
(I) Industrial      17289
(U) Urban               0
(M) Mountain         2157
(T) Technology       2157

[Advisors]
(1) Civilian    
(2) Economic    
(3) Military    
(4) Technology  
(0) Quit        


[Spending Menu]
Key Item                 Price       # Owned
(*) System Menu                             
(1) Troopers              271           100 
(2) Jets                  330             0 
(3) Turrets               383             0 
(4) Bombers              3138             0 
(5) HeadQuarters         5277             0 
(6) Regions              1412            15 
(7) Covert Agents         725             0 
(8) Tanks                1735             0 
(9) Carriers             5269             0 
(S) Sell                                    
(V) Visit Bank                              
(?) Help                                    
(0) Quit                                    

You have 49,325 gold and 10 turns.
Choice> 
        
"""
import os
from bbot.Utils import *
from bbot.Strategy import Strategy


class Stats(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)


    def get_priority(self,state):
        return VERYHIGH_PRIORITY
    
    def get_indicators(self):
        return {
            "You can afford "+NUM_REGEX+' regions\.':   50,
            "Key Name            Owned"             :   60,
            "\(C\) Coastal[ \t]+"+NUM_REGEX         :   70,
            "\(R\) River[ \t]+"+NUM_REGEX           :   80,
            "\(A\) Agricultural[ \t]+"+NUM_REGEX    :   90,
            "\(D\) Desert[ \t]+"+NUM_REGEX          :   100,
            "\(I\) Industrial[ \t]+"+NUM_REGEX      :   110,
            "\(U\) Urban[ \t]+"+NUM_REGEX           :   120,
            "\(M\) Mountain[ \t]+"+NUM_REGEX        :   130,
            "\(T\) Technology[ \t]+"+NUM_REGEX      :   140,




            NUM_REGEX+' gold was earned in taxes.'  :   500,
            NUM_REGEX+' gold was produced from the Ore Mines.'  :   510,
            NUM_REGEX+' gold was earned in Tourism.'    :   520,
            NUM_REGEX+' gold was earned by Solar Power Generators.' :   530,
            NUM_REGEX+' gold was created by Hydropower.'    :   540,
            NUM_REGEX+' Food units were grown.' :   550,

            NUM_REGEX+' Troopers were manufactured by Industrial Zones.'    :   560,
            NUM_REGEX+' Turrets were manufactured by Industrial Zones.' :   570,
            NUM_REGEX+' Jets were manufactured by Industrial Zones.'    :   580,
            NUM_REGEX+' Carriers were manufactured by Industrial Zones.'    :   590,
            NUM_REGEX+' Bombers were manufactured by Industrial Zones.' :   600,
            NUM_REGEX+' Tanks were manufactured by Industrial Zones.'   :   610,
            NUM_REGEX+' gold was earned from investment returns.'   :   620,
            

            "\-\*(^[\*]+)\*\-"  :   200,
            "Turns: "+NUM_REGEX :   210,
            "Score: "+NUM_REGEX :   220,
            "Gold: "+NUM_REGEX  :   230,
            "Bank: "+NUM_REGEX  :   240,
            "Population: "+NUM_REGEX+" Million \(Tax Rate: "+NUM_REGEX+"\%" :   250,
            "Popular Support: "+NUM_REGEX+"\%"  :   260,
            "Food: "+NUM_REGEX  :   270,
            "Agents: "+NUM_REGEX    :   280,
            "Headquarters: "+NUM_REGEX+"\% Complete"    :   290,
            "SDI Strength: "+NUM_REGEX+"\%" :   300,
            "This is year "+NUM_REGEX+" of your freedom."   :   310,
            "You have "+NUM_REGEX+" Years of Protection Left."  :   320,



            "\[Spending Menu\]"   : 800,
            "\(1\) Troopers"+SPACE_REGEX+NUM_REGEX+SPACE_REGEX+NUM_REGEX  : 810,
            "\(2\) Jets"+SPACE_REGEX+NUM_REGEX+SPACE_REGEX+NUM_REGEX  : 820,
            "\(3\) Turret"+SPACE_REGEX+NUM_REGEX+SPACE_REGEX+NUM_REGEX  : 830,
            "\(4\) Bombers"+SPACE_REGEX+NUM_REGEX+SPACE_REGEX+NUM_REGEX  : 840,
            "\(5\) HeadQuarters"+SPACE_REGEX+NUM_REGEX+SPACE_REGEX+NUM_REGEX  : 850,
            "\(6\) Regions"+SPACE_REGEX+NUM_REGEX+SPACE_REGEX+NUM_REGEX  : 860,
            "\(7\) Covert Agents"+SPACE_REGEX+NUM_REGEX+SPACE_REGEX+NUM_REGEX  : 870,
            "\(8\) Tanks"+SPACE_REGEX+NUM_REGEX+SPACE_REGEX+NUM_REGEX  : 880,
            "\(9\) Carriers"+SPACE_REGEX+NUM_REGEX+SPACE_REGEX+NUM_REGEX  : 890,
            "You have "+NUM_REGEX+" gold and "+NUM_REGEX+" turns\." : 900,


            "\[Industrial Production\]" :   1300,
            "Troopers        : "+NUM_REGEX+"\%[ \t]+\("+NUM_REGEX+" per year\)" :   1310,
            "Jets            : "+NUM_REGEX+"\%[ \t]+\("+NUM_REGEX+" per year\)" :   1320,
            "Turrets         : "+NUM_REGEX+"\%[ \t]+\("+NUM_REGEX+" per year\)" :   1330,
            "Bombers         : "+NUM_REGEX+"\%[ \t]+\("+NUM_REGEX+" per year\)" :   1340,
            "Tanks           : "+NUM_REGEX+"\%[ \t]+\("+NUM_REGEX+" per year\)" :   1350,
            "Carriers        : "+NUM_REGEX+"\%[ \t]+\("+NUM_REGEX+" per year\)" :   1360,

}


    def on_indicator(self, lastState, state):

        realm = self.app.data.realm
        regions = realm.regions
        manufacture = regions.industrial.zonemanufacturing
        army = realm.army

        if state == 10:
            self.app.data.set("Turn Tax Revenue", self.app.get_num(0))

        elif lastState != None and lastState < 200 and state == 200:
            realm.name=app.get_str()
            
        elif state == 50: regions.number_affordable = self.app.get_num()
        elif state == 60: pass
        elif lastState == 60 and state == 70: regions.coastal.number = self.app.get_num()
        elif lastState == 70 and state == 80: regions.river.number = self.app.get_num()
        elif lastState == 80 and state == 90: regions.agricultural.number = self.app.get_num()
        elif lastState == 100 and state == 100: regions.desert.number = self.app.get_num()
        elif lastState == 100 and state == 110: regions.industrial.number = self.app.get_num()
        elif lastState == 110 and state == 120: regions.urban.number = self.app.get_num()
        elif lastState == 120 and state == 130: regions.mountain.number = self.app.get_num()
        elif lastState == 130 and state == 140: regions.technology.number = self.app.get_num()
              
        elif state == 500: realm.population.taxearnings = self.app.get_num()
        elif state == 510: regions.mountain.earnings = self.app.get_num()
        elif state == 520: regions.coastal.earnings = self.app.get_num()
        elif state == 530: regions.desert.earnings = self.app.get_num()
        elif state == 540: regions.river.earnings = self.app.get_num()
        elif state == 550: regions.agricultural.foodyield = self.app.get_num()
        #TODO river producing food

        elif state == 560 : manufacture.troopers.number = self.app.get_num()
        elif state == 570 : manufacture.turrets.number = self.app.get_num()
        elif state == 580 : manufacture.jets.number = self.app.get_num()
        elif state == 590 : manufacture.carriers.number = self.app.get_num()
        elif state == 600 : manufacture.bomberstroopers.number = self.app.get_num()
        elif state == 610 : manufacture.tanks.number = self.app.get_num()

        elif state == 800 : pass
        elif state == 810 : 
            army.troopers.price = self.app.get_num(0)
            army.troopers.number = self.app.get_num(1)
        elif state == 820 : 
            army.jets.price = self.app.get_num(0)
            army.jets.number = self.app.get_num(1)
        elif state == 830 : 
            army.turrets.price = self.app.get_num(0)
            army.turrets.number = self.app.get_num(1)
        elif state == 840 : 
            army.bombers.price = self.app.get_num(0)
            army.bombers.number = self.app.get_num(1)
        elif state == 850 : 
            army.headquarters.price = self.app.get_num(0)
            army.headquarters.number = self.app.get_num(1)
        elif state == 860 : 
            regions.price = self.app.get_num(0)
            regions.number = self.app.get_num(1)
        elif state == 870 : 
            army.agents.price = self.app.get_num(0)
            army.agents.number = self.app.get_num(1)
        elif state == 880 : 
            army.tanks.price = self.app.get_num(0)
            army.tanks.number = self.app.get_num(1)
        elif state == 890 : 
            army.carriers.price = self.app.get_num(0)
            army.carriers.number = self.app.get_num(1)
        elif state == 900 :
            realm.gold = self.app.get_num(0)
            realm.bank.gold = self.app.get_num(1)
            realm.turns.remaining = self.app.get_num(1)
        elif state == 1300:
            pass
        elif state == 1310 : 
            manufacture.troopers.industrialallocation = self.app.get_num(0)
            manufacture.troopers.number = self.app.get_num(1)
        elif state == 1320 : 
            manufacture.jets.industrialallocation = self.app.get_num(0)
            manufacture.jets.number = self.app.get_num(1)
        elif state == 1330 : 
            manufacture.turrets.industrialallocation = self.app.get_num(0)
            manufacture.turrets.number = self.app.get_num(1)
        elif state == 1340 : 
            manufacture.bomberstroopers.industrialallocation = self.app.get_num(0)
            manufacture.bomberstroopers.number = self.app.get_num(1)
        elif state == 1350 : 
            manufacture.tanks.industrialallocation = self.app.get_num(0)
            manufacture.tanks.number = self.app.get_num(1)
        elif state == 1360 : 
            manufacture.carriers.industrialallocation = self.app.get_num(0)
            manufacture.carriers.number = self.app.get_num(1)


        else:
            return Strategy.UNHANDLED


