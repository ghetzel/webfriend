from __future__ import absolute_import
from __future__ import unicode_literals
from webfriend.scripting.commands.base import CommandProxy
from webfriend.scripting.scope import Scope


class StateProxy(CommandProxy):
    qualifier = 'vars'

    def default(self, parent=0):
        """
        Return a list of variable names that are defined in a scope.

        #### Arguments

        - **parent** (`int`, optional):

            If non-zero, specifies how many levels up to insepect relative to the current scope.
            This is used to query and manipulate scopes above our own.

        #### Returns
        A list of zero of more strings, one for each variable name.
        """
        return self._scope_at_level(parent).as_dict().keys()

    def interpolate(self, format, isolated=False, values=None):
        """
        Return a value interpolated with values from a scope or ones that are explicitly provided.

        #### Arguments

        - **format** (`str`):

            The format string to interpolate.

        - **isolated** (`bool`):

            If true, the calling scope will not be used to interpolate values.

        - **values** (`dict`, optional):

            If specified, these values will override the scope's values (if any) and be available
            to **format** during interpolation.

        #### Returns
        An autotyped value resulting from interpolating the given **format**.
        """
        if isolated:
            scope = Scope()
        else:
            scope = Scope(parent=self.scope)

        if isinstance(values, dict):
            for k, v in values.items():
                scope[k] = v

        return super(self).environment.interpolate(format, scope=scope)

    def get(self, key, fallback=None, parent=0):
        """
        Return the value of a specific variable defined in a scope.

        #### Arguments

        - **key** (`str`):

            The name of the variable to retrieve.

        - **fallback** (`bool`, optional):

            A value to return if the variable was not found.

        - **parent** (`int`, optional):

            If non-zero, specifies how many levels up to insepect relative to the current scope.
            This is used to query and manipulate scopes above our own.

        #### Returns
        The value of the named variable, or **fallback** if the value was not found.
        """
        return self._scope_at_level(parent).get(key, fallback)

    def set(self, key, value, interpolate=True, parent=0):
        if interpolate is True:
            value = self.interpolate(value)

        self._scope_at_level(parent)[key] = value
        return value

    def clear(self, key, parent=0):
        scope = self._scope_at_level(parent)

        if key in scope:
            del scope[key]
            return True

        return False

    def push(self, key, value, interpolate=True, parent=0):
        scope = self._scope_at_level(parent)

        if key not in scope:
            scope[key] = []

        if not isinstance(scope[key], list):
            scope[key] = [scope[key]]

        if interpolate is True:
            value = self.interpolate(value)

        scope[key].append(value)
        return value

    def pop(self, key, parent=0):
        scope = self._scope_at_level(parent)

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
            scope = self._scope_at_level(parent)
            return scope[key]
        except KeyError:
            raise KeyError(message.format(**{
                'key':   key,
                'scope': scope,
            }))

    def _scope_at_level(self, level=0):
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
