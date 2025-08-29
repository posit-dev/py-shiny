library(shiny)

ui <- fluidPage(
    # Application title
    titlePanel("My First Shiny App"),

    sidebarLayout(
        sidebarPanel(
            sliderInput(
                inputId = "num",
                label = "Select a number:",
                min = 1,
                max = 1000,
                value = 500
            ) # Default value
        ),

        mainPanel(
            textOutput("message")
        )
    )
)

server <- function(input, output) {
    output$message <- renderText({
        paste("You selected:", input$num)
    })
}

shinyApp(ui = ui, server = server)
