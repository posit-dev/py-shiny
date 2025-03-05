from shiny import App, ui

# Create a custom icon for the showcase using Font Awesome
icon = ui.tags.i(class_="fa-solid fa-chart-simple", style="font-size: 2rem;")

app_ui = ui.page_fillable(
    # Add Font Awesome CSS to the app
    ui.head_content(
        ui.HTML(
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">'
        )
    ),
    ui.layout_column_wrap(
        # 1. Basic value box with left-center showcase layout (default)
        ui.value_box(
            "Revenue",
            "$5.2M",
            "Up 12% from last month",
            id="left_center_value_box",
            showcase=icon,
            theme="primary",
            height="200px",
        ),
        # 2. Value box with top-right showcase layout
        ui.value_box(
            "Active Users",
            "2.4K",
            "Daily active users",
            id="top_right_value_box",
            showcase=icon,
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
            showcase=icon,
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
            showcase=icon,
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
            showcase=icon,
            theme=None,
            height="200px",
            class_="bg-warning text-dark",
        ),
        width="400px",
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)
