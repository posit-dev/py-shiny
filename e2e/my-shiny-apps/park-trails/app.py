from dis import dis
from re import sub
from shiny import App, render, ui
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np


sns.set_theme()

trail_list = pd.read_csv(Path(__file__).parent / "alltrails_data.csv")


# # DATA CLEANING: Extract Year from Date
# enroll_list["Date"] = enroll_list["Date"].astype('datetime64[ns]')
# enroll_list["Year"] = enroll_list["Date"].dt.year

# DATA CLEANING: Create a new column for difficuly level: 1 - easy, 3 - medium, 5 - hard, 7 - extreme
def definition(difficulty_rate):
    if difficulty_rate == 1:
        return 'easy'
    elif difficulty_rate == 3:
        return 'moderate'
    elif difficulty_rate == 5:
        return 'hard'
    else:
        return 'extreme'

trail_list['difficulty_level'] = trail_list.apply(lambda x: definition(difficulty_rate = x['difficulty_rating']), axis = 1)

# DATA CLEANING: Create new columns for features
condition1 = [
    (trail_list['features'].str.contains("dogs-leash")),
    (trail_list['features'].str.contains("dogs-no")),
    (trail_list['features'].str.contains("dogs")==False)
    ]
values1 = ['Dogs Allowed', 'no', 'Dogs Allowed']
trail_list['dogs_allowed'] = np.select(condition1, values1)

condition2 = [
    (trail_list['features'].str.contains("kids")),
    (trail_list['features'].str.contains("kids")==False)
    ]
values2 = ['Kid Friendly', 'no']
trail_list['kid_friendly'] = np.select(condition2, values2)

condition3 = [
    (trail_list['features'].str.contains("ada")),
    (trail_list['features'].str.contains("ada")==False)
    ]
values3 = ['ADA Accessible', 'no']
trail_list['ada_accessible'] = np.select(condition3, values3)

condition4 = [
    (trail_list['features'].str.contains("river")),
    (trail_list['features'].str.contains("river")==False)
    ]
values4 = ['River', 'no']
trail_list['river'] = np.select(condition4, values4)

# Create input lists
difficulty = trail_list["difficulty_level"].unique().tolist()
state = trail_list["state_name"].unique().tolist()
features = ["Dogs Allowed", "Kid Friendly", "ADA Accessible", "River"]


app_ui = ui.page_fluid(
    ui.input_selectize("state", "State", state, selected = "California", multiple=True),
    ui.input_radio_buttons(
        "difficulty", "Difficulty Level:", {"easy": "Easy", "moderate": "Moderate", "hard": "Hard", "extreme": "Extreme"}
    ),
    ui.input_selectize("features", "Accessibility & Features:", features, selected = "Kid Friendly", multiple=True),
    # ui.input_checkbox_group(
    #     "features", "Accessibility & Features:", {"kids": "Kid Friendly", "dogs": "Dogs Allowed", "ada": "ADA Accessible", "river": "River"}
    # ),
    #ui.output_plot("bar_chart"),
    ui.output_table("result"),
)

def server(input, output, session):
    # @output
    # @render.plot
    # def barchart():
    #     # Filter data by difficulty selection
    #     sub_df = trail_list[(trail_list["difficulty_level"] == input.difficulty())]

    #     # Filter data by state selection
    #     indx_states = sub_df["state_name"].isin(input.state())
    #     sub_df = sub_df[indx_states]

    #     # Filter data by accessibility and features
    #     indx_kids = sub_df["kid_friendly"].isin(input.features())
    #     indx_dogs = sub_df["dogs_allowed"].isin(input.features())
    #     indx_ada = sub_df["ada_accessible"].isin(input.features())
    #     indx_river = sub_df["river"].isin(input.features())

    #     sub_df = sub_df[indx_kids | indx_dogs | indx_ada | indx_river]
    #     top10 = sub_df.sort_values(by="num_reviews")[-10:]
    #     #plot data
    #     g = top10.plot(
    #         y="avg_rating",
    #        # x="name",
    #         kind="bar"
    #     )

    #     #format axis labels
    #     g.set_xticklabels(rotation=90)
    #     g.set_xlabels("")
    #     g.set_ylabels("Rating")

    #     return g

    @output
    @render.table
    def result():
        # Filter data by difficulty selection
        sub_df = trail_list[(trail_list["difficulty_level"] == input.difficulty())]

        # Filter data by state selection
        indx_states = sub_df["state_name"].isin(input.state())
        sub_df = sub_df[indx_states]

        # Filter data by accessibility and features
        indx_kids = sub_df["kid_friendly"].isin(input.features())
        indx_dogs = sub_df["dogs_allowed"].isin(input.features())
        indx_ada = sub_df["ada_accessible"].isin(input.features())
        indx_river = sub_df["river"].isin(input.features())

        sub_df = sub_df[indx_kids | indx_dogs | indx_ada | indx_river]

        return sub_df


app = App(app_ui, server)
