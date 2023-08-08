import asyncio
from typing import Any, overload

import pytest

from shiny._utils import is_async_callable
from shiny.render._render import TransformerMetadata, ValueFnAsync, output_transformer


def test_output_transformer_works():
    # No args works
    @output_transformer
    async def TestTransformer(
        _meta: TransformerMetadata,
        _afn: ValueFnAsync[str],
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
        _afn: ValueFnAsync[str],
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
        _afn: ValueFnAsync[str],
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
            _afn: ValueFnAsync[str],
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
            _afn: ValueFnAsync[str],
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
            _afn: ValueFnAsync[str],
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
        _afn: ValueFnAsync[str],
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
        assert "Expected `params` to be of type `RendererParams`" in str(e)


# # "Currently, `ValueFnAsync` can not be truely async and "
# # "support sync render methods"
# @pytest.mark.asyncio
# async def test_renderer_handler_fn_can_be_async():
#     @output_transformer
#     async def AsyncTransformer(
#         _meta: TransformerMetadata,
#         _afn: ValueFnAsync[str],
#     ) -> str:
#         # Actually sleep to test that the handler is truely async
#         await asyncio.sleep(0.1)
#         ret = await _afn()
#         return ret

#     @overload
#     def async_renderer() -> AsyncTransformer.OutputRendererDecorator:
#         ...

#     @overload
#     def async_renderer(
#         _fn: AsyncTransformer.ValueFn,
#     ) -> AsyncTransformer.OutputRenderer:
#         ...

#     def async_renderer(
#         _fn: AsyncTransformer.ValueFn | None = None,
#     ) -> AsyncTransformer.OutputRenderer | AsyncTransformer.OutputRendererDecorator:
#         return AsyncTransformer(_fn)

#     test_val = "Test: Hello World!"

#     def app_render_fn() -> str:
#         return test_val

#     renderer_sync = async_renderer(app_render_fn)
#     renderer_sync._set_metadata(
#         None,  # pyright: ignore[reportGeneralTypeIssues]
#         "renderer_sync",
#     )
#     if is_async_callable(renderer_sync):
#         raise RuntimeError("Expected `renderer_sync` to be a sync function")

#     # !! This line is currently not possible !!
#     ret = renderer_sync()
#     assert ret == test_val

#     async_test_val = "Async: Hello World!"

#     async def async_app_render_fn() -> str:
#         await asyncio.sleep(0.1)
#         return async_test_val

#     renderer_async = async_renderer(async_app_render_fn)
#     renderer_async._set_metadata(
#         None,  # pyright: ignore[reportGeneralTypeIssues]
#         "renderer_async",
#     )
#     if not is_async_callable(renderer_async):
#         raise RuntimeError("Expected `renderer_async` to be a coro function")

#     ret = await renderer_async()
#     assert ret == test_val
