from __future__ import absolute_import
import logging
import json
import click
import click_log
from . import Chrome, browser
from .scripting import execute_script, Scope


@click.group(invoke_without_command=True)
@click.argument('script', type=click.File('rb'))
@click.option(
    '--debugger-url', '-u',
    metavar='URL',
    help='The URL of the Chrome Remote Debugger to connect to.',
    default=browser.DEFAULT_DEBUGGER_URL
)
@click_log.simple_verbosity_option(
    '--log-level',
    '-L',
    default='DEBUG'
)
@click_log.init()
@click.pass_context
def main(ctx, script, debugger_url):
    chrome = Chrome(debug_url=debugger_url)
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
