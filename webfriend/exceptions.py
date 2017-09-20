class WebfriendError(Exception):
    pass


class ProtocolError(WebfriendError):
    pass


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
