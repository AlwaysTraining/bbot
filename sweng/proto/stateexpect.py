
import pexpect
import sys

import time

import os


switch_ip_address = "shenks.synchro.net"


print 'ip address is: ', switch_ip_address

t = pexpect.spawn('telnet ' + switch_ip_address,logfile=sys.stdout)
t.delaybeforesend=1
class state:
    def get_tokens(self):
        return []

    def parse_token(self,tok):
        return self

class seedo(state):
    def __init__(self, toks, response, nstate):
        self.toks = toks
        self.nstate = nstate
        self.response = response
    def get_tokens(self):
        return self.toks
    def parse_token(self,tok):
        t.sendline(self.response)
        return self.nstate

class pressenter(seedo):
    def __init__(self, nextstate):
        seedo.__init__(self,
                ['[Hit a key]','Enter number of bulletin to view or press (ENTER) to continue:'],
                '\r', 
                nextstate)

class pressn(seedo):
    def __init__(self, nextstate):
        seedo.__init__(self,
                ['Search all groups for new messages?','Search all groups for un-read messages to you'],
                'n', 
                nextstate)

class mmenu(state):
    def get_tokens(self):
        return ['...External programs','AFTERSHOCK:']
    def parse_token(self,tok):
        if tok == 0:
            print 'i^&^&matched to:', tok, t.after
            self.val = t.after[0]
            return self
        elif tok == 1:
            print 'i^&^&sending ' , self.val
            t.sendline(self.val+'\r')

        # get access to text here
        return None 

class password(state):
    def get_tokens(self):
        return ['Password: ']

    def parse_token(self,tok):
        t.sendline('RANDYPAS\r')
        return pressenter(pressenter(pressn(pressn(mmenu()))))

class username(state):
    def get_tokens(self):
        return ['Login: ']

    def parse_token(self, which):
        t.sendline('Randy32\r')
        return password()





def next_state(t, curstate):
    
    which_token = t.expect(curstate.get_tokens())
    return curstate.parse_token(which_token)

state = username()

while state is not None:
    state = next_state(t, state)

"""
t.expect('Login: ')
t.sendline('Randy32\r')
t.expect('Password: ')
t.sendline('RANDYPAS\r')
t.expect_exact('[Hit a key]')
t.sendline('\r')
t.expect_exact('Enter number of bulletin to view or press (ENTER) to continue:')
t.sendline('\r')
t.expect_exact('Search all groups for new messages?')
t.sendline('n')
t.expect_exact('Search all groups for un-read messages to you')
t.sendline('n')
t.expect('AFTERSHOCK:')
t.sendline('\/o')

"""

t.expect('zzzzzzsads232e1fd2312')
