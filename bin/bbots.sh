#!/bin/bash


# BRE Bot Command Line Interface
#
#       positional arguments:
#         strategies            list of actions to perform
#
#       optional arguments:
#         -h, --help            show this help message and exit
#         -u USERNAME, --username USERNAME
#                               Your BBS username.
#         -p PASSWORD, --password PASSWORD
#                               Your BBS password.
#         -a ADDRESS, --address ADDRESS
#                               BBS address
#         -r REALM, --realm REALM
#                               name of realm
#         -g GAME, --game GAME  menu number for the game
#         --smtp-server SMTP_SERVER
#                               Outgoing Mail Server address
#         --smtp-port SMTP_PORT
#                               Outgoing Mail Server port
#         --smtp-user SMTP_USER
#                               Outgoing Mail Server user name
#         --smtp-password SMTP_PASSWORD
#                               Outgoing Mail Server user password
#         -n [NOTIFY], --notify [NOTIFY]
#                               email addresses for recipiants of
#                                                notifications
#         -d, --debug           enable debug mode




bbot-cli.py IndMtn \
        --username                Randy32 \
        --password                RANDYPAS \
        --address                tnsoa.strangled.net \
        --realm                Randyland \
        --game                6 \
        --smtp-server        smtp.gmail.com \
        --smtp-port        587 \
        --smtp-user        dr.randy.myers \
        --smtp-password        dr.randy.myers.password \
        --notify                derrick.karimi@gmail.com