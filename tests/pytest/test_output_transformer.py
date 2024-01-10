from __future__ import annotations

import asyncio
from typing import Any, cast, overload

import pytest

from shiny._deprecated import ShinyDeprecationWarning
from shiny._namespaces import ResolvedId, Root
from shiny._utils import is_async_callable
from shiny.render.transformer import (
    TransformerMetadata,
    ValueFn,
    output_transformer,
    resolve_value_fn,
)
from shiny.session import Session, session_context

# import warnings
# warnings.filterwarnings("ignore", category=ShinyDeprecationWarning)


class _MockSession:
    ns: ResolvedId = Root

    # This is needed so that Outputs don't throw an error.
    def _is_hidden(self, name: str) -> bool:
        return False


test_session = cast(Session, _MockSession())


def test_output_transformer_works():
    # No args works
    @output_transformer
    async def TestTransformer(
        _meta: TransformerMetadata,
        _fn: ValueFn[str],
    ):
        ...

    @overload
    def test_renderer() -> TestTransformer.OutputRendererDecorator:
        ...

    @overload
    def test_renderer(
        _fn: TestTransformer.ValueFn,
    ) -> TestTransformer.OutputRenderer:
        ...

    def test_renderer(
        _fn: TestTransformer.ValueFn | None = None,
    ) -> TestTransformer.OutputRenderer | TestTransformer.OutputRendererDecorator:
        return TestTransformer(_fn)


def test_output_transformer_kwargs_are_allowed():
    # Test that kwargs can be allowed
    @output_transformer
    async def TestTransformer(
        _meta: TransformerMetadata,
        _fn: ValueFn[str],
        *,
        y: str = "42",
    ):
        ...

    @overload
    def test_renderer(*, y: str = "42") -> TestTransformer.OutputRendererDecorator:
        ...

    @overload
    def test_renderer(
        _fn: TestTransformer.ValueFn,
    ) -> TestTransformer.OutputRenderer:
        ...

    def test_renderer(
        _fn: TestTransformer.ValueFn | None = None,
        *,
        y: str = "42",
    ) -> TestTransformer.OutputRenderer | TestTransformer.OutputRendererDecorator:
        return TestTransformer(
            _fn,
            TestTransformer.params(y=y),
        )


def test_output_transformer_with_pass_through_kwargs():
    # No args works
    @output_transformer
    async def TestTransformer(
        _meta: TransformerMetadata,
        _fn: ValueFn[str],
        *,
        y: str = "42",
        **kwargs: float,
    ):
        ...

    @overload
    def test_renderer(
        *, y: str = "42", **kwargs: Any
    ) -> TestTransformer.OutputRendererDecorator:
        ...

    @overload
    def test_renderer(
        _fn: TestTransformer.ValueFn,
    ) -> TestTransformer.OutputRenderer:
        ...

    def test_renderer(
        _fn: TestTransformer.ValueFn | None = None,
        *,
        y: str = "42",
        **kwargs: Any,
    ) -> TestTransformer.OutputRenderer | TestTransformer.OutputRendererDecorator:
        return TestTransformer(
            _fn,
            TestTransformer.params(y=y, **kwargs),
        )


def test_output_transformer_pos_args():
    try:

        @output_transformer  # pyright: ignore[reportGeneralTypeIssues]
        async def TestTransformer(
            _meta: TransformerMetadata,
        ):
            ...

        raise RuntimeError()
    except TypeError as e:
        assert "must have 2 positional parameters" in str(e)


def test_output_transformer_limits_positional_arg_count():
    try:

        @output_transformer
        async def TestTransformer(
            _meta: TransformerMetadata,
            _fn: ValueFn[str],
            y: str,
        ):
            ...

        raise RuntimeError()
    except TypeError as e:
        assert "more than 2 positional" in str(e)


