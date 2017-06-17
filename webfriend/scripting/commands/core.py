from __future__ import absolute_import
from __future__ import unicode_literals
from urlparse import urlparse
from uuid import uuid4
from webfriend import exceptions
from webfriend import rpc, utils
from webfriend.scripting.commands.base import CommandProxy
from webfriend.scripting.execute import execute_script
from webfriend.scripting.environment import Environment
from webfriend.scripting.scope import Scope
from webfriend.scripting.parser.exceptions import UserError
from webfriend.utils import autotype
import json
import logging
import os
import re
import time
import urlnorm


class CoreProxy(CommandProxy):
    """
    These represent very common tasks that one is likely to perform in a browser, such as
    navigating to URLs, filling in form fields, and performing input with the mouse and keyboard.
    """

    @classmethod
    def qualify(cls, name):
        return name

    def configure(
        self,
        events=None,
        demo=None,
        user_agent=None,
        extra_headers=None,
        cache=None,
        console=None
    ):
        """
        Configures various features of the Remote Debugging protocol and provides environment
        setup.

        #### Arguments

        - **events** (`list`, optional):

            A list of strings specifying what kinds of events Chrome should send to this
            client.  Valid values are: `console`, `dom`, `network`, `page`.

        - **demo** (`dict`, optional):

            A section describing various runtime options useful for demonstrations and
            walkthroughs.

            - **delay** (`int`, optional):

                If specified, scripts will sleep for this amount of time (in milliseconds) between
                each command that is processed.  This is useful for slowing down the visual
                effects of commands to a rate that is easier to see.

        - **user_agent** (`str`, optional):

            If specified, this will be the User-Agent header value that is sent with all HTTP(S)
            requests initiated from here on.

        - **extra_headers** (`dict`, optional):

            If specified, these headers will be included in all HTTP(S) requests initiated from
            here on.  An empty dict will clear previously set headers.

        - **cache** (`bool`, optional):

            Whether caching is enabled or not for this session.

        - **console** (`bool`, optional):

            Whether console messages emitted from pages are logged to standard error.
        """
        if events and hasattr(events, 'values') and isinstance(events.values, list):
            for domain in events.values:
                domain = str(domain).lower()

                if hasattr(self.tab, domain):
                    r = getattr(self.tab, domain)

                    if isinstance(r, rpc.Base):
                        logging.info('Enabling events for domain "{}"'.format(domain))
                        r.enable()

        if isinstance(demo, dict):
            if 'delay' in demo:
                self.environment.set_execution_option(
                    'demo.post_command_delay',
                    float(demo['delay'])
                )

        if isinstance(user_agent, basestring):
            self.tab.network.set_user_agent(user_agent)

        if isinstance(extra_headers, dict):
            self.tab.network.set_headers(extra_headers)

        if cache is True:
            self.tab.network.enable_cache()
        elif cache is False:
            self.tab.network.disable_cache()

        if console is True:
            self.tab.enable_console_messages()
        else:
            self.tab.disable_console_messages()

    def go(self, uri, referrer='random', wait_for_load=True, timeout=30000, clear_requests=True):
        """
        Nagivate to a URL.

        #### Arguments

        - **referrer** (`str`, optional):

            If a URL is specified, it will be used as the HTTP Referer [sic] header field when
            going to the given page. If the URL of the currently-loaded page and the referrer
            are the same, the page will no change.

            For this reason, you may specify the special value 'random', which will generate a
            URL with a randomly generated path component to ensure that it is always different
            from the current page. Specifying None will omit the field from the request.

        - **wait_for_load** (`bool`):

            Whether to block until the page has finished loading.

        - **timeout** (`int`):

            The amount of time, in milliseconds, to wait for the the to load.

        - **clear_requests** (`bool`, optional):

            Whether the resources stack that is queried in [page::resources](#pageresources) and
            [page::resource](#pageresource) is cleared before navigating.  Set this to _false_ to
            preserve the ability to retrieve data that was loaded on previous pages.

        #### Returns
        The URL that was loaded (`str`)
        """

        if referrer is 'random':
            referrer = 'http://example.com/{}'.format(uuid4())

        if clear_requests:
            # since we've explicitly navigating, clear the network requests
            self.tab.dom.clear_requests()

        uri_p = urlparse(uri)

        if not len(uri_p.scheme):
            uri = 'https://{}'.format(uri)

        uri = urlnorm.norm(uri)

        reply = self.tab.page.navigate(uri, referrer=referrer)

        if wait_for_load:
            self.tab.wait_for('Page.loadEventFired', timeout=timeout)

        return reply

    def reload(self):
        self.tab.page.reload()

    def stop(self):
        self.tab.page.stop()

    def wait(self, milliseconds):
        """
        Pauses execution of the current script for the given number of milliseconds.

        #### Arguments

        - **milliseconds** (`int`):

            The number of milliseconds to sleep for; can be fractional.

        #### Returns
        The number of milliseconds.
        """

        time.sleep(milliseconds / 1e3)
        return milliseconds

    def resize(
        self,
        width=0,
        height=0,
        scale=0,
        mobile=False,
        fit_window=False,
        orientation=None,
        angle=0
    ):
        """
        Resizes the active viewport of the current page using the Chrome Device Emulation API. This
        does not resize the window itself, but rather the area the current page interprets the
        window to be.

        This is useful for setting the size of the area that will be rendered for screenshots and
        screencasts.

        #### Arguments

        - **width** (`int`, optional):
            The desired width of the viewport.

        - **height** (`int`, optional):
            The desired height of the viewport.

        - **scale** (`float`, optional):
            The scaling factor of the content.

        - **mobile** (`bool`, dict, optional):
            Whether to emulate a mobile device or not.  If a dict is provided, mobile emulation
            will be enabled and configured using the following keys:

            - *width* (`int`, optional):
                The width of the mobile screen to emulate.

            - *height* (`int`, optional):
                The height of the mobile screen to emulate.

            - *x* (`int`, optional):
                The horizontal position of the currently viewable portion of the mobile screen.

            - *y* (`int`, optional):
                The vertical position of the currently viewable portion of the mobile screen.

        - **fit_window** (`bool`, optional):
            Whether to fit the viewport contents to the available area or not.

        - **orientation** (`str`, optional):
            Which screen orientation to emulate, if any. Can be one of: `portraitPrimary`,
            `portraitSecondary`, `landscapePrimary`, `landscapeSecondary`.

        - **angle** (`int`, optional):
            The angle of the screen to emulate (in degrees; 0-360).

        #### Returns
        A `dict` containing the resulting *width* and *height* as keys.
        """

        if hasattr(mobile, 'as_dict'):
            _mobile   = True
            cfg       = mobile.as_dict()
            mobile_sw = cfg.get('width', 0)
            mobile_sh = cfg.get('height', 0)
            mobile_x  = cfg.get('x', 0)
            mobile_y  = cfg.get('y', 0)
        else:
            _mobile   = False
            mobile_sw = 0
            mobile_sh = 0
            mobile_x  = 0
            mobile_y  = 0

        self.tab.emulation.set_device_metrics_override(
            width=width,
            height=height,
            device_scale_factor=scale,
            mobile=_mobile,
            fit_window=fit_window,
            mobile_screen_width=mobile_sw,
            mobile_screen_height=mobile_sh,
            mobile_position_x=mobile_x,
            mobile_position_y=mobile_y,
            screen_orientation_type=orientation,
            screen_orientation_angle=angle,
        )

        return {
            'width':  width,
            'height': height,
        }

    def put(self, *args, **kwargs):
        """
        Store a value in the current scope.  Strings will be automatically converted into the
        appropriate data types (float, int, bool) if possible.

        #### Arguments

        If a single argument is given, automatic type detection will be applied to it and the
        resulting value will be returned.

        If options are provided, they will be interpreted as an object, each of whose values will
        have automatic type detection applied.  The resulting object will be returned.

        #### Returns
        The given value with automatic type detection applied.
        """
        if len(args) == 1:
            return utils.autotype(args[0])

        elif len(args) > 1:
            return [utils.autotype(a) for a in args]

        elif len(kwargs):
            return dict([
                (k, utils.autotype(v)) for k, v in kwargs.items()
            ])

        return None

    def log(self, line=None, level='info', indent=4, **kwargs):
        """
        Outputs a line to the log.

        #### Arguments

        - **line** (`str`):
                A line of text that will have all current variables, as well as any given
                kwargs, interpolated into it using the Python format() function.

        - **level** (`str`):
                The logging severity level to out as. Can be one of: 'debug', 'info', 'warning',
                or 'error'.

        - **indent** (`int`):
                If 'line' is a dictionary, list, or tuple, it will be printed as a JSON document
                with an indentation of this many spaces per level.  The special value -1 will
                disable JSON serialization for these types.

        - **kwargs**:
                All remaining arguments will be passed along to format() when interpolating 'line'.

        #### Returns
        None

        #### Raises
        `AttributeError` if the specified log level is not known.
        """
        # handle the case where we want to log a data structure without options or a format string
        if line is None:
            line = kwargs

        if hasattr(self.environment.log, level):
            if isinstance(line, (dict, list, tuple)) and indent >= 0:
                try:
                    line = json.dumps(line, indent=4)
                except:
                    pass

            # actually log the line
            getattr(self.environment.log, level)(line)
            return None
        else:
            raise AttributeError("Unknown log level '{}'".format(level))

    def fail(self, message):
        """
        Immediately exit the script in an error-like fashion with a specific message.

        #### Arguments

        - **message** (`str`):

            The message to display whilst exiting immediately.

        #### Raises
        - `webfriend.exceptions.UserError`
        """
        self.environment.log.error(message)
        raise UserError(message)

    def rpc(self, method, **kwargs):
        """
        Directly call an RPC method with the given parameters.

        #### Arguments

        - **method** (`str`):

        The name of the backend RPC method to call.

        - **kwargs**:

        Zero of more arguments to pass in the 'params' section of the RPC call.

        #### Returns
        A `dict` representation of the `webfriend.rpc.Reply` class.
        """
        return self.tab.rpc(method, **kwargs).as_dict()

    def wait_for(self, event_name, timeout=30000, match=None):
        """
        Block until a specific event is received, or until **timeout** elapses (whichever comes
        first).

        #### Arguments

        - **event_name** (`str`):

            The name of the event to wait for.

        - **timeout** (`int`):

            The timeout, in milliseconds, before raising a `webfriend.exceptions.TimeoutError`.

        - **match** (`dict`, optional):

            If specified, all keys in the given object must correspond to keys in the received
            event payload, and the values must match.  Regular expressions must match the
            corresponding payload value, and all other types must match exactly.

        #### Returns
        `webfriend.rpc.Event`

        #### Raises
        `webfriend.exceptions.TimeoutError`
        """
        if isinstance(match, dict):
            started_at = time.time()
            eventstream = self.tab.wait_for_caller_response(event_name, timeout=timeout)

            for event in eventstream:
                print('evt: {}'.format(event))

                if event.matches_criteria(match):
                    try:
                        eventstream.send(True)
                    except StopIteration:
                        pass

                    return {
                        'sequence': [event],
                        'duration': (time.time() - started_at),
                    }
        else:
            return self.tab.wait_for(event_name, timeout=timeout)

    def wait_for_idle(self, idle, events=[], timeout=30000, poll_interval=250):
        """
        Blocks for a specified amount of time _after_ an event has been received, or until
        **timeout** elapses (whichever comes first).

        This is useful for waiting for events to occur after performing an action, then giving some
        amount of time for those events to "settle" (e.g.: allowing the page time to react to those
        events without knowing ahead of time what, if any, listeners will be responding.)  A common
        use case for this would be to wait a few seconds _after_ a resize has occurred for anything
        that just loaded to finish doing so.


        #### Arguments

        - **idle** (`int`):

            The amount of time, in milliseconds, that the event stream should be idle before
            returning.

        - **events** (`list`, optional):

            If not empty, the **idle** time will be interpreted as the amount of time since _any
            of these specific events_ have occurred.  The default is to wait for the browser to be
            idle with respect to _any_ events.

        - **timeout** (`int`):

            The maximum amount of time to wait before raising a
            `webfriend.exceptions.TimeoutError`.

        - **poll_interval** (`int`):

            How often to check the event timings to see if the idle time has elapsed.

        #### Returns
        An `int` representing the number of milliseconds we waited for.

        #### Raises
        `webfriend.exceptions.TimeoutError`
        """
        if hasattr(events, 'values'):
            events = events.values

        return self.tab.wait_for_idle(
            idle,
            events=events,
            timeout=timeout,
            poll_interval=poll_interval
        )

    def wait_for_load(self, timeout=30000, idle_time=500):
        """
        Blocks until the "Page.loadEventFired" event has fired, or until timeout elapses (whichever
        comes first).

        #### Arguments

        - **timeout** (`int`):

            The timeout, in milliseconds, before raising a `webfriend.exceptions.TimeoutError`.

        #### Returns
        `webfriend.rpc.Event`

        #### Raises
        `webfriend.exceptions.TimeoutError`
        """

        if idle_time:
            return self.tab.wait_for_idle(idle_time, events=[
                'Page.loadEventFired',
            ], timeout=timeout)
        else:
            return self.tab.wait_for('Page.loadEventFired', timeout=timeout)

    def type(self, text, **kwargs):
        """
        See: `webfriend.rpc.Input.type_text`
        """
        return self.tab.input.type_text(text, **kwargs)

    def focus(self, selector):
        """
        Focuses the given HTML element described by **selector**.  One and only one element may
        match the selector.

        #### Arguments

        - **selector** (`str`):

            The page element to focus, given as a CSS-style selector, an ID (e.g. "#myid"), or an
            XPath query (e.g.: "xpath://body/p").

        #### Returns
        The matching `webfriend.rpc.DOMElement` that was given focus.

        #### Raises
        - `webfriend.exceptions.EmptyResult` if zero elements were matched, or
        - `webfriend.exceptions.TooManyResults` if more than one elements were matched.
        """
        elements = self.tab.dom.query_all(selector)
        self.tab.dom.ensure_unique_element(selector, elements)
        element = elements['nodes'][0]

        self.tab.dom.focus(element.id)
        return element

    def click(self, selector=None, x=None, y=None, unique_match=True, **kwargs):
        """
        Click on HTML element(s) or on a specific part of the page.  More complex click operations
        are supported (e.g.: double clicking, drag and drop) by supplying **x**/**y** coordinates
        directly.

        #### Arguments

        - **selector** (`str`, optional):

            The page element to focus, given as a CSS-style selector, an ID (e.g. "#myid"), or an
            XPath query (e.g.: "xpath://body/p").

        - **x** (`int`, optional):

            If **selector** is not specified, this is the X-coordinate component of the location
            to click at.

        - **y** (`int`, optional):

            If **selector** is not specified, this is the Y-coordinate component of the location
            to click at.

        - **unique_match** (`bool`):

            For **selector** matches, whether there can be one and only one match to click on. If
            false, every matched element will be clicked on in the order they were matched in.

        - **kwargs**:

            Only applies to **x**/**y** click events, see: `webfriend.rpc.Input.click_at`.

        #### Returns
        A `list` of elements that were clicked on.

        #### Raises
        For **selector**-based events:

        - `webfriend.exceptions.EmptyResult` if zero elements were matched, or
        - `webfriend.exceptions.TooManyResults` if more than one elements were matched.
        """
        if selector:
            elements = self.tab.dom.select_nodes(selector)
            results = []

            if unique_match:
                self.tab.dom.ensure_unique_element(selector, elements)

            for element in elements['nodes']:
                results.append(element.click())

            return results

        elif x is None or y is None:
            raise ValueError("Either 'selector' or 'x' and 'y' must be specified")

            return [
                self.tab.input.click_at(x, y, **kwargs)
            ]

    def field(self, selector, value, autoclear=True):
        """
        Locate and enter data into a form input field.

        #### Arguments

        - **selector** (`str`):

            The page element to enter data into, given as a CSS-style selector, an ID
            (e.g. "#myid"), or an XPath query (e.g.: "xpath://body/p").

        - **value** (`str`):

            The text value to type into the located field.

        - **autoclear** (`bool`, optional):

            Whether to clear the existing contents of the field before entering new data.

        #### Returns
        The text that was entered, as a string.
        """
        if not isinstance(value, basestring):
            raise ValueError("'value' must be specified")

        elements = self.tab.dom.select_nodes(selector)
        field = self.tab.dom.ensure_unique_element(selector, elements)

        if autoclear:
            field['value'] = ''

        field.focus()
        return self.type(value)

    def scroll_to(self, selector=None, x=None, y=None):
        """
        Scroll the viewport to the given location, either that of the named element or, if
        provided, the specfic (X,Y) coordinates relative to the top-left of the current page.

        #### Arguments

        - **selector** (`str`, optional):

            The page element to scroll to, given as a CSS-style selector, an ID (e.g. "#myid"), or
            an XPath query (e.g.: "xpath://body/p").

        - **x**, **y** (`int`, optional):

            If both **x* and **y** are provided, these are the coordinates to scroll to.

        #### Returns
        The result of the scroll operation.
        """
        if selector:
            elements = self.tab.dom.select_nodes(selector)
            self.tab.dom.ensure_unique_element(selector, elements)

            return elements['nodes'][0].scroll_to()

        elif x is None or y is None:
            raise ValueError("Either 'selector' or 'x' and 'y' must be specified")
            return self.tab.dom.root.scroll_to(x, y)

    def select(self, *args, **kwargs):
        """
        See: `webfriend.rpc.DOM.select_nodes`
        """
        return self.tab.dom.select_nodes(*args, **kwargs)

    def xpath(self, *args, **kwargs):
        """
        See: `webfriend.rpc.DOM.xpath`
        """
        return self.tab.dom.xpath(*args, **kwargs)

    def switch_root(self, selector=None):
        """
        Change the current selector scope to be rooted at the given element.
        """
        if selector is None:
            return self.tab.dom.root_to_top()
        else:
            return self.tab.dom.root_to(selector)

    def tabs(self, sync=True):
        """
        Return a description of all of the currently-open tabs.

        #### Arguments

        - **sync** (`bool`):

            Whether to perform a preemptive sync with the browser before returning the tab
            descriptions.

        #### Returns
        A `list` of `dicts` describing all browser tabs currently open.  Each `dict` will at least
        contain the keys:

        - *id* (`str`):

            The tab ID that can be used with other tab management commands.

        - *url* (`str`):

            The URL of the tab being described.

        - *webSocketDebuggerUrl* (`str`):

            The URL of the inspection Websocket used to issue and receive RPC traffic.

        - *target* (`bool`):

            Whether the tab being described is the active tab that other commands will be issued
            against.
        """
        if sync:
            self.browser.sync()

        return [
            t.as_dict() for t in self.browser.tabs.values()
        ]

    def new_tab(self, url, width=None, height=None, autoswitch=True):
        """
        Open a new tab and navigate to the given URL.

        #### Arguments

        - **url** (`str`):

            The URL that the new tab will be navigated to.

        - **width**, **height** (`int`, optional):

            If provided, these represent the width and height (in pixels) that the new tab should
            be created with.

        - **autoswitch** (`bool`, optional):

            Whether to automatically switch to the newly-created tab as the active tab for
            subsequent commands.

        #### Returns
        A `str` representing the ID of the newly-created tab.
        """
        tab_id = self.browser.create_tab(url, width=width, height=height)

        if autoswitch:
            self.browser.switch_to_tab(tab_id)

        return tab_id

    def switch_tab(self, tab_id):
        """
        See: `webfriend.browser.Chrome.switch_to_tab`
        """
        self.browser.switch_to_tab(tab_id)
        return self.tabs(sync=False)

    def close_tab(self, tab_id=None):
        """
        Close the tab identified by the given ID.

        #### Arguments

        - **tab_id** (`str`):

            The ID of the tab to close.

        #### Returns
        A `bool` value representing whether the tab was closed successfully or not.
        """
        if not tab_id:
            tab_id = self.browser.default_tab

        return self.browser.close_tab(tab_id)

    def javascript(self, body=None, file=None, expose_variables=True):
        """
        Inject Javascript into the current page, evaluate it, and return the results.  The script
        is wrapped in an anonymous function whose return value will be returned from this command
        as a native data type.

        By default, scripts will have access to all local variables in the calling script that are
        defined at the time of invocation.  They are available to injected scripts as a plain
        object accessible using the `this` variable.

        #### Arguments

        - **body** (`str`, optional):

            A string value that represents the script to be injected and executed.

        - **file** (`str`, optional):

            A filename that will loaded and injected into the browser.

        - **expose_variables** (`bool`):

            Whether to expose all local variables to the injected script or not.

        #### Returns
        Whatever data was returned from the injected script using a `return` statement,
        automatically parsed into native data types.  Objects, arrays, and all scalar types are
        supported as return values.
        """
        if not body and not file:
            raise ValueError("Must specify either body or file")

        if file:
            body = open(file, 'r').read()

        if expose_variables:
            data = self.scope.as_dict()
        else:
            data = {}

        return self.tab.evaluate(body, data=data, calling_context=self.environment)

    def env(self, name, fallback=None, ignore_empty=True, detect_type=True, joiner=None):
        """
        Retrieves a system environment variable and returns the value of it, or a fallback value if
        the variable does not exist or (optionally) is empty.

        #### Arguments

        - **name** (`str`):

            The name of the environment variable.  Matches are case-insensitive, and the last
            variable to be defined for a given key is the value that will be returned.

        - **fallback** (any):

            The value to return if the environment variable does not exist, or (optionally) is
            empty.

        - **ignore_empty** (`bool`):

            Whether empty values should be ignored or not.

        - **detect_type** (`bool`):

            Whether automatic type detection should be performed or not.

        - **joiner** (`str`, optional):

            If specified, this string will be used to split matching values into a list of values.
            This is useful for environment variables that contain multiple values joined by a
            separator (e.g: the `PATH` variable.)

        #### Returns
        The value of the environment variable **name**, or a list of values if **joiner** was
        specified. If **name** is non-existent or was empty, **fallback** will be returned instead.
        """
        value = None

        # perform case-insensitive search of all environment variables
        for k, v in os.environ.items():
            if k.upper() == name.upper():
                value = v
                break

        if value is None:
            return fallback

        # trim whitespace
        value = value.strip()

        if isinstance(joiner, basestring):
            value = value.split(joiner)

        # handle empty values AND empty lists post-split
        if ignore_empty and not len(value):
            return fallback

        # perform type detection (if specified)
        if detect_type:
            if isinstance(value, list):
                value = [autotype(v) for v in value]
            else:
                value = autotype(value)

        return value

    def require(self, plugin_name, package_format='webfriend.scripting.commands.{}'):
        """
        Loads a named plugin into the current environment.

        #### Arguments

        - **plugin_name** (`str`):

            The name of the plugin to load.  This corresponds to the name of a Python module that
            contains subclasses of `webfriend.scripting.commands.base.CommandProxy`.

        - **package_format** (`str`):

            Specifies which Python package contains the module named in **plugin_name**.  The
            default is to assume plugins are built as namespaced modules that overlay the core
            import tree at `webfriend.scripting.commands.<plugin_name>`.

        #### Returns
        The value of **plugin_name** if the load was successful.
        """
        self.environment.register_by_module_name(plugin_name)
        return plugin_name

    def run(
        self,
        script_name,
        data=None,
        isolated=True,
        preserve_state=True,
        merge_scopes=False,
        result_key=Environment.default_result_key
    ):
        """
        Evaluates another Friendscript loaded from another file.

        #### Arguments

        - **script_name** (`str`):

            The filename or basename of the file to search for in the `WEBFRIEND_PATH` environment
            variable to load and evaluate.  The `WEBFRIEND_PATH` variable behaves like the the
            traditional *nix `PATH` variable, wherein multiple paths can be specified as a
            colon-separated (`:`) list.  The current working directory will always be checked
            first.

        - **data** (`dict`, optional):

            If specified, these values will be made available to the evaluated script before it
            begins execution.

        - **isolated** (`bool`):

            Whether the script should have access to the calling script's variables or not.

        - **preserve_state** (`bool`):

            Whether event handlers created in the evaluated script should remain defined after the
            script has completed.

        - **merge_scopes** (`bool`):

            Whether the scope state at the end of the script's evaluation should be merged into the
            current execution scope.  Setting this to true allows variables defined inside of the
            evaluated script to stay defined after the script has completed.  Otherwise, only the
            value of the **result_key** variable is returned as the result of this command.

        - **result_key** (`str`):

            Defines the name of the variable that will be read from the evaluated script's scope
            and returned from this command.  Defaults to "result", which is the same behavior as
            all other commands.

        #### Returns
        The value of the variable named by **result_key** at the end of the evaluated script's
        execution.

        #### Raises
        Any exception that can be raised from Friendscript.
        """
        script = None
        final_script_name = None
        path_prefixes = ['.']

        # makes the ".fs" optional when passing scripts as arguments
        script_name = re.sub(r'\.fs$', '', script_name) + '.fs'

        # setup scopes
        if isolated:
            scope = Scope()
        else:
            scope = Scope(parent=self.scope)

        # if data is specified, set these values in the evaluated script's scope
        if isinstance(isolated, dict):
            scope.update(isolated)

        # process WEBFRIEND_PATH envvar
        for prefix in os.environ.get('WEBFRIEND_PATH', '').split(':'):
            path_prefixes.append(prefix)

        # search for file in all prefixes
        for prefix in path_prefixes:
            s = os.path.join(prefix, script_name)

            if os.path.isfile(s):
                final_script_name = s
                script = open(final_script_name, 'r').read()
                break

        # validate the script was read
        if script is None:
            raise exceptions.NotFound('Unable to locate script "{}" in any path'.format(
                script_name
            ))

        elif isinstance(script, str):
            script = script.decode('UTF-8')

        # evaluate the script
        logging.debug('Evaluating script {}'.format(final_script_name))
        scope = execute_script(
            self.browser,
            script,
            scope=scope,
            preserve_state=preserve_state
        )

        # if not using an isolated scope, then the top-level keys that were modified in this script
        # are set in our current scope (as if the included code ran inline)
        if merge_scopes:
            logging.debug(
                'Updating {} variables in calling scope with result scope (iso={})'.format(
                    len(scope),
                    isolated
                )
            )

            self.scope.update(scope)

        return scope.get('result')
