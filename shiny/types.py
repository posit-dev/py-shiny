# Sentinel value - indicates a missing value in a function call.

__all__ = ("MISSING", "MISSING_TYPE")


class MISSING_TYPE:
    pass


MISSING = MISSING_TYPE()
