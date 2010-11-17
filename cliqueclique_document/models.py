import django.db.models
import django.contrib.auth.models
from django.db.models import Q
import utils.modelhelpers
import settings

class Document(django.db.models.Model):
    document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH)
    parent_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    child_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    content = django.db.models.TextField()
