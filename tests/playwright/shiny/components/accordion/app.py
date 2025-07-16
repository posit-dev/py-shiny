from __future__ import annotations

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui


def make_panel(letter: str) -> ui.AccordionPanel:
    return ui.accordion_panel(
        f"Section {letter}",
        f"Some narrative for section {letter}",
    )


items = [make_panel(letter) for letter in "ABCD"]

accordion = ui.accordion(*items, id="acc")
app_ui = ui.page_fluid(
    ui.tags.div(
        ui.input_action_button("toggle_b", "Open/Close B"),
        ui.input_action_button("open_all", "Open All"),
        ui.input_action_button("close_all", "Close All"),
        ui.input_action_button("alternate", "Alternate"),
        ui.input_action_button("toggle_efg", "Add/Remove EFG"),
        ui.input_action_button("toggle_updates", "Add/Remove Updates"),
        class_="d-flex",
    ),
    ui.output_text_verbatim("acc_txt", placeholder=True),
    accordion,
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @reactive.calc
    def acc() -> list[str]:
        acc_val: list[str] | None = input.acc()
        if acc_val is None:
            acc_val = []
        return acc_val

    @reactive.effect
    def _():
        req(input.toggle_b())

        with reactive.isolate():
            if "Section B" in acc():
                ui.update_accordion_panel("acc", "Section B", show=False)
            else:
                ui.update_accordion_panel("acc", "Section B", show=True)

    @reactive.effect
    def _():
        req(input.open_all())
        ui.update_accordion("acc", show=True)

    @reactive.effect
    def _():
        req(input.close_all())
        ui.update_accordion("acc", show=False)

    has_efg = False
    has_alternate = True
    has_updates = False

    @reactive.effect
    def _():
        req(input.alternate())

        sections = [
            "updated_section_a" if has_updates else "Section A",
            "Section B",
            "Section C",
            "Section D",
        ]
        if has_efg:
            sections.extend(["Section E", "Section F", "Section G"])

        nonlocal has_alternate
        val = int(has_alternate)
        sections = [section for i, section in enumerate(sections) if i % 2 == val]
        ui.update_accordion("acc", show=sections)
        has_alternate = not has_alternate

    @reactive.effect
    def _():
        req(input.toggle_efg())

        nonlocal has_efg
        if has_efg:
            ui.remove_accordion_panel("acc", ["Section E", "Section F", "Section G"])
        else:
            ui.insert_accordion_panel("acc", make_panel("E"), "Section D")
            ui.insert_accordion_panel("acc", make_panel("F"), "Section E")
            ui.insert_accordion_panel("acc", make_panel("G"), "Section F")

        has_efg = not has_efg

    @reactive.effect
    def _():
        req(input.toggle_updates())

        nonlocal has_updates
        if has_updates:
            ui.update_accordion_panel(
                "acc",
                "updated_section_a",
                "Some narrative for section A",
                title="Section A",
                value="Section A",
                icon="",
            )
        else:
            with reactive.isolate():
                # print(acc())
                if "Section A" not in acc():
                    ui.notification_show("Opening Section A", duration=2)
                    ui.update_accordion_panel("acc", "Section A", show=True)
            ui.update_accordion_panel(
                "acc",
                "Section A",
                "Updated body",
                value="updated_section_a",
                title=ui.tags.h3("Updated title"),
                icon=ui.tags.div(
                    "Look! An icon! -->",
                    ui.HTML(
                        """\
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chat-right-quote" viewBox="0 0 16 16">
                          <path d="M2 1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h9.586a2 2 0 0 1 1.414.586l2 2V2a1 1 0 0 0-1-1H2zm12-1a2 2 0 0 1 2 2v12.793a.5.5 0 0 1-.854.353l-2.853-2.853a1 1 0 0 0-.707-.293H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h12z"/>
                          <path d="M7.066 4.76A1.665 1.665 0 0 0 4 5.668a1.667 1.667 0 0 0 2.561 1.406c-.131.389-.375.804-.777 1.22a.417.417 0 1 0 .6.58c1.486-1.54 1.293-3.214.682-4.112zm4 0A1.665 1.665 0 0 0 8 5.668a1.667 1.667 0 0 0 2.561 1.406c-.131.389-.375.804-.777 1.22a.417.417 0 1 0 .6.58c1.486-1.54 1.293-3.214.682-4.112z"/>
                        </svg>
                        """
                    ),
                ),
            )

        has_updates = not has_updates

    @render.text
    def acc_txt():
        return f"input.acc(): {input.acc()}"


app = App(app_ui, server)
