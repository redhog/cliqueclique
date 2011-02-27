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

import utils.smime

import time
import sys

import query

def format_change(n, o, trunk = False):
    nn = n
    oo = o
    if trunk:
        nn = nn[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH]
        oo = oo[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH]
    res = str(nn)
    if n != o:
        res += '(%s)' % (oo,)
    return res

class BaseDocumentSubscription(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    class Meta:
        abstract = True

    center_node_is_subscribed = django.db.models.BooleanField(default=False)
    center_node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    center_distance = django.db.models.IntegerField(default = 0)
    serial = django.db.models.IntegerField(default = 0)

    PROTOCOL_ATTRS = ('has_enought_peers',
                      'is_wanted',
                      'is_subscribed',
                      'center_node_is_subscribed',
                      'center_node_id',
                      'center_distance',
                      'serial')

class DocumentSubscription(BaseDocumentSubscription):
    class Meta:
        unique_together = (("node", "document"),)

    node = django.db.models.ForeignKey(cliqueclique_node.models.LocalNode, related_name="subscriptions")
    document = django.db.models.ForeignKey(cliqueclique_document.models.Document, related_name="subscriptions")

    read = django.db.models.BooleanField(default=False)
    bookmarked = django.db.models.BooleanField(default=False)
    local_is_subscribed = django.db.models.BooleanField(default = False)

    # Note, this might be empty if no document with self.document.{up,down}_document_id
    # exists at this node yet
    parents = django.db.models.ManyToManyField("DocumentSubscription", related_name="children", null=True, blank=True)

    peer_nrs = django.db.models.SmallIntegerField(default = 0) # Don't change this one manually
    wanters = django.db.models.SmallIntegerField(default = 0) # Don't change this one manually
    subscribed_parents = django.db.models.SmallIntegerField(default = 0) # Don't change this one manually

    subscribers = django.db.models.SmallIntegerField(default = 0) # Don't change this one manually

    old_has_enought_peers = django.db.models.BooleanField(default=False)
    old_is_wanted = django.db.models.BooleanField(default=False)
    old_is_subscribed = django.db.models.BooleanField(default=False)
    old_center_node_is_subscribed = django.db.models.BooleanField(default=False)
    old_center_node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    old_center_distance = django.db.models.IntegerField(default = 0)

    @classmethod
    def get_subscription(cls, node, document_id, content = None):
        is_new, doc = cliqueclique_document.models.Document.get_document(document_id, content)
        local_subs = DocumentSubscription.objects.filter(
            document = doc,
            node = node).all()
        if local_subs:
            local_sub = local_subs[0]
        else:
            if content is None:
                raise Exception("Unable to create new local subscription for document %s without any content" % (document_id,))
            local_sub = DocumentSubscription(node = node, document = doc)
            local_sub.save()
            is_new = True
        return is_new, local_sub

    def format_to_dict(self):
        return {
            'node_id': self.node.node_id[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH],
            'document_id': self.document.document_id[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH],

            'read': ['unread', 'read'][self.read],
            'bookmarked': ['unmarked', 'bookmarked'][self.bookmarked],
            'local_is_subscribed': ['nonsub', 'subscribed'][self.local_is_subscribed],

            'children': ', '.join(child.document.document_id[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH] for child in self.children.all()),

            'peer_nrs': self.peer_nrs,
            'wanters': self.wanters,
            'subscribed_parents': self.subscribed_parents,

            'subscribers': self.subscribers,

            'serial': self.serial,
            'has_enought_peers': format_change(self.has_enought_peers, self.old_has_enought_peers),
            'is_wanted': format_change(self.is_wanted, self.old_is_wanted),
            'is_subscribed': format_change(self.is_subscribed, self.old_is_subscribed),
            'center_node_is_subscribed': format_change(self.center_node_is_subscribed, self.old_center_node_is_subscribed),
            'center_node_id': format_change(self.center_node_id, self.old_center_node_id, True),
            'center_distance': format_change(self.center_distance, self.old_center_distance),
            }
            
    def __repr__(self):
        return """%(node_id)s.%(document_id)s (%(read)s %(bookmarked)s %(local_is_subscribed)s)
Children: %(children)s

Peers: %(peer_nrs)s
Wanters: %(wanters)s
Subscribed parents: %(subscribed_parents)s

Subscribers: %(subscribers)s

Serial: %(serial)s
Has enought peers: %(has_enought_peers)s
Is wanted: %(is_wanted)s
Is subscribed: %(is_subscribed)s
Center node is subscribed: %(center_node_is_subscribed)s
Center node id: %(center_node_id)s
Center distance: %(center_distance)s
""" % self.format_to_dict()


    @property
    def has_enought_peers(self):
       # we allways wanna have at least two peers, even if we're next
       # to the center node, so > not >=.
        return self.peer_nrs > min(settings.CLIQUECLIQUE_OPTIMAL_PEER_NRS, self.center_distance)

#max(min(self.center_distance, int(settings.CLIQUECLIQUE_OPTIMAL_PEER_NRS - settings.CLIQUECLIQUE_OPTIMAL_PEER_NRS / (self.center_distance + 1.0))), 1)

    @property
    def is_wanted(self):
        return self.wanters > 0 or self.bookmarked or self.subscribed_parents > 0

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

    def ensure_peer_subscription(self, peer):
        peer_subscription = self.peer_subscription(peer)
        if not peer_subscription:
            sys.stderr.write("Creating PeerDocumentSubscription(document=%s, peer=%s)\n" % (self.document.document_id, peer.node_id))
            peer_subscription = PeerDocumentSubscription(local_subscription=self, peer=peer, serial=-1)
            peer_subscription.save()
        return peer_subscription

    def update_subscribed_parents(self):
        subscribed_parents = self.parents.filter(local_is_subscribed=True).count()
        if subscribed_parents != self.subscribed_parents:
            self.subscribed_parents = subscribed_parents
            self.save()

    def update_child_subscriptions(self):
        if self.document.parent_document_id is not None:
            parent_document = cliqueclique_document.models.Document.objects.get(document_id=self.document.parent_document_id)
            parent_subscription = self.subscription_for_document(self.node, parent_document) 
            if parent_subscription not in self.parents.all():
                self.parents.add(parent_subscription)
                self.update_subscribed_parents()
                self.save()

        if self.document.child_document_id is not None:
            child_document = cliqueclique_document.models.Document.objects.get(document_id=self.document.child_document_id)
            child_subscription = self.subscription_for_document(self.node, child_document) 
            if child_subscription not in self.children.all():
                self.children.add(child_subscription)
                self.save()

        for child in self.children.all():
            child.update_subscribed_parents()

        for parent in self.parents.all():
            for peer_subscription in parent.peer_subscriptions.all():
                if peer_subscription.is_subscribed:
                    self.ensure_peer_subscription(peer_subscription.peer)

    def update_peer_nrs(self, diff):
        self.peer_nrs += diff
        self.save()

    def update_center_from_upstream_peer(self, peer_subscription):
        if peer_subscription.is_upstream():
            self.center_node_is_subscribed = peer_subscription.center_node_is_subscribed
            self.center_node_id = peer_subscription.center_node_id
            self.center_distance = peer_subscription.center_distance + 1
            self.save()

    def update_subscription_from_downstream_peer(self, peer_subscription):
        updated = False
        if self.wanters != peer_subscription.old_wanters:
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
        #sys.stderr.write("%s ELECTION: %s < %s\n" % (self.node.node_id[:5], self.center_node_is_subscribed, self.is_subscribed))
        if self.center_node_id == self.node.node_id:
            if self.center_node_is_subscribed != self.is_subscribed:
                pass
                #sys.stderr.write("%s %s %s\n" % (self.node.node_id[:5], "UPDATE CENTER NODE SUBSCRIPTION TO", self.is_subscribed))
            self.center_node_is_subscribed = self.is_subscribed
        elif self.center_node_id is None or self.center_node_is_subscribed < self.is_subscribed:
            #sys.stderr.write("%s %s\n" % (self.node.node_id[:5], "CHANGE CENTER NODE TO SELFT"))
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

    @classmethod
    def get_by_query(cls, q=None, node_id = None, document_id=None):
        ands = []
        if node_id is not None:
            ands.append(query.Owner(node_id))
        if document_id is not None:
            ands.append(query.Id(document_id))

        if ands:
            ands = query.And(*ands)
        if q:
            q = query.Query(q)

        if q and ands:
            q = query.Pipe(ands, q)
        elif ands:
            q = ands

        stmt = q.compile()
        sql = stmt.compile()
        #print "SQL", sql.sql
        #print "VARS", sql.vars
        return cls.objects.raw(sql.sql, sql.vars)


class PeerDocumentSubscription(BaseDocumentSubscription):
    # This is what a peer knows about us, as well as what we know about them

    class Meta:
        unique_together = (("local_subscription", "peer"),)

    local_subscription = django.db.models.ForeignKey(DocumentSubscription, related_name="peer_subscriptions")
    peer = django.db.models.ForeignKey(cliqueclique_node.models.Peer, related_name="subscriptions")

    local_serial = django.db.models.IntegerField(default = -1)
    local_resend_interval = django.db.models.FloatField(blank=True, null=True)
    local_resend_time = django.db.models.FloatField(default = 0)
    peer_send = django.db.models.BooleanField(default = True)

    has_copy = django.db.models.BooleanField(default = False)
    has_enought_peers = django.db.models.BooleanField(default=False)
    is_wanted = django.db.models.BooleanField(default = True)
    is_subscribed = django.db.models.BooleanField(default = False)

    old_wanters = django.db.models.IntegerField(default = 0)
    old_subscribers = django.db.models.IntegerField(default = 0)
 
    @classmethod
    def get_peer_subscription(cls, peer, document_id, only_existing_sub = False, content = None):
        if only_existing_sub: content = None
        is_new, local_sub = DocumentSubscription.get_subscription(peer.local, document_id, content)

        subs = PeerDocumentSubscription.objects.filter(
            local_subscription = local_sub,
            peer = peer).all()
        if subs:
            sub = subs[0]
        else:
            if only_existing_sub:
                raise Exception("Got asked about a peer subscription for %s for the peer %s that doesn't subscribe to that!" % (document_id, peer.node_id))
            sub = PeerDocumentSubscription(
                local_subscription = local_sub,
                peer = peer)
            sub.save()
            is_new = True
            
        return is_new, sub
    
    def format_to_dict(self):
        return {
            'local_subscription': repr(self.local_subscription),
            'peer_id': self.peer.node_id[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH],

            'center_node_is_subscribed': self.center_node_is_subscribed,
            'center_node_id': self.center_node_id,
            'center_distance': self.center_distance,
            'serial': self.serial,

            'local_serial': self.local_serial,
            'local_resend_interval': self.local_resend_interval,
            'local_resend_time': self.local_resend_time,
            'peer_send': self.peer_send,

            'has_copy': self.has_copy,
            'has_enought_peers': self.has_enought_peers,
            'is_wanted': self.is_wanted,
            'is_subscribed': self.is_subscribed,

            'wanters': format_change(self.wanters, self.old_wanters),
            'subscribers': format_change(self.subscribers, self.old_subscribers),
            }

    def __repr__(self):
        return """%(local_subscription)s

    %(peer_id)s

    Center node is subscribed: %(center_node_is_subscribed)s
    Center node id: %(center_node_id)s
    Center distance: %(center_distance)s
    Serial: %(serial)s

    Local serial: %(local_serial)s
    Local resend interval: %(local_resend_interval)s
    Local resend time: %(local_resend_time)s
    Peer send: %(peer_send)s

    Has copy: %(has_copy)s
    Has enought peers: %(has_enought_peers)s
    Is wanted: %(is_wanted)s
    Is subscribed: %(is_subscribed)s

    Wanters: %(wanters)s
    Subscribers: %(subscribers)s
""" % self.format_to_dict()

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
                child.ensure_peer_subscription(self.peer)

    @classmethod
    def on_pre_save(cls, sender, instance, **kwargs):
        self = instance
        self.was_new = self.id is None
        
        self.update_child_subscriptions()
        self.local_subscription.update_center_from_upstream_peer(self)
        self.local_subscription.update_subscription_from_downstream_peer(self)

    @classmethod
    def on_post_save(cls, sender, instance, **kwargs):
        if instance.was_new:
            instance.local_subscription.update_peer_nrs(1)

    @classmethod
    def on_post_delete(cls, sender, instance, **kwargs):
        self = instance
        self.local_subscription.update_peer_nrs(-1)

        sys.stderr.write("DELETING PEER SUBSCRIPTION\n")
        if not instance.local_subscription.is_wanted:
            sys.stderr.write("    DELETING SUBSCRIPTION\n")
            instance.local_subscription.delete()

    @classmethod
    def deserialize_update(cls, update):
        res = {}
        res['has_enought_peers'] = update['has_enought_peers'].lower() == 'true'
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
            if self.local_subscription.is_wanted:
                self.has_copy = True
                self.save()
            else:
                self.delete()

    def receive(self, update):
        if update['message_type'] == 'subscription_update':
            self.receive_update(update)
        elif update['message_type'] == 'subscription_ack':
            self.receive_ack(update)
        else:
            assert False

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

    def send_peer_suggestion(self):
        def get_offsetslice(lst, offset, count):
            lstlen = len(lst)
            offset = offset % lstlen
            return lst[offset:min(offset+count,lstlen)] + lst[:max(offset+count-lstlen, 0)]

        msgs = []
        if not self.has_enought_peers: # and not self.is_upstream():
            peer_subs = self.local_subscription.peer_subscriptions.filter(~Q(peer__node_id=self.peer.node_id)).order_by('?').all()[0:1]

            for peer_sub in peer_subs:
                msg = email.mime.text.MIMEText(utils.smime.der2pem(peer_sub.peer.public_key))
                msg.add_header('message_type', 'peer_suggestion')
                msg.add_header('document_id', self.local_subscription.document.document_id)
                msgs.append(msg)
        return msgs

    def send(self, export = False):
        return self.send_update(export) + self.send_ack() + self.send_peer_suggestion()

    def __unicode__(self):
        return "%s:s knowledge about %s" % (self.peer, self.local_subscription)

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(DocumentSubscription)
def conv(self, obj):
    return {'__cliqueclique_subscription_models_DocumentSubscription__': True,

            "center_node_is_subscribed": obj.center_node_is_subscribed,
            "center_node_id": obj.center_node_id,
            "center_distance": obj.center_distance,
            "serial": obj.serial,

            "node": obj.node.node_id,
            "document": obj.document,

            "read": obj.read,
            "bookmarked": obj.bookmarked,
            "local_is_subscribed": obj.local_is_subscribed,

            "parents": [parent.document.document_id for parent in obj.parents.all()],
            "children": [child.document.document_id for child in obj.children.all()],

            "peer_nrs": obj.peer_nrs,
            "wanters": obj.wanters,
            "subscribed_parents": obj.subscribed_parents,

            "subscribers": obj.subscribers,

            "old_has_enought_peers": obj.old_has_enought_peers,
            "old_is_wanted": obj.old_is_wanted,
            "old_is_subscribed": obj.old_is_subscribed,
            "old_center_node_is_subscribed": obj.old_center_node_is_subscribed,
            "old_center_node_id": obj.old_center_node_id,
            "old_center_distance": obj.old_center_distance
            }
