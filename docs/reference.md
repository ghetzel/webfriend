# Friendscript Language Quick Reference

## Commands

This is the generic structure of all commands:

```
command [ARGUMENT] [{
    OPTION: VALUE,
    ...
}]
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

## Whitespace Handling

The handling of whitespace in scripts is very flexible.  Spaces or tabs, indentation or not, is up to you.  The only places where whitespace is required is to separate reserved words from tokens (e.g.: variables, commands), and within commands between the command name and the argument.  Multiple commands can be on the same line if separated with a semicolon (`;`).

```
example "argument" {whitespace:"is",very:"flexible"}
```

## Variable Scope and Assignment

TODO


## Conditional Statements

Friendscript supports conditional statments like _if-else_ and _case-when_ (i.e: switches).  The basic form of the if-else syntax is:

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

| Operator | Tests                            | Example             |
| -------- | -------------------------------- | ------------------- |
| `==`     | value equality                   | `$a == $b`          |
| `!=`     | value inequality                 | `$a != $b`          |
| `>`      | left greater than right          | `$a > $b`           |
| `>=`     | left greater than/equal to right | `$a >= $b`          |
| `<`      | left less than right             | `$a < $b`           |
| `<=`     | left less than/equal to right    | `$a <= $b`          |
| `=~`     | left matches pattern on right    | `$a =~ "^[aeiou]$"` |
| `in`     | left is contained in right       | `$a in $b`          |
| `not in` | left is not contained in right   | `$a not in $b`      |


Additionally, there is an abbreviated inline syntax for cases in which a variable must be set by a command, then tested for a value:

```
if command "thing" -> $value; $value > 50 {
    # do stuff if $value (which came from executing the command) is > 50
    log "You also have access to $value in here: {value}"
} else {
    # fallback
    log "You also have access to $value in the else-case: {value}"
}

# this ^ is an alternative to:
command "thing" -> $value

if $value > 50 {
    ...
} else {
    ...
}
```

## Looping and Iteration

TODO: Loops: WE GOT EM'

```
# forever
loop { }

# while truthy
loop $truthy { }

# while $a < 10
loop $a < 10 { }

# for x in y
loop $x in $y { }

# unpacking
loop $k, $v in $object { }

# bounded iteration (classic for-loop)
loop command_that_returns_iterator -> $i; $i; next $i { }

# fixed-length constant
loop count 2 { }

# fixed-length via variable
loop count $n { }
```
