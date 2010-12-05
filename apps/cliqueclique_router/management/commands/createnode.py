# -*- coding: utf-8 -*-

import datetime
import codecs
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import cliqueclique_node.models
import cliqueclique_document.models
import cliqueclique_subscription.models
import utils.smime
import django.contrib.auth.models

class Command(BaseCommand):
    args = ''

    help = 'Create a node. Params: username password'

    def handle(self, username, password, *args, **options):
        user = django.contrib.auth.models.User(
            username=username,
            is_staff=True,
            is_active=True,
            is_superuser=True)
        user.set_password(password)
        user.save()

        print user.node.node_id
