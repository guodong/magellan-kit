def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@Singleton
class DataStore:
    def __init__(self):
        self.data = {}

    def init(self, args):
        for k, v in args.items():
            if v == 'map':
                self.data[k] = {'1': 's1:p1'}
            elif v == 'set':
                self.data[k] = []
            elif v == 'int':
                self.data[k] = 0

    def get(self, name):
        return self.data[name]

    def get_all(self):
        return self.data


class Map:
    def __init__(self):
        self.data = {}

    def set(self, key, val):
        self.data[key] = val

    def contains(self, key):
        return key in self.data
