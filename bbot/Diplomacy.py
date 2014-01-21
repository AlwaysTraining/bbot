#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import os
from bbot.Strategy import Strategy

"""
[Diplomacy Menu]
(1) Tariff Trade Agreement  
(2) Protective Trade        
(3) Free Trade Agreement    
(4) Terrorist Prevention    
(5) Intelligence Alliance   
(6) Technology Agreement    
(7) Full Defense Alliance   
(8) Declaration Of War      
(9) View Treaties           
(?) Help                    
(0) Quit                    

Choice> View Treaties


-*Relations*-

Id   Empire Name                             Relations

[A]  FesNick                                 Technology Agreement
[C]  Death Star                              Technology Agreement
[D]  halz                                    Technology Agreement
[E]  Supreme Leader                          Technology Agreement
[F]  Wraith Runner                           Technology Agreement

[Diplomacy Menu]
(1) Tariff Trade Agreement  
(2) Protective Trade        
(3) Free Trade Agreement    
(4) Terrorist Prevention    
(5) Intelligence Alliance   
(6) Technology Agreement    
(7) Full Defense Alliance   
(8) Declaration Of War      
(9) View Treaties           
(?) Help                    
(0) Quit                    

Choice> Technology Agreement

(A-Y,Z=All,?=List) Send to: ACDEF
Would you like to attach a message? (y/N) No
Technology Agreement proposed to FesNick
Technology Agreement proposed to Death Star
Technology Agreement proposed to halz
Technology Agreement proposed to Supreme Leader
Technology Agreement proposed to Wraith Runner

[Diplomacy Menu]
(1) Tariff Trade Agreement  
(2) Protective Trade        
(3) Free Trade Agreement    
(4) Terrorist Prevention    
(5) Intelligence Alliance   
(6) Technology Agreement    
(7) Full Defense Alliance   
(8) Declaration Of War      
(9) View Treaties           
(?) Help                    
(0) Quit                    

Choice> Quit
"""

class Diplomacy(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
'\[Diplomacy Menu\]' : 10,
'Choice>' : 20,
'\-\*Relations\*\-' : 30,
'\[([A-Z])\]  (.*)' : 40
}


    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass
        elif lastState == 10 and state == 20:
            # at the diplomacy menu view treatys
            self.app.send(9)
        elif lastState == 20 and state == 30:
            pass
        elif (lastState == 30 or lastState == 40) and state == 40:
            print "read !!@!!@!!!", self.app.telnet.match.group(0), self.app.telnet.match.group(1)





        else:
            return Strategy.UNHANDLED


