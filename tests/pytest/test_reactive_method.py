import pytest

from shiny.reactive import isolate
from shiny.render._data_frame_utils._reactive_method import reactive_calc_method


def test_is_class_method():

    class Placeholder:

        name: str

        @reactive_calc_method
        def get_name(self):
            return self.name

    ex_name = "42"
    with isolate():
        obj = Placeholder()
        obj.name = ex_name

        assert obj.get_name() == ex_name

    with pytest.raises(TypeError) as e:

        @reactive_calc_method
        def test_fn(x: object):
            return "test_fn"

    assert "reactive_calc_method" in str(e.value)

    def outer_fn():
        @reactive_calc_method
        def test_fn(x: object):
            return "test_fn"

        return test_fn

    with pytest.raises(TypeError) as e:
        outer_fn()

    def outer_placeholder():
        class InnerPlaceholder:

            name: str

            @reactive_calc_method
            def get_name(self):
                return self.name

        return InnerPlaceholder

    inner_placeholder = outer_placeholder()
    inner_placeholder.name = ex_name
    with isolate():
        obj = inner_placeholder()
        assert obj.get_name() == ex_name

    assert "<locals>" in obj.get_name.__qualname__
