
import pexpect
import sys

import time

import os



switch_ip_address = "shenks.synchro.net"


print 'ip address is: ', switch_ip_address

t = pexpect.spawn('telnet ' + switch_ip_address,logfile=sys.stdout)
t.delaybeforesend=1
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



t.expect('zzzzzzsads232e1fd2312')
