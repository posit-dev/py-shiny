from pathlib import Path

from shiny import express


def test_is_express_app(tmp_path: Path):
    tmp_file = str(tmp_path / "app.py")

    def write_tmp_file(s: str):
        with open(tmp_file, "w") as f:
            f.write(s)

    write_tmp_file("import shiny.express")
    assert express.is_express_app(tmp_file, None)
    # Check that it works when passing in app_path
    assert express.is_express_app("app.py", str(tmp_path))

    write_tmp_file("# comment\nimport sys\n\nimport shiny.express")
    assert express.is_express_app(tmp_file, None)

    write_tmp_file("import sys\n\nfrom shiny import App, express")
    assert express.is_express_app(tmp_file, None)

    write_tmp_file("import sys\n\nfrom shiny.express import layout, input")
    assert express.is_express_app(tmp_file, None)

    # Shouldn't find in comment
    write_tmp_file("# import shiny.express")
    assert not express.is_express_app(tmp_file, None)

    # Shouldn't find in a string, even if it looks like an import
    write_tmp_file('"""\nimport shiny.express\n"""')
    assert not express.is_express_app(tmp_file, None)

    # Shouldn't recurse into with, if, for, def, etc.
    write_tmp_file("with f:\n  from shiny import express")
    assert not express.is_express_app(tmp_file, None)

    write_tmp_file("if True:\n  import shiny.express")
    assert not express.is_express_app(tmp_file, None)

    write_tmp_file("for i in range(2):\n  import shiny.express")
    assert not express.is_express_app(tmp_file, None)

    write_tmp_file("def f():\n  import shiny.express")
    assert not express.is_express_app(tmp_file, None)
