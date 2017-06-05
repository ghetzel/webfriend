from __future__ import absolute_import
from textx.metamodel import metamodel_from_file
import textx.exceptions
import textx
import os


def to_value(value, scope):
    # expand variables into values first
    if isinstance(value, variables.Variable):
        value = value.resolve(scope)

    # do type detection and extraction
    if isinstance(value, types.String):
        value = value.value.decode('UTF-8')

    elif isinstance(value, types.Array):
        value = [to_value(v, scope) for v in value.values]

    elif isinstance(value, types.Object):
        value = dict([
            (k, to_value(v, scope)) for k, v in value.as_dict().items()
        ])

    elif isinstance(value, float):
        if int(value) == value:
            value = int(value)

    elif isinstance(value, str):
        value = value.decode('UTF-8')

    # null become None
    if value == 'null':
        return None

    return value


from .lang import MetaModel  # noqa
from . import commands, conditions, exceptions, lang, loops, types, variables  # noqa


class Friendscript(object):
    def __init__(self, filename=None, data=None, commandset=None):
        self.model = None
        self.data = None
        self.commandset = commandset

        try:
            self.metamodel = metamodel_from_file(
                os.path.join(
                    os.path.dirname(__file__),
                    'grammar.tx'
                ),
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
                    types.String,
                    variables.Assignment,
                    variables.CommandID,
                    variables.Variable,
                ]
            )

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
