Module webfriend.scripting.commands.file
----------------------------------------

Classes
-------
FileProxy 
    Ancestors (in MRO)
    ------------------
    webfriend.scripting.commands.file.FileProxy
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

    append(self, filename, data)

    as_qualifier(cls)

    close(self, handle)

    get_command_names(cls)

    open(self, filename, read=True, write=True, truncate=False, append=False, binary=False)

    qualify(cls, name)

    read(self, filename)

    temp(self, directory='.', prefix='cf', suffix='')

    write(self, filename, data)
