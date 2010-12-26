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
import utils.hash
import os
import sys

def msg2debug(msg):
    msg = utils.smime.message_from_anything(msg)
    cert = msg.verify()[0]
    container_msg = msg.get_payload()[0]

    sender_node_id = cliqueclique_node.models.Node.node_id_from_public_key(cert)
    receiver_node_id = container_msg['receiver_node_id']

    print "%s <- %s" % (receiver_node_id[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH], sender_node_id[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH])
    for part in container_msg.get_payload():
        print "  %s(%s)" % (part['message_type'], part['document_id'][:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH])
        for key, value in part.items():
            if key.lower() not in ('content-type', 'mime-version', 'message_type', 'document_id'):
                print "    %s = %s" % (key, value)


class Thread(threading.Thread):
    def __init__(self, **kw):
        threading.Thread. __init__(self)
        self.daemon = True
        for key, value in kw.iteritems():
            setattr(self, key, value)

class Webserver(Thread):
    local = threading.local()

    admin_media_path = ''
    port = 8000
    addr = '127.0.0.1'

    def __init__(self, addr, port, *arg, **kw):
        Thread.__init__(self, addr=addr, port=port, *arg, **kw)

    def run(self):
        print "Webserver is running at http://%s:%s/" % (self.addr, self.port)

        try:
            handler = django.core.servers.basehttp.AdminMediaHandler(django.core.handlers.wsgi.WSGIHandler(), self.admin_media_path)
            django.core.servers.basehttp.run(self.addr, int(self.port), handler)
        except django.core.servers.basehttp.WSGIServerException, e:
            # Use helpful error messages instead of ugly tracebacks.
            ERRORS = {
                13: "You don't have permission to access port %s." % self.port,
                98: "The port %s is already in use." % self.port,
                99: "The IP address %s can't be assigned-to." % self.addr,
            }
            try:
                error_text = ERRORS[e.args[0].args[0]]
            except (AttributeError, KeyError):
                error_text = str(e)
            sys.stderr.write(self.style.ERROR("Error: %s" % error_text) + '\n')
            # Need to use an OS exit because sys.exit doesn't work in a thread
            os._exit(1)

class Receiver(Thread):
    def __init__(self, sock, *arg, **kw):
        Thread.__init__(self, sock=sock, *arg, **kw)

    def run(self):
        print "Receiver is running."
        while True:
            if settings.CLIQUECLIQUE_LOCALHOST:
                (msg, address) = self.sock.recvfrom(10000)
            else:
                (msg, address) = self.sock.recvfrom(-1)

            print "========{From %s}========" % (utils.i2p.dest2b32(address),)
            msg2debug(msg)
            cliqueclique_node.models.LocalNode.receive_any(msg)

class Sender(Thread):
    def __init__(self, sock, *arg, **kw):
        Thread.__init__(self, sock = sock, *arg, **kw)

    def run(self):
        print "Sender is running."
        while True:
            for (msg, address) in cliqueclique_node.models.LocalNode.send_any():
                print "========{To %s}========" % (address,)
                # msg2debug(msg)

                self.sock.sendto(msg, 0, address)
                time.sleep(1)
            time.sleep(1)
