import django.db.models
import idmapper.models

class SignalAutoConnectMeta(idmapper.models.SharedMemoryModel.__metaclass__):
    def __init__(cls, *arg, **kw):
        idmapper.models.SharedMemoryModel.__metaclass__.__init__(cls, *arg, **kw)
        if not hasattr(cls, 'Meta') or not getattr(cls.Meta, 'abstract', False):
            for signame in ("pre_save", "post_save"):
                if hasattr(cls, signame):
                    getattr(django.db.models.signals, signame).connect(getattr(cls, signame), sender=cls)
