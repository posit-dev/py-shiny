# Getting Started with R Shiny

**R Shiny** is a powerful framework for building *interactive web applications* with R. Learn more at [shiny.posit.co](https://shiny.posit.co).

## Key Features

1. Reactive programming model
2. Built-in UI components
3. No JavaScript knowledge required
4. Easy deployment options

---

### Installation

Install Shiny from CRAN using the code below:

```r
install.packages("shiny")
library(shiny)
```

### Creating Your First App

A basic Shiny app requires:

- **UI function** to define the layout
- **Server function** to handle logic
- `shinyApp()` to combine both

> Tip: Use `shinyApp()` for simple apps or create separate `ui.R` and `server.R` files for larger projects.

For inline code, use backticks like `runApp()` to execute your application.

---

**Ready to build?** Start with `shinyAppTemplate()` and customize from there!
