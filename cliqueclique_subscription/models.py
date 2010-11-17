import django.db.models
import django.contrib.auth.models
import utils.modelhelpers
import settings
import cliqueclique_node.models
import cliqueclique_document.models
from django.db.models import Q
from utils.curryprefix import curryprefix

class BaseDocumentSubscription(django.db.models.Model):
    class Meta:
        abstract = True

    __metaclass__ = utils.modelhelpers.SignalAutoConnectMeta

    node = django.db.models.ForeignKey(cliqueclique_node.models.LocalNode, related_name="subscriptions")

    center_node_is_subscribed = django.db.models.BooleanField()
    center_node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH)
    center_distance = django.db.models.IntegerField()

class DocumentSubscription(BaseDocumentSubscription):
    document = django.db.models.ForeignKey(cliqueclique_document.models.Document, related_name="subscriptions")

    # Note, this might be NULL if no document with self.document.{up,down}_document_id
    # exists at this node yet
    parent = django.db.models.ForeignKey("DocumentSubscription", related_name="children", null=True, blank=True)

    # Did _we_ subscribe to this?
    local_is_subscribed = django.db.models.BooleanField()
    subscribers = django.db.models.SmallIntegerField()

    @property
    def is_subscribed(self): return self.subscribers > 0

    def peer_subscription(self, peer):
        try:
            return DocumentSubscription.objects.get(local_subscription=self, peer=peer) 
        except:
            return None

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        for peer_subscription in instance.peer_subscriptions:
            peer_subscription.update_child_subscriptions()
            peer_subscription.set_dirty()


class PeerDocumentSubscription(DocumentSubscription):
    # This is what a peer knows about us, as well as what we know about them

    local_subscription = django.db.models.ForeignKey(DocumentSubscription, related_name="peer_subscriptions")
    peer = django.db.models.ForeignKey(cliqueclique_node.models.Peer, related_name="subscriptions")

    is_dirty = django.db.models.BooleanField()

    is_subscribed = django.db.models.BooleanField()
 
    peer_old_is_subscribed = django.db.models.BooleanField() # Don't modify this by hand, it's just for internal use by the pre_save method
    peer_is_subscribed = django.db.models.BooleanField()
    peer_center_node_is_subscribed = django.db.models.BooleanField()
    peer_center_node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH)
    peer_center_distance = django.db.models.IntegerField()

    @property
    def subscribers(self): return [0, 1][self.is_subscribed]
    @property
    def peer_old_subscribers(self): return [0, 1][self.peer_old_is_subscribed]
    @property
    def peer_subscribers(self): return [0, 1][self.peer_is_subscribed]

    @classmethod
    def _compare(a, b, is_this_much_closer = 0):
        return (   a.center_node_id < b.center_node_id
                or a.center_node_is_subscribed < b.center_node_is_subscribed
                or (    a.center_node_id == b.center_node_id
                    and a.center_distance > b.center_distance + is_this_much_closer))

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
        for attr in ('is_subscribed',
                     'center_node_is_subscribed',
                     'center_node_id',
                     'center_distance'):
            if self.attr != self.local_subscription.attr:
                self.is_dirty = True
                self.save()
                return

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        if not instance.is_dirty:
            if instance.is_upstream(1):
                local = instance.local_subscription
                peer = curryprefix(instance, "peer_")

                local.center_node_is_subscribed = peer.center_node_is_subscribed
                local.center_node_id = peer.center_node_id
                local.center_distance = peer.center_distance + 1
                local.save()

            elif instance.is_downstream(1):

                local = instance.local_subscription
                peer = curryprefix(instance, "peer_")

                if peer.subscribers != peer.old_subscribers:
                    local.subscribers += peer.subscribers - peer.old_subscribers
                    peer.old_is_subscribed = peer.is_subscribed
                    local.save()
                    instance.save()
