# Command Reference

This module contains documentation on all of the commands supported by the WebFriend core
distribution.  Additional commands may be included via plugins.

## Documentation

All commands are documented by describing the format for executing the command.  All supported
options are presented, along with their default values.  If an option is required, it will be
shown with the value `<REQUIRED>`.

- [Core](#core-command-set)
   - **[click](#click)**
   - **[close_tab](#close_tab)**
   - **[configure](#configure)**
   - **[env](#env)**
   - **[fail](#fail)**
   - **[field](#field)**
   - **[focus](#focus)**
   - **[go](#go)**
   - [help](#help)
   - **[javascript](#javascript)**
   - **[log](#log)**
   - **[new_tab](#new_tab)**
   - **[put](#put)**
   - [reload](#reload)
   - **[require](#require)**
   - **[resize](#resize)**
   - **[rpc](#rpc)**
   - **[run](#run)**
   - **[scroll_to](#scroll_to)**
   - **[select](#select)**
   - [stop](#stop)
   - **[switch_root](#switch_root)**
   - **[switch_tab](#switch_tab)**
   - **[tabs](#tabs)**
   - **[type](#type)**
   - **[wait](#wait)**
   - **[wait_for](#wait_for)**
   - **[wait_for_idle](#wait_for_idle)**
   - **[wait_for_load](#wait_for_load)**
   - **[xpath](#xpath)**
- [Cookies](#cookies-command-set)
   - **[cookies::all](#cookiesall)**
   - **[cookies::delete](#cookiesdelete)**
   - **[cookies::get](#cookiesget)**
   - **[cookies::query](#cookiesquery)**
   - **[cookies::set](#cookiesset)**
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
- [Format](#fmt-command-set)
   - **[fmt::autotype](#fmtautotype)**
   - **[fmt::join](#fmtjoin)**
   - **[fmt::lower](#fmtlower)**
   - **[fmt::lstrip](#fmtlstrip)**
   - **[fmt::replace](#fmtreplace)**
   - **[fmt::rsplit](#fmtrsplit)**
   - **[fmt::rstrip](#fmtrstrip)**
   - **[fmt::split](#fmtsplit)**
   - **[fmt::strip](#fmtstrip)**
   - **[fmt::title](#fmttitle)**
   - **[fmt::upper](#fmtupper)**
- [Page](#page-command-set)
   - **[page::dialog_cancel](#pagedialog_cancel)**
   - **[page::dialog_ok](#pagedialog_ok)**
   - **[page::dump_dom](#pagedump_dom)**
   - [page::find](#pagefind)
   - **[page::prompt_text](#pageprompt_text)**
   - **[page::remove](#pageremove)**
   - **[page::resource](#pageresource)**
   - **[page::resources](#pageresources)**
   - [page::save_resource](#pagesave_resource)
   - **[page::screenshot](#pagescreenshot)**
   - **[page::source](#pagesource)**
   - [page::start_capture](#pagestart_capture)
   - [page::stop_capture](#pagestop_capture)
   - [page::wait_for_capture](#pagewait_for_capture)
- [Vars](#vars-command-set)
   - [vars::clear](#varsclear)
   - **[vars::default](#varsdefault)**
   - [vars::ensure](#varsensure)
   - **[vars::get](#varsget)**
   - **[vars::interpolate](#varsinterpolate)**
   - [vars::pop](#varspop)
   - [vars::push](#varspush)
   - [vars::set](#varsset)
- [Utilities](#utils-command-set)
   - **[utils::netrc](#utilsnetrc)**

## `core` Command Set

These represent very common tasks that one is likely to perform in a browser, such as
navigating to URLs, filling in form fields, and performing input with the mouse and keyboard.

### `click`

```
click <SELECTOR> {
    x:            null,
    y:            null,
    unique_match: true
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

    Only applies to **x**/**y** click events, see: `webfriend.rpc.Input.click_at`.

#### Returns
A `list` of elements that were clicked on.

#### Raises
For **selector**-based events:

- `webfriend.exceptions.EmptyResult` if zero elements were matched, or
- `webfriend.exceptions.TooManyResults` if more than one elements were matched.

---

### `close_tab`

```
close_tab <TAB_ID>
```

Close the tab identified by the given ID.

#### Arguments

- **tab_id** (`str`):

    The ID of the tab to close.

#### Returns
A `bool` value representing whether the tab was closed successfully or not.

---

### `configure`

```
configure <EVENTS> {
    demo:            null,
    user_agent:      null,
    extra_headers:   null,
    cache:           null,
    console:         null,
    referrer_prefix: null
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

- **console** (`bool`, optional):

    Whether console messages emitted from pages are logged to standard error.

- **referrer_prefix** (`str`, optional):

    The domain portion of the "Referer" header to send.

---

### `env`

```
env <NAME> {
    fallback:     null,
    ignore_empty: true,
    detect_type:  true,
    joiner:       null
}
```

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

---

### `fail`

```
fail <MESSAGE>
```

Immediately exit the script in an error-like fashion with a specific message.

#### Arguments

- **message** (`str`):

    The message to display whilst exiting immediately.

#### Raises
- `webfriend.exceptions.UserError`

---

### `field`

```
field <SELECTOR> {
    value:     <REQUIRED>,
    autoclear: true
}
```

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

---

### `focus`

```
focus <SELECTOR>
```

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

---

### `go`

```
go <URI> {
    referrer:            'random',
    wait_for_load:       true,
    timeout:             30000,
    clear_requests:      true,
    continue_on_error:   false,
    continue_on_timeout: true,
    load_event_name:     'Page.loadEventFired'
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

- **clear_requests** (`bool`, optional):

    Whether the resources stack that is queried in [page::resources](#pageresources) and
    [page::resource](#pageresource) is cleared before navigating.  Set this to _false_ to
    preserve the ability to retrieve data that was loaded on previous pages.

- **continue_on_error** (`bool`, optional):

    Whether to continue execution if an error is encountered during page load (e.g.: HTTP
    4xx/5xx, SSL, TCP connection errors).

- **continue_on_timeout** (`bool`, optional):

    Whether to continue execution if **load_event_name** is not seen before **timeout**
    elapses.

- **load_event_name** (`str`, optional):

    The RPC event to wait for before proceeding to the next command.

#### Returns
The URL that was loaded (`str`)

---

### `help`

```
help <COMMAND>
```

---

### `javascript`

```
javascript <BODY> {
    file:             null,
    expose_variables: true
}
```

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

---

### `log`

```
log <LINE> {
    level:  'info',
    indent: 4
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
None

#### Raises
`AttributeError` if the specified log level is not known.

---

### `new_tab`

```
new_tab <URL> {
    width:      null,
    height:     null,
    autoswitch: true
}
```

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

---

### `put`

```
put
```

Store a value in the current scope.  Strings will be automatically converted into the
appropriate data types (float, int, bool) if possible.

#### Arguments

If a single argument is given, automatic type detection will be applied to it and the
resulting value will be returned.

If options are provided, they will be interpreted as an object, each of whose values will
have automatic type detection applied.  The resulting object will be returned.

#### Returns
The given value with automatic type detection applied.

---

### `reload`

```
reload
```

---

### `require`

```
require <PLUGIN_NAME> {
    package_format: 'webfriend.scripting.commands.{}'
}
```

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

---

### `resize`

```
resize <WIDTH> {
    height:      0,
    scale:       0,
    mobile:      false,
    fit_window:  false,
    orientation: null,
    angle:       0
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
A `dict` containing the resulting *width* and *height* as keys.

---

### `rpc`

```
rpc <METHOD>
```

Directly call an RPC method with the given parameters.

#### Arguments

- **method** (`str`):

The name of the backend RPC method to call.

- **kwargs**:

Zero of more arguments to pass in the 'params' section of the RPC call.

#### Returns
A `dict` representation of the `webfriend.rpc.Reply` class.

---

### `run`

```
run <SCRIPT_NAME> {
    data:           null,
    isolated:       true,
    preserve_state: true,
    merge_scopes:   false,
    result_key:     'result'
}
```

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

---

### `scroll_to`

```
scroll_to <SELECTOR> {
    x:        null,
    y:        null
}
```

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

---

### `select`

```
select
```

Polls the DOM for an element that matches the given selector.  Either the element will be
found and returned within the given timeout, or a TimeoutError will be raised.

#### Arguments

- **selector** (`str`):

    The CSS-style selector that specifies the DOM element to look for.

- **timeout** (`int`):

    The number of milliseconds to wait for the element to be returned.

- **interval** (`int`):

    The polling interval, in milliseconds, used for rechecking for the element.

#### Returns
`webfriend.rpc.dom.DOMElement`

#### Raises
`webfriend.exceptions.TimeoutError`

---

### `stop`

```
stop
```

---

### `switch_root`

```
switch_root <SELECTOR>
```

Change the current selector scope to be rooted at the given element.

---

### `switch_tab`

```
switch_tab <TAB_ID>
```

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

---

### `tabs`

```
tabs <SYNC>
```

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

---

### `type`

```
type <TEXT>
```

Input the given textual data as keyboard input into the browser in its current state.

#### Arguments

- **text** (`str`, optional):

    The text string to input, one character or symbol at a time.

- **file** (`str`, optional):

    If specified, read the text to input from the named file.

- **alt**, **control**, **meta**, **shift** (`bool`):

    Declares that the Alt, Control, Meta/Command, and/or Shift keys (respectively) are
    depressed at the time of the click action.

- **is_keypad** (`bool`, optional):

    Whether the text being input is issued via the numeric keypad or not.

- **key_down_time** (`int`, optional):

    How long, in milliseconds, that each individual keystroke will remain down for.

- **key_down_jitter** (`int`, optional):

    An amount of time, in milliseconds, to randomly vary the **key_down_time** duration
    from within each keystroke.

- **delay** (`int`, optional):

    How long, in milliseconds, to wait between issuing individual keystrokes.

- **delay_jitter** (`int`, optional):

    An amount of time, in milliseconds, to randomly vary the **delay** duration
    from between keystrokes.

#### Returns
The text that was submitted.

---

### `wait`

```
wait <MILLISECONDS>
```

Pauses execution of the current script for the given number of milliseconds.

#### Arguments

- **milliseconds** (`int`):

    The number of milliseconds to sleep for; can be fractional.

#### Returns
The number of milliseconds.

---

### `wait_for`

```
wait_for <EVENT_NAME> {
    timeout:    30000,
    match:      null
}
```

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

---

### `wait_for_idle`

```
wait_for_idle <IDLE> {
    events:        [],
    timeout:       30000,
    poll_interval: 250
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

---

### `wait_for_load`

```
wait_for_load <TIMEOUT> {
    idle_time: 500
}
```

Blocks until the "Page.loadEventFired" event has fired, or until timeout elapses (whichever
comes first).

#### Arguments

- **timeout** (`int`):

    The timeout, in milliseconds, before raising a `webfriend.exceptions.TimeoutError`.

#### Returns
`webfriend.rpc.Event`

#### Raises
`webfriend.exceptions.TimeoutError`

---

### `xpath`

```
xpath
```

Query the DOM for elements matching the given XPath expression.

#### Arguments

- **expression** (`str`):

    An XPath expression to evaluate within the current DOM.

#### Returns
A list of matching elements.

---


## `cookies` Command Set

### `cookies::all`

```
cookies::all <URLS>
```

Return a list of all cookies, optionally restricted to just a specific URL.

#### Arguments

- **urls** (`list`, optional):
    If specified, this is a list of URLs to retrieve cookies for.

#### Returns
A `list` of `dict` objects containing definitions for each cookie.

---

### `cookies::delete`

```
cookies::delete <NAME> {
    domain: null
}
```

Delete the cookie specified by the given **name** and (optionally) **domain**.

#### Arguments

- **name** (`str`, optional):

    The name of the cookie to delete.

- **domain** (`str`, optional):

    The domain value of the cookie being retrieved to ensure an unambiguous result.

---

### `cookies::get`

```
cookies::get <NAME> {
    domain: null
}
```

Retrieve a specific cookie by name and (optionally) domain.  The domain should be provided
to ensure the cookie returns at most one result.

#### Arguments

- **domain** (`str`, optional):

    The domain value of the cookie being retrieved to ensure an unambiguous result.

#### Returns
A `dict` describing the cookie returned, or `None`.

#### Raises
A `webfriend.exceptions.TooManyResults` exception if more than one cookie matches the given
values.

---

### `cookies::query`

```
cookies::query <NAME>
```

Query all known cookies and return a list of cookies matching those with specific values.

#### Arguments

The first argument (optional) is the name of the cookie as defined in its description. All
options fields are taken as additional filters used to further restrict which cookies are
returned.

- **value** (`str`, optional):

    The value of the cookie.

- **domain** (`str`, optional):

    The domain for which the cookie is valid for.

- **path** (`str`, optional):

    The path valid of the cookie.

- **expires** (`int`, optional):

    Cookie expiration date as the number of seconds since the UNIX epoch.

- **size** (`int`, optional):

    The size of the cookie, in bytes.

- **httpOnly** (`bool`, optional):

    Whether the cookie is marked as "HTTP only" or not.

- **secure** (`bool`, optional):

    Whether the cookie is marked as secure or not.

- **session** (`bool`, optional):

    Whether the cookie is marked as a session cookie or not.

- **sameSite** (`bool`, optional):

    Whether the cookie is marked as a sameSite cookie or not.

#### Returns
A `list` of `dicts` describing the cookies that matched the given query, whose fields
will be the same as the ones described above.

---

### `cookies::set`

```
cookies::set <NAME>
```

Create or update a cookie based on the given values.

#### Arguments

- **name** (`str`):

    The name of the cookie to set.

- **value** (any):

    The value to set in the cookie.

- **url** (`str`, optional):

    The URL to associate the cookie with. This is important when dealing with things like
    host-only cookies (if **domain** isn't set, a host-only cookie will be created.)  In
    this case, the cookie will only be valid for the exact URL that was used.

    The default value is the URL of the currently active tab.

- **domain** (`str`, optional):

    The domain for which the cookie will be presented.

- **path** (`str`, optional):

    The path value of the cookie.

- **secure** (`bool`, optional):

    Whether the cookie is flagged as secure or not.

- **http_only** (`bool`, optional):

    Whether the cookie is flagged as an HTTP-only cookie or not.

- **same_site** (`str`, optional):

    Sets the "Same Site" attribute of the cookie.  The value "strict" will restrict any
    cross-site usage of the cookie.  The value "lax" allows top-level navigation changes
    to receive the cookie.

- **expires** (`int`, optional):

    Specifies when the cookie expires in epoch seconds (number of seconds
    since 1970-01-01 00:00:00 UTC).

---


## `file` Command Set

### `file::append`

```
file::append <FILENAME> {
    data:     <REQUIRED>
}
```

---

### `file::basename`

```
file::basename <FILENAME> {
    trim_query_string: true
}
```

---

### `file::close`

```
file::close <HANDLE>
```

---

### `file::dirname`

```
file::dirname <FILENAME> {
    trim_query_string: true
}
```

---

### `file::exists`

```
file::exists <FILENAME> {
    trim_query_string: true
}
```

---

### `file::mkdir`

```
file::mkdir <PATH> {
    recursive: true,
    mode:      493
}
```

---

### `file::open`

```
file::open <FILENAME> {
    read:     true,
    write:    true,
    truncate: false,
    append:   false,
    binary:   false
}
```

---

### `file::read`

```
file::read <FILENAME>
```

---

### `file::temp`

```
file::temp <DIRECTORY> {
    prefix:    'webfriend-',
    suffix:    ''
}
```

---

### `file::write`

```
file::write <FILENAME> {
    data:     <REQUIRED>
}
```

---


## `fmt` Command Set

### `fmt::autotype`

```
fmt::autotype <VALUE>
```

Takes a string value and attempts to automatically determines the data type.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

#### Returns
The value converted to the automatically-detected type, or the original unmodified value if
a type could not be determined.

---

### `fmt::join`

```
fmt::join <VALUES> {
    joiner: ','
}
```

Join a list of values into a single string.

#### Arguments

- **values** (`list`):

    A list of values (of any type) to stringify and join by a given joiner string.

- **joiner** (`str`):

    The string to join list elements by.

#### Returns
The resulting joined string.

---

### `fmt::lower`

```
fmt::lower <VALUE>
```

Returns the given string with all characters replaced with their lowercase variants.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

#### Returns
The lowercased string.

---

### `fmt::lstrip`

```
fmt::lstrip <VALUE> {
    characters: null
}
```

Removes the whitespace or a set of given characters from the leading end of the
given string.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

- **characters** (`str`, optional):

    If specified, any of these characters will be trimmed from the string instead of
    whitespace.

#### Returns
The trimmed string.

---

### `fmt::replace`

```
fmt::replace <VALUE> {
    find:    <REQUIRED>,
    replace: <REQUIRED>,
    count:   null
}
```

Locates a given string or pattern in the given string and replaces occurrences with the
given replacement value.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

- **find** (`str`, `regex`):

    The exact string or regular expression that will match the given **value**.

- **replace** (`str`):

    The string (or string pattern for regular expression) that will replace occurrences in
    the given **value**.

    If **find** is a regular expression, then **replace** is interpreted as follows:

    - Groups in the regular expression can be referenced numerically with backreferences
      like `\1`, `\3`.  The number following the backslash refers to the _nth_ group in
      the **find** expression, where group numbering starts from 1.  The `\0`
      backreference refers to the entire matched substring.

    - Named captures in **find** can be referenced such that `\g<name>` refers to named
      capture group `name` in **find** (which would be specified as `(?P<name>...)`.)

- **count** (`int`, optional):

    If specified, up to this many occurrences will be matched before matching stops.  Use
    this to limit the number of replacement operations that can occur.

#### Returns
The resulting string with all replacements (if any) applied.

---

### `fmt::rsplit`

```
fmt::rsplit <VALUE> {
    on:    <REQUIRED>,
    count: -1
}
```

Split an input string into a list of strings, starting from the right-hand side.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

- **on** (`str`):

    The character or substring to split **value** on.  This value will be
    discarded from the resulting list of strings.

- **count** (`int`, optional):

    If specified, only perform up to this many splits before returning the remaining
    unsplit string as the final element in the list.

#### Returns
A `list` of at least 1 element.

---

### `fmt::rstrip`

```
fmt::rstrip <VALUE> {
    characters: null
}
```

Removes the whitespace or a set of given characters from the trailing end of the
given string.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

- **characters** (`str`, optional):

    If specified, any of these characters will be trimmed from the string instead of
    whitespace.

#### Returns
The trimmed string.

---

### `fmt::split`

```
fmt::split <VALUE> {
    on:    <REQUIRED>,
    count: -1
}
```

Split an input string into a list of strings.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

- **on** (`str`):

    The character or substring to split **value** on.  This value will be
    discarded from the resulting list of strings.

- **count** (`int`, optional):

    If specified, only perform up to this many splits before returning the remaining
    unsplit string as the final element in the list.

#### Returns
A `list` of at least 1 element.

---

### `fmt::strip`

```
fmt::strip <VALUE> {
    characters: null
}
```

Removes the whitespace or a set of given characters from the leading and trailing ends of
the given string.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

- **characters** (`str`, optional):

    If specified, any of these characters will be trimmed from the string instead of
    whitespace.

#### Returns
The trimmed string.

---

### `fmt::title`

```
fmt::title <VALUE>
```

Returns the given string with the first character of each whitespace-separated word
capitalized.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

#### Returns
The title-cased string.

---

### `fmt::upper`

```
fmt::upper <VALUE>
```

Returns the given string with all characters replaced with their uppercase variants.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

#### Returns
The uppercased string.

---


## `page` Command Set

### `page::dialog_cancel`

```
page::dialog_cancel
```

Cancels an open modal dialog (presses 'Cancel').

---

### `page::dialog_ok`

```
page::dialog_ok
```

Accepts an open modal dialog (presses 'OK' or 'Yes').

---

### `page::dump_dom`

```
page::dump_dom
```

Print the portion of the DOM the local page cache is currently aware of to log output.
This is primarily useful for debugging WebFriend.

---

### `page::find`

```
page::find <TEXT>
```

---

### `page::prompt_text`

```
page::prompt_text <TEXT> {
    submit: true
}
```

Enters the given text into an open prompt dialog and (optionally) submits it.

#### Arguments

- **text** (`str`):

    The text value to enter into the prompt dialog.

- **submit** (`bool`, optional):

    Whether to automatically submit the dialog or not.

---

### `page::remove`

```
page::remove <SELECTOR>
```

Removes ALL elements that match the given selector from the page.

#### Arguments

- **selector** (`str`):

    The page elements to remove, given as a CSS-style selector, an ID
    (e.g. "#myid"), or an XPath query (e.g.: "xpath://body/p").

#### Returns
A `list` of `webfriend.rpc.DOMElement` instances that were matched and removed from the
page.

---

### `page::resource`

```
page::resource
```

Return a `dict` describing a specific network resource, or false if none was found.

#### Arguments

- **url** (`str`, optional):

    If specified, this is the URL of the requested resource to retrieve.

- **request_id** (`str`, optional):

    If specified, this is the specific resource to retrieve by Request ID.

#### Returns
A `dict` representing the resource, or _false_ if a match was not found.

---

### `page::resources`

```
page::resources
```

Return a list of objects describing every network request that has occurred since the last
invocation of `[go](#go)`, since the resource cache was last cleared with
`[page::clear_resources](#pageclear_resources)`, or since the current tab was loaded.

#### Returns
A `list` of `dict` containing details about the network requests that were performed.

---

### `page::save_resource`

```
page::save_resource <DESTINATION>
```

---

### `page::screenshot`

```
page::screenshot <DESTINATION> {
    width:          0,
    height:         0,
    x:              -1,
    y:              -1,
    format:         'png',
    jpeg_quality:   null,
    selector:       [],
    settle:         250,
    after_events:   null,
    settle_timeout: null,
    reply_timeout:  30000,
    autoclose:      true,
    use:            'tallest'
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

- **width**, **height** (`int`, optional):

    If given, this is the width and/or height the viewport will be resized to before
    capturing the image. If not specified, the dimensions of the element specified by
    'selector' will be queried and that element's outerWidth/outerHeight will be used.

- **x**, **y** (`int`, optional):

    If given, this is the x/y position the viewport will be moved to.  If a negative number
    is specified, then the x/y coordinates of the element matched by **selector** will be
    used.

- **format** (`str`):

    The output format of the image, either `png` or `jpeg`.

- **jpeg_quality** (`int`, optional):

    If given, and if **format** is `jpeg`, this is the quality of the JPEG image (0-100).

- **selector** (`str`, `list`):

    When detecting the width and/or height of the page area to render, this is the HTML
    element that will be measured.  Changing this to a selector that matches a specific
    element (using the default settings for **width**, **height**, **x**, and **y**) will
    result in taking a screenshot of _just_ that element.

    If a `list` is specified, all elements in the list will be retrieved and the one with
    the largest height will be used.

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

- **reply_timeout** (`int`, optional):

    The maximum amount of time to wait for the screenshot call to complete.

- **autoclose** (`bool`):

    If a file handle is given as the **destination**, should it be automatically closed
    when the screenshot is completed.

- **use** (`str`):

    Determines how to handle multiple elements that are matched by **selector**.

    - "tallest":
        Use the tallest element as the result for measuring screenshot dimensions.

    - "first":
        Use the first element matched as the result for measuring screenshot dimensions.

#### Returns
`dict`, with keys:

- _element_ (`webfriend.rpc.DOMElement`):
    The element that was used as a measurement reference.

- _width_ (`int`):
    The final width of the viewport that was captured.

- _height_ (`int`):
    The final height of the viewport that was captured.

- _x_ (`int`):
    The final X-position of the viewport that was captured.

- _y_ (`int`):
    The final Y-position of the viewport that was captured.

- _destination_ (`object`, optional):
    The destination file-like object data was written to, if specified.

- _path_ (`str`, optional):
    The filesystem path of the file data was written to, if specified.

---

### `page::source`

```
page::source <SELECTOR>
```

Retrieves the `outerHtml` of the matching page element.

#### Arguments

- **selector** (`str`):

    The page element to retrieve source for, given as a CSS-style selector, an ID
    (e.g. "#myid"), or an XPath query (e.g.: "xpath://body/p").

#### Returns
A `unicode` string representing the HTML contents of the matched element.

#### Raises
- `webfriend.exceptions.EmptyResult` if zero elements were matched, or
- `webfriend.exceptions.TooManyResults` if more than one elements were matched.

---

### `page::start_capture`

```
page::start_capture <DESTINATION> {
    duration:        null,
    format:          'png',
    jpeg_quality:    85,
    every_nth:       null,
    filename_format: null
}
```

---

### `page::stop_capture`

```
page::stop_capture
```

---

### `page::wait_for_capture`

```
page::wait_for_capture
```

---


## `vars` Command Set

### `vars::clear`

```
vars::clear <KEY> {
    parent: 0
}
```

---

### `vars::default`

```
vars::default <PARENT>
```

Return a list of variable names that are defined in a scope.

#### Arguments

- **parent** (`int`, optional):

    If non-zero, specifies how many levels up to insepect relative to the current scope.
    This is used to query and manipulate scopes above our own.

#### Returns
A list of zero of more strings, one for each variable name.

---

### `vars::ensure`

```
vars::ensure <KEY> {
    parent:  0,
    message: null
}
```

---

### `vars::get`

```
vars::get <KEY> {
    fallback: null,
    parent:   0
}
```

Return the value of a specific variable defined in a scope.

#### Arguments

- **key** (`str`):

    The name of the variable to retrieve.

- **fallback** (`bool`, optional):

    A value to return if the variable was not found.

- **parent** (`int`, optional):

    If non-zero, specifies how many levels up to insepect relative to the current scope.
    This is used to query and manipulate scopes above our own.

#### Returns
The value of the named variable, or **fallback** if the value was not found.

---

### `vars::interpolate`

```
vars::interpolate <FORMAT> {
    isolated: false,
    values:   null
}
```

Return a value interpolated with values from a scope or ones that are explicitly provided.

#### Arguments

- **format** (`str`):

    The format string to interpolate.

- **isolated** (`bool`):

    If true, the calling scope will not be used to interpolate values.

- **values** (`dict`, optional):

    If specified, these values will override the scope's values (if any) and be available
    to **format** during interpolation.

#### Returns
An autotyped value resulting from interpolating the given **format**.

---

### `vars::pop`

```
vars::pop <KEY> {
    parent: 0
}
```

---

### `vars::push`

```
vars::push <KEY> {
    value:       <REQUIRED>,
    interpolate: true,
    parent:      0
}
```

---

### `vars::set`

```
vars::set <KEY> {
    value:       <REQUIRED>,
    interpolate: true,
    parent:      0
}
```

---


## `utils` Command Set

### `utils::netrc`

```
utils::netrc <HOSTNAME> {
    filename: '~/.netrc'
}
```

Retrieves a username and password stored in a `.netrc`-formatted file.

#### Arguments

- **value** (`str`):

    The value to apply the operation to.

#### Returns
A 3-element tuple representing the hostname, username, and password of the matching record.

---


