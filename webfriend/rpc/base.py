"""
Implementation of the Chrome Remote DevTools debugging protocol.

See: https://chromedevtools.github.io/devtools-protocol
"""
from __future__ import absolute_import
from webfriend.rpc.event import Event
from uuid import uuid4
from collections import OrderedDict
import logging


class Base(object):
    supports_events = True
    domain = None

    def __init__(self, tab):
        if self.domain is None:
            raise ValueError("Cannot instantiate an RPC proxy without a domain class property.")

        self.tab       = tab
        self.callbacks = {}

    def initialize(self):
        pass

    def call(self, method, expect_reply=True, reply_timeout=None, **params):
        return self.tab.rpc(
            '{}.{}'.format(self.domain, method),
            expect_reply=expect_reply,
            reply_timeout=reply_timeout,
            **params
        )

    def enable(self):
        if self.supports_events:
            self.call('enable')

    def disable(self):
        if self.supports_events:
            self.call('disable')

    def call_boolean_response(self, method, field='result', **kwargs):
        if self.call(method, **kwargs).get(field) is True:
            return True

        return False

    def on(self, method, callback):
        # normalize method name
        if not method.startswith(self.domain + '.'):
            method = '{}.{}'.format(self.domain, method)

        # create handler dict if we need to
        if method not in self.callbacks:
            self.callbacks[method] = OrderedDict()

        callback_id = '{}.event_{}'.format(self.domain, uuid4())
        self.callbacks[method][callback_id] = callback

        logging.debug('Registered event handler {} for event {}'.format(
            callback_id,
            method
        ))

        return callback_id

    def remove_handler(self, callback_id):
        for _, callbacks in self.callbacks.items():
            for id, _ in callbacks.items():
                if callback_id == id:
                    del callbacks[callback_id]
                    return True

        return False

    def trigger(self, method, payload=None):
        event = Event(self, method, payload)

        if str(event) in self.callbacks:
            for callback_id, callback in self.callbacks[str(event)].items():
                if callable(callback):
                    response = callback(event)

                    if response is False:
                        break

        return event
