from __future__ import absolute_import
from webfriend.scripting.parser import MetaModel, to_value
import copy


class Variable(MetaModel):
    def as_key(self, scope):
        parts = tuple()

        for part in self.parts:
            if len(part.key):
                parts = parts + (part.key.decode('UTF-8'),)

            if part.index is not None:
                index = to_value(part.index, scope)

                if index is not None:
                    parts = parts + (index,)

        return parts

    def resolve(self, scope, fallback=None):
        if self.skip:
            return fallback

        value = scope.get(self.as_key(scope), fallback)

        return to_value(value, scope)


class CommandID(MetaModel):
    def resolve(self, scope):
        if self.variable:
            return self.variable.resolve(scope)

        return to_value(self.value, scope)


class Assignment(MetaModel):
    def assign(self, environment, scope, force=False):
        sources_consumed = 0
        sources = self.sources

        # provide support for unpacking lists and tuples into multiple variables
        if len(self.destinations) > 1:
            if len(self.sources) == 1:
                first_source = environment.interpolate(self.sources[0], scope=scope)

                if isinstance(first_source, (list, tuple)):
                    sources = first_source

        # for each source value
        for i, source in enumerate(sources):
            # if there is a destination for it
            if i < len(self.destinations):
                destination = self.destinations[i]

                if not destination.skip:
                    source = environment.interpolate(source, scope=scope)

                    # assignments are BY VALUE (e.g.: always incur a copy)
                    if self.op.eq:
                        value = copy.copy(source)

                    elif self.op.append:
                        value = scope.get(destination.as_key(scope))

                        if not isinstance(value, list):
                            value = [value]

                        value.append(copy.copy(source))
                    else:
                        value = scope.get(destination.as_key(scope), 0)
                        rhs = copy.copy(source)

                        if self.op.multi_eq:
                            value = value * rhs
                        elif self.op.div_eq:
                            value = value / rhs
                        elif self.op.plus_eq:
                            value = value + rhs
                        elif self.op.minus_eq:
                            value = value - rhs
                        elif self.op.and_eq:
                            value = value * rhs
                        elif self.op.or_eq:
                            value = value | rhs

                    scope.set(
                        destination.as_key(scope),
                        value,
                        force=force
                    )

                sources_consumed += 1

        # null out the remaining destinations
        if len(self.destinations) > sources_consumed:
            for unset_destination in self.destinations[sources_consumed:]:
                if not unset_destination.skip:
                    scope.set(
                        unset_destination.as_key(scope),
                        None,
                        force=force
                    )
