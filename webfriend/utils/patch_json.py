""" Module that monkey-patches json module when it's imported so
JSONEncoder.default() automatically checks for a special "to_json()"
method and uses it to encode the object if found.
"""
from json import JSONEncoder


def _default(self, obj):
    if hasattr(obj.__class__, 'to_json'):
        return obj.to_json()
    else:
        try:
            _default.default(obj)
        except TypeError:
            return obj.__repr__()
        except UnicodeEncodeError:
            return obj.__repr__()


_default.default = JSONEncoder().default  # Save unmodified default.
JSONEncoder.default = _default            # replacement
