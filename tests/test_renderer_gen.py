from shiny.render._render import RenderFunctionMeta, renderer_gen


def test_renderer_gen_assertions():
    @renderer_gen
    def test_fn1(
        meta: RenderFunctionMeta,
        x: str,
    ):
        ...

    try:

        @renderer_gen
        def test_fn2(
            meta: RenderFunctionMeta,
            x: str,
            y: str,
        ):
            ...

        raise RuntimeError()
    except TypeError as e:
        assert "more than 2 positional" in str(e)

    try:

        @renderer_gen
        def test_fn3(
            meta: RenderFunctionMeta,
            x: str,
            *args: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "No variadic parameters" in str(e)

    try:

        @renderer_gen
        def test_fn4(
            meta: RenderFunctionMeta,
            x: str,
            *,
            y: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "did not have a default value" in str(e)

    # Test that kwargs can be allowed
    @renderer_gen
    def test_fn5(
        meta: RenderFunctionMeta,
        x: str,
        *,
        y: str = "42",
        **kwargs: object,
    ):
        ...
