import asyncio
from typing import Any, overload

import pytest

from shiny._utils import is_async_callable
from shiny.render._render import TransformerMetadata, ValueFnAsync, output_transformer


def test_output_transformer_works():
    # No args works
    @output_transformer
    async def test_components(
        _meta: TransformerMetadata,
        _fn: ValueFnAsync[str],
    ):
        ...

    @overload
    def test_renderer() -> test_components.OutputRendererDecorator:
        ...

    @overload
    def test_renderer(
        _fn: test_components.ValueFn,
    ) -> test_components.OutputRenderer:
        ...

    def test_renderer(
        _fn: test_components.ValueFnOrNone = None,
    ) -> test_components.OutputRendererOrDecorator:
        return test_components.impl(_fn)


def test_output_transformer_kwargs_are_allowed():
    # Test that kwargs can be allowed
    @output_transformer
    async def test_components(
        _meta: TransformerMetadata,
        _fn: ValueFnAsync[str],
        *,
        y: str = "42",
    ):
        ...

    @overload
    def test_renderer(*, y: str = "42") -> test_components.OutputRendererDecorator:
        ...

    @overload
    def test_renderer(
        _fn: test_components.ValueFn,
    ) -> test_components.OutputRenderer:
        ...

    def test_renderer(
        _fn: test_components.ValueFnOrNone = None,
        *,
        y: str = "42",
    ) -> test_components.OutputRendererOrDecorator:
        return test_components.impl(
            _fn,
            test_components.params(y=y),
        )


def test_output_transformer_with_pass_through_kwargs():
    # No args works
    @output_transformer
    async def test_components(
        _meta: TransformerMetadata,
        _fn: ValueFnAsync[str],
        *,
        y: str = "42",
        **kwargs: float,
    ):
        ...

    @overload
    def test_renderer(
        *, y: str = "42", **kwargs: Any
    ) -> test_components.OutputRendererDecorator:
        ...

    @overload
    def test_renderer(
        _fn: test_components.ValueFn,
    ) -> test_components.OutputRenderer:
        ...

    def test_renderer(
        _fn: test_components.ValueFnOrNone = None,
        *,
        y: str = "42",
        **kwargs: Any,
    ) -> test_components.OutputRendererOrDecorator:
        return test_components.impl(
            _fn,
            test_components.params(y=y, **kwargs),
        )


def test_output_transformer_pos_args():
    try:

        @output_transformer  # type: ignore
        async def test_components(
            _meta: TransformerMetadata,
        ):
            ...

        raise RuntimeError()
    except TypeError as e:
        assert "must have 2 positional parameters" in str(e)


def test_output_transformer_limits_positional_arg_count():
    try:

        @output_transformer
        async def test_components(
            _meta: TransformerMetadata,
            _fn: ValueFnAsync[str],
            y: str,
        ):
            ...

        raise RuntimeError()
    except TypeError as e:
        assert "more than 2 positional" in str(e)


def test_output_transformer_does_not_allow_args():
    try:

        @output_transformer
        async def test_components(
            _meta: TransformerMetadata,
            _fn: ValueFnAsync[str],
            *args: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "No variadic positional parameters" in str(e)


def test_output_transformer_kwargs_have_defaults():
    try:

        @output_transformer
        async def test_components(
            _meta: TransformerMetadata,
            _fn: ValueFnAsync[str],
            *,
            y: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "did not have a default value" in str(e)


def test_output_transformer_result_does_not_allow_args():
    @output_transformer
    async def test_components(
        _meta: TransformerMetadata,
        _fn: ValueFnAsync[str],
    ):
        ...

    # Test that args can **not** be supplied
    def render_fn_sync(*args: str):
        return " ".join(args)

    try:
        test_components.impl(
            render_fn_sync,
            "X",  # type: ignore
        )
        raise RuntimeError()
    except TypeError as e:
        assert "Expected `params` to be of type `RendererParams`" in str(e)


@pytest.mark.asyncio
async def test_renderer_handler_fn_can_be_async():
    @output_transformer
    async def async_handler(
        _meta: TransformerMetadata,
        _fn: ValueFnAsync[str],
    ) -> str:
        # Actually sleep to test that the handler is truely async
        await asyncio.sleep(0.1)
        ret = await _fn()
        return ret

    @overload
    def async_renderer() -> async_handler.OutputRendererDecorator:
        ...

    @overload
    def async_renderer(
        _fn: async_handler.ValueFn,
    ) -> async_handler.OutputRenderer:
        ...

    def async_renderer(
        _fn: async_handler.ValueFn | None = None,
    ) -> async_handler.OutputRenderer | async_handler.OutputRendererDecorator:
        return async_handler.impl(_fn)

    test_val = "Test: Hello World!"

    def app_render_fn() -> str:
        return test_val

    renderer_sync = async_renderer(app_render_fn)
    renderer_sync._set_metadata(
        None,  # pyright: ignore[reportGeneralTypeIssues]
        "renderer_sync",
    )
    if is_async_callable(renderer_sync):
        raise RuntimeError("Expected `renderer_sync` to be a sync function")

    ret = renderer_sync()
    assert ret == test_val

    async_test_val = "Async: Hello World!"

    async def async_app_render_fn() -> str:
        await asyncio.sleep(0.1)
        return async_test_val

    renderer_async = async_renderer(async_app_render_fn)
    renderer_async._set_metadata(
        None,  # pyright: ignore[reportGeneralTypeIssues]
        "renderer_async",
    )
    if not is_async_callable(renderer_async):
        raise RuntimeError("Expected `renderer_async` to be a coro function")

    ret = await renderer_async()
    assert ret == test_val
