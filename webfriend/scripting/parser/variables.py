from __future__ import absolute_import
from . import MetaModel, to_value
import copy


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
                    scope.set(destination.name, copy.copy(source), force=force)

                sources_consumed += 1

        # null out the remaining destinations
        if len(self.destinations) > sources_consumed:
            for unset_destination in self.destinations[sources_consumed:]:
                if not unset_destination.skip:
                    scope.set(unset_destination.name, None, force=force)
