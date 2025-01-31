from chatlas import ChatAnthropic
from faicons import icon_svg

from shiny import reactive
from shiny.express import input, render, ui

chat_model = ChatAnthropic(
    system_prompt="""
    You are a helpful AI fitness coach.
    Give detailed workout plans to users based on their fitness goals and experience level.
    Before getting into details, give a brief introduction to the workout plan.
    Keep the overall tone encouraging and professional yet friendly.
    Generate the response in Markdown format and avoid using h1, h2, or h3.
    """,
)

ui.page_opts(title="Personalized Workout Plan Generator")

with ui.sidebar(open={"mobile": "always-above"}):
    ui.input_select(
        "goal",
        "Fitness Goal",
        ["Strength", "Cardio", "Flexibility", "General Fitness"],
    )
    ui.input_selectize(
        "equipment",
        "Available Equipment",
        ["Dumbbells", "Barbell", "Resistance Bands", "Bodyweight"],
        multiple=True,
        selected=["Bodyweight", "Barbell"],
    )
    ui.input_slider("experience", "Experience Level", min=1, max=10, value=5)
    ui.input_slider("duration", "Duration (mins)", min=15, max=90, step=5, value=45)
    ui.input_select(
        "daysPerWeek",
        "Days per Week",
        [str(i) for i in range(1, 8)],
        selected="3",
    )
    ui.input_task_button("generate", "Get Workout", icon=icon_svg("person-running"))

    @render.express
    def download_ui():
        if not workout_plan():
            return

        @render.download(filename="workout_plan.md", label="Download Workout")
        def download():
            yield workout_plan()


# Create a Markdown stream to display the workout plan
md_stream = ui.MarkdownStream("response-stream")
md_stream.ui(
    content="""
Hi there! 👋 I'm your AI fitness coach. 💪

Fill out the form in the sidebar to get started. 📝 🏋️‍♂ ️
    """,
)


# When the user clicks the "Generate Workout" button, generate a workout plan
@reactive.effect
@reactive.event(input.generate)
def _():
    prompt = f"""
    Generate a {input.duration()}-minute workout plan for a {input.goal()} fitness goal.
    On a scale of 1-10, I have a level  {input.experience()} experience,
    works out {input.daysPerWeek()} days per week, and have access to:
    {", ".join(input.equipment()) if input.equipment() else "no equipment"}.
    Format the response in Markdown.
    """

    def consume_stream():
        response = ""
        for chunk in chat_model.stream(prompt):
            response += chunk
            yield chunk
        workout_plan.set(response)

    md_stream.stream(consume_stream())


workout_plan = reactive.value(None)
