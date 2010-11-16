import django.db.models
import django.contrib.auth.models
from django.db.models import Q

ADDRESS_LENGTH = 512
HASH_LENGTH = 512

class SignalAutoConnectMeta(django.db.models.Model.__metaclass__):
    def __init__(cls, *arg, **kw):
        django.db.models.Model.__metaclass__.__init__(cls, *arg, **kw)
        if not getattr(cls.Meta, 'abstract', False):
            for signame in ("pre_save", "post_save"):
                if hasattr(cls, signame):
                    getattr(django.db.models.signals, signame).connect(getattr(cls, signame), sender=cls)


class Node(django.db.models.Model):
    node_id = django.db.models.CharField(max_length=HASH_LENGTH)
    public_key = django.db.models.TextField()
    address = django.db.models.CharField(max_length=ADDRESS_LENGTH)

class LocalNode(Node):
    private_key = django.db.models.TextField()

class Peer(Node):
    pass

class Document(django.db.models.Model):
    document_id = django.db.models.CharField(max_length=HASH_LENGTH)
    up_document_id = django.db.models.CharField(max_length=HASH_LENGTH)
    down_document_id = django.db.models.CharField(max_length=HASH_LENGTH)
    content = django.db.models.TextField()

class BaseDocumentSubscription(django.db.models.Model):
    class Meta:
        abstract = True

    __metaclass__ = SignalAutoConnectMeta

    node = django.db.models.ForeignKey(LocalNode, related_name="subscriptions")

    is_subscribed = django.db.models.BooleanField()
    center_node_is_subscribed = django.db.models.BooleanField()
    center_node_id = django.db.models.CharField(max_length=HASH_LENGTH)
    center_distance = django.db.models.IntegerField()


class LowerDocumentSubscriptionManager(models.Manager):
    def get_query_set(self):
        return models.Manager.get_query_set(self).

class DocumentSubscription(BaseDocumentSubscription):
    document = django.db.models.ForeignKey(Document, related_name="subscriptions")

    # Note, these might be NULL if no document with self.document.{up,down}_document_id
    # exists at this node yet
    up = django.db.models.ForeignKey(DocumentSubscription, related_name="down_from", null=True, blank=True)
    down = django.db.models.ForeignKey(DocumentSubscription, related_name="up_from", null=True, blank=True)

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        for peer_subscription in instance.peer_subscriptions:
            peer_subscription.update_down_subscriptions()
            peer_subscription.set_dirty()

    def peer_subscription(self, peer):
        try:
            return DocumentSubscription.objects.get(local_subscription=self, peer=peer) 
        except:
            return None

class PeerDocumentSubscription(DocumentSubscription):
    # This is what a peer knows about us, as well as what we know about them

    local_subscription = django.db.models.ForeignKey(DocumentSubscription, related_name="peer_subscriptions")
    peer = django.db.models.ForeignKey(Peer, related_name="subscriptions")

    is_dirty = django.db.models.BooleanField()

    peer_is_subscribed = django.db.models.BooleanField()
    peer_center_node_is_subscribed = django.db.models.BooleanField()
    peer_center_node_id = django.db.models.CharField(max_length=HASH_LENGTH)
    peer_center_distance = django.db.models.IntegerField()

    def update_down_subscriptions(self):
        if self.peer_is_subscribed:
            def update_down_subscriptions(down):
                if not down.peer_subscription(self.peer):
                    PeerDocumentSubscription(local_subscription=down, peer=self.peer, is_dirty=True).save()
            
            update_down_subscriptions(self.local_subscription.down)
            for down in self.local_subscription.down_from.all():
                update_down_subscriptions(down)


    def set_dirty(self):
        for attr in ('is_subscribed',
                     'center_node_is_subscribed',
                     'center_node_id',
                     'center_distance'):
            if self.attr != self.local_subscription.attr:
                self.is_dirty = True
                self.save()
                return

    def is_upstream(self, is_this_much_closer = 0):
        return (   self.local_subscription.center_node_id < self.peer_center_node_id
                   self.local_subscription.center_node_is_subscribed < self.peer_center_node_is_subscribed
                or (    self.local_subscription.center_node_id == self.peer_center_node_id
                    and self.local_subscription.center_distance > self.peer_center_distance + is_this_much_closer))

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        if not instance.is_dirty and instance.is_upstream(1):
            self.local_subscription._is_subscribed = self.peer_is_subscribed
            self.local_subscription._center_node_is_subscribed = self.peer_center_node_is_subscribed
            self.local_subscription.center_node_id = self.peer_center_node_id
            self.local_subscription.center_distance = self.peer_center_distance + 1
            self.local_subscription.save()
