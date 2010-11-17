"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

import django.test
import cliqueclique_node.models

def save(obj):
    obj.save()
    return obj

class SimpleTest(django.test.TestCase):
    def setUp(self):
        self.local_node = save(cliqueclique_node.models.LocalNode(node_id="local", public_key="X", address="localhost", private_key="X"))
        self.peers = [save(cliqueclique_node.models.Peer(node = self.local_node, node_id="peer%s" % n, public_key="X", address="localhost")) for n in xrange(0, 2)]

        self.documents = [save(cliqueclique_node.models.Document(document_id="document%s" % n, content="content%s" % n)) for n in xrange(0, 2)]

    def test_basic_addition(self):
        
        self.failUnlessEqual(1 + 1, 2)
