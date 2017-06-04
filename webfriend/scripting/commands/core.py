from __future__ import absolute_import
import logging
import time
import json
from .. import CommandProxy, Scope
from ... import rpc, utils
from uuid import uuid4


class CoreProxy(CommandProxy):
    def configure(
        self,
        events=None,
        demo=None,
        user_agent=None,
        extra_headers=None,
        plugins=None
    ):
        """
        Configures various features of the Remote Debugging protocol and provides environment
        setup.

        ### Arguments

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
                self.commandset.set_execution_option(
                    'demo.post_command_delay',
                    float(demo['delay'])
                )

        if isinstance(user_agent, basestring):
            self.tab.network.set_user_agent(user_agent)

        if isinstance(extra_headers, dict):
            self.tab.network.set_headers(extra_headers)

        if isinstance(plugins, dict):
            from .. import load_and_register_proxy

            for command_plugin in plugins.get('commands', []):
                if isinstance(command_plugin, basestring):
                    load_and_register_proxy(command_plugin)

                elif isinstance(command_plugin, dict):
                    if 'module' not in command_plugin:
                        raise ValueError("Command plugin must specify a 'module' attribute")

                    load_and_register_proxy(
                        command_plugin['module'],
                        name=command_plugin.get('name'),
                        browser=self.browser,
                        commandset=self.commandset
                    )

    def go(self, uri, referrer='random', wait_for_load=True, timeout=30000):
        """
        Nagivate to a URL.

        ### Arguments

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

        ### Returns
        The URL that was loaded (`str`)
        """

        if referrer is 'random':
            referrer = 'http://example.com/{}'.format(uuid4())

        reply = self.tab.page.navigate(uri, referrer=referrer)

        if wait_for_load:
            self.tab.wait_for('Page.loadEventFired', timeout=timeout)

        return reply

    def sleep(self, milliseconds):
        """
        Pauses execution of the current script for the given number of milliseconds.

        ### Arguments

        - **milliseconds** (`int`):
            The number of milliseconds to sleep for; can be fractional.

        ### Returns
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

        ### Arguments

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

        ### Returns
        `dict`
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

        ### Returns
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

        ### Arguments

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

        ### Returns
        The line as printed.

        ### Raises
        `AttributeError` if the specified log level is not known.
        """
        # handle the case where we want to log a data structure without options or a format string
        if line is None:
            line = kwargs

        if hasattr(logging, level):
            if isinstance(line, (dict, list, tuple)) and indent >= 0:
                try:
                    line = json.dumps(line, indent=4)
                except:
                    pass

            # actually log the line
            getattr(logging, level)(line)
            return line
        else:
            raise AttributeError("Unknown log level '{}'".format(level))

    def rpc(self, method, **kwargs):
        """
        Directly call an RPC method with the given parameters.

        ### Arguments

        - **method** (`str`):

        The name of the backend RPC method to call.

        - **kwargs**:

        Zero of more arguments to pass in the 'params' section of the RPC call.

        ### Returns
        A `dict` representation of the `webfriend.rpc.reply.Reply` class.
        """
        return self.tab.rpc(method, **kwargs).as_dict()

    def wait_for_load(self, timeout=30000, idle_time=500):
        """
        Blocks until the "Page.loadEventFired" event has fired, or until timeout elapses (whichever
        comes first).

        ### Arguments

        - **timeout** (`int`):

            The timeout, in milliseconds, before raising a `webfriend.exceptions.TimeoutError`.

        ### Returns
        `webfriend.rpc.event.Event`

        ### Raises
        `webfriend.exceptions.TimeoutError`
        """

        if idle_time:
            return self.tab.wait_for_idle(idle_time, events=[
                'Page.loadEventFired',
            ], timeout=timeout)
        else:
            return self.tab.wait_for('Page.loadEventFired', timeout=timeout)

    def input(self, text, **kwargs):
        """
        See: `webfriend.rpc.input.type_text`
        """
        return self.tab.input.type_text(text, **kwargs)

    def focus(self, selector):
        """
        Focuses the given HTML element described by **selector**.  One and only one element may
        match the selector.

        ### Arguments

        - **selector** (`str`):

            The page element to focus, given as a CSS-style selector, an ID (e.g. "#myid"), or an
            XPath query (e.g.: "xpath://body/p").

        ### Returns
        The matching `webfriend.rpc.dom.DOMElement` that was given focus.

        ### Raises
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

        ### Arguments

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

            Only applies to **x**/**y** click events, see: `webfriend.rpc.input.click_at`.

        ### Returns
        A `list` of elements that were clicked on.

        ### Raises
        For **selector**-based events:
            - `webfriend.exceptions.EmptyResult` if zero elements were matched, or
            - `webfriend.exceptions.TooManyResults` if more than one elements were matched.
        """
        if selector:
            elements = self.tab.dom.select_nodes(selector, wait_for_match=True)
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
        if not isinstance(value, basestring):
            raise ValueError("'value' must be specified")

        elements = self.tab.dom.select_nodes(selector, wait_for_match=True)
        self.tab.dom.ensure_unique_element(selector, elements)
        field = elements['nodes'][0]

        if autoclear:
            field['value'] = ''

        field.focus()
        return self.input(value)

    def scroll_to(self, selector=None, x=None, y=None):
        if selector:
            elements = self.tab.dom.select_nodes(selector, wait_for_match=True)
            self.tab.dom.ensure_unique_element(selector, elements)

            return elements['nodes'][0].scroll_to()

        elif x is None or y is None:
            raise ValueError("Either 'selector' or 'x' and 'y' must be specified")
            return self.tab.dom.root.scroll_to(x, y)

    def select(self, *args, **kwargs):
        """
        See: `webfriend.rpc.dom.DOM.select_nodes`
        """
        return self.tab.dom.select_nodes(*args, **kwargs)

    def xpath(self, *args, **kwargs):
        """
        See: `webfriend.rpc.dom.DOM.xpath`
        """
        return self.tab.dom.xpath(*args, **kwargs)
