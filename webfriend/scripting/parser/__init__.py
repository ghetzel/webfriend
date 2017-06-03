from __future__ import absolute_import
from textx.metamodel import metamodel_from_str
import textx.exceptions
from textx.model import model_root
from .grammar import generate_grammar
from collections import OrderedDict
import re
import copy
from termcolor import colored


class FlowControlMultiLevel(Exception):
    def __init__(self, message, levels=1, **kwargs):
        self.levels = levels
        super(FlowControlMultiLevel, self).__init__(message, **kwargs)


class FlowControlBreak(FlowControlMultiLevel):
    pass


class FlowControlContinue(FlowControlMultiLevel):
    pass


def to_value(value, scope):
    if str(value) == 'null':
        return None

    elif isinstance(value, Variable):
        value = value.resolve(scope)

    if isinstance(value, Array):
        value = [to_value(v, scope) for v in value.values]
    elif isinstance(value, Object):
        value = dict([
            (k, to_value(v, scope)) for k, v in value.as_dict().items()
        ])
    elif isinstance(value, float):
        if int(value) == value:
            value = int(value)
    elif isinstance(value, str):
        value = value.decode('UTF-8')

    return value


class ScriptError(Exception):
    context_lines_before = 3
    context_lines_after = 3

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

                self.line = line
                self.col = col

                # get the local Friendscript manager class from the root model,
                # then get the raw script data from there
                if root.manager and root.manager.data:
                    self.lines = root.manager.data.split('\n')
        else:
            self.lines = None

        message = self.prepare_message(message)
        self.message = message

        super(ScriptError, self).__init__(message)

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

        return message

    def __str__(self):
        if self.lines and self.line and self.col:
            out = "Syntax error on line {}, char {}\n".format(self.line, self.col)

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
                            re.sub(r' at position.*', '', self.message)
                        ), 'red', attrs=attrs)
        else:
            out = "Syntax Error: {}".format(self.message)

        return out


class MetaModel(object):
    def __init__(self, parent, **kwargs):
        self.parent = parent

        for k, v in kwargs.items():
            setattr(self, k, v)


class Array(MetaModel):
    pass


class Object(object):
    def __init__(self, parent, items=[]):
        self.parent = parent
        self.items  = items
        self._data  = OrderedDict()

        for kv in items:
            if not len(kv.values):
                continue

            if len(kv.values) == 1:
                self._data[kv.name] = kv.values[0]
            else:
                self._data[kv.name] = kv.values

    def to_json(self):
        return self.as_dict()

    def as_dict(self):
        return self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]


class Assignment(MetaModel):
    def assign(self, scope, force=False):
        sources_consumed = 0
        sources = self.sources

        # provide support for unpacking lists and tuples into multiple variables
        if len(self.destinations) > 1:
            if len(self.sources) == 1:
                first_source = to_value(self.sources[0], scope)

                if isinstance(first_source, (list, tuple)):
                    sources = first_source

        # for each source value
        for i, source in enumerate(sources):
            # if there is a destination for it
            if i < len(self.destinations):
                destination = self.destinations[i]

                if not destination.skip:
                    source = to_value(source, scope)

                    # assignments are BY VALUE (e.g.: always incur a copy)
                    scope.set(destination.name, copy.copy(source), force=force)

                sources_consumed += 1

        # null out the remaining destinations
        if len(self.destinations) > sources_consumed:
            for unset_destination in self.destinations[sources_consumed:]:
                if not unset_destination.skip:
                    scope.set(unset_destination.name, None, force=force)


class CommandStanza(object):
    def __init__(self, parent, options):
        self.parent     = parent
        self.options    = (options or {})

    def as_dict(self):
        out = {}

        for kv in self.options:
            if not len(kv.values):
                continue

            if len(kv.values) == 1:
                out[kv.name] = kv.values[0]
            else:
                out[kv.name] = kv.values

        return out


class Expression(MetaModel):
    def resolve_segment_to_value(self, expr_segment, scope):
        if expr_segment is not None:
            if expr_segment.value:
                return expr_segment.value

            elif expr_segment.variable:
                return expr_segment.variable.resolve(scope)

        return None

    def evaluate(self, commandset, scope=None):
        if scope is None:
            scope = commandset.scope

        # Inline Assignment and test condition
        # ------------------------------------------------------------------------------------------
        if self.assignment:
            self.assignment.assign(scope, force=True)

            # recursively evaluate the condition portion of the statement
            return self.condition.evaluate(commandset, scope)

        # Command Evaluation (with optional test condition)
        # ------------------------------------------------------------------------------------------
        elif self.command:
            # execute the command
            resultkey, result = commandset.execute(self.command, scope)

            # whatever the result of the expression command was, put it in the calling scope
            scope.set(resultkey, result, force=True)

            # if the statement has a condition, then evaluate using it
            if self.condition:
                # recursively evaluate the condition portion of the statement
                return self.condition.evaluate(commandset, scope)
            else:
                # no condition, so just do the same thing as a unary comparison
                return self.compare(result)

        # Comparison
        # ------------------------------------------------------------------------------------------
        else:
            result = self.compare(
                self.resolve_segment_to_value(self.lhs, scope),
                self.operator,
                self.resolve_segment_to_value(self.rhs, scope)
            )

        if self.negate is True:
            return not result
        else:
            return result

    def compare(self, lhs, operator=None, rhs=None):
        if operator is not None:
            if operator == '==':
                if rhs is None:
                    return (lhs is None)
                else:
                    return (lhs == rhs)

            elif operator == '!=':
                if rhs is None:
                    return (lhs is not None)
                else:
                    return (lhs != rhs)

            elif operator == '<':
                return (lhs < rhs)

            elif operator == '<=':
                return (lhs <= rhs)

            elif operator == '>':
                return (lhs > rhs)

            elif operator == '>=':
                return (lhs >= rhs)

            elif operator == '=~':
                return not (re.match('{}'.format(rhs), '{}'.format(lhs)) is None)

            elif operator == 'in':
                return (lhs in rhs)

            elif operator == 'not in':
                return (lhs not in rhs)

            else:
                raise ScriptError("Unsupported operator '{}'".format(operator))

        elif lhs:
            return True

        return False


