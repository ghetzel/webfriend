from __future__ import absolute_import
from webfriend.rpc import Base
from datetime import datetime
from base64 import b64decode


class Cookie(object):
    def __init__(self, rpc, definition):
        self._rpc          = rpc
        self._definition   = definition
        self.name          = definition['name']
        self.value         = definition['value']
        self.domain        = definition.get('domain')
        self.path          = definition.get('path')
        self.expires_epoch = definition.get('expires')
        self.size          = definition.get('size')
        self.http_only     = definition.get('httpOnly')
        self.secure        = definition.get('secure')
        self.session       = definition.get('session')
        self.same_site     = definition.get('sameSite')

        if self.expires_epoch is not None:
            self.expires   = datetime.fromtimestamp(self.expires_epoch / 1e3)

    def as_dict(self):
        return dict([
            (k, v) for k, v in self.__dict__.items() if not k.startswith('_')
        ])


class Network(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Network
    """
    domain = 'Network'

    connection_types = [
        'none', 'cellular2g', 'cellular3g', 'cellular4g', 'bluetooth', 'ethernet', 'wifi', 'wimax',
        'other'
    ]

    def set_user_agent(self, user_agent):
        self.call('setUserAgentOverride', userAgent=user_agent)

    def set_headers(self, headers):
        if not isinstance(headers, dict):
            raise AttributeError("Headers must be specified as a dict")

        self.call('setExtraHTTPHeaders', headers=headers)

    def get_response_body(self, request_id):
        reply = self.call('getResponseBody', requestId=request_id)
        body = reply.get('body')

        if not body:
            return None

        if reply.get('base64Encoded') is True:
            body = b64decode(body)

        return body

    @property
    def can_clear_browser_cache(self):
        return self.call_boolean_response('canClearBrowserCache')

    @property
    def can_clear_browser_cookies(self):
        return self.call_boolean_response('canClearBrowserCookies')

    @property
    def can_emulate_network_conditions(self):
        return self.call_boolean_response('canEmulateNetworkConditions')

    def clear_browser_cache(self):
        self.call('clearBrowserCache')

    def clear_browser_cookies(self):
        self.call('clearBrowserCookies')

    def emulate_network_conditions(
        self,
        offline=False,
        latency_ms=0,
        throughput_down_bps=None,
        throughput_up_bps=None,
        connection_type=None,
    ):
        params = {
            'offline': offline,
            'latency':            latency_ms,
            'downloadThroughput': 10e9,
            'uploadThroughput':   10e9,
        }

        if connection_type is not None:
            if connection_type not in self.connection_types:
                raise AttributeError("Connection Type must be one of: {}".format(
                    ', '.join(self.connection_types)
                ))

            params['connectionType'] = connection_type

        self.call('emulateNetworkConditions', **params)

    def disable_cache(self):
        self.call('setCacheDisabled', cacheDisabled=True)

    def enable_cache(self):
        self.call('setCacheDisabled', cacheDisabled=False)

    def set_blocked_urls(self, urls):
        if not isinstance(urls, list):
            raise AttributeError("Blocked URLs must be a list")
        self.call('setBlockedURLs', urls=urls)

    def replay_xhr(self, request_id):
        self.call('replayXHR', requestId=request_id)

    def get_cookies(self, urls=None):
        if isinstance(urls, list):
            reply = self.call('getCookies', urls=urls)
        else:
            reply = self.call('getAllCookies')

        return [
            Cookie(self, c) for c in reply.get('cookies', [])
        ]

    def delete_cookie(self, url, name):
        self.call('deleteCookie', cookieName=name, url=url)

    def set_cookie(
        self,
        url,
        name,
        value,
        domain=None,
        path=None,
        secure=None,
        http_only=None,
        same_site=None,
        expires=None
    ):
        """
        Create or update a cookie based on the given values.
        """
        params = {
            'url':   url,
            'name':  name,
            'value': value,
        }

        if domain is not None:
            params['domain'] = domain

        if path is not None:
            params['path'] = path

        if isinstance(secure, bool):
            params['secure'] = secure

        if isinstance(http_only, bool):
            params['httpOnly'] = http_only

        if isinstance(same_site, basestring):
            params['sameSite'] = same_site

        if isinstance(expires, int):
            params['expirationDate'] = expires
        elif isinstance(expires, datetime):
            params['expirationDate'] = int(expires.strftime('%s'))

        return self.call_boolean_response(self.call('setCookie', **params), 'success')

    def get_certificate(self, origin):
        # getCertificate
        return Exception("NOT IMPLEMENTED")
