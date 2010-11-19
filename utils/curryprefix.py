class curryprefix(object):
    def __init__(self, obj, prefix):
        self.__dict__['obj'] = obj
        self.__dict__['prefix'] = prefix

    def __getattr__(self, name):
        return getattr(self.obj, self.prefix + name)

    def __setattr__(self, name, value):
        return setattr(self.obj, self.prefix + name, value)
