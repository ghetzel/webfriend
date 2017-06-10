"""
The `webfriend.scripting` module implements a simplistic, straightforward scripting environment
for automating various tasks within the Chromium web browser.

## Overview

The commands implemented in this
module provide simplified, opinionated implementations of common tasks such as loading URLs,
parsing and extracting information from the DOM, injecting and executing Javascript into pages, and
capturing web page screenshots.

## Scripting

Scripts consist of plain text files containing a sequence of commands that are executed in the
order they are written.  Return values of each command are stored after the command executes,
allowing subsequent commands to access useful details about the evaluation of previous commands.

If a command experiences an error the error is either raised as a fatal exception, causing the
script to terminate without evaluating the remaining commands, or the error is specified as
non-fatal.  Non-fatal errors are stored and are accessible to the remaining commands and can be
used to make decisions.
"""
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)  # noqa
