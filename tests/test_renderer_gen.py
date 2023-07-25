from shiny.render._render import RenderFn, RenderMeta, renderer


def test_renderer_gen_name_and_docs_are_copied():
    @renderer
    async def my_handler(meta: RenderMeta, fn: RenderFn[str]) -> str:
        "Test docs go here"
        return str(await fn())

    assert my_handler.__doc__ == "Test docs go here"
    assert my_handler.__name__ == "my_handler"


def test_renderer_gen_works():
    # No args works
    @renderer
    async def test_renderer(
        meta: RenderMeta,
        fn: RenderFn[str],
    ):
        ...


def test_renderer_gen_kwargs_are_allowed():
    # Test that kwargs can be allowed
    @renderer
    async def test_renderer(
        meta: RenderMeta,
        fn: RenderFn[str],
        *,
        y: str = "42",
    ):
        ...


def test_renderer_gen_with_pass_through_kwargs():
    # No args works
    @renderer
    async def test_renderer(
        meta: RenderMeta,
        fn: RenderFn[str],
        *,
        y: str = "42",
        **kwargs: float,
    ):
        ...


def test_renderer_gen_limits_positional_arg_count():
    try:

        @renderer
        async def test_renderer(
            meta: RenderMeta,
            fn: RenderFn[str],
            y: str,
        ):
            ...

        raise RuntimeError()
    except TypeError as e:
        assert "more than 2 positional" in str(e)


def test_renderer_gen_does_not_allow_args():
    try:

        @renderer
        async def test_renderer(
            meta: RenderMeta,
            fn: RenderFn[str],
            *args: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "No variadic parameters" in str(e)


def test_renderer_gen_kwargs_have_defaults():
    try:

        @renderer
        async def test_renderer(
            meta: RenderMeta,
            fn: RenderFn[str],
            *,
            y: str,
        ):
            ...

        raise RuntimeError()

    except TypeError as e:
        assert "did not have a default value" in str(e)


def test_renderer_gen_kwargs_can_not_be_name_render_fn():
    try:

        @renderer
        async def test_renderer(
            meta: RenderMeta,
            fn: RenderFn[str],
            *,
            _render_fn: str,
        ):
            ...

        raise RuntimeError()

    except ValueError as e:
        assert "parameters can not be named `_render_fn`" in str(e)


def test_renderer_gen_result_does_not_allow_args():
    @renderer
    async def test_renderer(
        meta: RenderMeta,
        fn: RenderFn[str],
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
