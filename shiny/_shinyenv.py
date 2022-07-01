"""
Information about the execution environment for Shiny
"""

import sys

# True if we're executing in WASM mode, False if we're executing using actual Python
is_pyodide: bool = "pyodide" in sys.modules
