import django.db.models
import idmapper.models
import django.contrib.auth.models
from django.db.models import Q
import utils.modelhelpers
import utils.smime
import settings
import hashlib
import email
import email.mime.message
import email.mime.application
import email.mime.text
import email.mime.multipart

class Node(idmapper.models.SharedMemoryModel):
    __metaclass__ = utils.modelhelpers.SignalAutoConnectMeta

    # max_length should really be the max-length supported by X509 for CN
    name = django.db.models.CharField(max_length=200, blank=True)
    node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, blank=True)
    public_key = utils.modelhelpers.Base64Field(blank=True)
    address = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_ADDRESS_LENGTH, blank=True)

class LocalNode(Node):
    owner = django.db.models.OneToOneField(django.contrib.auth.models.User, related_name="node", blank=True, null=True)
    private_key = utils.modelhelpers.Base64Field(blank=True)

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        if not instance.public_key:
            instance.public_key, instance.private_key = utils.smime.make_self_signed_cert(instance.name, settings.CLIQUECLIQUE_KEY_SIZE)
        if not instance.node_id:
            h = hashlib.sha512()
            h.update(instance.public_key)
            instance.node_id = h.hexdigest()[:settings.CLIQUECLIQUE_HASH_LENGTH]

class Peer(Node):
    local = django.db.models.ForeignKey(LocalNode, related_name="peers")

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        assert instance.public_key
        if not instance.node_id:
            h = hashlib.sha512()
            h.update(instance.public_key)
            instance.node_id = h.hexdigest()[:settings.CLIQUECLIQUE_HASH_LENGTH]

    @property
    def updates(self):
        return self.subscriptions.filter(is_dirty=True)

    @property
    def new(self):
        return self.subscriptions.filter(has_copy=False)

    def send(self):
        msg = email.mime.multipart.MIMEMultipart()

        update = {'sender_node_id': self.local.node_id,
                  'receiver_node_id': self.node_id}

        keys = update.keys()
        keys.sort()
        for key in keys:
            msg.add_header(key, str(update[key]))

        for sub in self.updates.all():
            msg.attach(sub.send())
        
        return msg

    def receive(self, msg):
        import cliqueclique_document.models
        import cliqueclique_subscription.models

        if isinstance(msg, unicode):
            msg = str(msg)
        if isinstance(msg, str):
            msg = email.message_from_string(msg)

        for part in msg.get_payload():
            if part['message_type'] == 'subscription_update':
                subs = cliqueclique_subscription.models.PeerDocumentSubscription.objects.filter(
                    local_subscription__document__document_id = part['document_id'],
                    peer__node_id = msg['sender_node_id'],
                    local_subscription__node__node_id = msg['receiver_node_id']).all()
                if subs:
                    sub = subs[0]
                else:
                    local_subs = cliqueclique_subscription.models.DocumentSubscription.objects.filter(
                        document__document_id = part['document_id'],
                        node__node_id = msg['receiver_node_id']).all()
                    if local_subs:
                        local_sub = local_subs[0]
                    else:
                        docs = cliqueclique_document.models.Document.objects.filter(
                            document_id = part['document_id']).all()
                        if docs:
                            doc = docs[0]
                        else:
                            doc = cliqueclique_document.models.Document(content = part.get_payload())
                            doc.save()
                        local_sub = cliqueclique_subscription.models.DocumentSubscription(node = self.local, document = doc)
                        local_sub.save()

                    sub = cliqueclique_subscription.models.PeerDocumentSubscription(
                        local_subscription = local_sub,
                        peer = self)
                    sub.save()
                sub.receive(part)
            else:
                raise "Unknown message type %s" % (part['message_type'],)
            
