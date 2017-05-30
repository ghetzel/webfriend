Module webfriend.scripting.commands.core
----------------------------------------

Classes
-------
CoreProxy 
    Ancestors (in MRO)
    ------------------
    webfriend.scripting.commands.core.CoreProxy
    webfriend.scripting.proxy.CommandProxy
    __builtin__.object

    Class variables
    ---------------
    qualifier

    Instance variables
    ------------------
    tab

    Methods
    -------
    __init__(self, browser, commandset=None, scope=None)

    as_qualifier(cls)

    click(self, selector=None, x=None, y=None, unique_match=True, **kwargs)

    configure(self, events=None, demo=None)
        Configures various features of the Remote Debugging protocol and provides environment
        setup.

        ### Arguments

        - **events** (`list`, optional):

            A list of strings specifying what kinds of events Chrome should send to this
            client.  Valid values are: `console`, `dom`, `network`, `page`.

    field(self, selector, value, autoclear=True)

    focus(self, selector)

    get_command_names(cls)

    go(self, uri, referrer='random', wait_for_load=True, timeout=30000)
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

    input(self, text, **kwargs)

    log(self, line, level='info', indent=4, **kwargs)
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

    put(self, *args, **kwargs)

    qualify(cls, name)

    resize(self, width=0, height=0, scale=0, mobile=False, fit_window=False, orientation=None, angle=0)
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

    rpc(self, method, **kwargs)
        Directly call an RPC method with the given parameters.

        ### Arguments

        - **method** (`str`):

        The name of the backend RPC method to call.

        - **kwargs**:

        Zero of more arguments to pass in the 'params' section of the RPC call.

        ### Returns
        A `dict` representation of the `chromefriend.rpc.reply.Reply` class.

    scroll_to(self, selector=None, x=None, y=None)

    select(self, *args, **kwargs)
        See: `chromefriend.rpc.dom.DOM.select_nodes`

    sleep(self, milliseconds)
        Pauses execution of the current script for the given number of milliseconds.

        ### Arguments

        - **milliseconds** (`int`):
            The number of milliseconds to sleep for; can be fractional.

        ### Returns
        The number of milliseconds.

    wait_for_load(self, timeout=30000, idle_time=500)
        Blocks until the "Page.loadEventFired" event has fired, or until timeout elapses (whichever
        comes first).

        ### Arguments

        - **timeout** (`int`):

            The timeout, in milliseconds, before raising a `chromefriend.exceptions.TimeoutError`.

        ### Returns
        `chromefriend.rpc.event.Event`

        ### Raises
        `chromefriend.exceptions.TimeoutError`

    xpath(self, *args, **kwargs)
        See: `chromefriend.rpc.dom.DOM.xpath`
