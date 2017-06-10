from __future__ import absolute_import
import copy
import json
import logging
import os
import random
import requests
import shutil
import tempfile
import time
from webfriend.tab import Tab
from webfriend.scripting.execute import execute_script
from webfriend.utils.commands import locate_browser_process
from ephemeral_port_reserve import reserve, LOCALHOST
from gevent import monkey, subprocess
from urlparse import urlparse
from collections import OrderedDict

monkey.patch_all()

DEFAULT_DEBUGGER_URL = 'http://localhost:9222'


class Chrome(object):
    browser_arguments = [
        '--headless',
        '--disable-gpu',
        '--verbose',
        '--hide-scrollbars',
    ]

    temp_profile_preferences = {
        'homepage': 'about:blank',
        'homepage_is_newtabpage': True,
        'browser': {
            'show_home_button': False,
        },
        'session': {
            'restore_on_startup': 1,
            'startup_urls': [
                'about:blank',
            ],
        },
        'bookmark_bar': {
            'show_on_all_tabs': False,
        },
        'sync_promo': {
            'show_on_first_run_allowed': False,
        },
        'distribution': {
            'do_not_create_any_shortcuts': True,
            'do_not_create_desktop_shortcut': True,
            'do_not_create_quick_launch_shortcut': True,
            'do_not_create_taskbar_shortcut': True,
            'do_not_launch_chrome': True,
            'do_not_register_for_update_launch': True,
            'import_bookmarks': False,
            'import_history': False,
            'import_home_page': True,
            'import_search_engine': False,
            'make_chrome_default': False,
            'make_chrome_default_for_user': False,
            'ping_delay': 60,
            'require_eula': False,
            'suppress_first_run_bubble': True,
            'suppress_first_run_default_browser_prompt': True,
            'system_level': False,
            'verbose_logging': True,
        },
    }

    def __init__(self, debug_url=None, ping_retries=40, ping_delay=125, use_temp_profile=True):
        self.temp_profile_path = None
        self.args = copy.copy(self.browser_arguments)

        if os.getenv('WEBFRIEND_DEBUG', '').lower() in ['1', 'true']:
            self.debug_url = (debug_url or DEFAULT_DEBUGGER_URL)
            self.args.remove('--headless')
        else:
            self.debug_url = debug_url

        self._process = None
        self.tabs = OrderedDict()
        self.background = None
        self.default_tab = None
        self.ping_retries = ping_retries
        self.ping_delay = ping_delay
        self.use_temp_profile = use_temp_profile
        self.started_at = time.time()

    def start(self):
        retries = 0
        self.started_at = time.time()

        if self.debug_url is None:
            port = reserve()
            self.debug_url = 'http://{}:{}'.format(LOCALHOST, port)

        # if we can already ping the given debug url, then stop here and connect to that
        if self.ping():
            self.sync()
            self.postlaunch()
            return self

        else:
            if self.use_temp_profile:
                # otherwise, we're going to launch the process ourselves
                self.create_temp_profile()

            self.args = list(
                self.args + [
                    '--remote-debugging-port={}'.format(
                        urlparse(self.debug_url).port
                    ),
                ]
            )

            self.launch_browser(self.args)

            while True:
                if self.ping():
                    logging.info('Browser process running in {}ms, pid={}'.format(
                        int((time.time() - self.started_at) * 1e3),
                        self._process.pid
                    ))

                    self.sync()
                    self.postlaunch()

                    return self

                if retries >= self.ping_retries:
                    raise Exception("Failed to connect to browser RPC after {} attempts".format(retries))

                retries += 1
                time.sleep(self.ping_delay / 1e3)

    def stop(self):
        try:
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

        finally:
            self.destroy_temp_profile()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def ping(self):
        try:
            requests.head('{}/json'.format(self.debug_url))
            return True
        except requests.exceptions.ConnectionError:
            return False

    def sync(self, wait_for_tab=10000, interval=250):
        tabs_seen = set()
        default_tab = None
        started_at = time.time()
        tabs = []

        while time.time() < (started_at + (wait_for_tab / 1e3)):
            manifest = requests.get('{}/json'.format(
                self.debug_url)
            ).json()

            tabs = [
                t for t in manifest
            ]

            if len(tabs):
                break

            time.sleep(interval / 1e3)

        if not len(tabs):
            raise Exception("Browser creation failed")

        for tab in tabs:
            frame_id = tab.get('id')

            if frame_id is not None:
                tabs_seen.add(frame_id)

                if tab['type'] == 'page':
                    if frame_id in self.tabs:
                        self.tabs[frame_id].description.update(tab)

                    else:
                        logging.info('Register tab {}'.format(frame_id))
                        self.tabs[frame_id] = Tab(self, tab, frame_id=frame_id)

                        if default_tab is None:
                            default_tab = frame_id

        for k in self.tabs.keys():
            if k not in tabs_seen:
                del self.tabs[k]

        if default_tab is not None:
            self.default_tab = default_tab

        if not self.background:
            self.background = self.default

    def launch_browser(self, arguments=[]):
        process_path = locate_browser_process()
        logging.info('Launching browser process: {} {}'.format(
            process_path,
            ' '.join(arguments)
        ))

        self._process = subprocess.Popen(
            [process_path] + arguments
        )

    def postlaunch(self):
        if self.background:
            self.background.target.enable_auto_attach()
            self.background.target.enable_attach_to_frames()
            # self.background.target.enable_discover_targets()

    @property
    def default(self):
        if self.default_tab is None:
            raise Exception("No default tab available")

        if self.default_tab in self.tabs:
            return self.tabs[self.default_tab]
        else:
            raise Exception("Cannot find tab '{}'".format(self.default_tab))

    def create_tab(self, url, width=None, height=None):
        reply = self.background.target.create_target(url, width=width, height=height)
        target_id = reply.get('targetId')

        self.sync()
        return target_id

    def switch_to_tab(self, id):
        """
        Switches the active tab to a given tab.

        #### Arguments

        - **id** (`str`):
            The ID of the tab to switch to, or one of a selection of special values:

            #### Special Values

            - `next`: Switch to the next tab in the tab sequence (in the UI, this is the tab to
               the immediate _right_ of the current tab.)  If the current tab is the last in the
               sequence, wrap-around to the first tab.

            - `previous`: Switch to the previous tab in the tab sequence (in the UI, this is the
               tab to the immediate _left_ of the current tab.)  If the current tab is the first in
               the sequence, wrap-around to the last tab.

            - `first`: Switch to the first tab.

            - `last`: Switch to the last tab.

            - `random`: Switch to a randomly selected tab.

            - **Negative integer**: Switch to the tab _n_ tabs to the left of the current tab (e.g.
              if you specify `-2`, then switch to the tab two to the left of the current one.)

            - **Positive integer**: Switch to the _nth_ tab.  Tabs are counted from left-to-right,
              starting from zero (`0`).

        #### Returns
        An instance of `webfriend.Tab` representing the tab that was just switched to.
        """
        tab_ids = self.tabs.keys()
        current = tab_ids.index(self.default_tab)

        if current >= 0 and len(tab_ids):
            if id == 'next':
                id = tab_ids[(current + 1) % len(tab_ids)]
            elif id == 'previous':
                id = tab_ids[(current - 1) % len(tab_ids)]
            elif id == 'first':
                id = tab_ids[0]
            elif id == 'last':
                id = tab_ids[len(tab_ids) - 1]
            elif id == 'random':
                id = tab_ids[random.random(0, len(tab_ids))]
            elif isinstance(id, (int, float)):
                if id < 0:
                    id = tab_ids[(current + int(id)) % len(tab_ids)]
                else:
                    if int(id) >= len(tab_ids):
                        id = len(tab_ids) - 1

                    id = tab_ids[id]

        if id != self.default_tab:
            self.background.target.activate_target(id)
            self.default_tab = id

        return self.default

    def close_tab(self, id):
        success = self.background.target.close_target(id)
        self.sync()
        return success

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

    def create_temp_profile(self, tempdir=None):
        self.temp_profile_path = tempfile.mkdtemp(
            prefix='webfriend-',
            suffix='-chrome',
            dir=tempdir
        )

        with open(os.path.join(self.temp_profile_path, 'First Run'), 'wb') as preferences:
            data = json.dumps(self.temp_profile_preferences, indent=4)
            preferences.write(data)
            self.args = [
                '--user-data-dir={}'.format(self.temp_profile_path)
            ] + self.args

        logging.info('Created temporary profile at {}'.format(self.temp_profile_path))
        return self.temp_profile_path

    def destroy_temp_profile(self):
        if self.temp_profile_path:
            shutil.rmtree(self.temp_profile_path)
            self.temp_profile_path = None
            return True

        return False
