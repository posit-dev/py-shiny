from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_code_editor_initial_state(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    code = controller.InputCodeEditor(page, "code")
    code.expect_label("Python code")
    code.expect_language("python")
    code.expect_value(
        "def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))"
    )
    code.expect_height("200px")
    code.expect_theme_light("github-light")
    code.expect_theme_dark("github-dark")
    code.expect_read_only(False)
    code.expect_line_numbers(True)


def test_input_code_editor_readonly(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    readonly = controller.InputCodeEditor(page, "readonly")
    readonly.expect_language("javascript")
    readonly.expect_read_only(True)
    readonly.expect_value("// This code cannot be edited\nconst x = 42;")


def test_input_code_editor_markdown_defaults(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    markdown = controller.InputCodeEditor(page, "markdown")
    markdown.expect_language("markdown")
    markdown.expect_line_numbers(False)
    markdown.expect_word_wrap(True)


def test_input_code_editor_themed(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    themed = controller.InputCodeEditor(page, "themed")
    themed.expect_language("sql")
    themed.expect_theme_light("vs-code-light")
    themed.expect_theme_dark("dracula")
    themed.expect_tab_size(4)


def test_input_code_editor_set_value(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    code = controller.InputCodeEditor(page, "code")

    initial_value = (
        "def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))"
    )
    code.expect_value(initial_value)

    code.set("print('New code')")
    code.expect_value("print('New code')")


def test_input_code_editor_set_and_submit(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    code = controller.InputCodeEditor(page, "code")
    value_output = controller.OutputTextVerbatim(page, "code_value")

    code.set("print('Submitted!')", submit=True)
    code.expect_value("print('Submitted!')")
    value_output.expect_value("Current value:\nprint('Submitted!')")


def test_input_code_editor_submit(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    code = controller.InputCodeEditor(page, "code")
    value_output = controller.OutputTextVerbatim(page, "code_value")

    code.set("x = 42")
    code.submit()
    value_output.expect_value("Current value:\nx = 42")


def test_input_code_editor_update_value(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    code = controller.InputCodeEditor(page, "code")
    update_btn = controller.InputActionButton(page, "update_value")

    update_btn.click()
    code.expect_value("# Updated from server\nprint('Hello from server!')")


def test_input_code_editor_update_language(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    code = controller.InputCodeEditor(page, "code")
    update_btn = controller.InputActionButton(page, "update_language")

    code.expect_language("python")
    update_btn.click()
    code.expect_language("javascript")
    code.expect_value("function hello() {\n  console.log('Hello!');\n}")


def test_input_code_editor_toggle_read_only(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    code = controller.InputCodeEditor(page, "code")
    toggle_btn = controller.InputActionButton(page, "toggle_read_only")

    code.expect_read_only(False)
    toggle_btn.click()
    code.expect_read_only(True)
    toggle_btn.click()
    code.expect_read_only(False)


def test_input_code_editor_toggle_line_numbers(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    code = controller.InputCodeEditor(page, "code")
    toggle_btn = controller.InputActionButton(page, "toggle_line_numbers")

    code.expect_line_numbers(True)
    toggle_btn.click()
    code.expect_line_numbers(False)
    toggle_btn.click()
    code.expect_line_numbers(True)
