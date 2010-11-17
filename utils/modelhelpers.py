import django.db.models

class SignalAutoConnectMeta(django.db.models.Model.__metaclass__):
    def __init__(cls, *arg, **kw):
        django.db.models.Model.__metaclass__.__init__(cls, *arg, **kw)
        if not getattr(cls.Meta, 'abstract', False):
            for signame in ("pre_save", "post_save"):
                if hasattr(cls, signame):
                    getattr(django.db.models.signals, signame).connect(getattr(cls, signame), sender=cls)
