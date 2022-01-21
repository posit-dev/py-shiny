class SilentException(Exception):
    pass


def req(*args: object) -> object:
    for arg in args:
        if not arg:
            raise SilentException()
    return args[0]
