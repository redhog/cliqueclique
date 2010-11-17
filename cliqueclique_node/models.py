import django.db.models
import django.contrib.auth.models
from django.db.models import Q
import utils.modelhelpers
import settings

class Node(django.db.models.Model):
    node_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH)
    public_key = django.db.models.TextField()
    address = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_ADDRESS_LENGTH)

class LocalNode(Node):
    private_key = django.db.models.TextField()

class Peer(Node):
    node = django.db.models.ForeignKey(LocalNode, related_name="peers")
