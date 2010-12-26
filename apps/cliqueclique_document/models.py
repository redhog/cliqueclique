import django.db.models
import idmapper.models
import django.contrib.auth.models
from django.db.models import Q, F
import fcdjangoutils.signalautoconnectmodel
import settings
import email
import email.mime.message
import email.mime.application
import email.mime.text
import email.mime.multipart
import hashlib
import utils

class Document(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, unique=True, blank=True)
    parent_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    child_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    content = django.db.models.TextField()

    @classmethod
    def document_id_from_content(cls, content):
        return utils.hash.has_id_from_data(content)

    @classmethod
    def get_document(cls, document_id, content = None):
        is_new = False
        docs = Document.objects.filter(
            document_id = document_id).all()
        if docs:
            doc = docs[0]
        else:
            if content is None:
                raise Exception("Unable to create new document %s without any content" % (document_id,))
            doc = Document(content = content)
            doc.save()
            is_new = True
        return is_new, doc

    @property
    def as_mime(self):
        return email.message_from_string(str(self.content))

    @property
    def content_as_mime(self):
        mime = self.as_mime
        if mime.get_content_type() == 'multipart/signed':
            mime = mime.get_payload()[0]
        return mime

    @classmethod
    def on_pre_save(cls, sender, instance, **kwargs):
        # Generate id from content
        instance.document_id = instance.document_id_from_content(instance.content)

        # Grep out any document pointers and store them separately for easy access
        mime = instance.content_as_mime

        instance.parent_document_id = mime['parent_document_id']
        instance.child_document_id = mime['child_document_id']

    @classmethod
    def on_post_save(cls, sender, instance, **kwargs):
        import cliqueclique_node.models

        for part in instance.parts.all():
            part.delete()

        mime = instance.as_mime

        part = DocumentPart(document = instance, idx = 0)
        part.save()

        if mime.get_content_type() == 'multipart/signed':
            cert = mime.verify()[0]
            mime = mime.get_payload()[0]

            data = utils.smime.cert_get_data(cert)
            DocumentProperty(part = part, key = 'node_id', value = cliqueclique_node.models.Node.node_id_from_public_key(cert)).save()
            DocumentProperty(part = part, key = 'name', value = data['name']).save()
            DocumentProperty(part = part, key = 'address', value = data['address']).save()

        def properties_from_mime(parent, idx, mime):
            part = DocumentPart(parent = parent, idx = idx)
            part.save()

            for key, value in mime.items():
                DocumentProperty(part = part, key = key.lower(), value = value).save()

            if mime.get_content_maintype() == 'multipart':
                for idx, part_mime in enumerate(mime.get_payload()):
                    properties_from_mime(part, idx, part_mime)
    
        properties_from_mime(part, 0, mime)
        
    def __unicode__(self):
        try:
            subject = self.as_mime['subject']
        except:
            subject = None
        if not subject:
            subject = self.content[:10] + ".."
        return "%s [%s..]" % (subject, self.document_id[:10])

# Helper structure to organize the properties
class DocumentPart(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    document = django.db.models.ForeignKey(Document, related_name="parts", null=True)
    parent = django.db.models.ForeignKey('DocumentPart', related_name="parts", null=True)
    idx = django.db.models.IntegerField() # Index in get_payload() list.

class DocumentProperty(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    part = django.db.models.ForeignKey(DocumentPart, related_name="properties")
    key = django.db.models.TextField()
    value = django.db.models.TextField()

    class Meta:
        unique_together = (("part", "key",),)
