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
                'Hit a key'   :   3,
                'Enter number of bulletin to view or press'    :   3,
                'Search all groups for new messages'   :   4,
                'Search all groups for un-read messages to you' : 4,
                'AFTERSHOCK'   :   5
                }

    def on_indicator(self, lastState, state):
        if lastState is None and state == 1:

            self.app.sendl(self.app.get_app_value('username'))

        elif lastState == 1 and state == 2:

            self.app.sendl(self.app.get_app_value('password'))

        elif (lastState == 2 or lastState == 3) and state == 3:

            self.app.sendl('')

        elif (lastState == 3 or lastState == 4)  and state == 4:

            self.app.send('n')

# NOTE states 2 through 4 could be combined because there is no variability
# in the keypresses after password to login

        elif lastState == 4 and state == 5:

            self.app.send('x') # external menu
            self.app.send('2') # games
            self.app.send('10') # BRE Local Game

        else:
            return Strategy.UNHANDLED
