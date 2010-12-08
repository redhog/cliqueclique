import django.db.models
import idmapper.models
import django.contrib.auth.models
from django.db.models import Q
from django.db.models import F
import utils.modelhelpers
import utils.smime
import settings
import hashlib
import email
import email.mime.message
import email.mime.application
import email.mime.text
import email.mime.multipart
import M2Crypto.X509
import M2Crypto.BIO
import i2p.socket
import utils.i2p
import utils.hash
import time

class Node(idmapper.models.SharedMemoryModel):
    __metaclass__ = utils.modelhelpers.SignalAutoConnectMeta

    # max_length should really be the max-length supported by X509 for CN
    name = django.db.models.CharField(max_length=200, blank=True)
    node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, blank=True)
    public_key = utils.modelhelpers.Base64Field(blank=True)
    address = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_ADDRESS_LENGTH, blank=True)

    @classmethod
    def node_id_from_public_key(cls, public_key):
        return utils.hash.has_id_from_data(public_key)

    def __unicode__(self):
        return "%s %s [%s..]" % (type(self).__name__, self.name, self.node_id[:10])

class LocalNode(Node):
    owner = django.db.models.OneToOneField(django.contrib.auth.models.User, related_name="node", blank=True, null=True)
    private_key = utils.modelhelpers.Base64Field(blank=True)

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        if not instance.address:
            sock = i2p.socket.socket(settings.CLIQUECLIQUE_I2P_SESSION_NAME, i2p.socket.SOCK_DGRAM)
            instance.address = utils.i2p.dest2b32(sock.dest)
            sock.close()
        if not instance.public_key:
            instance.public_key, instance.private_key = utils.smime.make_self_signed_cert(instance.name, instance.address, settings.CLIQUECLIQUE_KEY_SIZE)
        if not instance.node_id:
            instance.node_id = instance.node_id_from_public_key(instance.public_key)

    def send(self):
        for peer in self.peers.all():
            msg = peer.send()
            if msg is not None:
                yield (msg.as_string(), peer.address)
    
    def receive(self, msg):
        msg = utils.smime.message_from_anything(msg)
        cert = msg.verify()[0]
        container_msg = msg.get_payload()[0]

        sender_node_id = self.node_id_from_public_key(cert)

        peers = self.peers.filter(node_id = sender_node_id).all()
        if peers:
            peer = peers[0]
        else:
            peer = Peer(local=self, node_id = sender_node_id, public_key=cert)
            peer.save()

        for part in container_msg.get_payload():
            peer.receive(part)

    @classmethod
    def send_any(cls):
        for self in cls.objects.all():
            for msg in self.send():
                yield msg

    @classmethod
    def receive_any(cls, msg):
        msg = utils.smime.message_from_anything(msg)
        container_msg = msg.get_payload()[0]

        self = cls.objects.get(
            node_id = container_msg['receiver_node_id']
            ).receive(msg)
        
    def sign(self, msg):
        signed = utils.smime.MIMESigned()
        signed.set_private_key(utils.smime.der2pem(self.private_key, "PRIVATE KEY"))
        signed.set_cert(utils.smime.der2pem(self.public_key))
        signed.attach(msg)
        return signed

def user_post_save(sender, instance, **kwargs):
    try:
        instance.node
    except:
        LocalNode(owner = instance, name = instance.username).save()
django.db.models.signals.post_save.connect(user_post_save, sender=django.contrib.auth.models.User)

class Peer(Node):
    local = django.db.models.ForeignKey(LocalNode, related_name="peers")

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        assert instance.public_key
        if not instance.node_id:
            instance.node_id = instance.node_id_from_public_key(instance.public_key)
        if not instance.name or not instance.address:
            data = utils.smime.cert_get_data(instance.public_key)
            if not instance.name: instance.name = data['name']
            if not instance.address: instance.address = data['address']

    @property
    def updates(self):
        return self.subscriptions.filter(Q(~Q(serial=F("local_subscription__serial")),
                                           local_resend_time__lte = time.time())
                                         |Q(peer_send=True))

    @property
    def new(self):
        return self.subscriptions.filter(has_copy=False)

    def send(self):
        updates = self.updates.all()
        if len(updates) == 0:
            return None
        update_msgs = []
        for sub in updates:
            update_msgs.extend(sub.send())
        if len(update_msgs) == 0:
            return None

        msg = email.mime.multipart.MIMEMultipart()

        update = {'receiver_node_id': self.node_id}

        keys = update.keys()
        keys.sort()
        for key in keys:
            msg.add_header(key, str(update[key]))

        for update in update_msgs:
            msg.attach(update)
        
        return self.local.sign(msg)

    def receive(self, part):
        import cliqueclique_document.models
        import cliqueclique_subscription.models

        if part['message_type'] in ('subscription_update', 'subscription_ack'):
            is_new = False
            subs = cliqueclique_subscription.models.PeerDocumentSubscription.objects.filter(
                local_subscription__document__document_id = part['document_id'],
                peer = self,
                local_subscription__node = self.local).all()
            if subs:
                sub = subs[0]
            else:
                if part['message_type'] == 'subscription_ack':
                    raise Exception("Received an ACK for a non-existent message %s" % (part['document_id'],))
                local_subs = cliqueclique_subscription.models.DocumentSubscription.objects.filter(
                    document__document_id = part['document_id'],
                    node = self.local).all()
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
                    is_new = True

                sub = cliqueclique_subscription.models.PeerDocumentSubscription(
                    local_subscription = local_sub,
                    peer = self)
                sub.save()
            sub.receive(part)

            # We don't want the other node to continue spamming us
            # about this, so make sure we send them something so they
            # know we now have a copy, to make them stop :)

            if is_new:
                sub.is_dirty = True # FIXME: needs_ack or dirty here?
                sub.save()
        else:
            raise Exception("Unknown message type %s" % (part['message_type'],))
