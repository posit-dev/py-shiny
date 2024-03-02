import asyncio
import io
import os
from datetime import date

import matplotlib.pyplot as plt
import numpy as np

from shiny.express import render, ui

ui.page_opts(title="Various download examples")

with ui.accordion(open=True):
    with ui.accordion_panel("Simple case"):
        ui.markdown("Downloads a pre-existing file, using its existing name on disk.")

        @render.download(label="Download CSV")
        def download1():
            """
            This is the simplest case. The implementation simply returns the name of a file.
            Note that the function name (`download1`) determines which download_button()
            corresponds to this function.
            """

            path = os.path.join(os.path.dirname(__file__), "mtcars.csv")
            return path

    with ui.accordion_panel("Dynamic data generation"):
        ui.markdown("Downloads a PNG that's generated on the fly.")

        ui.input_text("title", "Plot title", "Random scatter plot")
        ui.input_slider("num_points", "Number of data points", min=1, max=100, value=50)

        @render.download(label="Download plot", filename="image.png")
        def download2():
            """
            Another way to implement a file download is by yielding bytes; either all at
            once, like in this case, or by yielding multiple times. When using this
            approach, you should pass a filename argument to @render.download, which
            determines what the browser will name the downloaded file.
            """

            print(input.num_points())
            x = np.random.uniform(size=input.num_points())
            y = np.random.uniform(size=input.num_points())
            plt.figure()
            plt.scatter(x, y)
            plt.title(input.title())
            with io.BytesIO() as buf:
                plt.savefig(buf, format="png")
                yield buf.getvalue()

    with ui.accordion_panel("Dynamic filename"):
        ui.markdown(
            "Demonstrates that filenames can be generated on the fly (and use Unicode characters!)."
        )

        @render.download(
            label="Download filename",
            filename=lambda: f"新型-{date.today().isoformat()}-{np.random.randint(100, 999)}.csv",
        )
        async def download3():
            await asyncio.sleep(0.25)
            yield "one,two,three\n"
            yield "新,1,2\n"
            yield "型,4,5\n"

    with ui.accordion_panel("Failed downloads"):
        ui.markdown(
            "Throws an error in the download handler, download should not succeed."
        )

        @render.download(label="Download", filename="failuretest.txt")
        async def download4():
            yield "hello"
            raise Exception("This error was caused intentionally")
