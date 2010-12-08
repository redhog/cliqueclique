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

import time

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
    serial = django.db.models.IntegerField(default = 0)

    PROTOCOL_ATTRS = ('is_subscribed',
                      'center_node_is_subscribed',
                      'center_node_id',
                      'center_distance',
                      'serial')

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

    old_is_subscribed = django.db.models.BooleanField(default = False)
    old_center_node_is_subscribed = django.db.models.BooleanField(default=False)
    old_center_node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    old_center_distance = django.db.models.IntegerField(default = 0)

    @property
    def is_subscribed(self): return self.subscribers > 0 or self.local_is_subscribed

    @classmethod
    def subscription_for_document(cls, node, document):
        return document.subscriptions.get(node=node)

    def peer_subscription(self, peer):
        try:
            return PeerDocumentSubscription.objects.get(local_subscription=self, peer=peer)
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

    def update_center_from_upstream_peer(self, peer_subscription):
        self.center_node_is_subscribed = peer_subscription.center_node_is_subscribed
        self.center_node_id = peer_subscription.center_node_id
        self.center_distance = peer_subscription.center_distance + 1
        self.save()

    def update_subscription_from_downstream_peer(self, peer_subscription):
        if self.subscribers != peer_subscription.old_subscribers:
            self.subscribers += peer_subscription.subscribers - peer_subscription.old_subscribers
            peer_subscription.old_is_subscribed = peer_subscription.is_subscribed
            self.save()
            peer_subscription.save()

    def elect_center_node(self):
        if self.center_node_id is None or self.center_node_is_subscribed < self.is_subscribed:
            self.center_node_is_subscribed = self.is_subscribed
            self.center_node_id = self.node.node_id
            self.center_distance = 0

    def set_serial_on_change(self):
        changed = False
        for attr in self.PROTOCOL_ATTRS:
            if attr != 'serial' and getattr(self, "old_" + attr) != getattr(self, attr):
                changed = True
                setattr(self, "old_" + attr, getattr(self, attr))
        if changed:
            self.serial += 1

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        self = instance
        self.elect_center_node()
        self.set_serial_on_change()

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        # This only works for downstream 
        self = instance
        self.update_child_subscriptions()
        for peer_subscription in self.peer_subscriptions.all():
            peer_subscription.update_child_subscriptions()

    def send(self, include_body = False):
        msg = email.mime.multipart.MIMEMultipart()
        msg.add_header('message_type', 'subscription_update')
        msg.add_header('document_id', self.document.document_id)

        for attr in self.PROTOCOL_ATTRS:
            msg.add_header(attr, str(getattr(self, attr)))

        if include_body:
            msg.attach(self.document.as_mime)

        return msg

    def export(self):
        msg = email.mime.multipart.MIMEMultipart()
        msg.attach(self.send(True))
        return self.node.sign(msg)

    def __unicode__(self):
        return "%s @ %s" % (self.document, self.node)

class PeerDocumentSubscription(BaseDocumentSubscription):
    # This is what a peer knows about us, as well as what we know about them

    local_subscription = django.db.models.ForeignKey(DocumentSubscription, related_name="peer_subscriptions")
    peer = django.db.models.ForeignKey(cliqueclique_node.models.Peer, related_name="subscriptions")

    local_serial = django.db.models.IntegerField(default = 0)
    local_resend_interval = django.db.models.FloatField(default = 0)
    local_resend_time = django.db.models.FloatField(default = 0)
    peer_send = django.db.models.BooleanField(default = True)

    has_copy = django.db.models.BooleanField(default = False)
    is_subscribed = django.db.models.BooleanField(default = False)
    old_is_subscribed = django.db.models.BooleanField(default = False)
 
    @property
    def subscribers(self): return [0, 1][self.is_subscribed]
    @property
    def old_subscribers(self): return [0, 1][self.old_is_subscribed]

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
        return self._compare(self.local_subscription, self, is_this_much_closer)

    def is_downstream(self, is_this_much_closer = 0):
        # Note: Compares to our real current local subscription, not what the other node knows about us
        return self._compare(self, self.local_subscription, is_this_much_closer)

    def update_child_subscriptions(self):
        if self.is_subscribed:
            for child in self.local_subscription.children.all():
                if not child.peer_subscription(self.peer):
                    print "Creating PeerDocumentSubscription(document=%s, peer=%s)" % (child.document.document_id, self.peer.node_id)
                    PeerDocumentSubscription(local_subscription=child, peer=self.peer, serial=-1).save()

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        self = instance
        self.update_child_subscriptions()

        if self.is_upstream(1):
            self.local_subscription.update_center_from_upstream_peer(self)
        elif self.is_downstream(1):
            self.local_subscription.update_subscription_from_downstream_peer(self)

    @classmethod
    def deserialize_update(cls, update):
        res = {}
        res['is_subscribed'] = update['is_subscribed'].lower() == 'true'
        res['center_node_is_subscribed'] = update['center_node_is_subscribed'].lower() == 'true'
        res['center_node_id'] = update['center_node_id']
        res['center_distance'] = int(update['center_distance'])
        res['serial'] = int(update['serial'])
        return res

    def receive_update(self, update):
        update = self.deserialize_update(update)
        for attr in self.PROTOCOL_ATTRS:
            setattr(self, attr, update[attr])
        self.peer_send = True
        self.save()

    def receive_ack(self, update):
        update = self.deserialize_update(update)
        if self.local_subscription.serial == update['serial']:
            self.local_serial = self.local_subscription.serial
            self.has_copy = True
            self.save()

    def receive(self, update):
        if update['message_type'] == 'subscription_update':
            self.receive_update(update)
        elif update['message_type'] == 'subscription_ack':
            self.receive_ack(update)

    def send_update(self, export = False):
        if self.local_serial == self.local_subscription.serial:
            return []

        self.local_resend_interval *= 2.0
        self.local_resend_time = time.time() + self.local_resend_interval
        self.save()

        return [self.local_subscription.send(not self.has_copy or export)]

    def send_ack(self):
        if not self.peer_send:
            return []

        self.peer_send = False
        self.save()

        msg = email.mime.multipart.MIMEMultipart()
        msg.add_header('message_type', 'subscription_ack')
        msg.add_header('document_id', self.local_subscription.document.document_id)

        for attr in self.PROTOCOL_ATTRS:
            msg.add_header(attr, str(getattr(self, attr)))

        return [msg]

    def send(self, export = False):
        return self.send_update(export) + self.send_ack()

    def __unicode__(self):
        return "%s:s knowledge about %s" % (self.peer, self.local_subscription)
