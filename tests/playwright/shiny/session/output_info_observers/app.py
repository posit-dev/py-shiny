import json
from shiny import App, Inputs, Outputs, Session, reactive, render, ui


def dynamic_probe_ui():
    return (
        ui.output_text_verbatim("dynamic_probe")
        .add_class("shiny-report-size")
        .add_style("width: 220px; height: 110px;")
    )


app_ui = ui.page_fluid(
    ui.input_action_button("toggle_size", "Toggle size"),
    ui.input_action_button("toggle_visibility", "Toggle visibility"),
    ui.input_action_button("toggle_theme", "Toggle theme"),
    ui.input_action_button("toggle_dynamic_mount", "Toggle dynamic mount"),
    ui.input_action_button("toggle_dynamic_size", "Toggle dynamic size"),
    ui.tags.style("""
        #probe.theme-warm {
          background-color: rgb(250, 250, 248);
          color: rgb(34, 39, 46);
          font-family: "Courier New", monospace;
          font-size: 18px;
        }

        #probe.theme-warm a {
          color: rgb(12, 110, 253);
        }

        #probe.theme-cool {
          background-color: rgb(23, 27, 36);
          color: rgb(238, 241, 245);
          font-family: "Times New Roman", serif;
          font-size: 20px;
        }

        #probe.theme-cool a {
          color: rgb(255, 138, 76);
        }

        #dynamic_probe {
          box-sizing: border-box;
          width: 220px;
          height: 110px;
          margin: 0;
          padding: 0;
          border: 0;
        }
        """),
    ui.output_text_verbatim("probe")
    .add_class("shiny-report-size shiny-report-theme theme-warm")
    .add_style(
        "box-sizing: border-box; width: 240px; height: 120px; "
        "margin: 0; padding: 0; border: 0;"
    ),
    ui.output_text_verbatim("size_info"),
    ui.output_text_verbatim("hidden_info"),
    ui.output_text_verbatim("theme_info"),
    ui.navset_tab(
        ui.nav_panel("Observed", ui.output_text_verbatim("nav_probe")),
        ui.nav_panel("Other", "Other tab content"),
        id="probe_tabs",
    ),
    ui.output_text_verbatim("nav_hidden_info"),
    ui.div(dynamic_probe_ui(), id="dynamic_slot"),
    ui.tags.template(dynamic_probe_ui(), id="dynamic_probe_template"),
    ui.output_text_verbatim("dynamic_info"),
    ui.tags.script("""
        (() => {
          const toggleSize = document.getElementById("toggle_size");
          const toggleVisibility = document.getElementById("toggle_visibility");
          const toggleTheme = document.getElementById("toggle_theme");
          const toggleDynamicMount = document.getElementById("toggle_dynamic_mount");
          const toggleDynamicSize = document.getElementById("toggle_dynamic_size");
          const dynamicSlot = document.getElementById("dynamic_slot");
          const dynamicProbeTemplate = document.getElementById("dynamic_probe_template");
          const probe = document.getElementById("probe");

          if (!probe) {
            return;
          }

          if (toggleSize) {
            toggleSize.addEventListener("click", () => {
              const expanded = probe.dataset.expanded === "true";
              probe.dataset.expanded = expanded ? "false" : "true";
              probe.style.width = expanded ? "240px" : "360px";
              probe.style.height = expanded ? "120px" : "180px";
            });
          }

          if (toggleVisibility) {
            toggleVisibility.addEventListener("click", () => {
              const hidden = probe.style.display === "none";
              probe.style.display = hidden ? "" : "none";
            });
          }

          if (toggleTheme) {
            toggleTheme.addEventListener("click", () => {
              probe.classList.toggle("theme-warm");
              probe.classList.toggle("theme-cool");
            });
          }

          if (toggleDynamicSize) {
            toggleDynamicSize.addEventListener("click", () => {
              const dynamicProbe = document.getElementById("dynamic_probe");

              if (!dynamicProbe) {
                return;
              }

              const expanded = dynamicProbe.dataset.expanded === "true";
              dynamicProbe.dataset.expanded = expanded ? "false" : "true";
              dynamicProbe.style.width = expanded ? "220px" : "320px";
              dynamicProbe.style.height = expanded ? "110px" : "160px";
            });
          }

          if (toggleDynamicMount && dynamicSlot && dynamicProbeTemplate) {
            toggleDynamicMount.addEventListener("click", async () => {
              const dynamicProbe = document.getElementById("dynamic_probe");

              if (dynamicProbe) {
                if (window.Shiny) {
                  window.Shiny.unbindAll(dynamicProbe, true);
                }
                dynamicProbe.remove();
                return;
              }

              dynamicSlot.replaceChildren(
                dynamicProbeTemplate.content.cloneNode(true)
              );

              if (window.Shiny) {
                await window.Shiny.bindAll(dynamicSlot);
              }
            });
          }
        })();
    """),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    dynamic_mounted = reactive.value(True)

    @reactive.effect
    @reactive.event(input.toggle_dynamic_mount)
    def _toggle_dynamic_mount() -> None:
        dynamic_mounted.set(not dynamic_mounted())

    @render.text
    def probe():
        return "probe"

    @render.text
    def size_info():
        return json.dumps(
            {
                "width": session.clientdata.output_width("probe"),
                "height": session.clientdata.output_height("probe"),
            }
        )

    @render.text
    def hidden_info():
        return json.dumps(
            {
                "hidden": session.clientdata.output_hidden("probe"),
            }
        )

    @render.text
    def theme_info():
        return json.dumps(
            {
                "bg": session.clientdata.output_bg_color("probe"),
                "fg": session.clientdata.output_fg_color("probe"),
                "accent": session.clientdata.output_accent_color("probe"),
                "font": session.clientdata.output_font("probe"),
            }
        )

    @render.text
    def nav_probe():
        return "nav probe"

    @render.text
    def nav_hidden_info():
        return json.dumps(
            {
                "hidden": session.clientdata.output_hidden("nav_probe"),
            }
        )

    @render.text
    def dynamic_probe():
        return "dynamic probe"

    @render.text
    def dynamic_info():
        return json.dumps(
            {
                "mounted": dynamic_mounted(),
                "width": session.clientdata.output_width("dynamic_probe"),
                "hidden": session.clientdata.output_hidden("dynamic_probe"),
            }
        )


app = App(app_ui, server)
