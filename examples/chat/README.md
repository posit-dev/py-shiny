# Shiny `Chat` examples


This folder contains a collection of examples illustrating `shiny.ui.Chat` usage. Many of them require API keys from providers such as OpenAI, Anthropic, etc. In those cases, the example should have commentary explaining how to obtain keys as well as how to provide them to the app.

To get started with an app that doesn't require an API key, see the `hello-world` example. This example has both a Shiny Core and Express app to illustrate how it's used in either mode.


-----------------------

## Apps

* [hello-world](hello-world): A simple chat app that echoes back the user's input.
* [playground](playground): A playground for testing out different chat models: `openai`, `claude`, and `google`.
* RAG
  * [recipes](RAG/recipes): A simple recipe extractor chatbot that extracts recipes from URLs using the OpenAI API.
* UI
  * [clear](ui/clear): This example demonstrates how to clear the chat when the model changes.
  * [dark](ui/dark): This example demonstrates Shiny Chat's dark mode capability.
  * [dynamic](ui/dynamic): A basic example of dynamically re-rendering a Shiny Chat instance with different models.
  * [sidebar](ui/sidebar): An example of placing a Shiny Chat instance in a sidebar (and having it fill the sidebar).
