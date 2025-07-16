from __future__ import annotations

import re


def escape_to_var_name(x: str) -> str:
    """
    Given a string, escape it to a valid Python variable name which contains
    [a-zA-Z0-9_]. All other characters will be escaped to _<hex>_. Also, if the first
    character is a digit, it will be escaped to _<hex>_, because Python variable names
    can't begin with a digit.
    """
    encoded = ""
    is_first = True

    for char in x:
        if is_first and re.match("[0-9]", char):
            encoded += f"_{ord(char):x}_"
        elif re.match("[a-zA-Z0-9]", char):
            encoded += char
        else:
            encoded += f"_{ord(char):x}_"

        if is_first:
            is_first = False

    return encoded


def unescape_from_var_name(x: str) -> str:
    """
    Given a string that was escaped to a Python variable name, unescape it -- that is,
    convert it back to a regular string.
    """

    def replace_func(match: re.Match[str]) -> str:
        return chr(int(match.group(1), 16))

    decoded = re.sub("_([a-zA-Z0-9]+)_", replace_func, x)
    return decoded
