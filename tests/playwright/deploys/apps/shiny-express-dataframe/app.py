import pandas as pd

from shiny import render
from shiny.express import ui

data = {
    "A": [1, 2, 3, 4, 5, 6],
    "B": ["a", "b", "c", "d", "e", "f"],
    "C": [10.1, 20.2, 30.3, 40.4, 50.5, 60.6],
    "D": ["apple", "banana", "cherry", "date", "elderberry", "fig"],
    "E": [True, False, True, False, True, False],
    "F": ["John", "Jane", "Jim", "Jessie", "Jack", "Jill"],
}

df = pd.DataFrame(data)

ui.page_opts(fillable=True)

with ui.card(id="card"):
    ui.h2("Below is a sample dataframe")

    @render.data_frame
    def sample_data_frame(id: str = "dataframe"):
        return df
