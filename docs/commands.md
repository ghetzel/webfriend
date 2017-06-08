## Command Reference
- [Core](#core-command-set)
   - **[click](#click)**
   - [close_tab](#close_tab)
   - **[configure](#configure)**
   - [field](#field)
   - **[focus](#focus)**
   - **[go](#go)**
   - **[log](#log)**
   - [new_tab](#new_tab)
   - **[put](#put)**
   - **[resize](#resize)**
   - **[rpc](#rpc)**
   - [scroll_to](#scroll_to)
   - **[select](#select)**
   - [switch_tab](#switch_tab)
   - [tabs](#tabs)
   - **[type](#type)**
   - **[wait](#wait)**
   - **[wait_for_load](#wait_for_load)**
   - **[xpath](#xpath)**
- [Cookies](#cookies-command-set)
   - **[cookies::all](#cookiesall)**
   - [cookies::delete](#cookiesdelete)
   - [cookies::get](#cookiesget)
   - [cookies::query](#cookiesquery)
   - **[cookies::set](#cookiesset)**
- [Events](#events-command-set)
   - **[events::wait_for](#eventswait_for)**
   - **[events::wait_for_idle](#eventswait_for_idle)**
- [File](#file-command-set)
   - [file::append](#fileappend)
   - [file::basename](#filebasename)
   - [file::close](#fileclose)
   - [file::dirname](#filedirname)
   - [file::exists](#fileexists)
   - [file::mkdir](#filemkdir)
   - [file::open](#fileopen)
   - [file::read](#fileread)
   - [file::temp](#filetemp)
   - [file::write](#filewrite)
- [Page](#page-command-set)
   - [page::dump_dom](#pagedump_dom)
   - [page::find](#pagefind)
   - [page::remove](#pageremove)
   - [page::resource](#pageresource)
   - [page::resources](#pageresources)
   - **[page::screenshot](#pagescreenshot)**
   - [page::source](#pagesource)
   - [page::start_capture](#pagestart_capture)
   - [page::stop_capture](#pagestop_capture)
   - [page::wait_for_capture](#pagewait_for_capture)
- [Vars](#vars-command-set)
   - [vars::clear](#varsclear)
   - [vars::ensure](#varsensure)
   - [vars::get](#varsget)
   - [vars::interpolate](#varsinterpolate)
   - [vars::pop](#varspop)
   - [vars::push](#varspush)
   - [vars::scope_at_level](#varsscope_at_level)
   - [vars::set](#varsset)

## `core` Command Set

These represent very common tasks that one is likely to perform in a browser, such as
navigating to URLs, filling in form fields, and performing input with the mouse and keyboard.
### `click`

```
click _selector_ {
    x: 'null',
    y: 'null',
    unique_match: 'null'
}
```

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

    Only applies to **x**/**y** click events, see: `webfriend.rpc.input.click_at`.

#### Returns
A `list` of elements that were clicked on.

#### Raises
For **selector**-based events:
    - `webfriend.exceptions.EmptyResult` if zero elements were matched, or
    - `webfriend.exceptions.TooManyResults` if more than one elements were matched.

### `close_tab`

```
close_tab _tab_id_
```

### `configure`

```
configure _events_ {
    demo: 'null',
    user_agent: 'null',
    extra_headers: 'null',
    cache: 'null',
    plugins: 'null'
}
```

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

### `field`

```
field _selector_ {
    value: 'null',
    autoclear: 'null'
}
```

### `focus`

```
focus _selector_
```

Focuses the given HTML element described by **selector**.  One and only one element may
match the selector.

#### Arguments

- **selector** (`str`):

    The page element to focus, given as a CSS-style selector, an ID (e.g. "#myid"), or an
    XPath query (e.g.: "xpath://body/p").

#### Returns
The matching `webfriend.rpc.dom.DOMElement` that was given focus.

#### Raises
- `webfriend.exceptions.EmptyResult` if zero elements were matched, or
- `webfriend.exceptions.TooManyResults` if more than one elements were matched.

### `go`

```
go _uri_ {
    referrer: 'null',
    wait_for_load: 'null',
    timeout: 'null',
    clear_requests: 'null'
}
```

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

#### Returns
The URL that was loaded (`str`)

### `log`

```
log _line_ {
    level: 'null',
    indent: 'null'
}
```

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
The line as printed.

#### Raises
`AttributeError` if the specified log level is not known.

### `new_tab`

```
new_tab _url_ {
    width: 'null',
    height: 'null',
    autoswitch: 'null'
}
```

### `put`

```
put
```

Store a value in the current scope.  Strings will be automatically converted into the
appropriate data types (float, int, bool) if possible.
### Returns
The given value with automatic type detection applied.

### `resize`

```
resize _width_ {
    height: 'null',
    scale: 'null',
    mobile: 'null',
    fit_window: 'null',
    orientation: 'null',
    angle: 'null'
}
```

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
`dict`

### `rpc`

```
rpc _method_
```

Directly call an RPC method with the given parameters.

#### Arguments

- **method** (`str`):

The name of the backend RPC method to call.

- **kwargs**:

Zero of more arguments to pass in the 'params' section of the RPC call.

#### Returns
A `dict` representation of the `webfriend.rpc.reply.Reply` class.

### `scroll_to`

```
scroll_to _selector_ {
    x: 'null',
    y: 'null'
}
```

### `select`

```
select
```

See: `webfriend.rpc.dom.DOM.select_nodes`

### `switch_tab`

```
switch_tab _tab_id_
```

### `tabs`

```
tabs _sync_
```

### `type`

```
type _text_
```

See: `webfriend.rpc.input.type_text`

### `wait`

```
wait _milliseconds_
```

Pauses execution of the current script for the given number of milliseconds.

#### Arguments

- **milliseconds** (`int`):
    The number of milliseconds to sleep for; can be fractional.

#### Returns
The number of milliseconds.

### `wait_for_load`

```
wait_for_load _timeout_ {
    idle_time: 'null'
}
```

Blocks until the "Page.loadEventFired" event has fired, or until timeout elapses (whichever
comes first).

#### Arguments

- **timeout** (`int`):

    The timeout, in milliseconds, before raising a `webfriend.exceptions.TimeoutError`.

#### Returns
`webfriend.rpc.event.Event`

#### Raises
`webfriend.exceptions.TimeoutError`

### `xpath`

```
xpath
```

See: `webfriend.rpc.dom.DOM.xpath`


## `cookies` Command Set

### `cookies::all`

```
cookies::all _urls_
```

Return a list of all cookies, optionally restricted to just a specific URL.

#### Arguments

- **urls** (`list`, optional):
    If specified, this is a list of URLs to retrieve cookies for.

#### Returns
A `list` of `dict` objects containing definitions for each cookie.

### `cookies::delete`

```
cookies::delete _name_ {
    domain: 'null'
}
```

### `cookies::get`

```
cookies::get _name_ {
    domain: 'null'
}
```

### `cookies::query`

```
cookies::query _name_
```

### `cookies::set`

```
cookies::set _name_
```

See: `webfriend.rpc.network.set_cookie`


## `events` Command Set

### `events::wait_for`

```
events::wait_for _event_name_ {
    timeout: 'null'
}
```

Block until a specific event is received, or until **timeout** elapses (whichever comes
first).

#### Arguments

- **event_name** (`str`):

    The name of the event to wait for.

- **timeout** (`int`):

    The timeout, in milliseconds, before raising a `webfriend.exceptions.TimeoutError`.

#### Returns
`webfriend.rpc.event.Event`

#### Raises
`webfriend.exceptions.TimeoutError`

### `events::wait_for_idle`

```
events::wait_for_idle _idle_ {
    events: 'null',
    timeout: 'null',
    poll_interval: 'null'
}
```

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


## `file` Command Set

### `file::append`

```
file::append _filename_ {
    data: 'null'
}
```

### `file::basename`

```
file::basename _filename_ {
    trim_query_string: 'null'
}
```

### `file::close`

```
file::close _handle_
```

### `file::dirname`

```
file::dirname _filename_ {
    trim_query_string: 'null'
}
```

### `file::exists`

```
file::exists _filename_ {
    trim_query_string: 'null'
}
```

### `file::mkdir`

```
file::mkdir _path_ {
    recursive: 'null',
    mode: 'null'
}
```

### `file::open`

```
file::open _filename_ {
    read: 'null',
    write: 'null',
    truncate: 'null',
    append: 'null',
    binary: 'null'
}
```

### `file::read`

```
file::read _filename_
```

### `file::temp`

```
file::temp _directory_ {
    prefix: 'null',
    suffix: 'null'
}
```

### `file::write`

```
file::write _filename_ {
    data: 'null'
}
```


## `page` Command Set

### `page::dump_dom`

```
page::dump_dom
```

### `page::find`

```
page::find _text_
```

### `page::remove`

```
page::remove _selector_
```

### `page::resource`

```
page::resource _url_
```

### `page::resources`

```
page::resources
```

### `page::screenshot`

```
page::screenshot _destination_ {
    width: 'null',
    height: 'null',
    format: 'null',
    jpeg_quality: 'null',
    selector: 'null',
    settle: 'null',
    after_events: 'null',
    settle_timeout: 'null',
    autoclose: 'null'
}
```

Capture the current screen contents as an image and write the image to a file or return it
as a file-like object.

#### Arguments

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

    If a file handle is given as the **destination**, should it be automatically closed
    when the screenshot is completed.

#### Returns
`dict`, with keys:

- _element_ (`webfriend.rpc.dom.DOMElement`):
    The element that was used as a measurement reference.

- _width_ (`int`):
    The final width of the viewport that was captured.

- _height_ (`int`):
    The final height of the viewport that was captured.

- _destination_ (`object`, optional):
    The destination file-like object data was written to, if specified.

- _path_ (`str`, optional):
    The filesystem path of the file data was written to, if specified.

### `page::source`

```
page::source _selector_
```

### `page::start_capture`

```
page::start_capture _destination_ {
    duration: 'null',
    format: 'null',
    jpeg_quality: 'null',
    every_nth: 'null',
    filename_format: 'null'
}
```

### `page::stop_capture`

```
page::stop_capture
```

### `page::wait_for_capture`

```
page::wait_for_capture
```


## `vars` Command Set

### `vars::clear`

```
vars::clear _key_ {
    parent: 'null'
}
```

### `vars::ensure`

```
vars::ensure _key_ {
    parent: 'null',
    message: 'null'
}
```

### `vars::get`

```
vars::get _key_ {
    fallback: 'null',
    parent: 'null'
}
```

### `vars::interpolate`

```
vars::interpolate _value_
```

### `vars::pop`

```
vars::pop _key_ {
    parent: 'null'
}
```

### `vars::push`

```
vars::push _key_ {
    value: 'null',
    interpolate: 'null',
    parent: 'null'
}
```

### `vars::scope_at_level`

```
vars::scope_at_level _level_
```

### `vars::set`

```
vars::set _key_ {
    value: 'null',
    interpolate: 'null',
    parent: 'null'
}
```


