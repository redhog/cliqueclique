# -*- coding: utf-8 -*-

import datetime
import codecs
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import cliqueclique_node.models
import cliqueclique_document.models
import cliqueclique_subscription.models
import utils.smime

class Command(BaseCommand):
    args = ''

    help = 'Import a document. Params: node_id filename'

    def handle(self, node_id, filename, *args, **options):
        with open(filename) as f:
            data = f.read()
        node = cliqueclique_node.models.LocalNode.objects.get(node_id=node_id)

        msg = utils.smime.message_from_anything(data)
        container_msg = msg.get_payload()[0]
        update_msg = container_msg.get_payload()[0]

        print "Importing %s..." % (update_msg['document_id'],)

        node.receive(data)
