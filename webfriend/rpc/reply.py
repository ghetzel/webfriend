from __future__ import absolute_import
import logging


class Reply(object):
    def __init__(self, reply, request=None, events=None):
        if not isinstance(reply, dict):
            raise AttributeError("Reply payload must be a dict")

        if 'id' not in reply:
            raise AttributeError("Reply payload must contain an 'id' field")

        if not isinstance(reply.get('result'), dict):
            reply['result'] = {}

        self.reply   = reply
        self.id      = reply['id']
        self.result  = reply['result']
        self.request = (request or {})
        self.events  = (events or [])

        logging.debug(' << [{:04d}] OK'.format(
            self.id
        ))

    def as_dict(self):
        return {
            'request':    self.request,
            'message_id': self.id,
            'reply':      self.reply,
            'events':     self.events,
        }

    def get(self, key, fallback=None):
        return self.result.get(key, fallback)

    def ievents(self, type=None):
        for event in self.events:
            if isinstance(type, basestring):
                if type != str(event):
                    continue

            yield event
