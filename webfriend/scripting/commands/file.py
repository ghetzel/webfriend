from __future__ import absolute_import
from .. import CommandProxy
import tempfile


class FileProxy(CommandProxy):
    def open(self, filename, read=True, write=True, truncate=False, append=False, binary=False):
        mode = ''

        if read:
            if write:
                if truncate:
                    mode = 'w+'
                else:
                    mode = 'r+'
            elif append:
                mode = 'a+'
            else:
                mode = 'r'
        elif write:
            if truncate:
                mode = 'w'
        elif append:
            mode = 'a'

        if not len(mode):
            raise AttributeError("Must specify at least one of: 'read', 'write', or 'append'")

        if binary:
            mode += 'b'

        return open(filename, mode)

    def close(self, handle):
        handle.close()

    def read(self, filename):
        return open(filename, 'r').read()

    def write(self, filename, data):
        if data:
            if isinstance(data, unicode):
                data = data.encode('UTF-8')

            open(filename, 'wb').write(data)
            return data

        return None

    def append(self, filename, data):
        if data:
            with open(filename, 'a') as f:
                f.write(data)

    def temp(self, directory='.', prefix='cf', suffix=''):
        tmp = tempfile.mkstemp(
            suffix=suffix,
            prefix=prefix,
            dir=directory,
        )

        return {
            'handle':   tmp[0],
            'filename': tmp[1],
        }
