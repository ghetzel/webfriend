from __future__ import absolute_import
from textx.metamodel import metamodel_from_str
import textx.exceptions
import textx
from webfriend.scripting.parser.grammar import FRIENDSCRIPT_GRAMMAR


def to_value(value, scope, preserve_strings=False):
    # expand variables into values first
    if isinstance(value, variables.Variable):
        value = value.resolve(scope)

    # evaluate expressions
    if isinstance(value, lang.Expression):
        value, _ = value.process(scope)

    # if we're told to, return string classes directly (for interpolation)
    if preserve_strings and isinstance(value, (types.StringLiteral, types.Heredoc)):
        return value

    # do type detection and extraction
    elif isinstance(value, types.Array):
        value = [to_value(v, scope) for v in value.values]

    elif isinstance(value, types.Object):
        value = dict([
            (k, to_value(v, scope)) for k, v in value.as_dict().items()
        ])

    elif isinstance(value, float):
        if int(value) == value:
            value = int(value)

    if isinstance(value, str):
        value = value.decode('UTF-8')

    # null become None
    if value == 'null':
        return None

    return value


from .lang import MetaModel  # noqa
from . import commands, conditions, exceptions, lang, loops, types, variables  # noqa


class Friendscript(object):
    def __init__(self, filename=None, data=None, environment=None):
        self.model = None
        self.data = None
        self.environment = environment

        try:
            self.metamodel = metamodel_from_str(
                FRIENDSCRIPT_GRAMMAR,
                classes=[
                    commands.CommandSequence,
                    commands.CommandStanza,
                    conditions.ConditionalExpression,
                    conditions.IfElseBlock,
                    lang.Directive,
                    lang.EventHandlerBlock,
                    lang.Expression,
                    lang.LinearExecutionBlock,
                    loops.FlowControlWord,
                    loops.LoopBlock,
                    types.Array,
                    types.Object,
                    types.RegularExpression,
                    variables.Assignment,
                    variables.CommandID,
                    variables.Variable,
                ],
                match_filters={
                    'StringLiteral':      types.StringLiteral,
                    'StringInterpolated': types.StringInterpolated,
                    'Heredoc':            types.Heredoc,
                },
            )
        except textx.exceptions.TextXSyntaxError as e:
            raise

        try:
            if isinstance(data, basestring):
                self.loads(data)

            elif isinstance(filename, basestring):
                self.load_file(filename)

        except textx.exceptions.TextXSyntaxError as e:
            raise exceptions.SyntaxError(
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
            tuple(lang.LinearExecutionBlock._tx_inh_by)
        )

    @property
    def handlers(self):
        return self.blocks_by_type(lang.EventHandlerBlock)
