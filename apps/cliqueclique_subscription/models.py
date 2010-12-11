import django.db.models
import idmapper.models
import django.contrib.auth.models
import fcdjangoutils.signalautoconnectmodel
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
import sys

# TODO:
#
# * Handle unsubscribed
# * Handle delete

class BaseDocumentSubscription(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    class Meta:
        abstract = True

    center_node_is_subscribed = django.db.models.BooleanField(default=False)
    center_node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    center_distance = django.db.models.IntegerField(default = 0)
    serial = django.db.models.IntegerField(default = 0)

    PROTOCOL_ATTRS = ('is_wanted',
                      'is_subscribed',
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

    wanters = django.db.models.SmallIntegerField(default = 0) # Don't change this one manually

    # Did _we_ subscribe to this?
    local_is_subscribed = django.db.models.BooleanField(default = False)
    subscribers = django.db.models.SmallIntegerField(default = 0) # Don't change this one manually

    old_is_wanted = django.db.models.BooleanField(default=False)
    old_is_subscribed = django.db.models.BooleanField(default=False)
    old_center_node_is_subscribed = django.db.models.BooleanField(default=False)
    old_center_node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    old_center_distance = django.db.models.IntegerField(default = 0)

    @property
    def is_wanted(self):
        subscribed_parents = 0
        try:
            subscribed_parents = self.parents.filter(local_is_subscribed=True).count()
        except:
            pass
        return self.wanters > 0 or self.bookmarked or subscribed_parents > 0

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
        if peer_subscription.is_upstream():
            self.center_node_is_subscribed = peer_subscription.center_node_is_subscribed
            self.center_node_id = peer_subscription.center_node_id
            self.center_distance = peer_subscription.center_distance + 1
            self.save()

    def update_subscription_from_downstream_peer(self, peer_subscription):
        updated = False
        if self.wanters != peer_subscription.old_subscribers:
            updated = True
            self.wanters += peer_subscription.wanters - peer_subscription.old_wanters
            peer_subscription.old_wanters = peer_subscription.wanters
        if peer_subscription.subscribers != peer_subscription.old_subscribers:
            updated = True
            self.subscribers += peer_subscription.subscribers - peer_subscription.old_subscribers
            peer_subscription.old_subscribers = peer_subscription.subscribers
        if updated:
            self.save()
            peer_subscription.save()

    def elect_center_node(self):
        sys.stderr.write("%s ELECTION: %s < %s\n" % (self.node.node_id[:5], self.center_node_is_subscribed, self.is_subscribed))
        if self.center_node_id == self.node.node_id:
            if self.center_node_is_subscribed != self.is_subscribed:
                sys.stderr.write("%s %s %s\n" % (self.node.node_id[:5], "UPDATE CENTER NODE SUBSCRIPTION TO", self.is_subscribed))
            self.center_node_is_subscribed = self.is_subscribed
        elif self.center_node_id is None or self.center_node_is_subscribed < self.is_subscribed:
            sys.stderr.write("%s %s\n" % (self.node.node_id[:5], "CHANGE CENTER NODE TO SELFT"))
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
    def on_pre_save(cls, sender, instance, **kwargs):
        self = instance
        self.elect_center_node()
        self.set_serial_on_change()

    @classmethod
    def on_post_save(cls, sender, instance, **kwargs):
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
    local_resend_interval = django.db.models.FloatField(blank=True, null=True)
    local_resend_time = django.db.models.FloatField(default = 0)
    peer_send = django.db.models.BooleanField(default = True)

    has_copy = django.db.models.BooleanField(default = False)
    is_wanted = django.db.models.BooleanField(default = False)
    is_subscribed = django.db.models.BooleanField(default = False)

    old_wanters = django.db.models.IntegerField(default = 0)
    old_subscribers = django.db.models.IntegerField(default = 0)
 
    @property
    def wanters(self): return [0, 1][self.is_downstream(1)]
    @property
    def subscribers(self): return [0, 1][self.is_downstream(1) and self.is_subscribed]

    @classmethod
    def _compare(cls, a, b, is_this_much_closer = 0):
        # Test if a is upstream from b. NOTE: CHANGED ORDER A B!!!

        if a.center_node_id == b.center_node_id:
            # Yes, a.distance < b.distance for a to be upstream :)
            return cmp(b.center_distance, a.center_distance + is_this_much_closer)
        else:
            if a.center_node_is_subscribed == b.center_node_is_subscribed:
                return cmp(a.center_node_id, b.center_node_id)
            else:
                return cmp(a.center_node_is_subscribed, b.center_node_is_subscribed)

    def is_upstream(self, is_this_much_closer = 0):
        # Note: Compares to our real current local subscription, not what the other node knows about us
        return self._compare(self, self.local_subscription, is_this_much_closer) > 0

    def is_downstream(self, is_this_much_closer = 0):
        # Note: Compares to our real current local subscription, not what the other node knows about us
        return self._compare(self.local_subscription, self, is_this_much_closer) > 0

    def update_child_subscriptions(self):
        if self.is_subscribed:
            for child in self.local_subscription.children.all():
                if not child.peer_subscription(self.peer):
                    sys.stderr.write("Creating PeerDocumentSubscription(document=%s, peer=%s)\n" % (child.document.document_id, self.peer.node_id))
                    PeerDocumentSubscription(local_subscription=child, peer=self.peer, serial=-1).save()

    @classmethod
    def on_pre_save(cls, sender, instance, **kwargs):
        self = instance
        self.update_child_subscriptions()

        self.local_subscription.update_center_from_upstream_peer(self)
        self.local_subscription.update_subscription_from_downstream_peer(self)

    @classmethod
    def deserialize_update(cls, update):
        res = {}
        res['is_wanted'] = update['is_wanted'].lower() == 'true'
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
            if self.local_resend_interval is not None:
                self.local_resend_interval = None
                self.save()
            return []

        if self.local_resend_interval is None:
            self.local_resend_interval = 1.0
        else:
            self.local_resend_interval *= 2.0
        self.local_resend_time = time.time() + self.local_resend_interval
        self.save()

        return [self.local_subscription.send(not self.has_copy or export)]

    def send_ack(self):
        if not self.peer_send:
            return []

        if self.is_wanted:
            self.peer_send = False
            self.save()
        else:
            self.delete()

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
