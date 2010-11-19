import django.test
import cliqueclique_node.models
import cliqueclique_document.models
import cliqueclique_subscription.models

def save(obj):
    obj.save()
    return obj

class SimpleTest(django.test.TestCase):
    def setUp(self):
        self.local_node = save(cliqueclique_node.models.LocalNode(node_id="local", public_key="X", address="localhost", private_key="X"))
        self.peers = [save(cliqueclique_node.models.Peer(node = self.local_node, node_id="peer%s" % n, public_key="X", address="localhost")) for n in xrange(0, 2)]

#        self.documents = [save(cliqueclique_document.models.Document(document_id="document%s" % n, content="content%s" % n)) for n in xrange(0, 2)]

    def test_child_links(self):
        n = "test_child_links"
        root_doc = save(cliqueclique_document.models.Document(document_id=n+"root", content="root content"))
        child_doc = save(cliqueclique_document.models.Document(document_id=n+"child", content="child content", parent_document_id=n+"root"))
        parent_doc = save(cliqueclique_document.models.Document(document_id=n+"parent", content="parent content", child_document_id=n+"root"))

        root_sub = save(cliqueclique_subscription.models.DocumentSubscription(
                node = self.local_node,
                document = root_doc))

        child_sub = save(cliqueclique_subscription.models.DocumentSubscription(
                node = self.local_node,
                document = child_doc))

        parent_sub = save(cliqueclique_subscription.models.DocumentSubscription(
                node = self.local_node,
                document = parent_doc))

        self.assertTrue(len(parent_sub.children.all()) == 1)
        self.assertTrue(len(root_sub.children.all()) == 1)
        self.assertEqual(root_sub.children.all()[0].document.content, "child content")

    def test_upstream(self):
        n = "test_upstream"

        # p > l, so peer > local, so the peer will end up being center node 
        local = save(cliqueclique_node.models.LocalNode(node_id=n+"local", public_key="X", address="localhost", private_key="X"))
        peer = save(cliqueclique_node.models.Peer(node = self.local_node, node_id=n+"peer", public_key="X", address="localhost"))

        doc = save(cliqueclique_document.models.Document(document_id=n+"doc", content="content"))
        local_sub = save(cliqueclique_subscription.models.DocumentSubscription(
                node = local,
                document = doc))

        peer_sub = save(cliqueclique_subscription.models.PeerDocumentSubscription(
                local_subscription = local_sub,
                peer = peer))

        self.assertTrue(peer_sub.is_dirty)
        
        local_encoded = peer_sub.send()

        peer_sub.receive({
                'local': {
                    'is_subscribed': False,
                    'center_node_is_subscribed': False,
                    'center_node_id': 'a',
                    'center_distance':  1
                    },
                'peer': local_encoded['local']})

        self.assertFalse(peer_sub.is_dirty)
