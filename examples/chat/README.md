# Shiny `Chat` examples


This folder contains a collection of examples illustrating `shiny.ui.Chat` usage. Many of them require API keys from providers such as OpenAI, Anthropic, etc. In those cases, the example should have commentary explaining how to obtain keys as well as how to provide them to the app.

To get started with an app that doesn't require an API key, see the `hello-world` example. This example has both a Shiny Core and Express app to illustrate how it's used in either mode.


-----------------------

## Apps

* [hello-world](hello-world): A simple chat app that echoes back the user's input. <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fchat%2Fhello-world%2Fapp.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
* [playground](playground): A playground for testing out different chat models: `openai`, `claude`, and `google`. <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fchat%2Fplayground%2Fapp.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
* RAG
  * [recipes](RAG/recipes): A simple recipe extractor chatbot that extracts recipes from URLs using the OpenAI API. <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fchat%2FRAG%2Frecipes%2Fapp.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
* UI
  * [clear](ui/clear): This example demonstrates how to clear the chat when the model changes. <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fchat%2Fui%2Fclear%2Fapp.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * [dark](ui/dark): This example demonstrates Shiny Chat's dark mode capability. <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fchat%2Fui%2Fdark%2Fapp.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * [dynamic](ui/dynamic): A basic example of dynamically re-rendering a Shiny Chat instance with different models. <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fchat%2Fui%2Fdynamic%2Fapp.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * [sidebar](ui/sidebar): An example of placing a Shiny Chat instance in a sidebar (and having it fill the sidebar). <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fchat%2Fui%2Fsidebar%2Fapp.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
