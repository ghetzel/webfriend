Module webfriend.scripting.commands.events
------------------------------------------

Classes
-------
EventsProxy 
    Ancestors (in MRO)
    ------------------
    webfriend.scripting.commands.events.EventsProxy
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

    get_command_names(cls)

    qualify(cls, name)

    wait_for(self, event_name, timeout=30000)
        Block until a specific event is received, or until **timeout** elapses (whichever comes
        first).

        ### Arguments

        - **event_name** (`str`):

            The name of the event to wait for.

        - **timeout** (`int`):

            The timeout, in milliseconds, before raising a `chromefriend.exceptions.TimeoutError`.

        ### Returns
        `chromefriend.rpc.event.Event`

        ### Raises
        `chromefriend.exceptions.TimeoutError`

    wait_for_idle(self, idle, events=[], timeout=30000, poll_interval=250)
        Blocks for a specified amount of time _after_ an event has been received, or until
        **timeout** elapses (whichever comes first).

        This is useful for waiting for events to occur after performing an action, then giving some
        amount of time for those events to "settle" (e.g.: allowing the page time to react to those
        events without knowing ahead of time what, if any, listeners will be responding.)  A common
        use case for this would be to wait a few seconds _after_ a resize has occurred for anything
        that just loaded to finish doing so.

        ### Arguments

        - **idle** (`int`):

            The amount of time, in milliseconds, that the event stream should be idle before
            returning.

        - **events** (`list`, optional):

            If not empty, the **idle** time will be interpreted as the amount of time since _any
            of these specific events_ have occurred.  The default is to wait for the browser to be
            idle with respect to _any_ events.

        - **timeout** (`int`):

            The maximum amount of time to wait before raising a
            `chromefriend.exceptions.TimeoutError`.

        - **poll_interval** (`int`):

            How often to check the event timings to see if the idle time has elapsed.

        ### Returns
        An `int` representing the number of milliseconds we waited for.

        ### Raises
        `chromefriend.exceptions.TimeoutError`
