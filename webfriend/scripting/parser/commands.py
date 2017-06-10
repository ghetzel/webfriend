from __future__ import absolute_import
from webfriend.scripting.parser import MetaModel


class CommandStanza(object):
    def __init__(self, parent, options):
        self.parent     = parent
        self.options    = (options or {})

    def as_dict(self):
        out = {}

        for kv in self.options:
            if not len(kv.values):
                continue

            if len(kv.values) == 1:
                out[kv.name] = kv.values[0]
            else:
                out[kv.name] = kv.values

        return out


class CommandSequence(MetaModel):
    pass
