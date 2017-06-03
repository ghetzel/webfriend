from __future__ import absolute_import


class MetaModel(object):
    def __init__(self, parent, **kwargs):
        self.parent = parent

        for k, v in kwargs.items():
            setattr(self, k, v)


class Directive(MetaModel):
    pass


class LinearExecutionBlock(MetaModel):
    pass


class EventHandlerBlock(MetaModel):
    pass


class Expression(MetaModel):
    pass
