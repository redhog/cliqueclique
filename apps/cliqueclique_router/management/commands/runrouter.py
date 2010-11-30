# -*- coding: utf-8 -*-

import datetime
import codecs
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import cliqueclique_node.models
import cliqueclique_document.models
import cliqueclique_subscription.models
import i2p.socket
import threading
import time

class Command(BaseCommand):
    args = ''

    # option_list = BaseCommand.option_list + (
    #     make_option('--dry-run',
    #                 action='store_true',
    #                 default=False,
    #                 dest='dry-run',
    #                 help='Run without changing the database'),
    #     )

    help = 'Run the message router'

    def handle(self, *args, **options):

        sock = i2p.socket.socket('cliqueclique', i2p.socket.SOCK_DGRAM)
        print 'Serving at: %s.' % (sock.dest,)

        for local in cliqueclique_node.models.LocalNode.objects.all():
            if local.address != sock.dest:
                local.address = sock.dest
                local.save()

        class Receiver(threading.Thread):
            def run(self):
                print "Receiver is running."
                while True:
                    (msg, address) = sock.recvfrom(-1)
                    print "========{From %s}========" % (address,)
                    print msg
                    cliqueclique_node.models.LocalNode.receive_any(msg)

        class Sender(threading.Thread):
            def run(self):
                print "Sender is running."
                while True:
                    for (msg, address) in cliqueclique_node.models.LocalNode.send_any():
                        print "========{To %s}========" % (address,)
                        print msg
                        S.sendto(msg, 0, address)
                        time.sleep(1)
                    time.sleep(1)

        sender = Sender()
        sender.start()
        receiver = Receiver()
        receiver.start()

        sender.join()
