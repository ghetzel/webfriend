from __future__ import absolute_import
import logging
import time
import json
from .. import CommandProxy, Scope
from ... import rpc, utils
from uuid import uuid4


class CoreProxy(CommandProxy):
    def configure(self, events=None, demo=None):
        """
        Configures various features of the Remote Debugging protocol and provides environment
        setup.

        ### Arguments

        - **events** (`list`, optional):

            A list of strings specifying what kinds of events Chrome should send to this
            client.  Valid values are: `console`, `dom`, `network`, `page`.
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
        if len(args) == 1:
            return utils.autotype(args[0])

        elif len(args) > 1:
            return [utils.autotype(a) for a in args]

        elif len(kwargs):
            return dict([
                (k, utils.autotype(v)) for k, v in kwargs.items()
            ])

        return None

    def log(self, line, level='info', indent=4, **kwargs):
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
        if line is None:
            return None

        if hasattr(logging, level):
            if isinstance(line, basestring):
                if not isinstance(line, unicode):
                    line = line.decode('UTF-8')

                line = line.format(**Scope(kwargs, self.scope).as_dict()).strip()
            elif isinstance(line, (dict, list, tuple)) and indent >= 0:
                try:
                    line = json.dumps(line, indent=4)
                except:
                    pass

            if len(line) and line != 'None':
                getattr(logging, level)(line)
                return line
            else:
                return None

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
        A `dict` representation of the `chromefriend.rpc.reply.Reply` class.
        """
        return self.tab.rpc(method, **kwargs).as_dict()

    def wait_for_load(self, timeout=30000, idle_time=500):
        """
        Blocks until the "Page.loadEventFired" event has fired, or until timeout elapses (whichever
        comes first).

        ### Arguments

        - **timeout** (`int`):

            The timeout, in milliseconds, before raising a `chromefriend.exceptions.TimeoutError`.

        ### Returns
        `chromefriend.rpc.event.Event`

        ### Raises
        `chromefriend.exceptions.TimeoutError`
        """

        if idle_time:
            return self.tab.wait_for_idle(idle_time, events=[
                'Page.loadEventFired',
            ], timeout=timeout)
        else:
            return self.tab.wait_for('Page.loadEventFired', timeout=timeout)

    def input(self, text, **kwargs):
        return self.tab.input.type_text(text, **kwargs)

    def focus(self, selector):
        elements = self.tab.dom.query_all(selector)
        self.tab.dom.ensure_unique_element(selector, elements)

        return self.tab.dom.focus(elements['nodes'][0].id)

    def click(self, selector=None, x=None, y=None, unique_match=True, **kwargs):
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
        See: `chromefriend.rpc.dom.DOM.select_nodes`
        """
        return self.tab.dom.select_nodes(*args, **kwargs)

    def xpath(self, *args, **kwargs):
        """
        See: `chromefriend.rpc.dom.DOM.xpath`
        """
        return self.tab.dom.xpath(*args, **kwargs)
