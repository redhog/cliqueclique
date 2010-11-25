import django.db.models
import idmapper.models
import django.contrib.auth.models
from django.db.models import Q
import utils.modelhelpers
import settings

class Node(idmapper.models.SharedMemoryModel):
    node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH)
    public_key = django.db.models.TextField()
    address = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_ADDRESS_LENGTH)

class LocalNode(Node):
    owner = django.db.models.OneToOneField(django.contrib.auth.models.User, related_name="node", blank=True, null=True)
    private_key = django.db.models.TextField()

class Peer(Node):
    local = django.db.models.ForeignKey(LocalNode, related_name="peers")

    @property
    def updates(self):
        self.subscriptions.filter(is_dirty=True)

    @property
    def new(self):
        self.subscriptions.filter(has_copy=False)

    def get_updates_as_mime(self):
        return ([sub.send() for sub in self.updates.all()] +
                [sub.local_subscription.document.as_mime for sub in self.new.all()])
        

