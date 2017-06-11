class ChromeProtocolError(Exception):
    pass


class TimeoutError(Exception):
    pass


class HttpError(Exception):
    pass


class EmptyResult(Exception):
    pass


class TooManyResults(Exception):
    pass


class NotImplemented(Exception):
    pass


class UserError(Exception):
    pass
