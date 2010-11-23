import django.test
import cliqueclique_node.models
import cliqueclique_document.models
import cliqueclique_subscription.models
import email.mime.text
import email

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
        tmp = {}
        for attr in PROTOCOL_ATTRS + ('node_id',):
            tmp['sender_' + attr] = update['receiver_' + attr]
            tmp['receiver_' + attr] = update['sender_' + attr]
        for key, value in tmp.iteritems():
            update.replace_header(key, value)
        return update

    def test_child_links(self):
        n = "test_child_links"

        local = save(cliqueclique_node.models.LocalNode(node_id=n+"local", public_key="X", address="localhost", private_key="X"))

        root_doc = save(cliqueclique_document.models.Document(content=self.makedoc("root content")))

        child_doc = save(cliqueclique_document.models.Document(content=self.makedoc("child content", parent_document_id=root_doc.document_id)))
        parent_doc = save(cliqueclique_document.models.Document(content=self.makedoc("parent content", child_document_id=root_doc.document_id)))

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
        self.assertEqual(root_sub.children.all()[0].document.as_mime.get_payload(), "child content")


    def test_upstream(self):
        n = "test_upstream"

        local = save(cliqueclique_node.models.LocalNode(node_id=n+"local", public_key="X", address="localhost", private_key="X"))
        peer = save(cliqueclique_node.models.Peer(node = local, node_id=n+"peer", public_key="X", address="localhost"))

        doc = save(cliqueclique_document.models.Document(content=self.makedoc("content")))
        local_sub = save(cliqueclique_subscription.models.DocumentSubscription(
                node = local,
                document = doc))

        peer_sub = save(cliqueclique_subscription.models.PeerDocumentSubscription(
                local_subscription = local_sub,
                peer = peer))

        self.assertTrue(peer_sub.is_dirty)

        update = self.reverse_update(peer_sub.send())
        update.replace_header('sender_is_subscribed', "False")
        update.replace_header('sender_center_node_is_subscribed', "False")
        update.replace_header('sender_center_node_id', 'z')
        update.replace_header('sender_center_distance',  '1')
        peer_sub.receive(update)
        self.assertTrue(peer_sub.is_upstream())

        peer_sub.receive(self.reverse_update(peer_sub.send()))
        self.assertFalse(peer_sub.is_dirty)
        
        local_sub.local_is_subscribed = True
        local_sub.save()

        self.assertFalse(peer_sub.is_upstream())        

        update = self.reverse_update(peer_sub.send())
        for attr in PROTOCOL_ATTRS:
            update.replace_header('sender_' + attr, update['receiver_' + attr])
        
        update.replace_header('sender_center_distance', str(int(update['sender_center_distance']) + 1))
        update.replace_header('sender_is_subscribed', "False")
        peer_sub = peer_sub.receive(update)
        
        self.assertTrue(peer_sub.is_downstream())
