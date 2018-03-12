# Friendscript Language Quick Reference

## tl;dr

Friendscript is a domain-specific imperative scripting language used for performing automatic tasks within a web browser; such as loading URLs, searching the DOM for elements and content, and performing page rendering tasks like screenshots and video captures.  Scripts are plain text files that contain a series of commands that are executed linearly in a blocking manner, with a bias towards exiting upon encountering errors.  Logical operations, branching, and looping are supported as native language-level constructs for the purpose of building flexible and robust automation scripts.

## Commands

This is the generic structure of all commands:

```
command [ARGUMENT] [{
    OPTION: VALUE,
    ...
}] [ -> RESULT]
```

Commands have a variable syntax depending on the required arguments and options for a command.  Some commands are standalone (arity 0) and don't take arguments at all.  Some require an argument but do not accept options, where others take options but not an argument.  Consult the command's documentation to determine the proper usage for a command.  Command names map to the corresponding plugin's instance methods.  The command argument is the first positional argument to the method, and options map directly to the method's _keyword arguments_.

### Usage Examples:

- Standalone command with no arguments or options (arity 0):

  ```
  wait_for_load
  ```

- Command with argument, no options (arity 1):

  ```
  log "Hello, World!"
  ```

- Command with argument and options (arity 2+):

  ```
  field "input[type='password']" {
      value: "secret"
  }
  ```

- Command with argument and multiple options of all types (arity n):

  ```
  example "argument" {
      boolean:  true,
      boolean2: false,
      string:   "Example Text",
      integer:  42,
      float:    3.14,
      list:     [
          "1",
          true,
          3.14,
          {
              list_of_objects: true,
          },
          [
              "sublist"
          ],
      ],
      object:   {
          this: {
              is: {
                  a: "nested",
                  b: {
                      object: true,
                  }
              }
          }
      },
  }
  ```

### Command Output

By default, every command that runs will save a resulting value (which is command-specific) to a variable in the current scope called `$result`.  So, without doing anything else, the following code will do something useful:

```
go "https://google.com"
log "Got HTTP {result[status]} for {result[url]}"
```

The only caveat is that `$result` is updated for _every_ command, which means that if you run this:

```
go "https://google.com"
select "style"

log "Got HTTP {result[status]} for {result[url]}"
```

...it might not do what you expect it to.  The value of `$result` from the `go` command is replaced by the the return value of the `select` command, and so the subsequent `log` command will be expecting fields and data that aren't there.

To mitigate this, you can explicitly save the results of commands into named variables with the command assignment operator (`->`).  This is a working version of the above snippet:

```
go "https://google.com" -> $google
select "style"

log "Got HTTP {google[status]} for {google[url]}"
```

We've saved the output of the `go` command to a new variable `$google`, but the following `select` command will still put its results in `$result`.  Therefore, the `log` command (reading from the `$google` value) will print the expected information.

## Whitespace Handling

The handling of whitespace in scripts is very flexible.  Spaces or tabs, indentation or not, is up to you.  The only places where whitespace is required is to separate reserved words from tokens (e.g.: variables, commands), and within commands between the command name and the argument.  Multiple commands can be on the same line if separated with a semicolon (`;`).

```
example "argument" {whitespace:"is",very:"flexible"}
```

## Variable Assignment and Retrieval

Variables can be stored and retrieved throughout your script using the assignment operator (`=`):

```
# integers
$a = 1

# booleans
$b = true

# floats
$c = 3.1415

# strings
$d = "four"

# arrays
$e = [5, 6, 7]

# objects
$my = {
    g: "gee",
    cool: {
        value: "yay!",
    },
}
```

Variable retrieval can be achieved simply by using the variable in-line (e.g.: `if $a == $b {}`), or through string interpolation (`$x = "The value of $a is {a}"`).  For variables containing objects, keys and nested subkeys of those objects can be accessed using a dot-separated notation (e.g.: `$my.cool.value` from above would return `"yay!"`).  If the named key (or any intermediate keys) do not exist, the variable will return `null`.


## Variable Scope

All variables are set within a _scope_.  A scope defines a common area where variable data is stored.  Certain constructs, such as `if` and `loop` statements will create their own scope that is local to the statements defined between the braces (`{}`).

These scopes _inherit_ the scope of the block where it was defined, so these statements have access to all of the variables that came before them, but statements outside of these constructs won't be able to see variables created inside of them.  If you need to set a variable from within a scoped statement, you must first declare it outside of that statement.  For example:

```
$everyone_can_see_me      = true
$im_gonna_be_set_in_an_if = null

if 2 == 2 {
    $but_only_things_in_here_can_see_me = "yay!"
    $im_gonna_be_set_in_an_if = "I'm making a break for it."

    log "{everyone_can_see_me}"                 # this will work
    log "{but_only_things_in_here_can_see_me}"  # as will this
}

log "{everyone_can_see_me}"                 # this will work
log "{im_gonna_be_set_in_an_if}"            # as will this, but...
log "{but_only_things_in_here_can_see_me}"  # ERROR!!
```


## String Interpolation

When strings wrapped in double quotes (`"yay"`) are encountered, they are automatically scanned for Python-style interpolation sequences wrapped in curly braces (`{}`).  Single-quoted strings (`'yay'`) are **not** interpolated, and are returned exactly as entered.

When interpolating, all variables in the current scope and any parent scopes (recursively up to the global level) are made available for interpolation within any string, whether it is used as the value of a variable, command argument, command option, or condition expression.  Using the variables from above, here are some string patterns and their value:


