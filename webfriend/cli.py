from __future__ import absolute_import
import logging
import json
import click
import click_log
from . import Chrome
from .scripting import execute_script, Scope


@click.group(invoke_without_command=True)
@click.argument('script', type=click.File('rb'))
@click.option('--debug/--no-debug', default=False)
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
@click_log.init()
@click.pass_context
def main(ctx, script, debug, debugger_url):
    # if debug:
    #     Chrome.browser_arguments.remove('--headless')
    #     Chrome.browser_arguments.append('--temp-profile')

    with Chrome(debug_url=debugger_url) as chrome:
        scope = Scope()

        exit_state = execute_script(
            chrome,
            script.read(),
            scope=Scope(parent=scope)
        ).as_dict()

        click.echo(json.dumps(exit_state, indent=4))

try:
    main()
except Exception as e:
    logging.exception(e)
    exit(1)
