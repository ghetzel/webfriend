class WebfriendError(Exception):
    pass


class ProtocolError(WebfriendError):
    def __init__(self, message, **kwargs):
        if message.startswith('Protocol Error '):
            try:
                parts = message.split(':', 1)
                self.code = int(parts[0].replace('Protocol Error ', ''))
                message = parts[1]
            except:
                self.code = -1

        super(Exception, self).__init__(message, **kwargs)


class TimeoutError(WebfriendError):
    pass


class NotFound(WebfriendError):
    pass


class NetworkError(WebfriendError):
    pass


class HttpError(WebfriendError):
    pass


class EmptyResult(WebfriendError):
    pass


class TooManyResults(WebfriendError):
    pass


class NotImplemented(WebfriendError):
    pass
