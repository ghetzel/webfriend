from __future__ import absolute_import
import click
import click_log
import json
import logging
import os
import sys
import traceback
from webfriend.browser import Chrome
from webfriend.scripting.parser.exceptions import UserError
from webfriend.scripting.environment import Environment
from webfriend.scripting.execute import execute_script
from webfriend.repl import REPL
from webfriend.utils.docs import document_commands

log = logging.getLogger()
err = logging.StreamHandler(stream=sys.stderr)
err.setFormatter(click_log.ColorFormatter())
log.addHandler(err)


@click.group(invoke_without_command=True)
@click.option('--interactive', '-I', is_flag=True, default=False)
@click.option('--suppress-output', '-o', is_flag=True, default=False)
@click.option('--no-temp-profile', '-T', is_flag=True, default=False)
@click.option('--generate-docs', is_flag=True, default=False)
@click.option('--only-document-plugins', is_flag=True, default=False)
@click.option('--omit-header', is_flag=True, default=False)
@click.option('--debug', '-D', is_flag=True, default=False)
@click.option(
    '--debugger-url', '-u',
    metavar='URL',
    help='The URL of the Chrome Remote Debugger to connect to.'
)
@click.option(
    '--log-level',
    '-L',
    default='WARNING'
)
@click.option(
    '--script-log-level',
    '-S',
    default='DEBUG'
)
@click.option(
    '--plugins', '-p',
    metavar='PLUGIN[,PLUGIN ..]',
    help='A comma-separated list of additional plugins to load'
)
@click.argument('script', type=click.File('rb'), required=False)
@click.argument('remainder', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def main(
    ctx,
    interactive,
    suppress_output,
    no_temp_profile,
    generate_docs,
    only_document_plugins,
    omit_header,
    debug,
    debugger_url,
    log_level,
    script_log_level,
    plugins,
    script,
    remainder
):
    log.setLevel(logging.getLevelName(log_level.upper()))

    if plugins:
        plugins = plugins.split(',')

    if generate_docs:
        click.echo('\n'.join(document_commands(
            plugins=plugins,
            only_plugins=only_document_plugins,
            omit_header=omit_header
        )))
    else:
        if debug:
            os.environ['WEBFRIEND_DEBUG'] = 'true'

        if not interactive and script is None and sys.stdin.isatty():
            raise IOError("Must provide the path to script to execute.")

        # using the with-syntax launches an instance of chrome in the background before proceeding
        with Chrome(
            debug_url=debugger_url,
            use_temp_profile=(not no_temp_profile)
        ) as chrome:
            environment = Environment(browser=chrome, log_level=script_log_level)

            if isinstance(plugins, list):
                for plugin in plugins:
                    environment.register_by_module_name(plugin)

            # interactive REPL
            if interactive:
                repl = REPL(chrome, environment=environment)
                repl.run()
            else:
                # by now we've validated that there is not a TTY waiting at stdin, so there
                # must be some data to read.  In that case, read the script from stdin.
                #
                # This let's users call `webfriend` by piping commands to it or by passing in heredocs
                #
                if script is None:
                    script = sys.stdin

                # execute script as file (or via shebang invocation)
                scope = execute_script(
                    chrome,
                    script.read(),
                    environment=environment
                ).as_dict()

            if not suppress_output:
                click.echo(json.dumps(scope, indent=4))


try:
    main()
except UserError as e:
    exit(e.exit_code)
except Exception as e:
    log.debug(traceback.format_exc())
    log.error(str(e))
    exit(1)
