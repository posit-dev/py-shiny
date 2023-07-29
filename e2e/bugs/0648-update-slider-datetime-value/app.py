import datetime

from shiny import App, reactive, render, ui

start_time = datetime.datetime(2023, 7, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
end_time = start_time + datetime.timedelta(hours=1)

app_ui = ui.page_fluid(
    ui.input_slider(
        "times",
        "Times",
        start_time,
        end_time,
        start_time,
        time_format="%H:%M:%S",
    ),
    ui.output_text_verbatim("txt"),
    ui.input_action_button("reset", "Jump to end"),
)


def server(input, output, session):
    @output
    @render.text
    def txt():
        return input.times()

    @reactive.Effect
    @reactive.event(input.reset)
    def reset_time():
        ui.update_slider("times", value=end_time)


app = App(app_ui, server)
