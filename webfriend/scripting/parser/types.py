from __future__ import absolute_import
from collections import OrderedDict
from webfriend.scripting.parser import MetaModel
import re
import os


class Array(MetaModel):
    pass


class String(MetaModel):
    pass


class Heredoc(MetaModel):
    @property
    def value(self):
        lines = self.body.split('\n')

        if len(lines) > 1:
            common = os.path.commonprefix(lines[1:])
        else:
            common = ''

        return '\n'.join([
            line.lstrip(common) for line in lines
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
