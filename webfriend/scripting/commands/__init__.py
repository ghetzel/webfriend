from __future__ import absolute_import
from .core import CoreProxy
from .events import EventsProxy
from .page import PageProxy
from .state import StateProxy
from .file import FileProxy

ALL_PROXIES = [
    (CoreProxy.as_qualifier(), CoreProxy),
    (EventsProxy.as_qualifier(), EventsProxy),
    (PageProxy.as_qualifier(), PageProxy),
    (StateProxy.as_qualifier(), StateProxy),
    (FileProxy.as_qualifier(), FileProxy),
]
