from __future__ import absolute_import
from webfriend.rpc import Base


class Inspector(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Inspector
    """
    domain = 'Inspector'
