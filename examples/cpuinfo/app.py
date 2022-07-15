import psutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shiny import Inputs, Outputs, Session, App, reactive, render, ui


MAX_SAMPLES = 10_000
rate = 1  # secs between samples

RED_THRESHOLD = 90
ORANGE_THRESHOLD = 75
YELLOW_THRESHOLD = 50
RED = "#FFAAAA"
ORANGE = "#FFCCAA"
YELLOW = "#FFFFCC"


ncpu = psutil.cpu_count(logical=True)

app_ui = ui.page_fluid(
    ui.tags.style(
        """
        /* Don't apply fade effect, it's constantly recalculating */
        .recalculating {
            opacity: 1;
        }
        tbody > tr:last-child {
            border: 3px solid var(--bs-dark);
        }
        #table table {
            table-layout: fixed;
            width: %s;
        }
        th, td {
            text-align: right;
        }
        """
        % f"{ncpu*3.5}em"
    ),
    {"class": "p-3"},
    ui.input_numeric("sample_count", f"Samples to show ({rate}sec per sample)", 100),
    ui.input_checkbox("hold", "Hold graph", value=False),
    ui.input_action_button("reset", "Clear history"),
    ui.output_plot("plot", height=f"{ncpu * 80}px", width="400px"),
    ui.output_table("table"),
)


@reactive.Calc
def cpu_percent():
    reactive.invalidate_later(rate)
    return psutil.cpu_percent(percpu=True)


def server(input: Inputs, output: Outputs, session: Session):
    cpu_history = reactive.Value(None)

    @reactive.Calc
    def cpu_history_with_hold():
        # If "hold" is on, grab an isolated snapshot of cpu_history; if not, then do a
        # regular read
        if not input.hold():
            return cpu_history()
        else:
            # Even if frozen, we still want to respond to input.reset()
            input.reset()
            with reactive.isolate():
                return cpu_history()

    @reactive.Effect
    def collect_cpu_samples():
        """cpu_percent() reports just the current CPU usage sample; this Effect gathers
        them up and stores them in the cpu_history reactive value, in a numpy 2D array
        (rows are CPUs, columns are time)."""

        new_data = np.vstack(cpu_percent())
        with reactive.isolate():
            if cpu_history() is None:
                cpu_history.set(new_data)
            else:
                combined_data = np.hstack([cpu_history(), new_data])
                # Throw away extra data so we don't consume unbounded amounts of memory
                if combined_data.shape[1] > MAX_SAMPLES:
                    combined_data = combined_data[:, -MAX_SAMPLES:]
                cpu_history.set(combined_data)

    @reactive.Effect(priority=100)
    @reactive.event(input.reset)
    def reset_history():
        cpu_history.set(None)

    @output
    @render.plot
    def plot():
        history = cpu_history_with_hold()

        if history is None:
            history = np.array([])
            history.shape = (ncpu, 0)

        nsamples = input.sample_count()

        # Throw away samples too old to fit on the plot
        if history.shape[1] > nsamples:
            history = history[:, -nsamples:]

        fig, axeses = plt.subplots(nrows=ncpu, ncols=1)
        for i in range(0, ncpu):
            data = history[i]
            axes = axeses[i]
            axes.set_xlim(-(nsamples - 1), 0)
            axes.set_ylim(0, 100)

            assert len(data) <= nsamples

            # Set up an array of x-values that will right-align the data relative to the
            # plotting area
            x = np.arange(0, len(data))
            x = np.flip(-x)

            # Plot history as lines
            axes.plot(x, data, color="blue", linewidth=0.5)
            # Plot current sample as dot
            current = data[-1:]  # may be zero-length
            axes.scatter(np.zeros(len(current)), current, color="blue")

            axes.set_yticks([25, 50, 75])
            for ytl in axes.get_yticklabels():
                ytl.set_fontsize(7)
            for xtl in axes.get_xticklabels():
                if i == ncpu - 1:
                    xtl.set_fontsize(7)
                else:
                    xtl.set_visible(False)
            axes.grid(True, linewidth=0.25)

            if len(data) > 0 and data[-1] > RED_THRESHOLD:
                axes.set_facecolor(RED)
            elif len(data) > 0 and data[-1] > ORANGE_THRESHOLD:
                axes.set_facecolor(ORANGE)
            elif len(data) > 0 and data[-1] > YELLOW_THRESHOLD:
                axes.set_facecolor(YELLOW)
        return fig

    @output
    @render.table(index=True)
    def table():
        history = cpu_history_with_hold()
        latest = pd.DataFrame(history).transpose().tail()
        if latest.shape[0] == 0:
            return latest
        return (
            latest.style.format(precision=0)
            .set_table_attributes('class="dataframe shiny-table table font-monospace"')
            .highlight_between(
                color=YELLOW,
                left=YELLOW_THRESHOLD,
                right=ORANGE_THRESHOLD,
                inclusive="left",
            )
            .highlight_between(
                color=ORANGE,
                left=ORANGE_THRESHOLD,
                right=RED_THRESHOLD,
                inclusive="left",
            )
            .highlight_between(
                color=RED,
                left=RED_THRESHOLD,
                right=100,
                inclusive="both",
            )
        )


app = App(app_ui, server)
