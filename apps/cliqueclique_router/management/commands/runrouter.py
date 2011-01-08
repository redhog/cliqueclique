# -*- coding: utf-8 -*-

import cliqueclique_router.server

import datetime
import codecs
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import django.core.servers.basehttp
import django.core.handlers.wsgi
import django.utils.translation
import cliqueclique_node.models
import cliqueclique_document.models
import cliqueclique_subscription.models
import i2p.socket
import socket
import threading
import time
import django.core.management.commands.runserver
import settings
import utils.i2p
import utils.smime
import utils.thread
import os
import sys
import threading

class Command(django.core.management.commands.runserver.Command):
    args = ''

    option_list = django.core.management.commands.runserver.Command.option_list


    # BaseCommand.option_list + (
    #     make_option('--dry-run',
    #                 action='store_true',
    #                 default=False,
    #                 dest='dry-run',
    #                 help='Run without changing the database'),
    #     )

    help = 'Run the message router'

    def handle(self, *args, **options):
        print 'Connecting to i2p router...'

        django.utils.translation.activate(settings.LANGUAGE_CODE)

        if settings.CLIQUECLIQUE_LOCALHOST:
            local_address = settings.CLIQUECLIQUE_I2P_SESSION_NAME
            sock = cliqueclique_router.server.LocalSocket(local_address)
        else:
            sock = i2p.socket.socket(settings.CLIQUECLIQUE_I2P_SESSION_NAME, i2p.socket.SOCK_DGRAM)
            local_address = utils.i2p.dest2b32(sock.dest)
        print 'Serving at: %s.' % (local_address,)

        for local in cliqueclique_node.models.LocalNode.objects.all():
            if local.address != local_address:
                local.address = local_address
                local.save()

        sender = cliqueclique_router.server.Sender(sock)
        sender.start()
        receiver = cliqueclique_router.server.Receiver(sock)
        receiver.start()

        webservers = []
        for addr in settings.CLIQUECLIQUE_UI_SECURITY_CONTEXTS:
            webserver = cliqueclique_router.server.Webserver(*addr.split(":"))
            webserver.start()
            webservers.append(webserver)

        try:
            while True:
                time.sleep(500)
        except:
            sender.exit()
            receiver.exit()
            for webserver in webservers:
                webserver.exit()

            
