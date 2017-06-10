from __future__ import absolute_import
from webfriend.scripting.commands.base import CommandProxy


class StateProxy(CommandProxy):
    qualifier = 'vars'

    def interpolate(self, value, **kwargs):
        return super(self).interpolate(value, **kwargs)

    def scope_at_level(self, level=0):
        if not level:
            return self.scope
        else:
            if level is True:
                level = 1

            ancestors = self.scope.ancestors()
            index = len(ancestors) + (-1 * (level + 1))

            if index < 0:
                index = 0

            return ancestors[index]

    def get(self, key, fallback=None, parent=0):
        return self.scope_at_level(parent).get(key, fallback)

    def set(self, key, value, interpolate=True, parent=0):
        if interpolate is True:
            value = self.interpolate(value)

        self.scope_at_level(parent)[key] = value
        return value

    def clear(self, key, parent=0):
        scope = self.scope_at_level(parent)

        if key in scope:
            del scope[key]
            return True

        return False

    def push(self, key, value, interpolate=True, parent=0):
        scope = self.scope_at_level(parent)

        if key not in scope:
            scope[key] = []

        if not isinstance(scope[key], list):
            scope[key] = [scope[key]]

        if interpolate is True:
            value = self.interpolate(value)

        scope[key].append(value)
        return value

    def pop(self, key, parent=0):
        scope = self.scope_at_level(parent)

        if key in scope:
            if isinstance(scope[key], list):
                try:
                    return scope[key].pop()
                except IndexError:
                    pass

        return None

    def ensure(self, key, parent=0, message=None):
        if message is None:
            message = '{key} must be specified.'

        try:
            scope = self.scope_at_level(parent)
            return scope[key]
        except KeyError:
            raise KeyError(message.format(**{
                'key':   key,
                'scope': scope,
            }))
