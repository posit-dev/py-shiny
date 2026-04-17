from shiny import App, Inputs, Outputs, reactive, render, ui
from shiny.session import Session

app_ui = ui.page_fluid(
    ui.h3("Integer value (42)"),
    ui.tags.button("Send 42 (default)", id="btn_int_default"),
    ui.tags.button("Send 42 (event priority)", id="btn_int_event"),
    ui.output_text_verbatim("int_default_count"),
    ui.output_text_verbatim("int_event_count"),
    ui.h3("String values (event priority) - regression test for #1600"),
    ui.tags.button("Send '' (event priority)", id="btn_str_empty"),
    ui.tags.button("Send 'x=1' (event priority)", id="btn_str_nonempty"),
    ui.output_text_verbatim("str_event_count"),
    ui.h3("List value ([1, 2, 3])"),
    ui.tags.button("Send [1,2,3] (default)", id="btn_list_default"),
    ui.tags.button("Send [1,2,3] (event priority)", id="btn_list_event"),
    ui.output_text_verbatim("list_default_count"),
    ui.output_text_verbatim("list_event_count"),
    ui.tags.script("""
        document.getElementById('btn_int_default').addEventListener('click', function() {
            Shiny.setInputValue('int_default_input', 42);
        });
        document.getElementById('btn_int_event').addEventListener('click', function() {
            Shiny.setInputValue('int_event_input', 42, {priority: 'event'});
        });
        document.getElementById('btn_str_empty').addEventListener('click', function() {
            Shiny.setInputValue('str_event_input', '', {priority: 'event'});
        });
        document.getElementById('btn_str_nonempty').addEventListener('click', function() {
            Shiny.setInputValue('str_event_input', 'x=1', {priority: 'event'});
        });
        document.getElementById('btn_list_default').addEventListener('click', function() {
            Shiny.setInputValue('list_default_input', [1, 2, 3]);
        });
        document.getElementById('btn_list_event').addEventListener('click', function() {
            Shiny.setInputValue('list_event_input', [1, 2, 3], {priority: 'event'});
        });
        """),
)


def server(input: Inputs, output: Outputs, session: Session):
    int_default_counter = reactive.value(0)
    int_event_counter = reactive.value(0)
    str_event_counter = reactive.value(0)
    list_default_counter = reactive.value(0)
    list_event_counter = reactive.value(0)

    @reactive.effect
    @reactive.event(input.int_default_input)
    def _count_int_default():
        int_default_counter.set(int_default_counter() + 1)

    @reactive.effect
    @reactive.event(input.int_event_input)
    def _count_int_event():
        int_event_counter.set(int_event_counter() + 1)

    @reactive.effect
    @reactive.event(input.str_event_input)
    def _count_str_event():
        str_event_counter.set(str_event_counter() + 1)

    @reactive.effect
    @reactive.event(input.list_default_input)
    def _count_list_default():
        list_default_counter.set(list_default_counter() + 1)

    @reactive.effect
    @reactive.event(input.list_event_input)
    def _count_list_event():
        list_event_counter.set(list_event_counter() + 1)

    @render.text
    def int_default_count():
        return str(int_default_counter())

    @render.text
    def int_event_count():
        return str(int_event_counter())

    @render.text
    def str_event_count():
        return str(str_event_counter())

    @render.text
    def list_default_count():
        return str(list_default_counter())

    @render.text
    def list_event_count():
        return str(list_event_counter())


app = App(app_ui, server)
