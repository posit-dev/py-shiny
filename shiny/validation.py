# For use with shinysession.SANITIZE_ERRORS = True
class SafeException(Exception):
    pass


class SilentException(Exception):
    def __init__(self, cancel_output: bool = False) -> None:
        self.cancel_output = cancel_output


def req(*args: object, cancel_output: bool = False) -> object:
    for arg in args:
        if not arg:
            raise SilentException(cancel_output)
    return args[0]
