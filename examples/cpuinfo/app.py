import psutil

import numpy as np
import matplotlib.pyplot as plt
from shiny import Inputs, Outputs, Session, App, reactive, render, ui

ncpu = psutil.cpu_count(logical=True)

app_ui = ui.page_fluid(
    ui.tags.style(
        """
        /* Don't apply fade effect to plot, it's constantly recalculating */
        #plot.recalculating {
            opacity: 1;
        }
        """
    ),
    ui.input_numeric("sample_count", "Samples to show (0.5 sec per sample)", 100),
    ui.input_checkbox("hold", "Hold graph", value=False),
    ui.input_action_button("reset", "Clear history"),
    ui.output_plot("plot", height=f"{ncpu * 80}px", width="400px"),
)


@reactive.Calc
def cpu_percent():
    reactive.invalidate_later(0.5)
    return psutil.cpu_percent(percpu=True)


def server(input: Inputs, output: Outputs, session: Session):
    cpu_history = reactive.Value(None)

    @reactive.Effect
    def _():
        new_data = np.vstack(cpu_percent())
        with reactive.isolate():
            if cpu_history() is None:
                cpu_history.set(new_data)
            else:
                cpu_history.set(np.hstack([cpu_history(), new_data]))

    @reactive.Effect(priority=100)
    @reactive.event(input.reset)
    def _():
        cpu_history.set(None)

    @output
    @render.plot
    def plot():
        if not input.hold():
            history = cpu_history()
        else:
            # Even if frozen, we still want to respond to input.reset()
            input.reset()
            with reactive.isolate():
                history = cpu_history()

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
            axes.set_xlim(-nsamples, -1)
            axes.set_ylim(0, 100)

            assert len(data) <= nsamples

            x = np.array(range(nsamples - len(data), nsamples))
            x -= nsamples

            axes.plot(x, data, color="blue", linewidth=0.5)
            axes.set_yticks([25, 50, 75])
            for ytl in axes.get_yticklabels():
                ytl.set_fontsize(7)
            for xtl in axes.get_xticklabels():
                if i == ncpu - 1:
                    xtl.set_fontsize(7)
                else:
                    xtl.set_visible(False)
            axes.grid(True, linewidth=0.25)
            if len(data) > 0 and data[-1] > 90:
                axes.set_facecolor("#FF6666")
            elif len(data) > 0 and data[-1] > 80:
                axes.set_facecolor("pink")
            elif len(data) > 0 and data[-1] > 50:
                axes.set_facecolor("#FFFFCC")
        return fig


app = App(app_ui, server)
