from __future__ import absolute_import
from .scope import Scope
from . import parser, commands
import logging


class CommandSetNotReady(Exception):
    pass


class Environment(object):
    default_result_key = 'result'

    def __init__(self, scope=None, proxies=None, browser=None):
        self._scope = (scope or Scope())
        self.proxies = (proxies or {})
        self.script = None
        self.browser = browser
        self._is_ready = False
        self._exec_options = {}
        self.register_defaults()
        self.sync_scopes()
        self.ready()

    @property
    def scope(self):
        return self._scope

    def ready(self):
        if self._is_ready:
            return True

        if self.browser:
            self.browser.default.enable_events()

        self._is_ready = True
        return True

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

    def register_defaults(self):
        for name, cls in commands.ALL_PROXIES:
            self.register(cls, qualifier=name)

    def register(self, proxy_cls, qualifier=None):
        if not issubclass(proxy_cls, commands.CommandProxy):
            raise ValueError("Proxy class must be a subclass of CommandProxy")

        if qualifier is None:
            qualifier = proxy_cls.as_qualifier()

        self[qualifier] = proxy_cls(self.browser, environment=self)

    def get_proxy_for_command(self, command):
        q_command = command.name.split('::', 1)

        if len(q_command) == 1:
            proxy_name = commands.CommandProxy.default_qualifier
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

    def prepare_output_values(self, values):
        if isinstance(values, list):
            return [self.prepare_output_values(v) for v in values]

        elif isinstance(values, dict):
            return dict([
                (k, self.prepare_output_values(v)) for k, v in values.items()
            ])

        elif values is True:
            return 'true'

        elif values is False:
            return 'false'

        elif values is None:
            return ''

        return values

    def interpolate(self, value, scope=None, **kwargs):
        if scope is None:
            scope = self._scope

        scope = Scope(kwargs, parent=scope)
        scopevars = scope.as_dict()
        actual = parser.to_value(value, scope)

        # if this is an exact-match string, then interpolate is a no-op
        if isinstance(value, parser.types.String) and value.exact:
            return actual

        # lists get recursed into
        elif isinstance(actual, list):
            # recurse into lists
            return [self.interpolate(v, **scopevars) for v in actual]

        # dicts also get recursed into
        elif isinstance(actual, dict):
            # recurse into dicts
            return dict([
                (k, self.interpolate(v, **scopevars)) for k, v in actual.items()
            ])

        # strings (as returned from to_value) get interpolated
        elif isinstance(actual, basestring):
            # do the interpolation
            return actual.format(**self.prepare_output_values(scopevars))

        # everything else passes through
        else:
            return actual

    def execute(self, command, scope=None):
        if scope:
            # NOTE: Future Sadness May Await
            #
            # this here is why commands should not execute in parallel, because we're changing the scope
            # of the _entire_ environment to the given scope for the duration of this call
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
                # recursively interpolate all options
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
                logging.exception('Runtime error')

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

    def __getattr__(self, proxy_name):
        return self.proxies[proxy_name]

    def __getitem__(self, proxy_name):
        if not self._is_ready:
            raise CommandSetNotReady("Cannot work with CommandSet until ready() is called.")

        return self.proxies[proxy_name]

    def __setitem__(self, proxy_name, proxy):
        self.proxies[proxy_name] = proxy
        self.sync_scopes()
