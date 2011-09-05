import django.db.models
import idmapper.models
import django.contrib.auth.models
from django.db.models import Q, F
import fcdjangoutils.signalautoconnectmodel
import fcdjangoutils.jsonview
import settings
import email
import email.mime.message
import email.mime.application
import email.mime.text
import email.mime.multipart
import utils.smime
import hashlib
import utils

class Mime(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    content = django.db.models.TextField()

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
    def on_post_save(cls, sender, instance, **kwargs):
        import cliqueclique_node.models

        for part in instance.parts.all():
            part.delete()

        mime = instance.as_mime

        part = MimePart(mime = instance, idx = 0)
        part.save()

        if mime.get_content_type() == 'multipart/signed':
            cert = mime.verify()[0]
            mime = mime.get_payload()[0]

            data = utils.smime.cert_get_data(cert)
            MimeHeader(part = part, key = 'node_id', value = cliqueclique_node.models.Node.node_id_from_public_key(cert)).save()
            MimeHeader(part = part, key = 'name', value = data['name']).save()
            MimeHeader(part = part, key = 'address', value = data['address']).save()

        def properties_from_mime(parent, idx, mime):
            part = MimePart(parent = parent, idx = idx)
            part.save()

            for key, value in mime.items():
                MimeHeader(part = part, key = key.lower(), value = value).save()

            if mime.get_content_maintype() == 'multipart':
                for idx, part_mime in enumerate(mime.get_payload()):
                    properties_from_mime(part, idx, part_mime)
    
        properties_from_mime(part, 0, mime)
        
    def __unicode__(self):
        try:
            subject = self.as_mime['subject']
        except:
            subject = None
        if subject:
            return subject
        return self.content[:10] + ".."


# Helper structure to organize the properties
class MimePart(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    mime = django.db.models.ForeignKey(Mime, related_name="parts", null=True)
    parent = django.db.models.ForeignKey('MimePart', related_name="parts", null=True)
    idx = django.db.models.IntegerField() # Index in get_payload() list.

    def repr(self, ind=''):
        properties = ind + ('\n'+ ind).join(repr(p) for p in self.properties.all()) + '\n'
        parts = '\n'.join(part.repr(ind+'  ') for part in self.parts.order_by('idx').all())
        return ind + 'Part: %s\n'%self.idx + properties + '\n' + parts

    def __repr__(self):
        return self.repr()

class MimeHeader(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    part = django.db.models.ForeignKey(MimePart, related_name="properties")
    key = django.db.models.TextField()
    value = django.db.models.TextField()

    class Meta:
        unique_together = (("part", "key",),)

    def __repr__(self):
        return "%s=%s" % (self.key, repr(self.value))
