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

    help = 'Post a new document. Params: node_id filename'

    def handle(self, node_id, filename, *args, **options):
        with open(filename) as f:
            data = f.read()
        node = cliqueclique_node.models.LocalNode.objects.get(node_id=node_id)

        doc = cliqueclique_document.models.Document(content=data)
        doc.save()
        sub = cliqueclique_subscription.models.DocumentSubscription(
            node = node,
            document = doc,
            local_is_subscribed = True,
            bookmarked = options['bookmark'],
            read = options['read'])
        sub.save()

        print doc.document_id
