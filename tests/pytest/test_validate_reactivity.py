from textwrap import dedent

import pytest

from shiny.validate import validate_shiny_code


@pytest.mark.parametrize(
    "read", ["weights()", "weights.get()", "input.n()", "input['n']()", "doubled()"]
)
def test_extended_task_cannot_read_reactive_sources(read: str) -> None:
    result = validate_shiny_code(dedent(f"""\
        from shiny import Inputs, reactive
        def server(input: Inputs, weights: reactive.Value[dict]):
            @reactive.calc
            def doubled():
                return input.n() * 2
            @reactive.extended_task
            async def compute():
                return {read}
        """))
    assert [(issue["code"], issue["line"]) for issue in result.errors] == [
        ("EXTENDED_TASK_REACTIVE_READ", 8)
    ]


@pytest.mark.parametrize(
    "code, line",
    [
        # Core: reading an input directly in the server body.
        (
            "from shiny import Inputs, Outputs, Session\n"
            "def server(input: Inputs, output: Outputs, session: Session):\n"
            "    n = input.n()\n",
            3,
        ),
        # Core: a server function recognised by its (input, output, session) signature.
        (
            "from shiny import reactive\n"
            "count = reactive.value(0)\n"
            "async def app_server(input, output, session):\n"
            "    if count() > 1:\n"
            "        pass\n",
            4,
        ),
        # Module server function.
        (
            "from shiny import module, reactive\n"
            "@module.server\n"
            "def panel(input, output, session, weights: reactive.Value[dict]):\n"
            "    total = sum(weights().values())\n",
            4,
        ),
        # Calc read at server level.
        (
            "from shiny import reactive\n"
            "def server(input, output, session):\n"
            "    @reactive.calc\n"
            "    def doubled():\n"
            "        return input.n() * 2\n"
            "    print(doubled())\n",
            6,
        ),
        # Express: module-level read of an input.
        (
            "from shiny.express import input, ui\n"
            "ui.input_slider('n', 'N', 1, 10, 5)\n"
            "ui.h1(f'Value: {input.n()}')\n",
            3,
        ),
        # Express: module-level read of a reactive value inside a UI container.
        (
            "from shiny import reactive\n"
            "from shiny.express import ui\n"
            "state = reactive.value(1)\n"
            "with ui.card():\n"
            "    ui.p(state.get())\n",
            5,
        ),
        # A decorator argument is evaluated in the server body, not the function.
        (
            "from shiny import reactive\n"
            "def server(input, output, session):\n"
            "    @reactive.effect\n"
            "    @reactive.event(input.go())\n"
            "    def run():\n"
            "        pass\n",
            4,
        ),
    ],
)
def test_reactive_read_outside_reactive_context(code: str, line: int) -> None:
    result = validate_shiny_code(code)
    assert [(issue["code"], issue["line"]) for issue in result.errors] == [
        ("REACTIVE_READ_OUTSIDE_CONTEXT", line)
    ]
    assert "reactive.isolate" in result.errors[0]["message"]


@pytest.mark.parametrize(
    "code",
    [
        # Reads inside render/calc/effect functions.
        "from shiny import render\n"
        "def server(input, output, session):\n"
        "    @render.text\n    def txt():\n        return input.n()\n",
        # Reads inside a plain helper, which may be called from a reactive context.
        "from shiny import Inputs\n"
        "def summarize(input: Inputs):\n    return input.n()\n"
        "def server(input, output, session):\n"
        "    def nested():\n        return input.n()\n",
        # Reads wrapped in reactive.isolate(), including an imported alias.
        "from shiny import reactive\n"
        "def server(input, output, session):\n"
        "    with reactive.isolate():\n        start = input.n()\n",
        "from shiny.reactive import isolate\n"
        "from shiny.express import input, ui\n"
        "with isolate():\n    ui.p(input.n())\n",
        # Reads inside a lambda or a decorator-registered callback.
        "def server(input, output, session):\n"
        "    session.on_ended(lambda: print(input.n()))\n",
        # Passing the input itself (not a read) to reactive.event.
        "from shiny import reactive\n"
        "def server(input, output, session):\n"
        "    @reactive.effect\n    @reactive.event(input.go)\n"
        "    def run():\n        pass\n",
        # Express module-level renderers and effects are functions.
        "from shiny import reactive\n"
        "from shiny.express import input, render\n"
        "@render.text\ndef txt():\n    return input.n()\n"
        "@reactive.effect\ndef log():\n    print(input.n())\n",
    ],
)
def test_reads_inside_reactive_or_isolated_code_are_allowed(code: str) -> None:
    assert validate_shiny_code(code).clean