def test_output_transformer_does_not_allow_args():
    try:

        @output_transformer
        async def TestTransformer(
            _meta: TransformerMetadata,
            _fn: ValueFn[str],
            *args: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "No variadic positional parameters" in str(e)


def test_output_transformer_kwargs_have_defaults():
    try:

        @output_transformer
        async def TestTransformer(
            _meta: TransformerMetadata,
            _fn: ValueFn[str],
            *,
            y: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "did not have a default value" in str(e)


def test_output_transformer_result_does_not_allow_args():
    @output_transformer
    async def TestTransformer(
        _meta: TransformerMetadata,
        _fn: ValueFn[str],
    ):
        ...

    # Test that args can **not** be supplied
    def render_fn_sync(*args: str):
        return " ".join(args)

    try:
        TestTransformer(
            render_fn_sync,
            "X",  # pyright: ignore[reportGeneralTypeIssues]
        )
        raise RuntimeError()
    except TypeError as e:
        assert "Expected `params` to be of type `TransformerParams`" in str(e)


# "Currently, `ValueFn` can not be truly async and "support sync render methods"
@pytest.mark.asyncio
async def test_renderer_handler_or_transform_fn_can_be_async():
    @output_transformer
    async def AsyncTransformer(
        _meta: TransformerMetadata,
        _fn: ValueFn[str],
    ) -> str:
        assert is_async_callable(_fn)
        # Actually sleep to test that the handler is truly async
        await asyncio.sleep(0)
        ret = await _fn()
        return ret

    # ## Setup overloads =============================================

    @overload
    def async_renderer() -> AsyncTransformer.OutputRendererDecorator:
        ...

    @overload
    def async_renderer(
        _fn: AsyncTransformer.ValueFn,
    ) -> AsyncTransformer.OutputRenderer:
        ...

    def async_renderer(
        _fn: AsyncTransformer.ValueFn | None = None,
    ) -> AsyncTransformer.OutputRenderer | AsyncTransformer.OutputRendererDecorator:
        with pytest.warns(ShinyDeprecationWarning):
            return AsyncTransformer(_fn)

    test_val = "Test: Hello World!"

    def app_render_fn() -> str:
        return test_val

    # ## Test Sync: X =============================================

    renderer_sync = async_renderer(app_render_fn)
    renderer_sync._set_output_metadata(
        output_name="renderer_sync",
    )
    # All renderers are async in execution.
    assert is_async_callable(renderer_sync)

    with session_context(test_session):
        val = await renderer_sync()
        assert val == test_val

    # ## Test Async: √ =============================================

    async_test_val = "Async: Hello World!"

    async def async_app_render_fn() -> str:
        await asyncio.sleep(0)
        return async_test_val

    renderer_async = async_renderer(async_app_render_fn)
    renderer_async._set_output_metadata(
        output_name="renderer_async",
    )
    if not is_async_callable(renderer_async):
        raise RuntimeError("Expected `renderer_async` to be a coro function")

    with session_context(test_session):
        ret = await renderer_async()
        assert ret == async_test_val


# "Currently, `ValueFnA` can not be truly async and "support sync render methods".
# Test that conditionally calling async works.
@pytest.mark.asyncio
async def test_renderer_handler_fn_can_be_yield_while_async():
    @output_transformer
    async def YieldTransformer(
        _meta: TransformerMetadata,
        _fn: ValueFn[str],
    ) -> str:
        if is_async_callable(_fn):
            # Actually sleep to test that the handler is truly async
            await asyncio.sleep(0)
        ret = await _fn()
        return ret

    # ## Setup overloads =============================================

    @overload
    def yield_renderer() -> YieldTransformer.OutputRendererDecorator:
        ...

    @overload
    def yield_renderer(
        _fn: YieldTransformer.ValueFn,
    ) -> YieldTransformer.OutputRenderer:
        ...

    def yield_renderer(
        _fn: YieldTransformer.ValueFn | None = None,
    ) -> YieldTransformer.OutputRenderer | YieldTransformer.OutputRendererDecorator:
        with pytest.warns(ShinyDeprecationWarning):
            return YieldTransformer(_fn)

    test_val = "Test: Hello World!"

    def app_render_fn() -> str:
        return test_val

    # ## Test Sync: √ =============================================

    renderer_sync = yield_renderer(app_render_fn)
    renderer_sync._set_output_metadata(
        output_name="renderer_sync",
    )
    assert is_async_callable(renderer_sync)

    with session_context(test_session):
        ret = await renderer_sync()
        assert ret == test_val

    # ## Test Async: √ =============================================

    async_test_val = "Async: Hello World!"

    async def async_app_render_fn() -> str:
        await asyncio.sleep(0)
        return async_test_val

    renderer_async = yield_renderer(async_app_render_fn)
    renderer_async._set_output_metadata(
        output_name="renderer_async",
    )
    assert is_async_callable(renderer_async)

    with session_context(test_session):
        ret = await renderer_async()
        assert ret == async_test_val


@pytest.mark.asyncio
async def test_resolve_value_fn_is_deprecated():
    with pytest.warns(ShinyDeprecationWarning):
        test_val = 42

        async def value_fn():
            return test_val

        ret = await resolve_value_fn(value_fn)
        assert test_val == ret
