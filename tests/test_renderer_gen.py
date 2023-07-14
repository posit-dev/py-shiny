from shiny.render._render import RendererMeta, renderer_gen


def test_renderer_gen_name_and_docs_are_copied():
    @renderer_gen
    def fn_sync(meta: RendererMeta, x: str) -> str:
        "Sync test docs go here"
        return "42"

    assert fn_sync.__doc__ == "Sync test docs go here"
    assert fn_sync.__name__ == "fn_sync"

    @renderer_gen
    async def fn_async(meta: RendererMeta, x: str) -> str:
        "Async test docs go here"
        return "42"

    assert fn_async.__doc__ == "Async test docs go here"
    assert fn_async.__name__ == "fn_async"


def test_renderer_gen_works():
    # No args works
    @renderer_gen
    def test_renderer_sync(
        meta: RendererMeta,
        x: str,
    ):
        ...

    @renderer_gen
    async def test_renderer_async(
        meta: RendererMeta,
        x: str,
    ):
        ...


def test_renderer_gen_kwargs_are_allowed():
    # Test that kwargs can be allowed
    @renderer_gen
    def test_renderer_sync(
        meta: RendererMeta,
        x: str,
        *,
        y: str = "42",
    ):
        ...

    @renderer_gen
    async def test_renderer_async(
        meta: RendererMeta,
        x: str,
        *,
        y: str = "42",
    ):
        ...


def test_renderer_gen_with_pass_through_kwargs():
    # No args works
    @renderer_gen
    def test_renderer_sync(
        meta: RendererMeta,
        x: str,
        *,
        y: str = "42",
        **kwargs: float,
    ):
        ...

    @renderer_gen
    async def test_renderer_async(
        meta: RendererMeta,
        x: str,
        *,
        y: str = "42",
        **kwargs: float,
    ):
        ...


def test_renderer_gen_limits_positional_arg_count():
    try:

        @renderer_gen
        def test_renderer(
            meta: RendererMeta,
            x: str,
            y: str,
        ):
            ...

        raise RuntimeError()
    except TypeError as e:
        assert "more than 2 positional" in str(e)


def test_renderer_gen_does_not_allow_args():
    try:

        @renderer_gen
        def test_renderer(
            meta: RendererMeta,
            x: str,
            *args: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "No variadic parameters" in str(e)


def test_renderer_gen_kwargs_have_defaults():
    try:

        @renderer_gen
        def test_renderer(
            meta: RendererMeta,
            x: str,
            *,
            y: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "did not have a default value" in str(e)


def test_renderer_gen_kwargs_can_not_be_name_render_fn():
    try:

        @renderer_gen
        def test_renderer(
            meta: RendererMeta,
            x: str,
            *,
            _render_fn: str,
        ):
            ...

        raise RuntimeError()

    except ValueError as e:
        assert "parameters can not be named `_render_fn`" in str(e)


def test_renderer_gen_result_does_not_allow_args():
    @renderer_gen
    def test_renderer(
        meta: RendererMeta,
        x: str,
    ):
        ...

    # Test that args can **not** be supplied
    def render_fn_sync(*args: str):
        return " ".join(args)

    async def render_fn_async(*args: str):
        return " ".join(args)

    try:
        test_renderer(  # type: ignore
            "X",
            "Y",
        )(render_fn_sync)
        raise RuntimeError()
    except RuntimeError as e:
        assert "`args` should not be supplied" in str(e)

    try:
        test_renderer(  # type: ignore
            "X",
            "Y",
        )(render_fn_async)
    except RuntimeError as e:
        assert "`args` should not be supplied" in str(e)
