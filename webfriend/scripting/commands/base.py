from ..scope import Scope


class CommandProxy(object):
    qualifier = None
    default_qualifier = 'core'

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
