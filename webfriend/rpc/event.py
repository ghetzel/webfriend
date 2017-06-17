from __future__ import absolute_import


class Event(object):
    nested_joiner = '.'

    def __init__(self, rpc, event, payload=None):
        self.rpc     = rpc
        self.event   = '{}.{}'.format(rpc.domain, event)
        self.payload = {}

        if isinstance(payload, dict):
            self.payload = payload

    def to_json(self):
        return {
            'event':   str(self),
            'payload': self.payload,
        }

    def get(self, key, fallback=None):
        parts = key.split(self.nested_joiner)

        for i, part in enumerate(parts):
            if isinstance(part, str):
                parts[i] = part.decode('UTF-8')

        base = self.payload

        for k in parts:
            if isinstance(base, (list, tuple)):
                try:
                    base = base[int(k)]
                    continue
                except ValueError:
                    return fallback

            # try to access key via the [] operator
            if isinstance(base, dict):
                try:
                    base = base[k]
                    continue
                except KeyError:
                    return fallback

        if base is None:
            return fallback

        return base

    def matches_criteria(self, criteria):
        print('match: {}'.format(criteria))

        for key, criterion in criteria.items():
            # regex matches
            if hasattr(criterion, 'match'):
                if criterion.match('{}'.format(self.get(key))):
                    continue
                else:
                    return False

            # exact matches
            if self.get(key) == criterion:
                continue
            else:
                return False

        return True

    def __getitem__(self, key):
        if key == '__payload__':
            return self.payload
        else:
            return self.get(key)

    def __contains__(self, key):
        if key == '__payload__':
            return True

        return (key in self.payload)

    def __repr__(self):
        return self.event

    def __str__(self):
        return self.__repr__()
