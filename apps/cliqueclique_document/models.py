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
import utils.smime
import hashlib
import utils

class Document(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, unique=True, blank=True)
    parent_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    child_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    content = django.db.models.TextField()

    @classmethod
    def document_id_from_content(cls, content):
        return utils.hash.hash_id_from_data(content)

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
            if type(content) not in (unicode, str):
                content = content.as_string()
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
        if not instance.document_id:
            instance.document_id = instance.document_id_from_content(instance.content)
        else:
            if not instance.document_id == instance.document_id_from_content(instance.content):
                raise Exception("Document has id %s but should have %s" % (repr(instance.document_id), repr(instance.document_id_from_content(instance.content))))

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

    def repr(self, ind=''):
        properties = ind + ('\n'+ ind).join(repr(p) for p in self.properties.all()) + '\n'
        parts = '\n'.join(part.repr(ind+'  ') for part in self.parts.order_by('idx').all())
        return ind + 'Part: %s\n'%self.idx + properties + '\n' + parts

    def __repr__(self):
        return self.repr()

class DocumentProperty(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    part = django.db.models.ForeignKey(DocumentPart, related_name="properties")
    key = django.db.models.TextField()
    value = django.db.models.TextField()

    class Meta:
        unique_together = (("part", "key",),)

    def __repr__(self):
        return "%s=%s" % (self.key, repr(self.value))


class NewDocument(Document):
    class Meta(object):
        abstract = True

    def __init__(self, node, *arg, **kw):
        Document.__init__(self, *arg, **kw)
        self.signed = utils.smime.MIMESigned()
        self.signed.set_private_key(utils.smime.der2pem(node.private_key, "PRIVATE KEY"))
        self.signed.set_cert(utils.smime.der2pem(node.public_key))

        self.container = email.mime.multipart.MIMEMultipart()
        self.signed.attach(self.container)
        self.parts = {}

    @classmethod
    def on_pre_save(cls, sender, instance, **kwargs):
        self.content = self.signed.as_string()
        Document.on_pre_save(sender, instance, **kwargs)

    def set_part(self, type_name='content', part = None):
        if type_name in self.parts:
            self.container.get_payload().remove(self.parts[type_name])
        if part is None:
            part = email.mime.multipart.MIMEMultipart()
        part.set_header('part_type', type_name)
        self.parts[type_name] = part
        self.container.attach(part)
        return part

    def _set_link(self, document_id, direction = "child", reversed = False):
        assert direction in ("parent", "child")

        self.container.set_header(direction + '_document_id', document_id)

        part = self.set_part(direction + "_link")
        part.add_header("link_direction", ["natural", "reversed"][reversed])
        return part

    def set_parent(self, document_id, reversed = False):
        return self._set_link(document_id, "parent", reversed)

    def set_child(self, document_id, reversed = False):
        return self._set_link(document_id, "child", reversed)

class NewLink(NewDocument):
    class Meta(object):
        abstract = True

    def set_link(self, reversed = False):
        part = self.set_part("link")
        part.add_header("link_direction", ["natural", "reversed"][reversed])
        return part