| Pattern                           | Value                       |
| --------------------------------- | --------------------------- |
| `"Test {a}"`                      | `"Test 1"`                  |
| `"Test {b}"`                      | `"Test True"`               |
| `"Test {c}, {d}, {e[0]}, {e[2]}"` | `"Test 3.1415, four, 5, 7"` |
| `"Test {my[cool][value]}"`        | `"Test yay!"`               |


For more information on the supported formatting options, see the documentation on Python's [Format Specification Mini-Language](https://docs.python.org/2/library/string.html#formatspec).


## Multiline String Literals (Heredocs)

Friendscript supports a syntax for entering large string values that span multiple lines whose syntax may frequently conflict with Friendscript's own.  These are sometimes referred to as "heredocs", and are particularly useful for including the source code of other languages inside of an automation script.  Here is an example of some inline Javascript:

```
javascript begin
  var tag = document.getElementById('cool_tag');

  if(tag) {
    tag.nodeValue = 'My Stuff';
  }
end
```

Everything between the `begin` and `end` statements is part of the string value passed as the first argument to the `javascript` command.  This syntax is accepted wherever a string is, including setting variables and as command option values.

## Conditional Statements

Friendscript supports conditional statements in the form of `if/else if/else` constructs.  The basic form of conditional statements is:

```
if $somevariable {
    # do stuff
} else if $other {
    # do more stuff
} else {
    # do fallback stuff
}
```

Test expressions are supported:

```
if $a == $b { ... }
```

### Supported Operators

| Operator | Tests                                | Example             |
| -------- | ------------------------------------ | ------------------- |
| `==`     | value equality                       | `$a == $b`          |
| `!=`     | value inequality                     | `$a != $b`          |
| `>`      | left greater than right              | `$a > $b`           |
| `>=`     | left greater than/equal to right     | `$a >= $b`          |
| `<`      | left less than right                 | `$a < $b`           |
| `<=`     | left less than/equal to right        | `$a <= $b`          |
| `~`      | left matches pattern on right        | `$a ~ "^[aeiou]$"`  |
| `!~`     | left does not match pattern on right | `$a !~ "^[aeiou]$"` |
| `in`     | left is contained in right           | `$a in $b`          |
| `not in` | left is not contained in right       | `$a not in $b`      |


Additionally, there is an abbreviated inline syntax for cases in which a variable must be set by a command, then tested for a value:

```
if command "thing" -> $value; $value > 50 {
    # do stuff if $value (which came from executing the command) is > 50
    log "You also have access to $value in here: {value}"
} else {
    # fallback
    log "You also have access to $value in the else-case: {value}"
}

# the above is an alternative to:
command "thing" -> $value

if $value > 50 {
    ...
} else {
    ...
}
```

## Looping and Iteration

Friendscript supports several useful looping constructs for repeatedly running blocks of code, either for a fixed number of loops, or until a specific condition is met.  All loops, regardless of their bounds or termination conditions, have a variable implicitly defined within the scope of the loop's block: `$index`.  The `$index` variable stores the current iteration count (i.e.: number of times the loop has run).  This can be used by statements inside the loop for various purposes.  Below are some examples of this syntax and short descriptions of their usage

### Infinite Loop

Iterates forever, unless a condition in the loop definition exits the loop with a `break` statement.
```
loop {
    log "Round {index}"

    if $index > 500 {
        break
    }
}
```

### Loop while a variable evalutates to a "truthy" (non-null, non-zero) value.
```
loop $something {
    # do things
}
```

### Loop while the given condition is true
```
loop $a < 10 {
    command::output -> $out

    if $out == 5 {
        continue
    } else {
        $a = $out
    }
}
```

### Loop through all values in `$y`
```
loop $x in $y {
    log "Y #{index}: {x}"
}
```

### Loop through each key (`$k`) and value (`$v`) pair in object `$object`
```
loop $k, $v in $object {
    log "KEY {k} = {v}"
}
```

### Bounded Iteration (classic "for loop")
```
loop command_that_returns_iterator -> $i; $i; next $i {
    # do something with $i
}
```

### Loop a fixed number of times
```
loop count 2 {
    # define $word here so that the assignments inside the if-statements know
    # which scope to put the value in
    $word = null

    if $index == 0 {
        $word = "once"
    } else {
        $word = "twice"
    }

    log "Do it {word}"
}
```

### Loop a fixed number of times as defined by `$n`
```
loop count $n {
    # do something n times
}
```


## Includes

Friendscripts can include other Friendscripts, allowing you to build modular scripts to suit your organizational needs.  Script filenames are relative to the current script's location, and accept standard filename [globbing patterns](https://en.wikipedia.org/wiki/Glob_(programming)).

```
$test = 'yay'

include "other-friend.fs"
include "more-friends/*.fs"
```


## Event Handlers

As your script interacts with the browser, various events are generated for a multitude of actions involved in the process of loading and displaying a web page.  Friendscript is able to receive these events and perform actions when they occur.  Actions can include any valid sequence of commands or statements.

```
on "Network.responseReceived" {
    log "{event[name]}:"
    log $event.data
}
```

This event handler will fire whenever a "Network.responseReceived" event is received (which can be quite often), and log the event's data object.  Uses for event handlers can range from simple debugging and inspection of a web request or page change events, to data collection and reporting (e.g.: which URLs/domains is this page talking to?)


