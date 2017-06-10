from __future__ import absolute_import
from webfriend.rpc import Base


class Browser(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Browser
    """

    domain = 'Browser'
    supports_events = False

    def get_window_size(self):
        # response = self.call('getWindowBounds')
        pass
