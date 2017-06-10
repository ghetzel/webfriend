from webfriend.scripting import parser
from webfriend.scripting.environment import Environment
from webfriend.scripting.scope import Scope
from webfriend.scripting.commands import *  # noqa
import logging
import gevent
import time


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
