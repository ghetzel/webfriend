from __future__ import absolute_import
from . import Base


class Browser(Base):
    domain = 'Browser'
    enable_events = False

    def get_window_size(self):
        # response = self.call('getWindowBounds')
        pass
