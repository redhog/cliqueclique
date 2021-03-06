import django.test
import cliqueclique_node.models
import cliqueclique_document.models
import cliqueclique_subscription.models
import email.mime.text
import email
import utils.smime

def save(obj):
    obj.save()
    return obj

PROTOCOL_ATTRS = cliqueclique_subscription.models.BaseDocumentSubscription.PROTOCOL_ATTRS

class SimpleTest(django.test.TestCase):
    def setUp(self):
        pass

    def makedoc(self, content, **kw):
        doc = email.mime.text.MIMEText(content)
        for name, value in kw.iteritems():
            doc.add_header(name, value)

        return doc.as_string()

    def reverse_update(self, update):
        if update['message_type'] == 'subscription_update':
            update['message_type'] = 'subscription_ack'
        elif update['message_type'] == 'subscription_ack':
            update['message_type'] = 'subscription_update'
        return update

    def test_child_links(self):
        n = "test_child_links"

        local = save(cliqueclique_node.models.LocalNode(name=n+"_local", address="localhost"))

        root_doc = save(cliqueclique_document.models.Document(content=self.makedoc(n+"root content")))

        child_doc = save(cliqueclique_document.models.Document(content=self.makedoc(n+"child content", parent_document_id=root_doc.document_id)))
        parent_doc = save(cliqueclique_document.models.Document(content=self.makedoc(n+"parent content", child_document_id=root_doc.document_id)))

        root_sub = save(cliqueclique_subscription.models.DocumentSubscription(
                node = local,
                document = root_doc))

        child_sub = save(cliqueclique_subscription.models.DocumentSubscription(
                node = local,
                document = child_doc))

        parent_sub = save(cliqueclique_subscription.models.DocumentSubscription(
                node = local,
                document = parent_doc))

        self.assertTrue(len(parent_sub.children.all()) == 1)
        self.assertTrue(len(root_sub.children.all()) == 1)
        mime = root_sub.children.all()[0].document.as_mime
        self.assertEqual(root_sub.children.all()[0].document.as_mime.get_payload(), n+"child content")


    def Xtest_upstream(self):
        n = "test_upstream"

        local = save(cliqueclique_node.models.LocalNode(name=n+"_local", address="localhost"))
        other = save(cliqueclique_node.models.LocalNode(name=n+"_peer", address="localhost"))
        peer = save(cliqueclique_node.models.Peer(local = local, public_key=other.public_key, address=other.address))

        doc = save(cliqueclique_document.models.Document(content=self.makedoc("content")))
        local_sub = save(cliqueclique_subscription.models.DocumentSubscription(
                node = local,
                document = doc))

        peer_sub = save(cliqueclique_subscription.models.PeerDocumentSubscription(
                local_subscription = local_sub,
                peer = peer))

        self.assertTrue(peer_sub.local_serial != peer_sub.local_subscription.serial)

        update = self.reverse_update(peer_sub.send())
        update.replace_header('sender_is_subscribed', "False")
        update.replace_header('sender_center_node_is_subscribed', "False")
        update.replace_header('sender_center_node_id', 'z')
        update.replace_header('sender_center_distance',  '1')
        peer_sub.receive(update)
        peer_sub.receive(update) # ACK
        self.assertTrue(peer_sub.is_upstream())

        peer_sub.receive(self.reverse_update(peer_sub.send()))
        peer_sub.receive(self.reverse_update(peer_sub.send())) # ACK
        self.assertFalse(peer_sub.local_serial != peer_sub.local_subscription.serial)
        
        local_sub.local_is_subscribed = True
        local_sub.save()

        self.assertFalse(peer_sub.is_upstream())        

        update = self.reverse_update(peer_sub.send())
        for attr in PROTOCOL_ATTRS:
            update.replace_header('sender_' + attr, update['receiver_' + attr])
        
        update.replace_header('sender_center_distance', str(int(update['sender_center_distance']) + 1))
        update.replace_header('sender_is_subscribed', "False")
        peer_sub.receive(update)
        peer_sub.receive(update) # ACK
        self.assertTrue(peer_sub.is_downstream())

    def sync_two(self, local1, local2, peer1, peer2):
        while True:
            msg1 = peer2.send()
            msg2 = peer1.send()
            if msg1 is None and msg2 is None:
                break
            if msg1 is not None: local1.receive(msg1.as_string())
            if msg2 is not None: local2.receive(msg2.as_string())

    def test_child_distribution(self):
        n = "test_child_distribution"
        local1 = save(cliqueclique_node.models.LocalNode(name=n+"_node1", address="addr1"))
        local2 = save(cliqueclique_node.models.LocalNode(name=n+"_node2", address="addr2"))

        peer1 = save(cliqueclique_node.models.Peer(local = local1, public_key=local2.public_key, address=local2.address))
        peer2 = save(cliqueclique_node.models.Peer(local = local2, public_key=local1.public_key, address=local1.address))

        root_doc = save(cliqueclique_document.models.Document(content=self.makedoc(n+"root content")))
        child_doc = save(cliqueclique_document.models.Document(content=self.makedoc(n+"child content", parent_document_id=root_doc.document_id)))

        root_sub1 = save(cliqueclique_subscription.models.DocumentSubscription(node = local1, document = root_doc, local_is_subscribed=True))
        child_sub1 = save(cliqueclique_subscription.models.DocumentSubscription(node = local1, document = child_doc))

        root_sub2 = save(cliqueclique_subscription.models.DocumentSubscription(node = local2, document = root_doc, local_is_subscribed=False))

        root_peer_sub1 = save(cliqueclique_subscription.models.PeerDocumentSubscription(local_subscription = root_sub1, peer = peer1))
        root_peer_sub2 = save(cliqueclique_subscription.models.PeerDocumentSubscription(local_subscription = root_sub2, peer = peer2))

        self.sync_two(local1, local2, peer1, peer2)

        root_sub2.local_is_subscribed = True
        root_sub2.save()

        self.sync_two(local1, local2, peer1, peer2)

        self.assertTrue(child_sub1.peer_subscription(peer1) is not None)
        self.assertTrue(len(root_sub2.children.all()) == 1)
        child_sub2 = root_sub2.children.all()[0]
        self.assertTrue(child_sub2.peer_subscription(peer2) is not None)

#        print peer1.send()
