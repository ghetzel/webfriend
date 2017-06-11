from __future__ import absolute_import
from __future__ import unicode_literals
from collections import OrderedDict
from webfriend.scripting.parser import MetaModel
import re


class Array(MetaModel):
    pass


class String(unicode):
    def __new__(cls, value, *args, **kwargs):
        if not isinstance(value, unicode):
            value = value.encode('UTF-8')

        value = cls.preprocess(value)

        return unicode.__new__(cls, value, *args, **kwargs)

    @classmethod
    def preprocess(cls, value):
        return value


class StringLiteral(String):
    rx_start = re.compile('^\'')
    rx_end   = re.compile('\'$')

    @classmethod
    def preprocess(cls, value):
        value = cls.rx_start.sub('', value)
        value = cls.rx_end.sub('', value)
        return value


class StringInterpolated(String):
    rx_start = re.compile('^\"')
    rx_end   = re.compile('\"$')

    @classmethod
    def preprocess(cls, value):
        value = cls.rx_start.sub('', value)
        value = cls.rx_end.sub('', value)
        return value


class Heredoc(String):
    rx_start = re.compile('^begin(\s*\n)?')
    rx_end   = re.compile('\s+end$')

    @classmethod
    def preprocess(cls, value):
        value = cls.rx_start.sub('', value)
        value = cls.rx_end.sub('', value)
        return value

    def deindent(self, n):
        return '\n'.join([
            line.replace(' ' * n, '', 1) for line in self.split('\n')
        ])


class RegularExpression(MetaModel):
    def __init__(self, parent, **kwargs):
        super(RegularExpression, self).__init__(parent, **kwargs)

        if not len(self.pattern):
            raise ValueError("Must specify a pattern")

        self.rx = re.compile(self.pattern, flags=self.get_flags())

    def get_flags(self):
        flags = 0

        for option in self.options:
            if option == 'i':
                flags |= re.IGNORECASE
            elif option == 'l':
                flags |= re.LOCALE
            elif option == 'm':
                flags |= re.MULTILINE
            elif option == 's':
                flags |= re.DOTALL
            elif option == 'u':
                flags |= re.UNICODE

        return flags

    def is_match(self, value):
        if self.rx.match(value):
            return True

        return False

    def sub(self, repl, value):
        return self.rx.sub(repl, value)


class Object(MetaModel):
    def __init__(self, parent, **kwargs):
        self.items = []
        self._data  = OrderedDict()

        super(Object, self).__init__(parent, **kwargs)

        for kv in self.items:
            if not len(kv.values):
                continue

            if len(kv.values) == 1:
                self._data[kv.name] = kv.values[0]
            else:
                self._data[kv.name] = kv.values

    def to_json(self):
        return self.as_dict()

    def as_dict(self):
        return self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]
