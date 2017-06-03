from __future__ import absolute_import
from .scope import Scope
from . import parser
import logging


class CommandProxy(object):
    qualifier = None

    def __init__(self, browser, commandset=None, scope=None):
        self.browser = browser
        self.commandset = commandset
        self.scope   = (scope or Scope())
        self._tab    = None

    @property
    def tab(self):
        if self._tab is None:
            return self.browser.default
        else:
            try:
                return self.browser.tabs[self._tab]
            except KeyError:
                raise KeyError("Could not retrieve unknown tab '{}'".format(self._tab))

    def __contains__(self, local_command_name):
        try:
            return callable(getattr(self, local_command_name))
        except AttributeError:
            pass

        return False

    def __getitem__(self, local_command_name):
        return getattr(self, local_command_name)

    @classmethod
    def get_command_names(cls):
        names = set()

        for name in dir(cls):
            # underscored items are not commands
            if name.startswith('_'):
                continue

            # methods inherited from CommandProxy are not commands
            if name in dir(CommandProxy):
                continue

            if callable(getattr(cls, name)):
                if len(cls.as_qualifier()):
                    if cls.as_qualifier() == CommandSet.default_qualifier:
                        names.add(name)
                    else:
                        names.add(cls.qualify(name))

        return names

    @classmethod
    def qualify(cls, name):
        return '{}::{}'.format(cls.as_qualifier(), name)

    @classmethod
    def as_qualifier(cls):
        if cls.qualifier is not None:
            return cls.qualifier

        return cls.__name__.split('.')[-1].replace('Proxy', '').lower()


class CommandSet(object):
    default_qualifier = 'core'
    default_result_key = 'result'

    def __init__(self, scope=None, proxies=None):
        self._scope = (scope or Scope())
        self.proxies = (proxies or {})
        self.script = None
        self._exec_options = {}
        self.sync_scopes()

    @property
    def scope(self):
        return self._scope

    def sync_scopes(self):
        for _, proxy in self.proxies.items():
            proxy.scope = self._scope

    def set_scope(self, scope):
        self._scope = scope
        self.sync_scopes()

    def get_command_names(self):
        names = []

        for _, proxy in self.proxies.items():
            names += proxy.get_command_names()

        # sort the list of by longest-to-shortest
        names.sort(key=len, reverse=True)

        return names

    def get_proxy_for_command(self, command):
        q_command = command.name.split('::', 1)

        if len(q_command) == 1:
            proxy_name = self.default_qualifier
            command_name = q_command[0]
        else:
            proxy_name = q_command[0]
            command_name = q_command[1]

        try:
            return self[proxy_name], command_name
        except KeyError:
            raise parser.exceptions.ScriptError("Unregistered qualifier '{}'".format(proxy_name))

    def has_execution_option(self, key):
        return key in self._exec_options

    def get_execution_option(self, key, fallback=None):
        return self._exec_options.get(key, fallback)

    def set_execution_option(self, key, value):
        self._exec_options[key] = value

    def clear_execution_option(self, key):
        try:
            del self._exec_options[key]
        except KeyError:
            pass

    def interpolate(self, value, **kwargs):
        scope = Scope(kwargs, self._scope)
        variables = scope.as_dict()
        value = parser.to_value(value, scope)

        if isinstance(value, list):
            # recurse into lists
            return [self.interpolate(v, **variables) for v in value]

        elif isinstance(value, dict):
            # recurse into dicts
            return dict([
                (k, self.interpolate(v, **variables)) for k, v in value.items()
            ])

        elif isinstance(value, basestring):
            # do the interpolation
            value = value.format(**variables)

        return value

    def execute(self, command, scope=None):
        if scope:
            # this here is why commands should not execute in parallel, because we're changing the scope
            # of the _entire_ commandset to the given scope for the duration of this call
            self.set_scope(scope)

        # get the proxy and proxy-local command name from the CommandSet
        proxy, command_name = self.get_proxy_for_command(command)

        # the proxy needs to know about the command
        if command_name in proxy:
            fn = proxy[command_name]

            # interpolate option values
            if command.options is not None:
                opts = command.options.as_dict()
            else:
                opts = {}

            try:
                # recursively interpolate all values in the stanza options list
                opts = self.interpolate(opts)

                command_id = command.id

                if command_id is not None:
                    if command_id.variable:
                        command_id = command_id.resolve(scope)
                    else:
                        # interpolate command ID
                        command_id = self.interpolate(command_id.value)

                # figure out where we want to store results
                if isinstance(command.resultkey, parser.variables.Variable):
                    resultkey = command.resultkey.name

                elif isinstance(command.resultkey, basestring) and len(command.resultkey):
                    resultkey = self.interpolate(command.resultkey)

                else:
                    resultkey = self.default_result_key

            except KeyError as e:
                raise parser.exceptions.ScriptError(
                    "Use of undefined variable '{}' in string pattern".format(
                        str(e).lstrip("u'").rstrip("'")
                    ),
                    model=command
                )

            # call function
            logging.debug(' ========= Execute: {} -> {}'.format(
                proxy.qualify(command_name),
                resultkey
            ))

            try:
                if command_id is None:
                    return resultkey, fn(**opts)
                else:
                    return resultkey, fn(
                        command_id,
                        **opts
                    )
            except Exception as e:
                raise parser.exceptions.CommandExecutionError(
                    "Error running command '{}': {}".format(command_name, e),
                    model=command
                )

        else:
            raise parser.exceptions.ScriptError("No such command '{}'".format(command_name), model=command)

    def __contains__(self, proxy_name):
        if proxy_name in self.proxies:
            return True

        return False

    def __getitem__(self, proxy_name):
        return self.proxies[proxy_name]

    def __setitem__(self, proxy_name, proxy):
        self.proxies[proxy_name] = proxy
        self.sync_scopes()
