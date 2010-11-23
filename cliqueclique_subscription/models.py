import django.db.models
import idmapper.models
import django.contrib.auth.models
import utils.modelhelpers
import settings
import cliqueclique_node.models
import cliqueclique_document.models
from django.db.models import Q
from utils.curryprefix import curryprefix

import email
import email.mime.message
import email.mime.application
import email.mime.text
import email.mime.multipart


# TODO:
#
# * Handle unsubscribed
# * Handle delete

class BaseDocumentSubscription(idmapper.models.SharedMemoryModel):
    class Meta:
        abstract = True

    __metaclass__ = utils.modelhelpers.SignalAutoConnectMeta

    center_node_is_subscribed = django.db.models.BooleanField(default=False)
    center_node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    center_distance = django.db.models.IntegerField(default = 0)

    PROTOCOL_ATTRS = ('is_subscribed',
                      'center_node_is_subscribed',
                      'center_node_id',
                      'center_distance')

class DocumentSubscription(BaseDocumentSubscription):
    node = django.db.models.ForeignKey(cliqueclique_node.models.LocalNode, related_name="subscriptions")
    document = django.db.models.ForeignKey(cliqueclique_document.models.Document, related_name="subscriptions")
    read = django.db.models.BooleanField(default=False)
    bookmarked = django.db.models.BooleanField(default=False)

    # Note, this might be empty if no document with self.document.{up,down}_document_id
    # exists at this node yet
    parents = django.db.models.ManyToManyField("DocumentSubscription", related_name="children", null=True, blank=True)

    # Did _we_ subscribe to this?
    local_is_subscribed = django.db.models.BooleanField(default = False)
    subscribers = django.db.models.SmallIntegerField(default = 0) # Don't change this one manually

    @property
    def is_subscribed(self): return self.subscribers > 0 or self.local_is_subscribed

    @classmethod
    def subscription_for_document(cls, node, document):
        return document.subscriptions.get(node=node)

    def peer_subscription(self, peer):
        try:
            return DocumentSubscription.objects.get(local_subscription=self, peer=peer) 
        except:
            return None

    def update_child_subscriptions(self):
        if self.document.parent_document_id is not None:
            parent_document = cliqueclique_document.models.Document.objects.get(document_id=self.document.parent_document_id)
            parent_subscription = self.subscription_for_document(self.node, parent_document) 
            if parent_subscription not in self.parents.all():
                self.parents.add(parent_subscription)
                self.save()

        if self.document.child_document_id is not None:
            child_document = cliqueclique_document.models.Document.objects.get(document_id=self.document.child_document_id)
            child_subscription = self.subscription_for_document(self.node, child_document) 
            if child_subscription not in self.children.all():
                self.children.add(child_subscription)
                self.save()

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        self = instance
        if self.center_node_id is None or self.center_node_is_subscribed < self.is_subscribed:
            self.center_node_is_subscribed = self.is_subscribed
            self.center_node_id = self.node.node_id
            self.center_distance = 0

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        self = instance
        self.update_child_subscriptions()
        for peer_subscription in self.peer_subscriptions.all():
            peer_subscription.update_child_subscriptions()
            peer_subscription.set_dirty()


