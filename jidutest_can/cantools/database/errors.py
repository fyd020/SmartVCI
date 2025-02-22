from jidutest_can.cantools.tools.errors import Error as _Error


class Error(_Error):
    pass


class ParseError(Error):
    pass


class EncodeError(Error):
    pass


class DecodeError(Error):
    pass
