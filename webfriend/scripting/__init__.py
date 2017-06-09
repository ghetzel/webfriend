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
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)  # noqa

from . import parser
from .environment import Environment
from .scope import Scope
import logging
import gevent
import time
from .commands import *  # noqa


def execute_script(browser, script, scope=None, environment=None, preserve_state=False):
    # setup the environment
    if not environment:
        environment = Environment(scope, browser=browser)

    if not scope:
        scope = environment.scope

    callbacks = set()

    # load and parse the script
    friendscript = parser.Friendscript(data=script, environment=environment)

    # tell the environment about the calling script
    environment.script = friendscript

    if browser:
        # setup event handlers for this execution
        for handler in friendscript.handlers:
            callback_id = browser.default.on(
                parser.to_value(handler.pattern, scope),
                _handle_event(friendscript, handler, scope)
            )

            logging.debug('Add event handler {}'.format(callback_id))
            callbacks.add(callback_id)

    # Script Execution starts NOW
    # ---------------------------------------------------------------------------------------------
    try:
        # recursively evaluate all blocks and nested blocks starting from the top level
        for block in friendscript.blocks:
            try:
                evaluate_block(friendscript, block, scope)
            except parser.exceptions.ScriptError:
                raise
            except Exception as e:
                logging.debug('Exception')
                raise parser.exceptions.ScriptError(str(e), model=block)

    finally:
        if not preserve_state:
            # unregister the event handlers we created for this run
            for callback_id in callbacks:
                logging.debug('Remove event handler {}'.format(callback_id))
                browser.default.remove_handler(callback_id)

    # ...and done.
    # ---------------------------------------------------------------------------------------------

    # return the final state after script execution
    return scope


def evaluate_block(scriptmgr, block, scope):
    environment = scriptmgr.environment
    # line, column = scriptmgr.get_item_position(block)
    # print('{} = line {}, column: {}'.format(block.__class__, line, column))

    # Assignment
    # ---------------------------------------------------------------------------------------------
    if isinstance(block, parser.variables.Assignment):
        block.assign(environment, scope)

    # Directives
    # ---------------------------------------------------------------------------------------------
    elif isinstance(block, parser.lang.Directive):
        if block.is_unset:
            for var in block.variables:
                scope.unset(var.as_key(scope))

    # Expressions
    # ---------------------------------------------------------------------------------------------
    elif isinstance(block, parser.lang.Expression):
        result, put_result_in = block.process(environment, scope)

        if put_result_in:
            scope.set(put_result_in.as_key(scope), result)

    # Commands
    # ---------------------------------------------------------------------------------------------
    elif isinstance(block, parser.commands.CommandSequence):
        # for each command in the pipeline...
        for command in block.commands:
            key, value = environment.execute(command, scope)
            value = parser.to_value(value, scope)

            if key is not None:
                scope.set(key, value, force=True)

            # perform delay if we have one
            if environment.has_execution_option('demo.post_command_delay'):
                delay = environment.get_execution_option('demo.post_command_delay')
                time.sleep(delay / 1e3)

    # If / Else If / Else
    # ---------------------------------------------------------------------------------------------
    elif isinstance(block, parser.conditions.IfElseBlock):
        subscope = Scope(parent=scope)

        for subblock in block.get_blocks(environment, scope=subscope):
            evaluate_block(scriptmgr, subblock, subscope)

    # Loops
    # ---------------------------------------------------------------------------------------------
    elif isinstance(block, parser.loops.LoopBlock):
        loopscope = Scope(parent=scope)

        for i, _, subblock, scope in block.execute_loop(environment, scope=loopscope):
            try:
                evaluate_block(scriptmgr, subblock, scope=scope)

            except parser.loops.FlowControlMultiLevel as e:
                if e.levels > 1:
                    e.levels -= 1
                    raise
                elif isinstance(e, parser.loops.FlowControlBreak):
                    break
                elif isinstance(e, parser.loops.FlowControlContinue):
                    continue

    # Flow Control
    # ---------------------------------------------------------------------------------------------
    elif isinstance(block, parser.loops.FlowControlWord):
        if block.is_break:
            raise parser.loops.FlowControlBreak('break', levels=block.levels)

        elif block.is_continue:
            raise parser.loops.FlowControlContinue('continue', levels=block.levels)

        else:
            raise parser.exceptions.ScriptError('Unrecognized statement')


def _handle_event(scriptmgr, handler, scope):
    def handle(e):
        def actual(event):
            local_scope_data = {
                'event': {
                    'name':     event.event,
                    'instance': event,
                    'data':     event.payload,
                },
            }

            if handler.isolated:
                local_scope = Scope(data=local_scope_data)
            else:
                local_scope = Scope(data=local_scope_data, parent=scope)

            # execute all commands, accumulating output into the local state
            for block in handler.blocks:
                try:
                    evaluate_block(scriptmgr, block, local_scope)
                except parser.exceptions.ScriptError:
                    raise
                except Exception as e:
                    logging.debug('Exception')
                    raise parser.exceptions.ScriptError(str(e), model=block)

            return local_scope

        gevent.spawn(actual, e)

    return handle
