from __future__ import absolute_import
from __future__ import unicode_literals
from webfriend.scripting.commands.base import CommandProxy
from webfriend import exceptions
import netrc
import os
import stat


class UtilsProxy(CommandProxy):
    qualifier = 'utils'
    doc_name = 'Utilities'

    def netrc(self, hostname, filename='~/.netrc'):
        """
        Retrieves a username and password stored in a `.netrc`-formatted file.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        #### Returns
        A 3-element tuple representing the hostname, username, and password of the matching record.
        """
        filename = os.path.expanduser(filename)

        # verify the permissions on the netrc file
        if os.path.isfile(filename):
            netrc_stat = os.stat(filename)
            mode = netrc_stat.st_mode

            for perm, lbl in [
                (stat.S_IRGRP, 'group-readable'),
                (stat.S_IRGRP, 'group-writable'),
                (stat.S_IXGRP, 'group-executable'),
                (stat.S_IROTH, 'world-readable'),
                (stat.S_IROTH, 'world-writable'),
                (stat.S_IXOTH, 'world-executable'),
            ]:
                if mode & perm:
                    raise OSError("Refusing to read credentials from {} file".format(lbl))
        else:
            raise IOError("Cannot locate netrc file at {}".format(filename))

        # python, why would you return these in this order?
        auth = netrc.netrc(filename).authenticators(hostname)

        if auth is None:
            raise exceptions.NotFound("No credentials found for host '{}'".format(hostname))

        # seriously, why?
        # username, hostname, then password? i know this is a nit, but come on...
        # does everything in this language have to be crooked and weird?
        return auth[1], auth[0], auth[2]
