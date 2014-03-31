#!/bin/bash


# BRE Bot Command Line Interface
#
# positional arguments:
#  strategies S1 S2 ...  list of actions to perform
#    AntiPirate          Attack random pirate every turn
#    IndMtn              But primarily industry and mountain regions, sell
#                        army in the beginning of the game to fund regions
#    LocalLackey         Send trade deals once a day to the master realm        
#    Investor            Invest money if bank is full
# optional arguments:
#  -h, --help            show this help message and exit
#  -u USERNAME, --username USERNAME
#                        Your BBS username.
#  -p PASSWORD, --password PASSWORD
#                        Your BBS password.
#  -a ADDRESS, --address ADDRESS
#                        BBS address
#  -r REALM, --realm REALM
#                        name of realm
#  -g GAME, --game GAME  menu number for the game
#  --smtp-server SMTP_SERVER
#                        Outgoing Mail Server address
#  --smtp-port SMTP_PORT
#                        Outgoing Mail Server port
#  --smtp-user SMTP_USER
#                        Outgoing Mail Server user name
#  --smtp-password SMTP_PASSWORD
#                        Outgoing Mail Server user password
#  -n NOTIFY, --notify NOTIFY
#                        comma seperated email addresses for recipients of
#                        notifications
#  --LocalLackey-master LOCALLACKEY_MASTER
#                        Name of the realm who a LocalLackey will send trade
#                        deals to
#  -d, --debug           enable debug mode
#
# bot sandbox:         http://botbox.strangled.net/bbot
# bot cron Log:         http://botbox.strangled.net/bbot/cron_log.txt
# source code:         https://github.com/AlwaysTraining/bbot
# ec2 console:         https://console.aws.amazon.com/ec2/v2/#Instances:


mailargs="
    --smtp-server   smtp.gmail.com \
    --smtp-port     587 \
    --smtp-user     dr.randy.myers \
    --smtp-password dr.randy.myers.password \
    --notify        derrick.karimi@gmail.com"


#######################
# prime time on shenks
#
  league 555 on shenks
  bbot-cli.py IndMtn Lackey \
         --username                        Randy32 \
         --password                        RANDYPAS \
         --address                        shenks.synchro.net \
         --realm                                Randyland \
         --game                                9 \
        --Lackey-master-planet 'trans canada' \
        --Lackey-master-realm 'Bonk' \
        --Lackey-trade-items 'Tanks,Gold' \
        --Lackey-tribute-ratio 0.25 \
        --debug \
         $mailargs
 
