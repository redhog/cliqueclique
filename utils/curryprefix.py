class curryprefix(object):
    def __init__(self, obj, prefix):
        self.obj = obj
        self.prefix = prefix

    def __getattr__(self, name):
        return getattr(self.obj, self.prefix + name)
