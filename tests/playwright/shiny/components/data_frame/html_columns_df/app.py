import random
import string

from htmltools import HTMLDependency
from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.render import CellPatch

df = load_penguins_raw()


def random_generator():
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(8)
    )


df.iloc[1, 0] = (  # pyright: ignore[reportArgumentType]
    HTMLDependency(  # pyright: ignore[reportUnknownLambdaType, reportArgumentType]
        "studyname".join(random_generator()),
        version="1",
        head="""
                <script>window.shinytestvalue = "testing"</script>
                """,
    )
)
df["Species"] = df["Species"].apply(lambda x: ui.HTML(f"<u>{x}</u>"))  # type: ignore
df["Region"] = df["Region"].apply(  # type: ignore
    lambda y: ui.tags.h1(  # pyright: ignore[reportUnknownLambdaType, reportArgumentType]
        f"{y}"
    )
)  # pyright: ignore[reportUnknownMemberType]
df["Island"] = df["Island"].apply(  # pyright: ignore[reportUnknownMemberType]
    lambda z: ui.TagList(  # pyright: ignore[reportUnknownLambdaType]
        ui.input_checkbox(f"checkbox_{z}".join(random_generator()), f"{z}"),
        ui.tags.img(
            src="https://dka575ofm4ao0.cloudfront.net/pages-transactional_logos/retina/276517/posit-logo-fullcolor-TM.png",
            height="20%",
            width="20%",
        ),
    )
)
df.iloc[1, 5] = ui.p(  # pyright: ignore[reportArgumentType]
    ui.input_action_button("test_cell_button", "Test button"),
    ui.output_text_verbatim("test_cell_text", placeholder=True),
)

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.output_data_frame("penguins_df"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:

    @render.text
    def test_cell_text():
        return f"test_cell_value {input.test_cell_button()}"

    @render.data_frame
    def penguins_df():
        return render.DataGrid(
            data=df,  # pyright: ignore[reportUnknownArgumentType]
            filters=True,
            editable=True,
        )

    @penguins_df.set_patch_fn
    async def upgrade_patch(
        *,
        patch: CellPatch,
    ):
        if patch["column_index"] == 6:  # only for Individual ID
            return f"ID: {patch['value']}"
        else:
            return patch["value"]


app = App(app_ui, server)
