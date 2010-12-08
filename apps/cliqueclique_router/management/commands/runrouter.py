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
import django.core.management.commands.runserver
import settings
import utils.i2p
import utils.smime

def msg2debug(msg):
    msg = utils.smime.message_from_anything(msg)
    cert = msg.verify()[0]
    container_msg = msg.get_payload()[0]

    sender_node_id = cliqueclique_node.models.Node.node_id_from_public_key(cert)
    receiver_node_id = container_msg['receiver_node_id']

    print "%s <- %s" % (receiver_node_id[:5], sender_node_id[:5])
    for part in container_msg.get_payload():
        print "  %s(%s)" % (part['message_type'], part['document_id'][:5])
        for key, value in part.items():
            if key.lower() not in ('content-type', 'mime-version', 'message_type', 'document_id'):
                print "    %s = %s" % (key, value)

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

        sock = i2p.socket.socket(settings.CLIQUECLIQUE_I2P_SESSION_NAME, i2p.socket.SOCK_DGRAM)
        local_address = utils.i2p.dest2b32(sock.dest)
        print 'Serving at: %s.' % (local_address,)

        for local in cliqueclique_node.models.LocalNode.objects.all():
            if local.address != local_address:
                local.address = local_address
                local.save()

        class Receiver(threading.Thread):
            def run(self):
                print "Receiver is running."
                while True:
                    (msg, address) = sock.recvfrom(-1)

                    print "========{From %s}========" % (utils.i2p.dest2b32(address),)
                    msg2debug(msg)
                    cliqueclique_node.models.LocalNode.receive_any(msg)

        class Sender(threading.Thread):
            def run(self):
                print "Sender is running."
                while True:
                    for (msg, address) in cliqueclique_node.models.LocalNode.send_any():
                        print "========{To %s}========" % (address,)
                        msg2debug(msg)

                        sock.sendto(msg, 0, address)
                        time.sleep(1)
                    time.sleep(1)

        sender = Sender()
        sender.daemon = True
        sender.start()
        receiver = Receiver()
        receiver.daemon = True
        receiver.start()

        print "Starting webserver..."
        import os
        os.environ["RUN_MAIN"] = "true"
        django.core.management.commands.runserver.Command.handle(self, *args, **options)
