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

from __future__ import absolute_import
from .parser import AutomationScript, CommandSequence, IfElseBlock
from .proxy import CommandProxy, CommandSet
from .scope import Scope
import logging
import gevent
import time
from .commands import *  # noqa

PROXIES = dict([(p.as_qualifier(), p) for _, p in ALL_PROXIES])  # noqa
EXEC_OPTIONS = {}


class SyntaxError(Exception):
    pass


def register_proxy(name, proxy_cls):
    if name in PROXIES:
        raise AttributeError("Proxy '{}' is already registered".format(name))

    if not issubclass(proxy_cls, CommandProxy):
        raise ValueError("Proxy class must be a subclass of CommandProxy")

    return PROXIES[name]


def get_all_proxy_commands():
    return CommandSet(proxies=PROXIES).get_command_names()


def execute_script(browser, script, scope=None):
    # setup a new scope if we weren't given one
    if not scope:
        scope = Scope()

    # setup the commandset
    commandset = CommandSet(scope)
    callbacks = set()

    # initalize proxy instances with a common scope
    for name, proxy_cls in PROXIES.items():
        commandset[name] = proxy_cls(browser, commandset=commandset)

    # load and parse the script
    instructions = AutomationScript(
        data=script,
        commands=commandset.get_command_names()
    )

    # zero out the initial result if it's not there already
    if commandset.DEFAULT_RESULT_KEY not in scope:
        scope[commandset.DEFAULT_RESULT_KEY] = None

    # show the initial state
    for k, v in scope.items():
        logging.debug('VAR: {}={}'.format(k, v))

    # setup event handlers for this execution
    for handler in instructions.handlers:
        callback_id = browser.default.on(
            handler.pattern,
            _handle_event(handler, commandset, scope)
        )

        logging.debug('Add event handler {}'.format(callback_id))
        callbacks.add(callback_id)

    # for each pipeline (or command, which is just a pipeline of length=1)...
    for block in instructions.blocks:
        if isinstance(block, CommandSequence):
            commands = block.commands
        elif isinstance(block, IfElseBlock):
            sequence = block.get_command_sequence(commandset)

            if sequence is None:
                continue

            commands = sequence.commands

        # for each command in the pipeline...
        for command in commands:
            key, value = commandset.execute(command, scope)

            if key != 'null':
                scope[key] = value

            # perform delay if we have one
            if commandset.has_execution_option('demo.post_command_delay'):
                delay = commandset.get_execution_option('demo.post_command_delay')
                time.sleep(delay / 1e3)

    # unregister the event handlers we created for this run
    for callback_id in callbacks:
        logging.debug('Remove event handler {}'.format(callback_id))
        browser.default.remove_handler(callback_id)

    # return the final state after script execution
    return scope


def _handle_event(handler, commandset, scope):
    def handle(e):
        def actual(event):
            local_scope_data = {
                'event': event,
            }

            if handler.isolated:
                local_scope = Scope(local_scope_data)
            else:
                local_scope = Scope(local_scope_data, scope)

            # execute all commands, accumulating output into the local state
            for sequence in handler.sequences:
                for command in sequence.commands:
                    key, value = commandset.execute(command, local_scope)

                    if key != 'null':
                        local_scope[key] = value

            return local_scope

        gevent.spawn(actual, e)

    return handle
