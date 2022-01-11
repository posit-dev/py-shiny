# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

# Add parent directory to path, so we can find the prism module.
# (This is just a temporary fix)
import asyncio
from datetime import date
import os
import io
import matplotlib.pyplot as plt
import numpy as np

from shiny import *


def make_example(id: str, label: str, title: str, desc: str, extra: Any = None):
    return column(
        3,
        tags.div(
            class_="card mb-4",
            children=[
                tags.div(title, class_="card-header"),
                tags.div(
                    class_="card-body",
                    children=[
                        tags.p(desc, class_="card-text text-muted"),
                        extra,
                        download_button(id, label, class_="btn-primary"),
                    ],
                ),
            ],
        ),
    )


ui = page_fluid(
    tags.h1("Download examples"),
    row(
        make_example(
            "download1",
            label="Download CSV",
            title="Simple case",
            desc="Downloads a pre-existing file, using its existing name on disk.",
        ),
    ),
    row(
        make_example(
            "download2",
            label="Download plot",
            title="Dynamic data generation",
            desc="Downloads a PNG that's generated on the fly.",
            extra=[
                input_text("title", "Plot title", "Random scatter plot"),
                input_slider("num_points", "Number of data points", 1, 100, 50),
            ],
        ),
    ),
    row(
        make_example(
            "download3",
            "Download",
            "Dynamic filename",
            "Demonstrates that filenames can be generated on the fly (and use Unicode characters!).",
        ),
    ),
    row(
        make_example(
            "download4",
            "Download",
            "Failed downloads",
            "Throws an error in the download handler, download should not succeed.",
        ),
    ),
    row(
        make_example(
            "download5",
            "Download",
            "Undefined download",
            "This button doesn't have corresponding server code registered to it, download should result in 404 error",
        ),
    ),
)


def server(session: ShinySession):
    @session.download()
    def download1():
        """
        This is the simplest case. The implementation simply returns the name of a file.
        Note that the function name (`download1`) determines which download_button()
        corresponds to this function.
        """

        path = os.path.join(os.path.dirname(__file__), "mtcars.csv")
        return path

    @session.download(filename="image.png")
    def download2():
        """
        Another way to implement a file download is by yielding bytes; either all at
        once, like in this case, or by yielding multiple times. When using this
        approach, you should pass a filename argument to @session.download, which
        determines what the browser will name the downloaded file.
        """

        x = np.random.uniform(size=session.input["num_points"])
        y = np.random.uniform(size=session.input["num_points"])
        plt.figure()
        plt.scatter(x, y)
        plt.title(session.input["title"])
        with io.BytesIO() as buf:
            plt.savefig(buf, format="png")
            yield buf.getvalue()

    @session.download(
        filename=lambda: f"新型-{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def download3():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"
        yield "新,1,2\n"
        yield "型,4,5\n"

    @session.download(name="download4", filename="failuretest.txt")
    async def _():
        yield "hello"
        raise Exception("This error was caused intentionally")


app = ShinyApp(ui, server)

if __name__ == "__main__":
    app.run()
    # Alternately, to listen on a TCP port:
    # app.run(conn_type = "tcp")
