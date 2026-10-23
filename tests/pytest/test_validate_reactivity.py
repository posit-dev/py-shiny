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
    "access", ["weights.items()", "weights.keys()", "weights['AAPL']"]
)
def test_reactive_value_parameter_requires_a_call(access: str) -> None:
    result = validate_shiny_code(dedent(f"""\
        from shiny import module, reactive
        @module.server
        def allocation(input, output, session, weights: reactive.Value[dict]):
            @reactive.calc
            def summary():
                return {access}
        """))
    assert [issue["code"] for issue in result.errors] == ["UNCALLED_REACTIVE"]


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
        ("REACTIVE_MUTATION", 7)
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
    assert [issue["code"] for issue in result.warnings] == ["REACTIVE_MUTATION"]


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


def test_wrapping_task_result_exceptions_does_not_preserve_pending_signal() -> None:
    result = validate_shiny_code(
        "from shiny import reactive\n"
        "@reactive.extended_task\nasync def compute():\n    return 1\n"
        "def data():\n    try:\n        return compute.result()\n"
        "    except Exception as error:\n        raise ValueError('failed') from error\n"
    )
    assert [issue["code"] for issue in result.warnings] == ["SWALLOWED_TASK_ERROR"]
