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
        res = {}
        for attr in PROTOCOL_ATTRS:
            res['sender_' + attr] = update['receiver_' + attr]
            res['receiver_' + attr] = update['sender_' + attr]
        return res

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
        
        update = self.reverse_update(peer_sub.find_update())
        update['sender_is_subscribed'] = False
        update['sender_center_node_is_subscribed'] = False
        update['sender_center_node_id'] = 'z'
        update['sender_center_distance'] =  1
        
        peer_sub.update(update)

        self.assertFalse(peer_sub.is_dirty)
        self.assertTrue(peer_sub.is_upstream())
        
        local_sub.local_is_subscribed = True
        local_sub.save()

        self.assertFalse(peer_sub.is_upstream())        

        update = peer_sub.find_update()
        for attr in PROTOCOL_ATTRS:
            update['receiver_' + attr] = update['sender_' + attr]
        update['sender_center_distance'] += 1
        update['sender_is_subscribed'] = False
        peer_sub.update(update)
        
        self.assertTrue(peer_sub.is_downstream())
