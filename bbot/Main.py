#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Strategy import Strategy

"""
[Barren Realms Elite]
(1) Play Game             (7) Send Messages         
(2) See Status            (8) Game Bulletins        
(3) See Scores            (A) Game Instructions     
(4) See Today's News      (B) Help Database         
(5) See Yesterday's News  (P) Preferences           
(6) Read Messages         (0) Quit                  

Choice> Play Game
"""

class Main(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
            '\[Barren Realms Elite\]' : 10,
            '\(1\) Play Game             \(7\) Send Messages' : 20,
            '\(6\) Read Messages         \(0\) Quit' : 30,
            }


    def on_indicator(self, lastState, state):
            
        if state == 10:
            pass # read the menu header
        elif lastState == 10 and state == 20:
            pass 
        elif lastState == 20 and state == 30:
            # press enter to do the default prompt
            self.app.sendl() 


        else:
            return Strategy.UNHANDLED


