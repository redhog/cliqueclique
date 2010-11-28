import django.db.models
import idmapper.models
import base64

class SignalAutoConnectMeta(idmapper.models.SharedMemoryModel.__metaclass__):
    def __init__(cls, *arg, **kw):
        idmapper.models.SharedMemoryModel.__metaclass__.__init__(cls, *arg, **kw)
        if not hasattr(cls, 'Meta') or not getattr(cls.Meta, 'abstract', False):
            for signame in ("pre_save", "post_save"):
                if hasattr(cls, signame):
                    getattr(django.db.models.signals, signame).connect(getattr(cls, signame), sender=cls)

class Base64Field(django.db.models.TextField):
    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name + '_base64'
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return base64.decodestring(getattr(obj, self.field_name))

    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.encodestring(data))
