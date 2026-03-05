"""
Playwright tests for async reactivity with OpenTelemetry instrumentation.

These tests verify that:
1. Async render functions create proper OTel spans
2. Async calcs that spawn tasks maintain correct context
3. Async effects with background work are instrumented
4. Concurrent operations maintain separate span contexts
5. Span parent-child relationships are correct through async boundaries

Note: This test primarily verifies that the app works correctly with OTel enabled.
The actual span verification is done in unit tests (test_otel_async_context.py).
This integration test ensures the full async reactive flow works end-to-end.
"""

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_async_render_with_otel(page: Page, local_app: ShinyAppProc) -> None:
    """Test that async render functions work with OTel instrumentation."""
    page.goto(local_app.url)

    # Verify async render output appears
    output = controller.OutputCode(page, "async_render_output")
    output.expect_value("Render result: Processed: Processed: test")

    # Change input and verify render updates
    text_input = controller.InputText(page, "text_input")
    text_input.set("hello")
    output.expect_value("Render result: Processed: Processed: hello")


def test_async_calc_with_background_tasks(page: Page, local_app: ShinyAppProc) -> None:
    """Test that async calcs spawning background tasks work with OTel."""
    page.goto(local_app.url)

    # Trigger the calc
    trigger = controller.InputActionButton(page, "trigger_calc")
    trigger.click()

    # Verify calc output appears with all background task results
    output = controller.OutputCode(page, "calc_output")
    output.expect_value(
        "Calc result: Processed: test, Processed: test_2, Processed: test_3"
    )

    # Change input and trigger again
    text_input = controller.InputText(page, "text_input")
    text_input.set("async")
    trigger.click()

    output.expect_value(
        "Calc result: Processed: async, Processed: async_2, Processed: async_3"
    )


def test_async_effect_with_otel(page: Page, local_app: ShinyAppProc) -> None:
    """Test that async effects with background work are instrumented."""
    page.goto(local_app.url)

    # Initial state
    output = controller.OutputCode(page, "effect_output")
    output.expect_value("Effect executed: 0 times")

    # Trigger effect
    trigger = controller.InputActionButton(page, "trigger_effect")
    trigger.click()

    # Verify effect executed
    output.expect_value("Effect executed: 1 times")

    # Trigger again
    trigger.click()
    output.expect_value("Effect executed: 2 times")


def test_concurrent_async_operations(page: Page, local_app: ShinyAppProc) -> None:
    """Test that concurrent async operations (gather) work with OTel."""
    page.goto(local_app.url)

    # Verify background tasks output with parallel execution
    output = controller.OutputCode(page, "background_tasks_output")
    output.expect_value("Task1: test | Task2: test | Task3: test")

    # Change input and verify all tasks update
    text_input = controller.InputText(page, "text_input")
    text_input.set("parallel")
    output.expect_value("Task1: parallel | Task2: parallel | Task3: parallel")


def test_full_async_flow_integration(page: Page, local_app: ShinyAppProc) -> None:
    """
    Integration test verifying the entire async reactive flow works with OTel.

    This test exercises all async patterns simultaneously:
    - Multiple async renders
    - Async calc with spawned tasks
    - Async effect with background work
    - Concurrent operations with gather

    If OTel context propagation is broken, one or more of these would fail.
    """
    page.goto(local_app.url)

    text_input = controller.InputText(page, "text_input")
    trigger_calc = controller.InputActionButton(page, "trigger_calc")
    trigger_effect = controller.InputActionButton(page, "trigger_effect")

    # Set input and trigger all operations
    text_input.set("integration")
    trigger_calc.click()
    trigger_effect.click()

    # Verify all outputs updated correctly
    controller.OutputCode(page, "async_render_output").expect_value(
        "Render result: Processed: Processed: integration"
    )
    controller.OutputCode(page, "calc_output").expect_value(
        "Calc result: Processed: integration, Processed: integration_2, Processed: integration_3"
    )
    controller.OutputCode(page, "effect_output").expect_value(
        "Effect executed: 1 times"
    )
    controller.OutputCode(page, "background_tasks_output").expect_value(
        "Task1: integration | Task2: integration | Task3: integration"
    )

    # Trigger again to verify consistency
    text_input.set("second")
    trigger_calc.click()
    trigger_effect.click()

    controller.OutputCode(page, "async_render_output").expect_value(
        "Render result: Processed: Processed: second"
    )
    controller.OutputCode(page, "calc_output").expect_value(
        "Calc result: Processed: second, Processed: second_2, Processed: second_3"
    )
    controller.OutputCode(page, "effect_output").expect_value(
        "Effect executed: 2 times"
    )
    controller.OutputCode(page, "background_tasks_output").expect_value(
        "Task1: second | Task2: second | Task3: second"
    )
