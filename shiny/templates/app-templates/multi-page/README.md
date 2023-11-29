
This template provides an example of how large, production-level apps should be built.
There are a few things to note about this code:

1) Most of the functionality is implemented using [modules](https://shiny.posit.co/py/docs/workflow-modules.html).
Which are extremely important for breaking your application into small blocks which can be predictably assembled into larger applications.

2) We pass a `reactive.Calc` down to the modules, and call it within the module to return the data frame.
This is an example of [module communication](https://shiny.posit.co/py/docs/workflow-module-communication.html) which is how you can share reactive objects betwene modules and the main application context.

3) The app uses a css file to implement custom styling.
Shiny apps can be fully styled with CSS and you can learn more about the options [here](https://shiny.posit.co/py/docs/ui-styling.html).
