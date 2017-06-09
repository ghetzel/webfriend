from __future__ import absolute_import
from textx.model import model_root
from termcolor import colored
import re


class ScriptError(Exception):
    context_lines_before = 3
    context_lines_after = 3
    error_type = 'Error'

    def __init__(
        self,
        message,
        model=None,
        line=None,
        col=None,
        filename=None,
        data=None,
        **kwargs
    ):
        self.model = model
        self.line = line
        self.col = col
        self.filename = None

        # populate the lines list
        if isinstance(filename, basestring):
            self.filename = filename
            self.lines = open(filename).read().split('\n')

        elif isinstance(data, basestring):
            self.lines = data.split('\n')

        elif isinstance(model, object) and hasattr(model, '_tx_position'):
            root = model_root(model)

            if root and root._tx_metamodel:
                # determine line number and line position from absolute offsets
                line, col = root._tx_metamodel.parser.pos_to_linecol(
                    model._tx_position
                )

                if self.line is None:
                    self.line = line

                if self.col is None:
                    self.col = col

                # get the local Friendscript manager class from the root model,
                # then get the raw script data from there
                if root.manager and root.manager.data:
                    self.lines = root.manager.data.split('\n')
        else:
            self.lines = None

        self.message = self.prepare_message(message)

        super(ScriptError, self).__init__(self.message)

    def prepare_message(self, message):
        offending_char = None

        try:
            if self.lines and self.line and self.col:
                if self.line < len(self.lines):
                    offending_char = self.lines[self.line - 1][self.col - 1]
        except:
            pass

        if message.startswith('Expected ') and offending_char:
            message = "Unexpected character '{}'".format(offending_char)

        if self.lines and self.line and self.col:
            out = "{} on line {}, char {}\n".format(self.error_type, self.line, self.col)

            if self.filename:
                out += "  in file: {}\n".format(self.filename)

            if self.line <= len(self.lines):
                out += "Source:\n"
                start_line = (self.line - self.context_lines_before)
                end_line = (self.line + self.context_lines_after)

                if start_line < 1:
                    start_line = 1

                if len(self.lines) > 1:
                    if end_line >= len(self.lines):
                        end_line = len(self.lines) - 1
                else:
                    end_line = self.line

                for i in range(start_line, end_line + 1):
                    prefix = '   '
                    color = 'blue'
                    attrs = ['bold']

                    if i == self.line:
                        prefix = '>> '
                        color = 'yellow'
                        attrs = ['bold']

                    out += colored("{}{:4d}: {}\n".format(
                        prefix,
                        i,
                        self.lines[i - 1]
                    ), color, attrs=attrs)

                    if i == self.line:
                        out += colored("{}      {}{} {}\n".format(
                            prefix,
                            ' ' * (self.col - 1),
                            '^',
                            re.sub(r' at position.*', '', message)
                        ), 'red', attrs=attrs)
        else:
            out = "Syntax Error: {}".format(message)

        return out

    def __str__(self):
        return self.message


class SyntaxError(ScriptError):
    error_type = 'Syntax error'


class CommandExecutionError(ScriptError):
    error_type = 'Runtime error'
