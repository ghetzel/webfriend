from __future__ import absolute_import
from webfriend.rpc import Base


class Schema(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Schema
    """
    domain = 'Schema'

    def get_domains(self):
        return self.call('getDomains')
