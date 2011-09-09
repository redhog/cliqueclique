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
import cliqueclique_mime.models

class Document(fcdjangoutils.signalautoconnectmodel.SharedMemorySignalAutoConnectModel):
    document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, unique=True, blank=True)
    parent_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    child_document_id = django.db.models.CharField(max_length=settings.CLIQUECLIQUE_HASH_LENGTH, null=True, blank=True)
    content = django.db.models.ForeignKey(cliqueclique_mime.models.Mime, related_name="is_document", null=False)

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
            mime = cliqueclique_mime.models.Mime(content = content)
            mime.save()
            doc = Document(content = mime)
            doc.save()
            is_new = True
        return is_new, doc

    @classmethod
    def on_pre_save(cls, sender, instance, **kwargs):
        # Generate id from content
        if not instance.document_id:
            instance.document_id = instance.document_id_from_content(instance.content.content)
        else:
            if not instance.document_id == instance.document_id_from_content(instance.content.content):
                raise Exception("Document has id %s but should have %s" % (repr(instance.document_id), repr(instance.document_id_from_content(instance.content.content))))

        # Grep out any document pointers and store them separately for easy access
        mime = instance.content.content_as_mime

        instance.parent_document_id = mime['parent_document_id']
        instance.child_document_id = mime['child_document_id']

    # These mirror the methods on Document objects in JavaScript...
    @property
    def parts(self):
        content = this.content.content_as_mime
        parts = {}
        for part in content.get_payload():
            parts[part['part_type']] = part;
        return parts

    @property
    def subject(self):
      content = this.content.content_as_mime
      try:
          return content['subject']
      except KeyError:
          return this.document_id[:5]

    @property
    def body(self):
        parts = this.parts
        try:
            return parts['content'].get_payload();
        except:
            return this.content.content_as_mime.get_payload()
        
    def __unicode__(self):
        subject = unicode(self.content)
        return "%s [%s..]" % (subject, self.document_id[:10])


@fcdjangoutils.jsonview.JsonEncodeRegistry.register(Document)
def conv(self, obj):
    return {'__cliqueclique_document_models_Document__': True,
            'document_id': obj.document_id,
            'parent_document_id': obj.parent_document_id,
            'child_document_id': obj.child_document_id,
            'content': obj.content.as_mime}

# @fcdjangoutils.jsonview.JsonDecodeRegistry.register('__cliqueclique_document_models_Document__')
# def conv(self, obj):
#     if 'document_id' in obj:
#         return Document.objects.get(document_id = obj['document_id'])
#     else:
#         content = obj['content']
#         if hasattr(content, "as_string"):
#             content = content.as_string()
#         res = Document(content = content)
#         res.save()
#     return res

# @fcdjangoutils.jsonview.JsonDecodeRegistry.register('__cliqueclique_document_models_DocumentId__')
# def conv(self, obj):
#     return obj['document'].document_id