class PeerDocumentSubscription(BaseDocumentSubscription):
    # This is what a peer knows about us, as well as what we know about them

    local_subscription = django.db.models.ForeignKey(DocumentSubscription, related_name="peer_subscriptions")
    peer = django.db.models.ForeignKey(cliqueclique_node.models.Peer, related_name="subscriptions")

    is_dirty = django.db.models.BooleanField(default = True)

    is_subscribed = django.db.models.BooleanField(default = False)
 
    peer_old_is_subscribed = django.db.models.BooleanField(default = False) # Don't modify this by hand, it's just for internal use by the pre_save method
    peer_is_subscribed = django.db.models.BooleanField(default = False)
    peer_center_node_is_subscribed = django.db.models.BooleanField(default = False)
    peer_center_node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    peer_center_distance = django.db.models.IntegerField(default = 0)

    @property
    def subscribers(self): return [0, 1][self.is_subscribed]
    @property
    def peer_old_subscribers(self): return [0, 1][self.peer_old_is_subscribed]
    @property
    def peer_subscribers(self): return [0, 1][self.peer_is_subscribed]

    @classmethod
    def _compare(cls, a, b, is_this_much_closer = 0):
        # Test if a is downstream from b. Should really have the same
        # semantics as cmp, but it doesn't :P
        return (   a.center_node_is_subscribed < b.center_node_is_subscribed
                or (   a.center_node_is_subscribed == b.center_node_is_subscribed
                    and (   a.center_node_id < b.center_node_id
                         or (    a.center_node_id == b.center_node_id
                             and a.center_distance > b.center_distance + is_this_much_closer))))

    def is_upstream(self, is_this_much_closer = 0):
        # Note: Compares to our real current local subscription, not what the other node knows about us
        return self._compare(self.local_subscription, curryprefix(self, "peer_"), is_this_much_closer)

    def is_downstream(self, is_this_much_closer = 0):
        # Note: Compares to our real current local subscription, not what the other node knows about us
        return self._compare(curryprefix(self, "peer_"), self.local_subscription, is_this_much_closer)

    def update_child_subscriptions(self):
        if self.peer_is_subscribed:
            for child in self.local_subscription.children.all():
                if not child.peer_subscription(self.peer):
                    PeerDocumentSubscription(local_subscription=child, peer=self.peer, is_dirty=True).save()

    def set_dirty(self):
        for attr in self.PROTOCOL_ATTRS:
            if getattr(self, attr) != getattr(self.local_subscription, attr):
                #print "DIRTY BECAUSE %s: peer=%s != local=%s" % (attr, getattr(self, attr), getattr(self.local_subscription, attr))
                self.is_dirty = True
                self.save()
                return

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        self = instance
        if not self.is_dirty:
            if self.is_upstream(1):
                local = self.local_subscription
                peer = curryprefix(self, "peer_")

                local.center_node_is_subscribed = peer.center_node_is_subscribed
                local.center_node_id = peer.center_node_id
                local.center_distance = peer.center_distance + 1
                local.save()

            elif self.is_downstream(1):

                local = self.local_subscription
                peer = curryprefix(self, "peer_")

                if peer.subscribers != peer.old_subscribers:
                    local.subscribers += peer.subscribers - peer.old_subscribers
                    peer.old_is_subscribed = peer.is_subscribed
                    local.save()
                    self.save()

    def find_update(self):
        local = self.local_subscription
        peer = curryprefix(self, "peer_")
        
        update = {}
        for attr in self.PROTOCOL_ATTRS:
            update['sender_' + attr] = getattr(local, attr)
            update['receiver_' + attr] = getattr(peer, attr)

        return update

    def update(self, update):
        local = self # yes, not self.local_subscription - this is
                     # about what the other node knows, not about
                     # what's true
        peer = curryprefix(self, "peer_")

        local.is_subscribed = update['receiver_is_subscribed'].lower() == "true"
        local.center_node_is_subscribed = update['receiver_center_node_is_subscribed'].lower() == "true"
        local.center_node_id = update['receiver_center_node_id']
        local.center_distance = int(update['receiver_center_distance'])

        peer.is_subscribed = update['sender_is_subscribed'].lower() == "true"
        peer.center_node_is_subscribed = update['sender_center_node_is_subscribed'].lower() == "true"
        peer.center_node_id = update['sender_center_node_id']
        peer.center_distance = int(update['sender_center_distance'])

        self.is_dirty = False
        self.set_dirty()
        self.save()

    def send(self):
        update = self.find_update()

        update['message_type'] = 'subscription_update'
        update['document_id'] = self.local_subscription.document.document_id
        update['sender_node_id'] = self.local_subscription.node.node_id
        update['receiver_node_id'] = self.peer.node_id

        msg = email.mime.text.MIMEText("")
        
        keys = update.keys()
        keys.sort()
        for key in keys:
            msg.add_header(key, str(update[key]))

        return msg

    @classmethod
    def receive(cls, msg):
        if isinstance(msg, unicode):
            msg = str(msg)
        if isinstance(msg, str):
            msg = email.message_from_string(msg)

        subs = cls.objects.filter(local_subscription__document__document_id = msg['document_id'],
                                  peer__node_id = msg['sender_node_id'],
                                  local_subscription__node__node_id = msg['receiver_node_id']).all()
        if subs:
            sub = subs[0]
        else:
            local_subscription = DocumentSubscription.objects.get(document__document_id = msg['document_id'],
                                                                  node__node_id = msg['receiver_node_id'])
            peers = cliqueclique_node.models.Peer.objects.filter(node_id = msg['sender_node_id'],
                                                                 node__node_id = msg['receiver_node_id']).all()
            if peers:
                peer = peers[0]
            else:
                node = cliqueclique_node.models.LocalNode.objects.get(node_id = msg['receiver_node_id'])
                peer = cliqueclique_node.models.Peer(node_id = msg['sender_node_id'], node = node)
                peer.save()

            sub = cls(local_subscription = local_subscription,
                      peer = peer)

        sub.update(msg)
        return sub
