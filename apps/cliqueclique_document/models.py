import django.db.models
import idmapper.models
import django.contrib.auth.models
from django.db.models import Q
import utils.modelhelpers
import settings
import email
import email.mime.message
import email.mime.application
import email.mime.text
import email.mime.multipart
import hashlib
import utils.modelhelpers

class Document(idmapper.models.SharedMemoryModel):
    __metaclass__ = utils.modelhelpers.SignalAutoConnectMeta

    document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH)
    parent_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    child_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    content = django.db.models.TextField()

    @property
    def as_mime(self):
        return email.message_from_string(str(self.content))

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        # Generate id from content
        h = hashlib.sha512()
        h.update(str(instance.content))
        instance.document_id = h.hexdigest()

        # Grep out any document pointers and store them separately for easy access
        mime = instance.as_mime
        instance.parent_document_id = mime['parent_document_id']
        instance.child_document_id = mime['child_document_id']

    def __unicode__(self):
        try:
            subject = self.as_mime['subject']
        except:
            subject = self.content[:10] + ".."
        return "%s [%s..]" % (subject, self.document_id[:10])
