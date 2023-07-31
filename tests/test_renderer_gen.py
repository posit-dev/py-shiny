from typing import Any, overload

from shiny.render._render import (
    Renderer,
    RenderFnAsync,
    RenderMeta,
    renderer_components,
)


def test_renderer_components_works():
    # No args works
    @renderer_components
    async def test_components(
        meta: RenderMeta,
        fn: RenderFnAsync[str],
    ):
        ...

    @overload
    def test_renderer() -> test_components.type_decorator:
        ...

    @overload
    def test_renderer(
        _fn: test_components.type_renderer_fn,
    ) -> test_components.type_renderer:
        ...

    def test_renderer(
        _fn: test_components.type_impl_fn = None,
    ) -> test_components.type_impl:
        return test_components.impl(_fn)


def test_renderer_components_kwargs_are_allowed():
    # Test that kwargs can be allowed
    @renderer_components
    async def test_components(
        meta: RenderMeta,
        fn: RenderFnAsync[str],
        *,
        y: str = "42",
    ):
        ...

    @overload
    def test_renderer(*, y: str = "42") -> test_components.type_decorator:
        ...

    @overload
    def test_renderer(
        _fn: test_components.type_renderer_fn,
    ) -> test_components.type_renderer:
        ...

    def test_renderer(
        _fn: test_components.type_impl_fn = None,
        *,
        y: str = "42",
    ) -> test_components.type_impl:
        return test_components.impl(_fn, y=y)


def test_renderer_components_with_pass_through_kwargs():
    # No args works
    @renderer_components
    async def test_components(
        meta: RenderMeta,
        fn: RenderFnAsync[str],
        *,
        y: str = "42",
        **kwargs: float,
    ):
        ...

    @overload
    def test_renderer(
        *, y: str = "42", **kwargs: Any
    ) -> test_components.type_decorator:
        ...

    @overload
    def test_renderer(
        _fn: test_components.type_renderer_fn,
    ) -> test_components.type_renderer:
        ...

    def test_renderer(
        _fn: test_components.type_impl_fn = None,
        *,
        y: str = "42",
        **kwargs: Any,
    ) -> test_components.type_impl:
        return test_components.impl(_fn, y=y, **kwargs)


def test_renderer_components_limits_positional_arg_count():
    try:

        @renderer_components
        async def test_components(
            meta: RenderMeta,
            fn: RenderFnAsync[str],
            y: str,
        ):
            ...

        raise RuntimeError()
    except TypeError as e:
        assert "more than 2 positional" in str(e)


def test_renderer_components_does_not_allow_args():
    try:

        @renderer_components
        async def test_components(
            meta: RenderMeta,
            fn: RenderFnAsync[str],
            *args: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "No variadic parameters" in str(e)


def test_renderer_components_kwargs_have_defaults():
    try:

        @renderer_components
        async def test_components(
            meta: RenderMeta,
            fn: RenderFnAsync[str],
            *,
            y: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "did not have a default value" in str(e)


def test_renderer_components_kwargs_can_not_be_name_render_fn():
    try:

        @renderer_components
        async def test_components(
            meta: RenderMeta,
            fn: RenderFnAsync[str],
            *,
            _render_fn: str,
        ):
            ...

        raise RuntimeError()

    except ValueError as e:
        assert "parameters can not be named `_render_fn`" in str(e)


def test_renderer_components_result_does_not_allow_args():
    @renderer_components
    async def test_components(
        meta: RenderMeta,
        fn: RenderFnAsync[str],
    ):
        ...

    # Test that args can **not** be supplied
    def render_fn_sync(*args: str):
        return " ".join(args)

    async def render_fn_async(*args: str):
        return " ".join(args)

    try:
        test_components(  # type: ignore
            "X",
            "Y",
        ).impl(render_fn_sync)
        raise RuntimeError()
    except RuntimeError as e:
        assert "`args` should not be supplied" in str(e)

    try:
        test_components(  # type: ignore
            "X",
            "Y",
        ).impl(render_fn_async)
    except RuntimeError as e:
        assert "`args` should not be supplied" in str(e)


def test_renderer_components_makes_calls_render_fn_once():
    @renderer_components
    async def test_renderer_components_no_calls(
        meta: RenderMeta,
        fn: RenderFnAsync[str],
    ):
        # Does not call `fn`
        return "Not 42"

    @renderer_components
    async def test_renderer_components_multiple_calls(
        meta: RenderMeta,
        fn: RenderFnAsync[str],
    ):
        # Calls `fn` > 1 times
        return f"{await fn()} - {await fn()}"

    # Test that args can **not** be supplied
    def render_fn():
        return "42"

    renderer_fn_none = test_renderer_components_no_calls.impl(render_fn)
    renderer_fn_none._set_metadata(None, "test_out")  # type: ignore
    if not isinstance(renderer_fn_none, Renderer):
        raise RuntimeError()
    try:
        renderer_fn_none()
        raise RuntimeError()
    except RuntimeError as e:
        assert (
            str(e)
            == "The total number of calls (`0`) to 'render_fn' in the 'test_renderer_components_no_calls' handler did not equal `1`."
        )

    renderer_fn_multiple = test_renderer_components_multiple_calls.impl(render_fn)
    renderer_fn_multiple._set_metadata(None, "test_out")  # type: ignore
    if not isinstance(renderer_fn_multiple, Renderer):
        raise RuntimeError()
    try:
        renderer_fn_multiple()
        raise RuntimeError()
    except RuntimeError as e:
        assert (
            str(e)
            == "The total number of calls (`2`) to 'render_fn' in the 'test_renderer_components_multiple_calls' handler did not equal `1`."
        )
