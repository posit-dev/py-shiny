from typing import Any, overload

from shiny.render._render import TransformerMetadata, ValueFnAsync, output_transformer


def test_renderer_components_works():
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


def test_renderer_components_kwargs_are_allowed():
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


def test_renderer_components_with_pass_through_kwargs():
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


def test_renderer_components_pos_args():
    try:

        @output_transformer  # type: ignore
        async def test_components(
            _meta: TransformerMetadata,
        ):
            ...

        raise RuntimeError()
    except TypeError as e:
        assert "must have 2 positional parameters" in str(e)


def test_renderer_components_limits_positional_arg_count():
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


def test_renderer_components_does_not_allow_args():
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


def test_renderer_components_kwargs_have_defaults():
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


def test_renderer_components_result_does_not_allow_args():
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
