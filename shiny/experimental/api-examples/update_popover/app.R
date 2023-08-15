library(shiny)
library(bslib)

ui <- page_fluid(
    actionButton("btn_update", "Update popover phrase", class="mt-3 me-3"),
    br(),
    br(),
    popover(
        actionButton("btn_w_popover", "A button w/ a popover", class="mt-3"),
        "A message",
        id="popover_id",
        title="To start"
    )
)

server <- function(input, output) {

    observeEvent(input$btn_update, {
        content <- paste0("A ", paste(rep("NEW", input$btn_update), collapse=" "), " message")
        update_popover("popover_id", content)
    })

    observeEvent(input$btn_w_popover, {
        showNotification("Button clicked!", duration=3, type="message")
    })
}

shinyApp(ui, server)
