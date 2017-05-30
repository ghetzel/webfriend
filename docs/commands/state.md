Module webfriend.scripting.commands.state
-----------------------------------------

Classes
-------
StateProxy 
    Ancestors (in MRO)
    ------------------
    webfriend.scripting.commands.state.StateProxy
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

    clear(self, key, parent=0)

    ensure(self, key, parent=0, message=None)

    get(self, key, fallback=None, parent=0)

    get_command_names(cls)

    interpolate(self, value, **kwargs)

    pop(self, key, parent=0)

    push(self, key, value, interpolate=True, parent=0)

    qualify(cls, name)

    scope_at_level(self, level=0)

    set(self, key, value, interpolate=True, parent=0)