class LinearExecutionBlock(MetaModel):
    pass


class IfElseBlock(MetaModel):
    def get_blocks(self, commandset, scope=None):
        if self.if_expr.expression.evaluate(commandset, scope=scope):
            return self.if_expr.blocks

        for elseif in self.elseif_expr:
            if elseif.statement.expression.evaluate(commandset, scope=scope):
                return elseif.statement.blocks

        if self.else_expr:
            return self.else_expr.blocks

        return []


class LoopBlock(MetaModel):
    def execute_loop(self, commandset, scope=None):
        if scope is None:
            scope = commandset.scope

        i = 0

        if self.iterable:
            loop = self.iterable

            if isinstance(loop.iterator, Variable):
                iter_value = to_value(loop.iterator, scope)
            else:
                _, iter_value = commandset.execute(loop.iterator, scope=scope)

            try:
                if isinstance(iter_value, dict):
                    iter_value = iter_value.items()

                if not iter_value:
                    return

                for item in iter(iter_value):
                    if len(loop.variables) > 1 and isinstance(item, tuple):
                        # unpack iter items into the variables we were given
                        for var_i, var in enumerate(loop.variables[0:len(item)]):
                            if not var.skip:
                                if var_i < len(item):
                                    scope.set(var.name, item[var_i], force=True)

                        # null out any remaining variables
                        if len(loop.variables) > len(item):
                            for var in loop.variables[len(item):]:
                                scope.set(var.name, None, force=True)

                    else:
                        scope.set(loop.variables[0].name, item, force=True)

                    scope.set('index', i, force=True)

                    for result in self.iterate_blocks(i, commandset, scope):
                        yield result

                    i += 1

            except TypeError:
                raise TypeError("Cannot loop on result of {}".format(loop.iterator))

        elif self.bounded:
            loop = self.bounded
            commandset.execute(loop.initial, scope=scope)

            while loop.termination.evaluate(commandset, scope=scope):
                scope.set('index', i, force=True)

                for result in self.iterate_blocks(i, commandset, scope):
                    yield result

                commandset.execute(loop.next, scope=scope)
                i += 1

        elif self.truthy:
            loop = self.truthy

            while loop.termination.evaluate(commandset, scope=scope):
                scope.set('index', i, force=True)

                for result in self.iterate_blocks(i, commandset, scope):
                    yield result

                i += 1

        elif self.fixedlen:
            loop = self.fixedlen

            if isinstance(loop.count, Variable):
                count = int(loop.count.resolve(scope))
            else:
                count = loop.count

            for _ in range(count):
                scope.set('index', i, force=True)

                for result in self.iterate_blocks(i, commandset, scope):
                    yield result

                i += 1

        else:
            while True:
                scope.set('index', i, force=True)

                for result in self.iterate_blocks(i, commandset, scope):
                    yield result

                i += 1

    def iterate_blocks(self, i, commandset, scope):
        for subblock in self.blocks:
            yield i, commandset, subblock, scope


class CommandSequence(MetaModel):
    pass


class FlowControlWord(MetaModel):
    pass


class Directive(MetaModel):
    pass


class Variable(MetaModel):
    def resolve(self, scope, fallback=None):
        if self.skip:
            return fallback

        value = scope.get(self.name, fallback)

        return to_value(value, scope)


class CommandID(MetaModel):
    def resolve(self, scope):
        if self.variable:
            return self.variable.resolve(scope)

        return to_value(self.value, scope)


class EventHandlerBlock(MetaModel):
    pass


class Friendscript(object):
    def __init__(self, filename=None, data=None, commandset=None):
        self.model = None
        self.data = None
        self.commandset = commandset

        try:
            self.metamodel = metamodel_from_str(
                generate_grammar(),
                classes=[
                    Array,
                    Assignment,
                    CommandID,
                    CommandSequence,
                    CommandStanza,
                    Directive,
                    EventHandlerBlock,
                    Expression,
                    FlowControlWord,
                    IfElseBlock,
                    LinearExecutionBlock,
                    LoopBlock,
                    Object,
                    Variable,
                ]
            )

            if isinstance(data, basestring):
                self.loads(data)

            elif isinstance(filename, basestring):
                self.load_file(filename)

        except textx.exceptions.TextXSyntaxError as e:
            raise ScriptError(
                str(e),
                filename=filename,
                data=data,
                line=e.line,
                col=e.col
            )

        # and tell the model who we are
        self.model.manager = self

    def load_file(self, filename):
        self.model = self.metamodel.model_from_file(filename)
        self.data = open(filename).read()

    def loads(self, data):
        self.model = self.metamodel.model_from_str(data)
        self.data = data

    def blocks_by_type(self, metatypes):
        if isinstance(self.model, basestring):
            return []

        return [
            b for b in self.model.blocks if isinstance(b, metatypes)
        ]

    def get_item_position(self, item):
        if not hasattr(item, '_tx_position'):
            raise ValueError("Must specify a textx model object")

        return self.metamodel.parser.pos_to_linecol(item._tx_position)

    @property
    def blocks(self):
        return self.blocks_by_type(
            tuple(LinearExecutionBlock._tx_inh_by)
        )

    @property
    def handlers(self):
        return self.blocks_by_type(EventHandlerBlock)
