from __future__ import absolute_import
from __future__ import unicode_literals
from webfriend.rpc import (
    Base,
    Browser,
    Console,
    DOM,
    Emulation,
    Input,
    Network,
    Overlay,
    Page,
    Reply,
    Runtime,
    Target,
)
import json
import time
from webfriend import exceptions
from webfriend.utils import patch_json  # noqa
import websocket
import logging
from Queue import Queue, Empty, Full
from threading import Thread

ANY_KEY = 'ANY'


class Tab(object):
    default_width  = 0
    default_height = 0

    def __init__(
        self,
        browser,
        description,
        domains=None,
        width=None,
        height=None,
        frame_id=None,
        callbacks=True,
        autoresize=True
    ):
        if not isinstance(description, dict):
            raise AttributeError("Tab descriptor must be a dict")

        if 'webSocketDebuggerUrl' not in description:
            raise AttributeError("Cannot operate on tab without a webSocketDebuggerUrl")

        if width is None:
            width = self.default_width

        if height is None:
            height = self.default_height

        self.browser           = browser
        self.frame_id          = frame_id
        self.description       = description
        self.message_id        = 0
        self.socket            = websocket.create_connection(self.wsurl)
        self.waiters           = {}
        self.triggerqueue      = Queue()
        self.last_event_m      = {}
        self.last_event_t      = {}
        self._network_requests = {}
        self.g_recv_ctl        = Queue(1)
        self.g_recv            = Thread(target=self.receive_messages, args=(self.g_recv_ctl,))
        self.replies           = {}
        self.initial_w         = width
        self.initial_h         = height
        self.msg_enable        = False
        self.netreq_tracking   = True
        self._trigger_worker   = None

        # setup and enable all the RPC domains we support
        self.page              = Page(self)
        self.dom               = DOM(self)
        self.console           = Console(self)
        self.emulation         = Emulation(self)
        self.input             = Input(self)
        self.network           = Network(self)
        self.runtime           = Runtime(self)
        self.window            = Browser(self)
        self.overlay           = Overlay(self)
        self.target            = Target(self)

        # start the receive thread
        self.g_recv.start()

        for domain in self.rpc_domains:
            domain.initialize()

        # setup internal callbacks
        if callbacks:
            self.setup_callbacks()

        # perform initial calls
        if autoresize:
            if self.initial_w or self.initial_h:
                self.emulation.set_device_metrics_override(
                    width=self.initial_w,
                    height=self.initial_h,
                )

    @property
    def url(self):
        return self.description.get('url')

    @property
    def wsurl(self):
        return self.description.get('webSocketDebuggerUrl')

    @property
    def rpc_domains(self):
        instances = []

        for k in dir(self):
            if k == 'rpc_domains':
                continue

            attr = getattr(self, k)

            if isinstance(attr, Base):
                instances.append(attr)

        return instances

    def as_dict(self):
        return {
            'id': self.frame_id,
            'url': self.url,
            'webSocketDebuggerUrl': self.wsurl,
            'target': (self.frame_id == self.browser.default_tab),
        }

    def enable_events(self):
        for domain in self.rpc_domains:
            domain.enable()

    def enable_console_messages(self):
        self.msg_enable = True

    def disable_console_messages(self):
        self.msg_enable = False

    def enable_network_request_tracking(self):
        self.netreq_tracking = True

    def disable_network_request_tracking(self):
        self.netreq_tracking = False

    def stop(self):
        if self.g_recv.is_alive():
            logging.debug('Sending stop to receive thread')
            self.g_recv_ctl.put(StopIteration)
            self.socket.close()

        while self.g_recv.is_alive():
            logging.debug('Waiting for receive thread...')
            time.sleep(1)

    def send(self, data, expect_reply=True, reply_timeout=None, context=None):
        if not isinstance(data, dict):
            raise AttributeError("Data must be a dict")

        if not reply_timeout:
            reply_timeout = 10000

        # increment and include message ID
        self.message_id += 1
        data['id'] = self.message_id

        body = json.dumps(data)

        try:
            request_handle = {
                'id':    data['id'],
                'reply': Queue(1),
            }

            self.replies[data['id']] = request_handle

            # send the request to the Remote Debugger
            logging.debug(' >> [{:04d}] {} {}'.format(
                data['id'],
                data['method'],
                ' '.join([
                    '{}={}'.format(k, v) for k, v in data.get('params', {}).items()
                ])
            ))

            # send the request
            self.socket.send(body)

            # block until the receive loop says so
            if expect_reply:
                try:
                    reply, events = request_handle['reply'].get(timeout=(reply_timeout / 1e3))
                except Empty:
                    raise exceptions.TimeoutError("Timed out waiting for reply to command '{}', id={}".format(
                        data['method'],
                        data['id']
                    ))

                # if there was an exception, raise it now
                if isinstance(reply, Exception):
                    raise reply

                # make sure the IDs match
                if reply['id'] == data['id']:
                    return Reply(reply, request=data, events=events)
                else:
                    raise exceptions.ProtocolError("Reply Message ID does not match Request Message ID")

            else:
                return None

        finally:
            del self.replies[data['id']]

    def dispatch_event(self, message):
        if message is StopIteration:
            logging.info('Sending stop to trigger thread')
            self.triggerqueue.put((None, None, StopIteration))
        else:
            domain, method = message.get('method').split('.', 1)
            payload = message.get('params', {})

            try:
                proxy = self.get_domain_instance(domain)
            except ValueError:
                logging.exception('Unhandled Event Type')
                return

            self.triggerqueue.put((proxy, method, payload))

    def trigger_worker(self):
        while True:
            proxy, method, payload = self.triggerqueue.get()

            if payload is StopIteration:
                logging.debug('Stopping trigger thread')
                return

            event = proxy.trigger(method, payload)
            event_name = str(event)

            if event:
                logging.debug(' >> [ .. ] EVENT: {}'.format(
                    event
                ))

                # record the current time as the last time we saw an event of this type
                now = time.time()
                self.last_event_m[str(event)] = now
                self.last_event_t = now

                # attempt to send this event to whoever is waiting for it
                if event_name in self.waiters:
                    try:
                        self.waiters[event_name].put(event)
                    except Full:
                        pass

                if ANY_KEY in self.waiters:
                    try:
                        self.waiters[ANY_KEY].put(event)
                    except Full:
                        pass

    def dispatch_reply(self, request_id, message, events):
        if request_id in self.replies:
            self.replies[request_id]['reply'].put((message, events))
        else:
            logging.warning('Received message without a sender (id={})'.format(request_id))

    def receive_messages(self, controlq):
        self._trigger_worker = Thread(target=self.trigger_worker)
        self._trigger_worker.start()

        while True:
            try:
                try:
                    if controlq.get_nowait() is StopIteration:
                        raise
                except Empty:
                    pass

                message = self.receive()

                if message is None:
                    continue

                # print(json.dumps(message, indent=4))

                if isinstance(message, Exception):
                    self.dispatch_reply(message.id, message, [])

                elif 'id' in message:
                    self.dispatch_reply(message['id'], message, [])

                else:
                    self.dispatch_event(message)

            except (KeyboardInterrupt, StopIteration, websocket.WebSocketException) as e:
                logging.debug('Fatal receive message: {}'.format(e))
                break

        self.dispatch_event(StopIteration)
        logging.info('Stopping receive thread')

    def receive(self, timeout=10):
        message = self.socket.recv()

        if message is not None:
            body = json.loads(message)
            exc = None

            if 'error' in body:
                if isinstance(body['error'], dict):
                    error = body['error']

                    message = error.get('message', 'Unknown Error')

                    if 'data' in error:
                        message += ' - {}'.format(error['data'])

                    exc = exceptions.ProtocolError(
                        'Protocol Error {}: {}'.format(error.get('code', -1), message)
                    )
                else:
                    exc = exceptions.ProtocolError('Malformed Error Response')

            if exc is not None:
                exc.id = body.get('id')
                return exc

            return body

        else:
            return None

    def wait_for_caller_response(self, event_name, timeout=30000):
        """
        Yields events of
        Block until a specific event is received, or until **timeout** elapses (whichever comes first).

        #### Arguments

        - **event_name** (`str`):

            The name of the event to wait for.

        - **timeout** (`int`):

            The timeout, in milliseconds, before raising a `webfriend.exceptions.TimeoutError`.

        #### Returns
        `webfriend.rpc.event.Event`

        #### Raises
        `webfriend.exceptions.TimeoutError`
        """

        # get or create the async result for this event
        if event_name not in self.waiters:
            result = Queue(1)
            self.waiters[event_name] = result
        else:
            result = self.waiters[event_name]

        try:
            event = result.get(timeout=(timeout / 1e3))
            accepted = yield event

            # generator received a response from the caller
            if accepted is not None:
                return

        except Empty:
            raise exceptions.TimeoutError("Timed out waiting for events")

        finally:
            del self.waiters[event_name]

    def wait_for(self, event_name, **kwargs):
        """
        Block until a specific event is received, or until **timeout** elapses (whichever comes first).

        #### Arguments

        - **event_name** (`str`):

            The name of the event to wait for.

        - **timeout** (`int`):

            The timeout, in milliseconds, before raising a `webfriend.exceptions.TimeoutError`.

        #### Returns
        `webfriend.rpc.event.Event`

        #### Raises
        `webfriend.exceptions.TimeoutError`
        """
        wfc = self.wait_for_caller_response(event_name, **kwargs)
        started_at = time.time()

        for event in wfc:
            try:
                wfc.send(True)
            except StopIteration:
                pass

            return {
                'sequence': [event],
                'duration': (time.time() - started_at),
            }

    def wait_for_idle(self, idle, events=[], timeout=30000, poll_interval=250):
        """
        Blocks for a specified amount of time _after_ an event has been received, or until
        **timeout** elapses (whichever comes first).

        This is useful for waiting for events to occur after performing an action, then giving some
        amount of time for those events to "settle" (e.g.: allowing the page time to react to those
        events without knowing ahead of time what, if any, listeners will be responding.)  A common
        use case for this would be to wait a few seconds _after_ a resize has occurred for anything
        that just loaded to finish doing so.


        #### Arguments

        - **idle** (`int`):

            The amount of time, in milliseconds, that the event stream should be idle before
            returning.

        - **events** (`list`, optional):

            If not empty, the **idle** time will be interpreted as the amount of time since _any
            of these specific events_ have occurred.  The default is to wait for the browser to be
            idle with respect to _any_ events.

        - **timeout** (`int`):

            The maximum amount of time to wait before raising a
            `webfriend.exceptions.TimeoutError`.

        - **poll_interval** (`int`):

            How often to check the event timings to see if the idle time has elapsed.

        #### Returns
        An `int` representing the number of milliseconds we waited for.

        #### Raises
        `webfriend.exceptions.TimeoutError`
        """
        started_at = time.time()
        idle = (idle / 1e3)

        # clear out the old timings we're interested in
        if len(events):
            for name in events:
                if name in self.last_event_m:
                    del self.last_event_m[name]

        while time.time() < (started_at + (timeout / 1e3)):
            # if we don't have an event filter, then we just want to wait idle seconds
            # after ANY event has been received
            if not len(events):
                # if the time since ANY event has met/exceeded our idle time
                if time.time() >= (self.last_event_t + idle):
                    return (time.time() - started_at) * 1e3

            else:
                for name in events:
                    if name in self.last_event_m:
                        # if the time since this event has met/exceeded our idle time
                        if time.time() >= (self.last_event_m[name] + idle):
                            # now that we've gotten the event, remove it so subsequent calls wait
                            # for the next one to occur
                            del self.last_event_m[name]
                            return (time.time() - started_at) * 1e3

            time.sleep(poll_interval / 1e3)

        raise exceptions.TimeoutError("Timed out waiting for events to stop coming in")

    def evaluate(self, *args, **kwargs):
        return self.runtime.evaluate(*args, **kwargs)

    def rpc(self, method, expect_reply=True, reply_timeout=None, context=None, **params):
        payload = {
            'method': method,
        }

        if len(params):
            payload['params'] = params

        return self.send(
            payload,
            expect_reply=expect_reply,
            reply_timeout=reply_timeout,
            context=context
        )

    def get_domain_instance(self, domain):
        for attr in dir(self):
            instance = getattr(self, attr)

            if isinstance(instance, Base):
                if instance.domain == domain:
                    return instance

        raise ValueError("No such instance for domain '{}'".format(domain))

    def on(self, event_pattern, callback):
        domain, _ = event_pattern.split('.', 1)
        instance = self.get_domain_instance(domain)
        return instance.on(event_pattern, callback)

    def remove_handler(self, callback_id):
        domain, _ = callback_id.split('.', 1)
        instance = self.get_domain_instance(domain)
        return instance.remove_handler(callback_id)

    def reset_network_request_cache(self):
        self._network_requests = {}

    def get_network_request(self, request_id):
        return self._network_requests.get(request_id)

    def setup_callbacks(self):
        def on_net_pre_request(e):
            self._network_requests[e.get('requestId')] = {
                'before': e,
            }

        def on_net_response_received(e):
            nid = e.get('requestId')

            if isinstance(self._network_requests.get(nid), dict):
                self._network_requests[nid]['success'] = True
                self._network_requests[nid]['completed'] = True
                self._network_requests[nid]['response'] = e

        def on_net_load_failed(e):
            nid = e.get('requestId')

            if isinstance(self._network_requests.get(nid), dict):
                self._network_requests[nid]['success'] = False
                self._network_requests[nid]['response'] = e

        def on_message(e):
            message = e.get('message', {})
            level = message.get('level', 'log')
            body = message.get('text', '').strip()

            if isinstance(body, str):
                body = body.encode('UTF-8')

            if len(body):
                l = '--'

                if level == 'info':
                    l = 'II'
                elif level == 'warning':
                    l = 'WW'
                elif level == 'error':
                    l = 'EE'
                elif level == 'debug':
                    l = 'DD'

                logging.info('[{}] {}'.format(l, body))

        if self.netreq_tracking:
            self.network.on('requestWillBeSent', on_net_pre_request)
            self.network.on('responseReceived',  on_net_response_received)
            self.network.on('loadingFailed',     on_net_load_failed)
            logging.debug('Network request tracking is enabled')
        else:
            logging.debug('Network request tracking is disabled')

        if self.msg_enable:
            self.console.on('messageAdded', on_message)
