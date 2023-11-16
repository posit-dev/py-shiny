This repo is an example of a python package that defines a simple custom input component for Shiny.

## Structure

The code structure is as follow:

```
package.json        # Contains the dependencies needed to build the components javascript
srcts/              # Source Typescript files
  index.ts          # Where we define the input component
custom_component/
  custom_component.py   # Python functions for the input component
  __init__.py       # Used to define exports for python package.
  distjs/           # Where the bundled js files are put
example-app/
  app.py            # Example app for the custom-input component
...                 # ...Various other config files needed for python and js projects
```

## Using/ Developing package

### Setting up python package in "editable" mode

This should be run from the root of the repo

```
pip install -e .
```

## Setting up JS for development

Install the dependencies for javascript:

```
npm install
```

Build assets into the `custom_component/distjs` folder:

```
npm run build
```

Or if you want to watch the files for changes and rebuild on the fly you can run:

```
npm run watch
```

## Running the example app

With both the python package and the javascript built, you can run the example apps (typically using the Shiny vscode extension).

If you want to run the example app from the command line you can run:

```
Shiny run example-app/app.py
```

custom_component
custom_component
custom-component
Shinycustom_component
