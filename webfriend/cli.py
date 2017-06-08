from __future__ import absolute_import
import os
import logging
import json
import click
import click_log
from . import Chrome
from .scripting import execute_script, Scope
from .repl import REPL


@click.group(invoke_without_command=True)
@click.option('--interactive', '-I', is_flag=True, default=False)
@click.option('--debug', '-D', is_flag=True, default=False)
@click.option(
    '--debugger-url', '-u',
    metavar='URL',
    help='The URL of the Chrome Remote Debugger to connect to.'
)
@click_log.simple_verbosity_option(
    '--log-level',
    '-L',
    default='INFO'
)
@click.argument('script', type=click.File('rb'), required=False)
@click.argument('remainder', nargs=-1, type=click.UNPROCESSED)
@click_log.init()
@click.pass_context
def main(ctx, interactive, debug, debugger_url, script, remainder):
    if debug:
        os.environ['WEBFRIEND_DEBUG'] = 'true'

    with Chrome(debug_url=debugger_url) as chrome:
        scope = Scope()

        if interactive:
            repl = REPL(chrome, scope)
            repl.run()
        else:
            scope = execute_script(
                chrome,
                script.read(),
                scope=Scope(parent=scope)
            ).as_dict()

        click.echo(json.dumps(scope, indent=4))


try:
    main()
except Exception as e:
    logging.exception(e)
    exit(1)
