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

    help = 'Export a document. Params: node_id document_id filename'

    def handle(self, node_id, document_id, filename, *args, **options):
        with open(filename, "w") as f:
            sub = cliqueclique_subscription.models.DocumentSubscription.objects.get(
                node__node_id=node_id,
                document__document_id=document_id)
            f.write(sub.export().as_string())
