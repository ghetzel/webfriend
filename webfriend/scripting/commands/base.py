from webfriend.scripting.scope import Scope
import inspect
import importlib


class CommandProxy(object):
    qualifier = None
    doc_name = None
    default_qualifier = 'core'
    enabled_proxies = [
        'cookies',
        'core',
        'events',
        'file',
        'fmt',
        'page',
        'state',
    ]

    def __init__(self, browser, environment=None, scope=None):
        self.browser = browser
        self.environment = environment
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
    def get_all_proxies(cls):
        proxies = []
        for proxy_module in cls.enabled_proxies:
            module = importlib.import_module('webfriend.scripting.commands.{}'.format(
                proxy_module
            ))

            members = inspect.getmembers(module, inspect.isclass)

            for subcls in members:
                if issubclass(subcls[1], CommandProxy) and subcls[1] is not CommandProxy:
                    proxies.append((subcls[1].as_qualifier(), subcls[1]))

        return proxies

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
                    if cls.as_qualifier() == cls.default_qualifier:
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
