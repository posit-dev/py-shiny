from shiny import render, ui
from shiny.express import output_args
from shiny.types import MISSING


def test_decorator_plot_sizing():
    """render.plot width/height are passed through to implicit output"""

    @render.plot(width=1280, height=960)
    def foo():
        ...

    rendered = str(foo.tagify())
    assert "1280px" in rendered
    assert "960px" in rendered
    assert rendered == str(ui.output_plot("foo", width=1280, height=960))


def test_decorator_plot_default():
    """render.plot default is the same as ui.output_plot default"""

    @render.plot()
    def foo():
        ...

    rendered = str(foo.tagify())
    assert rendered == str(ui.output_plot("foo"))


def test_decorator_output_args():
    """@output_args is respected"""

    @output_args(width="640px", height="480px")
    @render.plot()
    def foo():
        ...

    rendered = str(foo.tagify())
    assert rendered == str(ui.output_plot("foo", width="640px", height="480px"))


def test_decorator_output_args_priority():
    """@output_args should override render.plot width/height"""

    @output_args(width="640px", height=480)
    @render.plot(width=1280, height=960)
    def foo():
        ...

    rendered = str(foo.tagify())
    # Note "640px" => 640 and 480 => "480px"
    assert rendered == str(ui.output_plot("foo", width=640, height="480px"))


def test_decorator_output_args_MISSING():
    """Not saying we support this, but test how MISSING interacts"""

    @output_args(width=MISSING)
    @render.plot(width=1280, height=MISSING)
    def foo():
        ...

    rendered = str(foo.tagify())
    assert rendered == str(ui.output_plot("foo", width="1280px"))
