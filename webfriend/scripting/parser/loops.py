from __future__ import absolute_import
from webfriend.scripting.parser import MetaModel, to_value, variables


class LoopBlock(MetaModel):
    def execute_loop(self, environment, scope=None):
        if scope is None:
            scope = environment.scope

        i = 0

        if self.iterable:
            loop = self.iterable

            if isinstance(loop.iterator, variables.Variable):
                iter_value = to_value(loop.iterator, scope)
            else:
                _, iter_value = environment.execute(loop.iterator, scope=scope)

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
                                    scope.set(var.as_key(scope), item[var_i], force=True)

                        # null out any remaining variables
                        if len(loop.variables) > len(item):
                            for var in loop.variables[len(item):]:
                                scope.set(var.as_key(scope), None, force=True)

                    else:
                        scope.set(loop.variables[0].as_key(scope), item, force=True)

                    scope.set('index', i, force=True)

                    for result in self.iterate_blocks(i, environment, scope):
                        yield result

                    i += 1

            except TypeError:
                raise TypeError("Cannot loop on result of {}".format(loop.iterator))

        elif self.bounded:
            loop = self.bounded
            environment.execute(loop.initial, scope=scope)

            while loop.termination.evaluate(environment, scope=scope):
                scope.set('index', i, force=True)

                for result in self.iterate_blocks(i, environment, scope):
                    yield result

                environment.execute(loop.next, scope=scope)
                i += 1

        elif self.truthy:
            loop = self.truthy

            while loop.termination.evaluate(environment, scope=scope):
                scope.set('index', i, force=True)

                for result in self.iterate_blocks(i, environment, scope):
                    yield result

                i += 1

        elif self.fixedlen:
            loop = self.fixedlen
            count = int(to_value(loop.count, scope))

            for _ in range(count):
                scope.set('index', i, force=True)

                for result in self.iterate_blocks(i, environment, scope):
                    yield result

                i += 1

        else:
            while True:
                scope.set('index', i, force=True)

                for result in self.iterate_blocks(i, environment, scope):
                    yield result

                i += 1

    def iterate_blocks(self, i, environment, scope):
        for subblock in self.blocks:
            yield i, environment, subblock, scope


class FlowControlWord(MetaModel):
    pass


class FlowControlMultiLevel(Exception):
    def __init__(self, message, levels=1, **kwargs):
        self.levels = levels
        super(FlowControlMultiLevel, self).__init__(message, **kwargs)


class FlowControlBreak(FlowControlMultiLevel):
    pass


class FlowControlContinue(FlowControlMultiLevel):
    pass
