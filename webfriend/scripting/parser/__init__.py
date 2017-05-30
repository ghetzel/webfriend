from __future__ import absolute_import
from textx.metamodel import metamodel_from_str
import textx.exceptions
from .grammar import generate_grammar
from collections import OrderedDict
import re
from ..scope import Scope


class SyntaxError(Exception):
    pass


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
        return self.__dict__()

    def __dict__(self):
        return self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]


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

        # if this expression is a command, then we need to execute it and evaluate
        # the result
        if self.command:
            # execute the command
            result = commandset.execute(self.command, scope)

            # if the statement has a condition, then evaluate using it
            if self.condition:
                # get custom resultkey, if specified
                if self.command.resultkey:
                    resultkey = self.command.resultkey
                else:
                    resultkey = commandset.DEFAULT_RESULT_KEY

                # evaluate the given condition with a new scope that sets the
                # resultkey to the command's result value
                return self.condition.evaluate(commandset, Scope({
                    resultkey: result,
                }, parent=scope))
            else:
                # no condition, so just do the same thing as a unary if-statement
                return self.compare(result)
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
                raise SyntaxError("Unsupported operator '{}'".format(operator))

        elif lhs:
            return True

        return False


class LinearExecutionBlock(MetaModel):
    pass


class IfElseBlock(MetaModel):
    def get_command_sequence(self, commandset):
        if self.if_expr.expression.evaluate(commandset):
            return self.if_expr.sequence

        for elseif in self.elseif_expr:
            if elseif.statement.expression.evaluate(commandset):
                return elseif.statement.sequence

        if self.else_expr:
            return self.else_expr.sequence

        return None


class CommandSequence(MetaModel):
    pass


class Variable(MetaModel):
    def resolve(self, scope, fallback=None):
        if self.name:
            return scope.get(self.name, fallback)


class CommandID(MetaModel):
    def resolve(self, scope):
        if self.variable:
            return self.variable.resolve(scope)

        return self.value


class EventHandlerBlock(MetaModel):
    pass


class AutomationScript(object):
    def __init__(self, filename=None, data=None, commands=None):
        self.model = None

        try:
            self.metamodel = metamodel_from_str(
                generate_grammar(commands or []),
                classes=[
                    Array,
                    CommandID,
                    CommandSequence,
                    CommandStanza,
                    EventHandlerBlock,
                    Expression,
                    IfElseBlock,
                    LinearExecutionBlock,
                    Object,
                    Variable,
                ]
            )
        except textx.exceptions.TextXSyntaxError as e:
            raise SyntaxError(str(e))

        if isinstance(data, basestring):
            self.loads(data)

        elif isinstance(filename, basestring):
            self.load_file(filename)

    def load_file(self, filename):
        self.model = self.metamodel.model_from_file(filename)

    def loads(self, data):
        self.model = self.metamodel.model_from_str(data)

    def blocks_by_type(self, metatypes):
        if self.model is None:
            return []

        return [b for b in self.model.blocks if isinstance(b, metatypes)]

    @property
    def blocks(self):
        return self.blocks_by_type(
            tuple(LinearExecutionBlock._tx_inh_by)
        )

    @property
    def handlers(self):
        return self.blocks_by_type(EventHandlerBlock)
