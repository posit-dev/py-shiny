"""
Internal utilities for the reactive module.

This module contains helper functions used by reactive classes.
"""

from __future__ import annotations

import os

__all__ = ("is_user_code_frame",)


def is_user_code_frame(filename: str) -> bool:
    """
    Check if a filename represents user code (not internal shiny package code).

    This is used by stack inspection code to filter out internal shiny frames
    and find the first frame of user code.

    Parameters
    ----------
    filename
        Path to the file to check

    Returns
    -------
    bool
        True if the file is user code, False if it's internal shiny code

    Examples
    --------
    >>> is_user_code_frame("/home/user/app.py")
    True
    >>> is_user_code_frame("/usr/lib/python/site-packages/shiny/reactive/_reactives.py")
    False
    >>> is_user_code_frame("/usr/lib/python/site-packages/shiny/tests/test_reactive.py")
    True

    Notes
    -----
    The function considers these as user code:
    - Any file outside the shiny package
    - Test files (files starting with "test_")
    - Files in the shiny/tests directory

    The function filters out:
    - Special/generated frames (filename starts with "<")
    - Internal shiny package code (except tests)
    """
    # Skip special/generated frames
    if not filename or filename.startswith("<"):
        return False

    # Test files are always considered user code
    basename = os.path.basename(filename)
    if basename.startswith("test_"):
        return True

    # Check if file is within shiny package directory
    try:
        # Get the shiny package directory (two levels up from this file)
        # This file is at shiny/reactive/_utils.py, so we go up to shiny/
        shiny_package_dir = os.path.dirname(os.path.dirname(__file__))

        # Use os.path.commonpath to check if file is under shiny package
        common = os.path.commonpath([filename, shiny_package_dir])
        if common == shiny_package_dir:
            # File is within shiny package, skip it unless it's in tests
            if "tests" not in filename:
                return False
    except (ValueError, TypeError):
        # Different drives on Windows or other path issues - treat as user code
        pass

    return True
