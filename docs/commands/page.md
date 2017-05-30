Module webfriend.scripting.commands.page
----------------------------------------

Classes
-------
PageProxy 
    Ancestors (in MRO)
    ------------------
    webfriend.scripting.commands.page.PageProxy
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

    dump_dom(self)

    find(self, text, **kwargs)

    get_command_names(cls)

    qualify(cls, name)

    remove(self, selector)

    screenshot(self, destination=None, width=0, height=0, format='png', jpeg_quality=None, selector='html', settle=1000, after_events=None, settle_timeout=None, autoclose=True)
        Capture the current screen contents as an image and write the image to a file or return it
        as a file-like object.

        ### Arguments

        - **destination** (`str`, _file-like object_, optional):

            If given as a string, this will be the filesystem path that the image is written to.
            If given as a file-like object, that object will be written to, seeked back to zero,
            and returned.  If `None`, an `io.BytesIO` buffer will be allocated, written to, and
            returned.

        - **width** (`int`, optional):

            If given, this is the width viewport will be resized to before capturing the image. If
            not specified, the dimensions of the element specified by 'selector' will be queried
            and that element's outerWidth will be used.

        - **height** (`int`, optional):

            If given, this is the height viewport will be resized to before capturing the image. If
            not specified, the dimensions of the element specified by **selector** will be queried
            and that element's _outerHeight_ will be used.

        - **format** (`str`):

            The output format of the image, either `png` or `jpeg`.

        - **jpeg_quality** (`int`, optional):

            If given, and if **format** is `jpeg`, this is the quality of the JPEG image (0-100).

        - **selector** (`str`):

            When detecting the width and/or height of the page area to render, this is the HTML
            element that will be measured.

        - **settle** (`int`, optional):

            The number of milliseconds to wait after performing the viewport resize before
            actually capturing the image.  This gives newly-exposed elements time to load.

        - **after_events** (`str`, `list`, optional):

            If an event name or list of event names is given, then **settle** will be interpreted
            as an amount of time _after_ the last of these named events has been received. If the
            special value `any` is provided, then **settle** will wait for that amount of time
            since any event has been received to elapse, up to 'settle_timeout' seconds.

        - **settle_timeout** (`int`, optional):

            The maximum amount of time to wait for events to stop coming in as described in by
            **after_events**.

        - **autoclose** (`bool`):

            If a file handle is given as the **destination**, should it be automatically closed when
            the screenshot is completed.

        ### Returns
        `dict`, with keys:

        - _element_ (`chromefriend.rpc.dom.DOMElement`):
            The element that was used as a measurement reference.

        - _width_ (`int`):
            The final width of the viewport that was captured.

        - _height_ (`int`):
            The final height of the viewport that was captured.

        - _destination_ (`object`, optional):
            The destination file-like object data was written to, if specified.

        - _path_ (`str`, optional):
            The filesystem path of the file data was written to, if specified.

    source(self, selector=None)

    start_capture(self, destination, duration=None, format='png', jpeg_quality=85, every_nth=None, filename_format=None)

    stop_capture(self)

    wait_for_capture(self)
