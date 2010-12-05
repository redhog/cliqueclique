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

    option_list = BaseCommand.option_list + (
        make_option('--bookmark',
                    action='store_true',
                    default=False,
                    dest='bookmark',
                    help='Bookmark the document'),
        make_option('--read',
                    action='store_true',
                    default=False,
                    dest='read',
                    help='Mark the document as read'),
        )

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

        sub = cliqueclique_subscription.models.DocumentSubscription.objects.get(
            node = node,
            document__document_id = update_msg['document_id'])

        sub.bookmarked = options['bookmark']
        sub.read = options['read']

        sub.save()
