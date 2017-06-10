from __future__ import absolute_import
from __future__ import unicode_literals
import json
from webfriend.scripting.environment import Environment
from webfriend.scripting.execute import execute_script
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments
from prompt_toolkit.token import Token
from webfriend.scripting.parser.pygments import FriendscriptLexer
from pygments.styles.monokai import MonokaiStyle


class FriendscriptCompleter(Completer):
    def __init__(self, commands, *args, **kwargs):
        self.commands = commands
        super(FriendscriptCompleter, self).__init__(*args, **kwargs)

    def get_completions(self, document, complete_event):
        line = document.current_line.lstrip()

        for command in self.commands:
            if command.startswith(line):
                yield Completion(command, start_position=len(line) - len(command))


class REPL(object):
    prompt = '(friendscript) '

    def __init__(self, browser, scope):
        self.browser = browser
        self.scope = scope
        self.environment = Environment(self.scope, browser=self.browser)
        self.completer = FriendscriptCompleter(
            sorted(self.environment.get_command_names())
        )
        self.history = InMemoryHistory()
        self.last_result = None
        self.echo_results = True

    def get_last_result(self, cli):
        toolbar = []

        if isinstance(self.last_result, Exception):
            toolbar.append((Token.Error, str(self.last_result)))

        return toolbar

    def run(self):
        while True:
            line = prompt(
                '{}'.format(self.prompt),
                lexer=PygmentsLexer(FriendscriptLexer),
                style=style_from_pygments(MonokaiStyle, {
                    Token.Error: '#ansiwhite bg:#ansired',
                }),
                completer=self.completer,
                history=self.history,
                get_bottom_toolbar_tokens=self.get_last_result
            )

            try:
                self.last_result = execute_script(
                    self.browser,
                    line,
                    environment=self.environment,
                    preserve_state=True
                )

                self.scope = self.last_result
                self.environment.set_scope(self.scope)

                if self.echo_results:
                    print(json.dumps(self.last_result.as_dict(), indent=4))

            except Exception as e:
                self.last_result = e
                print(e)
