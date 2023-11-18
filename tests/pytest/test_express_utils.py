from pathlib import Path

from shiny.express._utils import escape_to_var_name, unescape_from_var_name


def test_escape_var_name(tmp_path: Path):
    x = "myapp.py"
    y = escape_to_var_name(x)
    assert y == "myapp_2e_py"
    assert unescape_from_var_name(y) == x

    x = "01myápp.py"
    y = escape_to_var_name(x)
    assert y == "_30_1my_e1_pp_2e_py"
    assert unescape_from_var_name(y) == x

    x = "path/to/your_🐍file.py"
    y = escape_to_var_name(x)
    assert y == "path_2f_to_2f_your_5f__1f40d_file_2e_py"
    assert unescape_from_var_name(y) == x
