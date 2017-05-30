from __future__ import absolute_import


class Scope(object):
    """
    A Scope is an object that allows for a split view of keys that are readable from all associated
    parent scopes, but only settable locally.

    This means that when retrieving values, a
    non-existent key will propagate the get up to the scope's parent, and so on until a value is
    found or a scope without a parent throws a KeyError.

    Setting values, on the other hand, are always set locally and only locally.  Taken together,
    these two behaviors form a hierarchical data structure in which children can override the values
    of their parents without modifying the parent.

    This is used to track the state of variables at various levels during the execution of commands,
    event handlers, and routine definitions during script evaluation.

    Args:
        data (dict, optional):
            The initial data, if any, to populate the Scope with.

        parent (Scope, optional):
            The parent scope, if any, to inherit values from.
    """

    def __init__(self, data=None, parent=None):
        if parent and not isinstance(parent, Scope):
            raise ValueError("Parent scope must also be a Scope")

        self.parent = parent
        self.data   = (data or {})

    def ancestors(self):
        out = []

        if self.parent:
            out += self.parent.ancestors()

        out.append(self)

        return out

    def as_dict(self):
        out = {}

        if self.parent:
            out.update(self.parent.as_dict())

        out.update(self.data)
        return out

    def items(self):
        return self.as_dict().items()

    def is_local(self, key):
        if key in self.data:
            return True

        return False

    def get(self, key, fallback=None):
        try:
            return self[key]
        except KeyError:
            return fallback

    def set(self, key, value):
        self[key] = value

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            if self.parent:
                return self.parent[key]
            raise

    def __setitem__(self, key, value):
        if isinstance(value, str):
            value = value.decode('UTF-8')

        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __contains__(self, key):
        if key in self.data:
            return True

        if self.parent:
            if key in self.parent:
                return True

        return False
