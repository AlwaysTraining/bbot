
import pexpect
import sys

import time

import os



switch_ip_address = "shenks.synchro.net"


print 'ip address is: ', switch_ip_address

telnet_child = pexpect.spawn('telnet ' + switch_ip_address)
telnet_child.logfile = sys.stdout
telnet_child.expect('Login: ')
telnet_child.sendline('Randy32')
telnet_child.expect('Password: ')
telnet_child.sendline('RANDYPAS')
