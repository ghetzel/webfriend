from __future__ import absolute_import
from . import to_value


class MetaModel(object):
    def __init__(self, parent, **kwargs):
        self.parent = parent

        for k, v in kwargs.items():
            if isinstance(v, list):
                v = tuple(v)

            setattr(self, k, v)


class Directive(MetaModel):
    pass


class LinearExecutionBlock(MetaModel):
    pass


class EventHandlerBlock(MetaModel):
    pass


# Expression:
#     lhs=Variable operator=Operator rhs=VariableOrType
# ;
# NumericOperator:
#     (
#         add='+' |
#         subtract='-' |
#         multiply='*' |
#         divide='/' |
#         modulus='%' |
#         power='**'
#     )
# ;

# LogicOperator:
#     (
#         bitwise_and='&' |
#         bitwise_or='|' |
#         bitwise_not='~'
#     )
# ;

# AssignmentOperator:
#     (
#         plus_eq='+=' |
#         minus_eq='-=' |
#         multi_eq='*=' |
#         div_eq='/=' |
#         and_eq='&=' |
#         or_eq='|=' |
#         append='<<'
#     )
# ;
class Expression(MetaModel):
    def process(self, scope, preserve_types=False):
        lhs = to_value(self.lhs, scope)
        op = self.operator

        if op is not None:
            rhs = to_value(self.rhs, scope)

            if op.power:
                return lhs ** rhs, None
            elif op.bitwise_not:
                return ~rhs, None
            elif op.multiply:
                return lhs * rhs, None
            elif op.divide:
                return lhs / rhs, None
            elif op.modulus:
                return lhs & rhs, None
            elif op.add:
                return lhs + rhs, None
            elif op.subtract:
                return lhs - rhs, None
            elif op.bitwise_and:
                return lhs & rhs, None
            elif op.bitwise_xor:
                return lhs ^ rhs, None
            elif op.bitwise_or:
                return lhs | rhs, None

            return None, None

        if preserve_types:
            return self.lhs, None
        else:
            return lhs, None
