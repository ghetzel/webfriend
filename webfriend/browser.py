from __future__ import absolute_import
from .tab import Tab
from .scripting import execute_script
import requests
import logging
from gevent import monkey

monkey.patch_all()

DEFAULT_DEBUGGER_URL = 'http://localhost:9222'


class Chrome(object):
    def __init__(self, debug_url=DEFAULT_DEBUGGER_URL):
        self.debug_url = debug_url
        self.tabs = {}
        self.default_tab = None
        self.sync()

    def sync(self):
        tabs_seen = set()
        default_tab = None

        for tab in requests.get('{}/json'.format(self.debug_url)).json():
            if tab['type'] == 'page':
                frame_id = tab.get('id')

                if default_tab is None:
                    default_tab = frame_id

                if frame_id is not None:
                    tabs_seen.add(frame_id)
                    logging.info('Register tab {}'.format(frame_id))
                    self.tabs[frame_id] = Tab(self, 'about:blank', tab, frame_id=frame_id)

        for k in self.tabs.keys():
            if k not in tabs_seen:
                del self.tabs[k]

        if default_tab is not None:
            self.default_tab = default_tab

    @property
    def default(self):
        if self.default_tab is None:
            raise Exception("No default tab available")

        if self.default_tab in self.tabs:
            return self.tabs[self.default_tab]
        else:
            raise Exception("Cannot find tab '{}'".format(self.default_tab))

    def execute_script(self, script, scope=None):
        """
        Execute an automation script against this browser session.

        Args:
            script (str):
                The full text of the script to execute.

            scope (`webfriend.scripting.Scope`, optional):
                An optional initial scope to execute the script from.  This can be used to provide the
                script with initial values for variables used in the script.
        """
        return execute_script(self, script, scope)