@pytest.mark.parametrize(
    "mutation",
    [
        "current['AAPL'] = 0.5",
        "current.update(AAPL=0.5)",
        "current.append(1)",
        "del current['AAPL']",
    ],
)
def test_mutation_followed_by_setting_same_reactive_object(mutation: str) -> None:
    result = validate_shiny_code(dedent(f"""\
        from shiny import reactive
        state = reactive.Value({{}})
        @reactive.effect
        def update():
            current = state()
            {mutation}
            state.set(current)
        """))
    assert [(issue["code"], issue["line"]) for issue in result.warnings] == [
        ("REACTIVE_MUTATION", 7),
        # Reading and setting `state` in one effect also re-triggers it.
        ("EFFECT_SELF_INVALIDATION", 7),
    ]


def test_mutation_through_alias_is_detected() -> None:
    result = validate_shiny_code(
        "from shiny import reactive\n"
        "state = reactive.value({})\n"
        "@reactive.effect\n"
        "def update():\n"
        "    current = state.get()\n"
        "    alias = current\n"
        "    alias['x'] = 1\n"
        "    state.set(current)\n"
    )
    assert [issue["code"] for issue in result.warnings] == [
        "REACTIVE_MUTATION",
        "EFFECT_SELF_INVALIDATION",
    ]


@pytest.mark.parametrize(
    "handler", ["except Exception:", "except BaseException:", "except:"]
)
def test_broad_catch_must_not_swallow_extended_task_result(handler: str) -> None:
    result = validate_shiny_code(dedent(f"""\
        from shiny import reactive
        @reactive.extended_task
        async def compute():
            return [1]
        @reactive.calc
        def data():
            try:
                trajectories = compute.result()
            {handler}
                trajectories = None
            return trajectories
        """))
    assert [(issue["code"], issue["line"]) for issue in result.warnings] == [
        ("SWALLOWED_TASK_ERROR", 9)
    ]


@pytest.mark.parametrize(
    "code",
    [
        "from shiny import reactive\nstate = reactive.Value({})\n"
        "def update():\n    current = state().copy()\n    current['x'] = 1\n    state.set(current)",
        "from shiny import reactive\nstate = reactive.Value({})\n"
        "def update():\n    current = dict(state())\n    current['x'] = 1\n    state.set(current)",
        "from shiny import reactive\nstate = reactive.Value({})\n"
        "def update():\n    current = state()\n    state.set({**current, 'x': 1})",
        "from shiny import reactive\nstate = reactive.Value({})\n"
        "def update():\n    current = state()\n    current = {}\n    current['x'] = 1\n    state.set(current)",
        "from shiny import reactive\nstate = reactive.Value(0)\n"
        "def update():\n    current = state()\n    current += 1\n    state.set(current)",
        "from shiny import reactive\nstate = reactive.Value({})\n"
        "def unrelated(state: dict):\n    return state.items()",
        "from shiny import reactive\nstate = reactive.Value(1)\n"
        "@reactive.extended_task\nasync def compute(state: int):\n    return state * 2",
        "from shiny import reactive\n"
        "@reactive.extended_task\nasync def compute():\n    return [1]\n"
        "@reactive.calc\ndef data():\n    try:\n        return compute.result()\n    except Exception:\n        raise",
        "from shiny import reactive\n"
        "@reactive.extended_task\nasync def compute():\n    return [1]\n"
        "@reactive.calc\ndef data():\n    try:\n        return compute.result()\n    except ValueError:\n        return []",
        "from shiny import reactive\n"
        "state = reactive.Value(1)\n"
        "@reactive.extended_task\nasync def compute(n):\n    return n * 2\n"
        "@reactive.effect\ndef invoke():\n    compute(state())",
    ],
)
def test_valid_reactive_usage_is_not_reported(code: str) -> None:
    assert validate_shiny_code(code).clean


def test_reactive_rules_support_import_aliases_and_string_annotations() -> None:
    result = validate_shiny_code(
        "from shiny.reactive import Value as RV, extended_task as task\n"
        "def server(weights: 'RV[dict]'):\n"
        "    @task\n"
        "    async def compute():\n"
        "        return weights()\n"
    )
    assert [issue["code"] for issue in result.errors] == ["EXTENDED_TASK_REACTIVE_READ"]


