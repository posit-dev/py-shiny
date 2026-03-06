library(shiny)
library(bslib)
library(coro)
library(promises)

ui <- fluidPage(
  p(
    "Launch this app in two different tabs. In one tab, press the button and see if ",
    "the clock stops in the other tab."
  ),
  input_task_button("block", "Perform blocking operation"),
  textOutput("fast")
)

server <- function(input, output, session) {
  msg <- function(...) {
    message("[", substr(session$token, 1, 5), "] ", ...)
  }
  output$fast <- renderText({
    invalidateLater(1000)
    format(Sys.time(), "%H:%M:%S")
  })

  observe({
    invalidateLater(1000)
    msg("Fast observer is running")
  })

  # Observe button clicks and perform slow operation
  observeEvent(input$block, {
    msg("Starting slow operation")
    async_sleep(3) %...>%
      {
        msg("Slow operation completed")
      }
  })
}

shinyApp(ui = ui, server = server)
