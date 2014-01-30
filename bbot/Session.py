#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

from bbot.Strategy import Strategy
 

class Session(Strategy):

    def __init__(self, app):
        Strategy.__init__(self, app)

    def get_indicators(self):
        return {
                'Login:'    :   1,
                'Password'  :   2,
                '\[Hit a key\]'   :   3,
                'Enter number of bulletin to view or press \(ENTER\) to continue:'    :   3,
                'Search all groups for new messages'   :   4,
                'Search all groups for un-read messages to you' : 4,
                '.+fidonet.+AFTERSHOCK:'   :   5,                                       #Shenks Main Menu
                '. Main .* Xbit Local Echo \[[0-9]+\] InterBBS FE:'  :   6,             #XBIT Main Menu
                '\(S\)ub\-board, \(G\)roup, or \(A\)ll:' :   7,  
                'Select External Program Section:'    :   8,
                'Games External Programs:'  :   9,
                'Connection closed by foreign host\.'  :   100000,
                '\[\+\] Read your mail now\? \[Yes\] No'    :   10,
                '\* Main \* [0-9:]+ \[[0-9]+\] Main \[[0-9]+\] Notices:'    :   11,     #TNSOA Main Menu
                }

    played=False 

    def on_indicator(self, lastState, state):
        if state == 1:

            self.app.sendl(self.app.get_app_value('username'))

        elif state == 2:

            self.app.sendl(self.app.get_app_value('password',secret=True))

        elif state == 3:

            self.app.sendl()
        elif state == 4 or state == 10:

            self.app.send('n',sleep=3)
                
        elif state == 5 or state == 11:

            # shenk's 

            if not self.played:
                # get to the bre menu
                self.app.send('X',sleep=3) # external menu
            else:
                # bre is done, log out
                self.app.send('o',sleep=3)
                self.app.sendl('y',sleep=3)

        elif state == 7:
            
            # for some infernal reason on shenk's bbs, when trying to access
            # the game menu's it doesn't take, ant it ens up in the stupid 
            # messages menu, press enter to get out of it
            self.app.sendl()

        elif state == 8:

            if not self.played:
                self.app.send('2',sleep=3) # games
            else:
                self.app.send('q',sleep=3)

        elif state == 9:

            if not self.played:
                self.app.send(self.app.get_app_value('game'),sleep=3)
                self.played = True
            else:
                self.app.send('q',sleep=3)

        elif state == 6:

            self.app.send('x',sleep=3) # external menu
            self.app.send('4',sleep=3) # games
            self.app.send(self.app.get_app_value('game'),sleep=3)
            self.played = True

        elif state == 100000:
            return Strategy.TERMINATE

        else:
            return Strategy.UNHANDLED
