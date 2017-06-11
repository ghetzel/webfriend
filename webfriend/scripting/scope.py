from __future__ import absolute_import
from __future__ import unicode_literals


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
    SCALAR_TYPES = (basestring, int, float, bool)

    def __init__(self, data=None, parent=None):
        if parent and not isinstance(parent, Scope):
            raise ValueError("Parent scope must also be a Scope")

        self.parent = parent
        self.data   = (data or {})

    @property
    def level(self):
        lvl = 1

        if self.parent:
            lvl += self.parent.level

        return lvl

    @classmethod
    def split_key(cls, key):
        if isinstance(key, tuple):
            if not len(key):
                raise KeyError("Must specify an index value")

            return key[0], key
        else:
            parts = key.split('.')

            for i, part in enumerate(parts):
                if isinstance(part, str):
                    parts[i] = part.decode('UTF-8')

            return parts[0], parts

    def ancestors(self):
        out = []

        if self.parent:
            out += self.parent.ancestors()

        out.append(self)

        return out

    def owner_of(self, key):
        top_key, _ = self.split_key(key)

        # if the key exists, but is not ours...
        if top_key in self and not self.is_local(top_key):
            # and if we have a parent...
            if self.parent:
                # then let the parent deal with it
                return self.parent.owner_of(key)

        return self

    def as_dict(self):
        out = {}

        if self.parent:
            out.update(self.parent.as_dict())

        out.update(self.data)
        return out

    def items(self):
        return self.as_dict().items()

    def is_local(self, key):
        top_key, _ = self.split_key(key)

        if top_key in self.data:
            return True

        return False

    def get(self, key, fallback=None):
        try:
            return self[key]
        except KeyError:
            return fallback

    def set(self, key, value, force=False, unset=False):
        # only unset if the key exists
        if unset and key not in self:
            return

        top_key, parts = self.split_key(key)

        if isinstance(value, str):
            value = value.decode('UTF-8')

        # force means that we always make ourself the owner
        if force:
            owner = self
        else:
            owner = self.owner_of(key)

        base = owner.data

        for k in parts[:-1]:
            if k not in base:
                base[k] = {}
            elif not isinstance(base[k], dict):
                raise ValueError(
                    "Cannot set intermediate key '{}': key exists, but not a dict (is: {})".format(
                        k,
                        base[k].__class__.__name
                    )
                )

            base = base[k]

        if unset:
            if parts[-1] in base:
                del base[parts[-1]]
        else:
            base[parts[-1]] = value

    def unset(self, key, force=False):
        self.set(key, None, force=force, unset=True)

    def __getitem__(self, key):
        top_key, parts = self.split_key(key)

        try:
            base = self.data

            # try to traverse our local data and retrieve the value
            # if that fails at any point, make our parent do the same, on and on
            # until there are no parents left and we just raise the KeyError
            for k in parts:
                if isinstance(base, (list, tuple)):
                    try:
                        base = base[int(k)]
                    except ValueError as e:
                        if str(e).startswith('invalid literal for int'):
                            raise ValueError(
                                "Attempted to use non-numeric value '{}' to access an array element".format(k)
                            )
                        else:
                            raise

                elif hasattr(base, '__getitem__') and not isinstance(base, self.SCALAR_TYPES):
                    base = base[k]

                elif isinstance(base, object) and hasattr(base, str(k)):
                    base = getattr(base, str(k))

                else:
                    raise KeyError(
                        "Cannot access key '{}' on {} value".format(k, base.__class__.__name__)
                    )

            return base
        except KeyError:
            if self.parent:
                return self.parent[key]
            raise

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.unset(key)

    def __contains__(self, key):
        _, parts = self.split_key(key)

        # traverse our local data and make sure we have the given key
        try:
            base = self.data

            for k in parts[:-1]:
                base = base[k]

            if parts[-1] in base:
                return True

        except KeyError:
            pass

        # if we got to this point, try our parent
        if self.parent:
            if key in self.parent:
                return True

        return False

    def __str__(self):
        return 'Scope<level={},variables={}>'.format(
            self.level,
            len(self.data)
        )
