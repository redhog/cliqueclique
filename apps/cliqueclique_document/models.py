import django.db.models
import idmapper.models
import django.contrib.auth.models
from django.db.models import Q
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

        mime = instance.as_mime

        properties = {}
        if mime.get_content_type() == 'multipart/signed':
            cert = mime.verify()[0]
            mime = mime.get_payload()[0]

            data = utils.smime.cert_get_data(cert)
            properties[':signature'] = cliqueclique_node.models.Node.node_id_from_public_key(cert)
            properties[':signature_name'] = data['name']
            properties[':signature_address'] = data['address']

        def properties_from_mime(mime, prefix = '/0'):
            for key, value in mime.items():
                properties[prefix + ':' + key.lower()] = value
                if mime.get_content_maintype() == 'multipart':
                    for idx, part in enumerate(mime.get_payload()):
                        properties_from_mime(part, "%s/%s" % (prefix, ix))
    
        properties_from_mime(mime)

        for property in DocumentProperty.objects.filter(document = instance).all():
            property.delete()

        for key, value in properties.iteritems():
            doc = DocumentProperty(document=instance, key=key, value=value)
            doc.save()

    def __unicode__(self):
        try:
            subject = self.as_mime['subject']
        except:
            subject = None
        if not subject:
            subject = self.content[:10] + ".."
        return "%s [%s..]" % (subject, self.document_id[:10])

class DocumentProperty(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    document = django.db.models.ForeignKey(Document, related_name="properties")
    key = django.db.models.TextField()
    value = django.db.models.TextField()

    class Meta:
        unique_together = (("document", "key",),)
