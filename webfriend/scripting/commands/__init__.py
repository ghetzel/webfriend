"""
This module contains documentation on all of the commands supported by the WebFriend core
distribution.  Additional commands may be included via plugins.

## Documentation

All commands are documented by describing the format for executing the command.  All supported
options are presented, along with their default values.  If an option is required, it will be
shown with the value `<REQUIRED>`.
"""

from __future__ import absolute_import
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)  # noqa

from .base import CommandProxy  # noqa
from .core import CoreProxy
from .events import EventsProxy
from .page import PageProxy
from .state import StateProxy
from .file import FileProxy
from .cookies import CookiesProxy

ALL_PROXIES = [
    (CoreProxy.as_qualifier(), CoreProxy),
    (EventsProxy.as_qualifier(), EventsProxy),
    (PageProxy.as_qualifier(), PageProxy),
    (StateProxy.as_qualifier(), StateProxy),
    (FileProxy.as_qualifier(), FileProxy),
    (CookiesProxy.as_qualifier(), CookiesProxy),
]
