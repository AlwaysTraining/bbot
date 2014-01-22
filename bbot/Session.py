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
                '.+fidonet.+AFTERSHOCK:'   :   5,
                '. Main .* Xbit Local Echo \[[0-9]+\] InterBBS FE:'  :   6,
                'Sub\-board, Group, or All:' :   7,  
                }

    def on_indicator(self, lastState, state):
        if state == 1:

            self.app.sendl(self.app.get_app_value('username'))

        elif state == 2:

            self.app.sendl(self.app.get_app_value('password'))

        elif state == 3:

            self.app.sendl()
        elif state == 4:

            self.app.send('n')
                
        elif state == 5:

            # shenk's BBS

            if lastState != 5:
                # get to the bre menu
                self.app.send('x') # external menu
                self.app.send('2') # games
                self.app.send(self.app.get_app_value('game'))
        elif state == 7:
            # for some infernal reason on shenk's bbs, when trying to access
            # the game menu's it doesn't take, ant it ens up in the stupid 
            # messages menu, press enter to get out of it
            self.app.sendl()

        elif state == 6:

            self.app.send('x') # external menu
            self.app.send('4') # games
            self.app.send(self.app.get_app_value('game'))


        else:
            return Strategy.UNHANDLED
