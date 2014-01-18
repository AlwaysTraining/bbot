
import pexpect
import sys

import time

import os



switch_ip_address = "shenks.synchro.net"


print 'ip address is: ', switch_ip_address

telnet_child = pexpect.spawn('telnet ' + switch_ip_address,logfile=sys.stdout)
telnet_child.delaybeforesend=1
telnet_child.expect('Login: ')
telnet_child.sendline('Randy32\r')
telnet_child.expect('Password: ')
telnet_child.sendline('RANDYPAS\r')
telnet_child.expect_exact('[Hit a key]')
telnet_child.sendline('\r')
