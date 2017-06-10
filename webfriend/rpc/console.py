from __future__ import absolute_import
from webfriend.rpc import Base


class Console(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Console
    """
    domain = 'Console'
