import sys

if "pyodide" in sys.modules:
    # psutil doesn't work on pyodide--use fake data instead
    from fakepsutil import cpu_count, cpu_percent
else:
    from psutil import cpu_count, cpu_percent

import matplotlib
import numpy as np
import pandas as pd
from helpers import plot_cpu

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

# The agg matplotlib backend seems to be a little more efficient than the default when
# running on macOS, and also gives more consistent results across operating systems
matplotlib.use("agg")

# max number of samples to retain
MAX_SAMPLES = 1000
# secs between samples
SAMPLE_PERIOD = 1


ncpu = cpu_count(logical=True)

app_ui = ui.page_sidebar(
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
        ui.input_action_button("reset", "Clear history", class_="btn-sm"),
        ui.input_switch("hold", "Freeze output", value=False),
    ),
    ui.tags.style(
        """
        /* Don't apply fade effect, it's constantly recalculating */
        .recalculating {
            opacity: 1;
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
        % f"{ncpu*4}em"
    ),
    ui.card(
        ui.navset_bar(
            ui.nav(
                "Graphs",
                ui.output_plot("plot", height=f"{ncpu * 40}px"),
                ui.input_numeric("sample_count", "Number of samples per graph", 50),
            ),
            ui.nav(
                "Heatmap",
                ui.output_table("table"),
                ui.input_numeric("table_rows", "Rows to display", 5),
            ),
            title="CPU Usage",
        )
    ),
)


@reactive.Calc
def cpu_current():
    reactive.invalidate_later(SAMPLE_PERIOD)
    return cpu_percent(percpu=True)


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

    @reactive.Effect(priority=100)
    @reactive.event(input.reset)
    def reset_history():
        cpu_history.set(None)

    @render.plot
    def plot():
        return plot_cpu(
            cpu_history_with_hold(), input.sample_count(), ncpu, input.cmap()
        )

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


app = App(app_ui, server)
