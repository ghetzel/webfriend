from __future__ import absolute_import
from webfriend.scripting.parser import MetaModel, to_value, exceptions, types


class ConditionalExpression(MetaModel):
    def evaluate(self, environment, scope=None):
        if scope is None:
            scope = environment.scope

        # Inline Assignment and test condition
        # ------------------------------------------------------------------------------------------
        if self.assignment:
            self.assignment.assign(environment, scope, force=True)

            # recursively evaluate the condition portion of the statement
            return self.condition.evaluate(environment, scope)

        # Command Evaluation (with optional test condition)
        # ------------------------------------------------------------------------------------------
        elif self.command:
            # execute the command
            resultkey, result = environment.execute(self.command, scope)

            # whatever the result of the expression command was, put it in the calling scope
            scope.set(resultkey, result, force=True)

            # if the statement has a condition, then evaluate using it
            if self.condition:
                # recursively evaluate the condition portion of the statement
                return self.condition.evaluate(environment, scope)
            else:
                # no condition, so just do the same thing as a unary comparison
                return self.compare(result)

        # Comparison
        # ------------------------------------------------------------------------------------------
        else:
            result = self.compare(
                to_value(self.lhs, scope),
                self.operator,
                to_value(self.rhs, scope)
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
                if isinstance(rhs, types.RegularExpression):
                    return rhs.is_match('{}'.format(lhs))

                elif hasattr(rhs, 'match'):
                    return (rhs.match('{}'.format(lhs)) is not None)

                else:
                    raise ValueError(
                        "Match operator must specify a regular expression on the right-hand side"
                    )

            elif operator == '!~':
                if isinstance(rhs, types.RegularExpression):
                    return not rhs.is_match('{}'.format(lhs))

                elif hasattr(rhs, 'match'):
                    return (rhs.match('{}'.format(lhs)) is None)

                else:
                    raise ValueError(
                        "Unmatch operator must specify a regular expression on the right-hand side"
                    )

            elif operator == 'in':
                return (lhs in rhs)

            elif operator == 'notin':
                return (lhs not in rhs)

            else:
                raise exceptions.ScriptError("Unsupported operator '{}'".format(operator))

        elif lhs:
            return True

        return False


class IfElseBlock(MetaModel):
    def get_blocks(self, environment, scope=None):
        if self.if_expr.expression.evaluate(environment, scope=scope):
            return self.if_expr.blocks

        for elseif in self.elseif_expr:
            if elseif.statement.expression.evaluate(environment, scope=scope):
                return elseif.statement.blocks

        if self.else_expr:
            return self.else_expr.blocks

        return []
