from __future__ import absolute_import
from webfriend.scripting.commands.base import CommandProxy
import tempfile
import shutil
import os


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

            if isinstance(data, str):
                open(filename, 'wb').write(data)
            else:
                shutil.copyfileobj(data, open(filename, 'wb'))

            return data

        return None

    def append(self, filename, data):
        if data:
            if isinstance(data, unicode):
                data = data.encode('UTF-8')

            if isinstance(data, str):
                with open(filename, 'a') as f:
                    f.write(data)
            else:
                shutil.copyfileobj(data, open(filename, 'a'))

    def temp(self, directory='.', prefix='webfriend-', suffix=''):
        tmp = tempfile.mkstemp(
            suffix=suffix,
            prefix=prefix,
            dir=directory,
        )

        return {
            'handle':   tmp[0],
            'filename': tmp[1],
        }

    def dirname(self, filename, trim_query_string=True):
        if trim_query_string:
            filename = filename.split('?', 1)[0]

        return os.path.dirname(filename)

    def basename(self, filename, trim_query_string=True):
        if trim_query_string:
            filename = filename.split('?', 1)[0]

        return os.path.basename(filename)

    def exists(self, filename, trim_query_string=True):
        if trim_query_string:
            filename = filename.split('?', 1)[0]

        return os.path.exists(filename)

    def mkdir(self, path, recursive=True, mode=0o755):
        if not os.path.exists(path):
            if recursive:
                os.makedirs(path, mode)
            else:
                os.makedir(path, mode)

        elif not os.path.isdir(path):
            raise OSError("Path '{}' exists, but is not a directory".format(path))

        return True
