# Friendscript: An Introduction

Friendscript is a small yet robust scripting language designed to provide easy, flexible access
to web browser automation with WebFriend.  It can be used to write reusable procedures that perform
tasks on web pages; such as logging into a site and extracting data, or taking screenshots of web
pages.

## Basic Introduction for Beginners to Programming

Friendscript scripts are plain text files that are executed by the `webfriend` program in this
package.  When running a script, `webfriend` takes care of automatically launching the web browser
(which, depending on your setup, you may or may not see on your screen.)  It then uses a special
protocol for telling the browser to do specific things, like "go to a website" or "click on a link".
These actions are called _commands_ in Friendscript.  Let's take a look at what a command that goes
to google.com looks like:

```
go "http://google.com"
```

That's it.  That one line is (technically) a complete script.  In this case, all it does is launch
a browser, go to Google, then close the browser.  While not powerful on its own, navigating to a
page is often the first thing that needs to happen when performing browser automation tasks, so it's
a good thing to know up front.

Now, let's search for something on Google automatically.

```
# Go to Google
go "https://google.com"

# Type in our search for "cool cat pictures"
field "input[name='q']" {
    value: "cool cat pictures"
}

# Click the 'Google Search' button
click "input[type='submit'][value='Google Search']"

# Wait for the next page to finish loading before moving on
wait_for_load
```

Okay, so there's a bit to unpack there.  Let's break it down.  You'll see the `go` command that we already know, but we've added some text above it to help describe what it's doing.  This is a _comment_.

### A Comment on Comments

Any line that you write that starts with the pound sign (`#`) (or hash, or _octothorpe_ if you fancy) is a comment, which is to say that WebFriend will ignore it when reading the script.  It's there solely for you to communicate to others reading your code (which might just be Future You!) what the code is up to.

Commands are the code that actually does the work, but comments are just as important when coding because they help clarify your _intentions_, which code on its own is not always good at doing.  Modern websites can be immensely complex beasts that require you to go down many winding roads to accomplish your goals, so comments are there to provide yourself and others with helpful road signs to help navigate the way should you ever need to retrace your steps.

Commenting is considered very good practice to help clarify code that you've written that might not be immediately obvious upon re-reading.  You also don't want to _over-comment_, which is to say that you don't need to write comments for every single thing you're doing.  A good gut-check on when to write comments is to think about how much thought you had to put into reasoning through the code you just wrote.  If you found yourself holding a lot of details and minutiae in your head while writing it (other than the language itself, which gets much simpler to recall over time,) then that might be a great place to write a comment summarizing what the code is doing.

Comments are there to tell the story of what your code is doing as it's doing it.


So, back to our script.  The next command we run after `go` is the `field` command.  The `field` command does two things on a web page: locates a specific form field on the page (which may contain many such fields), and enter a value into that field.  In this case, we need to locate the text input where search text gets typed in, and type in our search.

### Selecting HTML Tags

In HTML, text input fields are traditionally (but not always) defined by the `<input>` HTML tag.  Here we specify that we want to search for an HTML `<input>` tag, but not just any tag.  Specifically, we want an input tag with a specific property on it.  Choosing these properties is both a science and an art.  The goal is to build a _selector_ that will reliably match _one and only one_ item.  If the selector is ambiguous, some commands won't know what to do because they are performing tasks that make sense with one item, but less sense with many items.  In this case, we need to do some investigation to figure out the selector that makes sense for our purposes.  In your main web browser, manually go to [google.com](https://google.com), right click on the search input box, and click "Inspect".  A small window will appear showing you the source code of the page you're looking at (Google), with the code that created the search box highlighted.  It should look something like this:

![Google Chrome DevTools](https://github.com/ghetzel/webfriend/raw/master/docs/images/devtools.png)

The highlighted line is the HTML tag we're targeting, and from that we need to determine a selector that will always return that tag on this page.  There are many options to choose from.  For example, you could select the tag based on the `class` attribute "gsfi", but you'll note that that is not unique to this tag, with a few other examples appearing right below it.  There is also the `id` attribute, whose value is "lst-ib".  This is a great option because IDs are unique to a page, so no other tags can have the attribute `id="lst-ib"`.

In our case, to illustrate a little bit more of the selector syntax, we're going to use `name="q"`.  Putting it all together, the selector for choosing this text field is `input[name='q']` (use single quotes in Friendscript for selector values like this).  The square brackets used here denote that we wish to select only `<input>` tags that have
the _attribute_ "name", whose value is "q".


### Command Options

The `field` command we've created accepts one mandatory option (the selector), which we must always specify for this command.  However, which field on the page to fill in is only half of the story; we need to specify _what_ to put in that field.  This is given as a _command option_.  Command options are always specified between curly braces (`{`, `}`).  The options come in the form of name:value pairs.  In the example, we specify the option `value` to be "cool cat pictures".  To specify multiple options for the same command, separate them with commas (`,`), like so:

```
command "mandatory" {
    option1: true,
    option2: 3.1415,
    option3: "My Option",
}
```

### Finishing Up

To complete the script, we need to click the "Google Search" button and wait for the next page to load.  This is achieved using the `click` command, which accepts a mandatory option that selects the HTML element representing the search button.

Finally, the `wait_for_load` command doesn't require any options, as its function is pretty straightforward.  This command is very useful for when you perform an action that you know is about to change pages, as it waits until the next page finishes loading before proceeding with the script.  This is useful because the commands that come after a `wait_for_load` call will likely be selectors and actions intended for the following page, so that page will need to load first before any of those commands will make sense.
