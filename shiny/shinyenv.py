"""
Functions for inspecting the execution environment for Shiny
"""

import sys

__all__ = ["is_pyodide"]

# True if we're executing in WASM mode, False if we're executing using actual Python
is_pyodide = "pyodide" in sys.modules
