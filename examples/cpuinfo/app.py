import sys

if "pyodide" in sys.modules:
    # psutil doesn't work on pyodide--use fake data instead
    from fakepsutil import cpu_count, cpu_percent
else:
    from psutil import cpu_count, cpu_percent

from math import ceil

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

# The agg matplotlib backend seems to be a little more efficient than the default when
# running on macOS, and also gives more consistent results across operating systems
matplotlib.use("agg")

# max number of samples to retain
MAX_SAMPLES = 1000
# secs between samples
SAMPLE_PERIOD = 1


ncpu = cpu_count(logical=True)

app_ui = ui.page_fluid(
    ui.tags.style(
        """
        /* Don't apply fade effect, it's constantly recalculating */
        .recalculating, .recalculating > * {
            opacity: 1 !important;
        }
        tbody > tr:last-child {
            /*border: 3px solid var(--bs-dark);*/
            box-shadow:
                0 0 2px 1px #fff, /* inner white */
                0 0 4px 2px #0ff, /* middle cyan */
                0 0 5px 3px #00f; /* outer blue */
        }
        #table table {
            table-layout: fixed;
            width: %s;
            font-size: 0.8em;
        }
        th, td {
            text-align: center;
        }
        """
        % f"{ncpu * 4}em"
    ),
    # Disable busy indicators
    ui.busy_indicators.use(spinners=False, pulse=False),
    ui.h3("CPU Usage %", class_="mt-2"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "cmap",
                "Colormap",
                {
                    "inferno": "inferno",
                    "viridis": "viridis",
                    "copper": "copper",
                    "prism": "prism (not recommended)",
                },
            ),
            ui.p(ui.input_action_button("reset", "Clear history", class_="btn-sm")),
            ui.input_switch("hold", "Freeze output", value=False),
            class_="mb-3",
        ),
        ui.div(
            {"class": "card mb-3"},
            ui.div(
                {"class": "card-body"},
                ui.h5({"class": "card-title mt-0"}, "Graphs"),
                ui.output_plot("plot", height=f"{ncpu * 40}px"),
            ),
            ui.div(
                {"class": "card-footer"},
                ui.input_numeric("sample_count", "Number of samples per graph", 50),
            ),
        ),
        ui.div(
            {"class": "card"},
            ui.div(
                {"class": "card-body"},
                ui.h5({"class": "card-title m-0"}, "Heatmap"),
            ),
            ui.div(
                {"class": "card-body overflow-auto pt-0"},
                ui.output_table("table"),
            ),
            ui.div(
                {"class": "card-footer"},
                ui.input_numeric("table_rows", "Rows to display", 5),
            ),
        ),
    ),
)


@reactive.calc
def cpu_current():
    reactive.invalidate_later(SAMPLE_PERIOD)
    return cpu_percent(percpu=True)


def server(input: Inputs, output: Outputs, session: Session):
    cpu_history = reactive.value(None)

    @reactive.calc
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

    @reactive.effect
    def collect_cpu_samples():
        """cpu_percent() reports just the current CPU usage sample; this Effect gathers
        them up and stores them in the cpu_history reactive value, in a numpy 2D array
        (rows are CPUs, columns are time)."""

        new_data = np.vstack(cpu_current())
        with reactive.isolate():
            if cpu_history() is None:
                cpu_history.set(new_data)
            else:
                combined_data = np.hstack([cpu_history(), new_data])
                # Throw away extra data so we don't consume unbounded amounts of memory
                if combined_data.shape[1] > MAX_SAMPLES:
                    combined_data = combined_data[:, -MAX_SAMPLES:]
                cpu_history.set(combined_data)

    @reactive.effect(priority=100)
    @reactive.event(input.reset)
    def reset_history():
        cpu_history.set(None)

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

        ncols = 2
        nrows = int(ceil(ncpu / ncols))
        fig, axeses = plt.subplots(
            nrows=nrows,
            ncols=ncols,
            squeeze=False,
        )
        for i in range(0, ncols * nrows):
            row = i // ncols
            col = i % ncols
            axes = axeses[row, col]
            if i >= len(history):
                axes.set_visible(False)
                continue
            data = history[i]
            axes.yaxis.set_label_position("right")
            axes.yaxis.tick_right()
            axes.set_xlim(-(nsamples - 1), 0)
            axes.set_ylim(0, 100)

            assert len(data) <= nsamples

            # Set up an array of x-values that will right-align the data relative to the
            # plotting area
            x = np.arange(0, len(data))
            x = np.flip(-x)

            # Color bars by cmap
            color = plt.get_cmap(input.cmap())(data / 100)
            axes.bar(x, data, color=color, linewidth=0, width=1.0)

            axes.set_yticks([25, 50, 75])
            for ytl in axes.get_yticklabels():
                if col == ncols - 1 or i == ncpu - 1 or True:
                    ytl.set_fontsize(7)
                else:
                    ytl.set_visible(False)
                    hide_ticks(axes.yaxis)
            for xtl in axes.get_xticklabels():
                xtl.set_visible(False)
            hide_ticks(axes.xaxis)
            axes.grid(True, linewidth=0.25)

        return fig

    @render.table
    def table():
        history = cpu_history_with_hold()
        latest = pd.DataFrame(history).transpose().tail(input.table_rows())
        if latest.shape[0] == 0:
            return latest
        return (
            latest.style.format(precision=0)
            .hide(axis="index")
            .set_table_attributes(
                'class="dataframe shiny-table table table-borderless font-monospace"'
            )
            .background_gradient(cmap=input.cmap(), vmin=0, vmax=100)
        )


def hide_ticks(axis):
    for ticks in [axis.get_major_ticks(), axis.get_minor_ticks()]:
        for tick in ticks:
            tick.tick1line.set_visible(False)
            tick.tick2line.set_visible(False)
            tick.label1.set_visible(False)
            tick.label2.set_visible(False)


app = App(app_ui, server)