def test_reactive_rule_findings_can_be_suppressed() -> None:
    result = validate_shiny_code(
        "from shiny import reactive\n"
        "state = reactive.Value({})\n"
        "@reactive.extended_task\n"
        "async def compute():\n"
        "    return state()  # shiny: ignore EXTENDED_TASK_REACTIVE_READ\n"
        "def update():\n"
        "    current = state()\n"
        "    current['x'] = 1\n"
        "    state.set(current)  # shiny: ignore REACTIVE_MUTATION\n"
    )
    assert result.clean


def test_annotated_read_alias_is_checked_for_mutation() -> None:
    result = validate_shiny_code(
        "from shiny import reactive\nstate = reactive.Value({})\n"
        "def update():\n    current: dict = state()\n"
        "    current['x'] = 1\n    state.set(current)\n"
    )
    assert [issue["code"] for issue in result.warnings] == ["REACTIVE_MUTATION"]


@pytest.mark.parametrize(
    "body, line",
    [
        ("    count.set(count() + 1)\n", 5),
        ("    if count() < 10:\n        count.set(count() + 1)\n", 6),
        ("    n = count.get()\n    count.set(n + 1)\n", 6),
    ],
)
def test_effect_that_reads_and_sets_the_same_value_re_triggers(
    body: str, line: int
) -> None:
    result = validate_shiny_code(
        "from shiny import reactive\n"
        "count = reactive.value(0)\n"
        "@reactive.effect\n"
        "def tick():\n" + body
    )
    assert [(issue["code"], issue["line"]) for issue in result.warnings] == [
        ("EFFECT_SELF_INVALIDATION", line)
    ]


@pytest.mark.parametrize(
    "code",
    [
        # Read inside isolate, then set.
        "from shiny import reactive\ncount = reactive.value(0)\n"
        "@reactive.effect\ndef tick():\n"
        "    with reactive.isolate():\n        n = count()\n    count.set(n + 1)\n",
        # Triggered by an event, so it only reruns on the event.
        "from shiny import reactive\ncount = reactive.value(0)\n"
        "@reactive.effect\n@reactive.event(lambda: None)\ndef tick():\n"
        "    count.set(count() + 1)\n",
        # Sets a different value than it reads.
        "from shiny import reactive\na = reactive.value(0)\nb = reactive.value(0)\n"
        "@reactive.effect\ndef copy():\n    b.set(a())\n",
        # The read and set happen in a nested function, which runs elsewhere.
        "from shiny import reactive\ncount = reactive.value(0)\n"
        "@reactive.effect\ndef tick():\n"
        "    def later():\n        count.set(count() + 1)\n",
    ],
)
def test_effect_without_self_invalidation_is_not_reported(code: str) -> None:
    assert validate_shiny_code(code).clean


def test_calc_that_sets_a_reactive_value_is_reported() -> None:
    result = validate_shiny_code(
        "from shiny import reactive\n"
        "count = reactive.value(0)\n"
        "@reactive.calc\n"
        "def doubled():\n"
        "    count.set(1)\n"
        "    return 2\n"
    )
    assert [(issue["code"], issue["line"]) for issue in result.warnings] == [
        ("CALC_SIDE_EFFECT", 5)
    ]
    assert validate_shiny_code(
        "from shiny import reactive\ncount = reactive.value(0)\n"
        "@reactive.calc\ndef doubled():\n    return count() * 2\n"
    ).clean


def test_configuring_inputs_in_the_server_body_is_allowed() -> None:
    assert validate_shiny_code(
        "def server(input, output, session):\n"
        "    input.set_snapshot_preprocess('secret', lambda value: '<redacted>')\n"
        "    input.set_serializer('secret', lambda value: '<redacted>')\n"
    ).clean


def test_wrapping_task_result_exceptions_does_not_preserve_pending_signal() -> None:
    result = validate_shiny_code(
        "from shiny import reactive\n"
        "@reactive.extended_task\nasync def compute():\n    return 1\n"
        "def data():\n    try:\n        return compute.result()\n"
        "    except Exception as error:\n        raise ValueError('failed') from error\n"
    )
    assert [issue["code"] for issue in result.warnings] == ["SWALLOWED_TASK_ERROR"]
