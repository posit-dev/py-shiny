from shiny.express import ui

ui.page_opts(fillable=True)

# Create a custom icon for the showcase using Font Awesome
icon = ui.tags.i(class_="fa-solid fa-chart-simple", style="font-size: 2rem;")

# Add Font Awesome CSS to the app
ui.head_content(
    ui.HTML(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">'
    )
)

with ui.layout_column_wrap(width="400px"):
    # 1. Basic value box with left-center showcase layout (default)
    with ui.value_box(
        id="left_center_value_box", showcase=icon, theme="primary", height="200px"
    ):
        "Revenue"
        "$5.2M"
        "Up 12% from last month"

    # 2. Value box with top-right showcase layout
    with ui.value_box(
        id="top_right_value_box",
        showcase=icon,
        showcase_layout="top right",
        theme="bg-gradient-purple-red",
        height="200px",
    ):
        "Active Users"
        "2.4K"
        "Daily active users"

    # 3. Value box with bottom showcase layout
    with ui.value_box(
        id="bottom_value_box",
        showcase=icon,
        showcase_layout="bottom",
        theme="text-success",
        height="200px",
    ):
        "Conversion Rate"
        "3.8%"
        "Increased by 0.5%"

    # 4. Value box with full screen capability and custom theme
    with ui.value_box(
        id="full_screen_value_box",
        showcase=icon,
        full_screen=True,
        theme="bg-gradient-orange-red",
        height="600px",
        min_height="150px",
        max_height="300px",
        fill=True,
    ):
        "Total Sales"
        "8,742"
        "Year to date performance"

    # 5. Value box with custom background color using class_
    with ui.value_box(
        id="custom_bg_value_box",
        showcase=icon,
        theme=None,
        height="200px",
        class_="bg-warning text-dark",
    ):
        "Pending Orders"
        "156"
        "Requires attention"
