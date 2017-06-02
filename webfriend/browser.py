from __future__ import absolute_import
from .tab import Tab
from .scripting import execute_script
from .utils.commands import locate_browser_process
import requests
import logging
import time
from ephemeral_port_reserve import reserve, LOCALHOST
from gevent import monkey, subprocess
from urlparse import urlparse

monkey.patch_all()

DEFAULT_DEBUGGER_URL = 'http://localhost:9222'


class Chrome(object):
    browser_arguments = [
        '--headless',
        '--disable-gpu',
        '--verbose',
        '--hide-scrollbars',
    ]

    def __init__(self, debug_url=None, ping_retries=40, ping_delay=125):
        self.debug_url = debug_url
        self._process = None
        self.default_tab = None
        self.ping_retries = ping_retries
        self.ping_delay = ping_delay
        self.started_at = time.time()

    def __enter__(self):
        retries = 0
        self.started_at = time.time()

        if self.debug_url is None:
            port = reserve()
            self.debug_url = 'http://{}:{}'.format(LOCALHOST, port)

        browser_arguments = list(
            self.browser_arguments + [
                '--remote-debugging-port={}'.format(
                    urlparse(self.debug_url).port
                ),
            ]
        )

        self.launch_browser(browser_arguments)

        while True:
            if self.ping():
                logging.info('Browser process running in {}ms, pid={}'.format(
                    int((time.time() - self.started_at) * 1e3),
                    self._process.pid
                ))

                self.sync()
                return self

            if retries >= self.ping_retries:
                raise Exception("Failed to connect to browser RPC after {} attempts".format(retries))

            retries += 1
            time.sleep(self.ping_delay / 1e3)

    def __exit__(self, exc_type, exc_value, traceback):
        for tab_id, tab in self.tabs.items():
            logging.info('Stopping tab {}'.format(tab_id))
            tab.stop()

        if self._process:
            logging.info('Stopping browser process pid={}'.format(self._process.pid))
            self._process.terminate()
            self._process.wait()
            logging.info('Browser exited with status {}'.format(self._process.returncode))
            logging.info('Total run time: {}ms'.format(
                int((time.time() - self.started_at) * 1e3)
            ))

    def ping(self):
        try:
            requests.head('{}/json'.format(self.debug_url))
            return True
        except requests.exceptions.ConnectionError:
            return False

    def sync(self, wait_for_tab=10000, interval=250):
        tabs_seen = set()
        default_tab = None
        self.tabs = {}
        started_at = time.time()
        tabs = []

        while time.time() < (started_at + (wait_for_tab / 1e3)):
            tabs = [
                t for t in requests.get('{}/json'.format(
                    self.debug_url)
                ).json() if t['type'] == 'page'
            ]

            if len(tabs):
                break

            time.sleep(interval / 1e3)

        if not len(tabs):
            raise Exception("Browser creation failed")

        for tab in tabs:
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

    def launch_browser(self, arguments=[]):
        process_path = locate_browser_process()
        logging.info('Launching browser process: {} {}'.format(
            process_path,
            ' '.join(arguments)
        ))

        self._process = subprocess.Popen(
            [process_path] + arguments
        )

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
