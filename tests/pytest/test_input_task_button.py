from shiny.ui import input_task_button


def test_input_task_button_class_default_type():
    btn = input_task_button("go", "Go")
    assert btn.attrs["class"] == "bslib-task-button btn btn-primary"


def test_input_task_button_class_explicit_type():
    btn = input_task_button("go", "Go", type="danger")
    assert btn.attrs["class"] == "bslib-task-button btn btn-danger"


def test_input_task_button_keeps_binding_class_when_type_is_none():
    # `type=None` documents "leave off the Bootstrap-specific button CSS classes",
    # but `.bslib-task-button` is the selector bslib's input binding uses to find
    # the button, so dropping it would leave the button unbound.
    btn = input_task_button("go", "Go", type=None)
    assert btn.attrs["class"] == "bslib-task-button"
