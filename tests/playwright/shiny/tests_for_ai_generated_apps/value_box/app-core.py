import pandas as pd
import plotly.graph_objects as go
import shinywidgets as sw

from shiny import App, ui

# Create a custom icon for the showcase using Font Awesome
chart_icon = ui.tags.i(class_="fa-solid fa-chart-simple", style="font-size: 8rem;")
chart_thumbs_up_icon = ui.tags.i(
    class_="fa-solid fa-thumbs-up", style="font-size: 5rem;"
)
chart_star_icon = ui.tags.i(class_="fa-solid fa-star", style="font-size: 5rem;")
chart_heart_icon = ui.tags.i(class_="fa-solid fa-heart", style="font-size: 5rem;")
chart_lightbulb_icon = ui.tags.i(
    class_="fa-solid fa-lightbulb", style="font-size: 10rem;"
)

data = pd.DataFrame(
    {"Year": range(2018, 2024), "Revenue": [100, 120, 110, 122, 118, 130]}
)

app_ui = ui.page_fluid(
    # Add Font Awesome CSS to the app
    ui.head_content(
        ui.HTML(
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">'
        )
    ),
    ui.br(),
    ui.layout_column_wrap(
        # 1. Basic value box with left-center showcase layout (default)
        ui.value_box(
            "Revenue",
            "$5.2M",
            "Up 12% from last month",
            id="left_center_value_box",
            showcase=chart_icon,
            theme="primary",
        ),
        # 2. Value box with top-right showcase layout
        ui.value_box(
            "Active Users",
            "2.4K",
            "Daily active users",
            id="top_right_value_box",
            showcase=chart_thumbs_up_icon,
            showcase_layout="top right",
            theme="bg-gradient-purple-red",
            height="200px",
        ),
        # 3. Value box with bottom showcase layout
        ui.value_box(
            "Conversion Rate",
            "3.8%",
            "Increased by 0.5%",
            id="bottom_value_box",
            showcase=sw.output_widget("graph"),
            showcase_layout="bottom",
            theme="text-success",
            height="200px",
        ),
        # 4. Value box with full screen capability and custom theme
        ui.value_box(
            "Total Sales",
            "8,742",
            "Year to date performance",
            id="full_screen_value_box",
            showcase=chart_lightbulb_icon,
            full_screen=True,
            theme="bg-gradient-orange-red",
            height="600px",
            min_height="150px",
            max_height="300px",
            fill=True,
        ),
        # 5. Value box with custom background color using class_
        ui.value_box(
            "Pending Orders",
            "156",
            "Requires attention",
            id="custom_bg_value_box",
            showcase=chart_heart_icon,
            theme=None,
            height="200px",
            class_="bg-warning text-dark",
        ),
        width="400px",
    ),
)


def server(input, output, session):
    @sw.render_plotly
    def graph():
        fig = go.Figure()

        # Add line trace
        fig.add_trace(
            go.Scatter(
                x=data["Year"],
                y=data["Revenue"],
                mode="lines+markers",
                line=dict(color="blue", width=2),
                marker=dict(size=4),
            )
        )

        # Update layout for sparkline appearance
        fig.update_layout(
            showlegend=False,
            paper_bgcolor="mistyrose",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
        )

        return fig


app = App(app_ui, server)
