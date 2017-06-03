from __future__ import absolute_import
from collections import OrderedDict
from . import MetaModel


class Array(MetaModel):
    pass


class String(MetaModel):
    pass


class Object(MetaModel):
    def __init__(self, parent, **kwargs):
        self.items = []
        self._data  = OrderedDict()

        super(Object, self).__init__(parent, **kwargs)

        for kv in self.items:
            if not len(kv.values):
                continue

            if len(kv.values) == 1:
                self._data[kv.name] = kv.values[0]
            else:
                self._data[kv.name] = kv.values

    def to_json(self):
        return self.as_dict()

    def as_dict(self):
        return self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]
