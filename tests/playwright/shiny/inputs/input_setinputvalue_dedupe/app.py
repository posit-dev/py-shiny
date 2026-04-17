from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h3("Integer value (42)"),
    ui.tags.button("Send 42 (default)", id="btn_int_default"),
    ui.tags.button("Send 42 (event priority)", id="btn_int_event"),
    ui.output_text_verbatim("int_default_count"),
    ui.output_text_verbatim("int_event_count"),
    ui.h3("List value ([1, 2, 3])"),
    ui.tags.button("Send [1,2,3] (default)", id="btn_list_default"),
    ui.tags.button("Send [1,2,3] (event priority)", id="btn_list_event"),
    ui.output_text_verbatim("list_default_count"),
    ui.output_text_verbatim("list_event_count"),
    ui.tags.script(
        """
        document.getElementById('btn_int_default').addEventListener('click', function() {
            Shiny.setInputValue('int_default_input', 42);
        });
        document.getElementById('btn_int_event').addEventListener('click', function() {
            Shiny.setInputValue('int_event_input', 42, {priority: 'event'});
        });
        document.getElementById('btn_list_default').addEventListener('click', function() {
            Shiny.setInputValue('list_default_input', [1, 2, 3]);
        });
        document.getElementById('btn_list_event').addEventListener('click', function() {
            Shiny.setInputValue('list_event_input', [1, 2, 3], {priority: 'event'});
        });
        """
    ),
)


def server(input, output, session):
    int_default_counter = reactive.value(0)
    int_event_counter = reactive.value(0)
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
    def list_default_count():
        return str(list_default_counter())

    @render.text
    def list_event_count():
        return str(list_event_counter())


app = App(app_ui, server)
