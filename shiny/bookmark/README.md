
# Shiny for Python Bookmarking

Bookmarking in Shiny for Python allows users to save and restore the state of an
application, making it possible to share specific application states via URLs or to
restore previous sessions. This document explains how bookmarking works and how to
implement it in your Shiny applications.

## Overview

Bookmarking captures the state of your application, including input values and custom
data, and allows users to restore that state later. There are two primary storage
methods:

- **URL bookmarking**: Encodes the application state in the URL, making it easy to share
  but limited in size
- **Server bookmarking**: Stores the application state on the server, providing more
  storage capacity but requiring server-side storage management

It is recommended to use `"url"` storage if your bookmark state can be serialized into
65k characters.

## Enabling Bookmarking

To enable bookmarking, you must:

1. Make your UI a function that accepts a `starlette.Request` object
2. Set the `bookmark_store` parameter when creating your app

```python
from starlette.requests import Request
from shiny import App, Inputs, Outputs, Session, ui

# UI must be a function to restore properly
def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_radio_buttons("choice", "Make a choice", choices=["A", "B", "C"]),
        ui.input_bookmark_button()
    )

def server(input: Inputs, output: Outputs, session: Session):
    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)

# Enable URL bookmarking
app = App(app_ui, server, bookmark_store="url")
```

## Bookmark State Components

Bookmark state consists of two main components:

### 1. Input Values

By default, all input values are included in the bookmark state. You can exclude
specific inputs using:

```python
session.bookmark.exclude.append("input_id")
```

Any adjusted `.input` values on the `BookmarkState` object are ignored when saving.
Please use `session.bookmark.exclude` to ignore any values.

Input values are **only** restored during UI rendering and server-side dynamic UI. They are
provided as a courtesy during `on_restore` and `on_restored` callbacks.

### 2. Custom Values

You can store additional data in the bookmark state using the `values` dictionary:

```python
@session.bookmark.on_bookmark
async def _(state: BookmarkState):
    state.values["custom_data"] = "some value"
```

Values are **never** restored via UI. They are only restored within the server. Hooks:
`@session.on_restore` and `@session.on_restored`. Typically you'll only need to use
`@session.on_restore` to update the UI with the restored values. If a component develops
slowly, you may need to use `@session.on_restored` to update the UI with the restored
values.

## RestoreContext and RestoreState

Shiny uses two key objects to manage the restoration of bookmarked states:

### RestoreContext

`RestoreContext` is an internal object that handles the mechanics of state restoration.
They are created during both UI **and** server initialization phases:

- During UI rendering, it extracts bookmark data from the request's query string
- During server initialization, it creates an identical context for the session

The `RestoreContext` contains:
- `.input`: A `RestoreInputSet` object that holds input values to be restored.
- `.values`: A dictionary of custom values stored in the bookmark
- `.dir`: The directory path for server-side bookmarks (if applicable). When missing, it
  is considered to be restoring from the `"url"`

### RestoreState

`RestoreState` is a user-facing object derived from `RestoreContext` that's passed to
your bookmark restoration callbacks. It provides a simplified interface for accessing
the restored state:

```python
@session.bookmark.on_restore
def _(state: RestoreState):
    # Access restored inputs
    if "choice" in state.input:
        print(f"Restoring choice: {state.input['choice']}")

    # Access restored custom values
    if "custom_data" in state.values:
        print(f"Restoring custom data: {state.values['custom_data']}")

    # Access bookmark directory (for server bookmarks)
    if state.dir:
        print(f"Bookmark directory: {state.dir}")
```

The restoration process happens in two phases:

1. **UI Phase**: Default input values in the UI are overridden with bookmarked values
2. **Server Phase**: The server receives the same `RestoreState` to initialize any
   dynamic UI elements or reactive values

This two-phase approach ensures that inputs are properly initialized with bookmarked
values before any server-side logic runs.


## Bookmark Lifecycle Hooks

Shiny provides several hooks to customize the bookmarking process:

### Saving State

```python
# Called before saving bookmark state
@session.bookmark.on_bookmark
async def _(state: BookmarkState):
    # Customize state before saving
    state.values["custom_data"] = "some value"

# Called after bookmark state is saved
@session.bookmark.on_bookmarked
async def _(url: str):
    # Use the bookmark URL (e.g., update browser URL)
    await session.bookmark.update_query_string(url)
```

### Restoring State

```python
# Called before restoring bookmark state
@session.bookmark.on_restore
def _(state: RestoreState):
    # Access restored state before UI updates
    if "custom_data" in state.values:
        print(f"Restoring custom data: {state.values['custom_data']}")

# Called after bookmark state is fully restored
@session.bookmark.on_restored
def _(state: RestoreState):
    # Perform actions after the session is fully restored
    pass
```

## Triggering Bookmarks

There are two ways to trigger bookmarking:

### 1. Bookmark Button

Add a bookmark button to your UI:

```python
ui.input_bookmark_button(label="Save current state")
```

### 2. Programmatic Bookmarking

Trigger bookmarking from server code:

```python
@reactive.effect
@reactive.event(input.some_input, ignore_init=True)
async def _():
    # Save bookmark when input changes
    await session.bookmark()
```

## Updating UI with Restored Values

When restoring custom values that aren't directly tied to inputs, you need to manually
update the UI:

```python
@session.bookmark.on_restore
def _(state: RestoreState):
    if "custom_value" in state.values:
        # Update an input with the restored value
        ui.update_radio_buttons("some_input", selected=state.values["custom_value"])
```

## Server-Side Bookmarking

!! This approach is only for hosting environments !!

For server-side bookmarking, you can customize where bookmark data is stored:

```python
from pathlib import Path
from shiny.bookmark import set_global_save_dir_fn, set_global_restore_dir_fn

bookmark_dir = Path(__file__).parent / "bookmarks"

def save_bookmark_dir(id: str) -> Path:
    save_dir = bookmark_dir / id
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir

def restore_bookmark_dir(id: str) -> Path:
    return bookmark_dir / id

# Set global defaults for bookmark saving and restoring
set_global_restore_dir_fn(restore_bookmark_dir)
set_global_save_dir_fn(save_bookmark_dir)

app = App(app_ui, server, bookmark_store="server")
```

## Bookmarking with Modules

Bookmarking works with modules too. Each module can have its own bookmark callbacks:

```python
@module.server
def my_module(input: Inputs, output: Outputs, session: Session):
    # Exclude specific inputs from bookmarking
    session.bookmark.exclude.append("transient_input")

    # Store custom values
    @session.bookmark.on_bookmark
    def _(state: BookmarkState):
        state.values["module_data"] = input.some_input()

    # Restore custom values
    @session.bookmark.on_restore
    def _(state: RestoreState):
        if "module_data" in state.values:
            ui.update_input("some_input", state.values["module_data"])
```

## Best Practices

1. **Always make your UI a function** that accepts a `starlette.Request` parameter
2. **Use `session.bookmark.update_query_string()`** to update the URL within a
   `@session.bookmark.on_bookmarked` decorated function
3. **Exclude transient inputs** that shouldn't be restored (like file "last click location")
4. **Test bookmark restoration** to ensure your app state is properly restored
5. **Consider URL size limits** when using URL bookmarking - use server bookmarking for
   larger states

## Limitations

- URL bookmarking has size limitations based on browser URL length restrictions
- Server bookmarking requires proper server configuration for persistence
- Some input types (like file uploads) may not be suitable for bookmarking

## Complete Example

```python
from starlette.requests import Request
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.bookmark import BookmarkState, RestoreState

def app_ui(request: Request):
    return ui.page_fluid(
        ui.markdown(
            "Directions: "
            "\n1. Change the radio buttons below"
            "\n2. Refresh your browser."
            "\n3. The radio buttons should be restored to their previous state."
        ),
        ui.hr(),
        ui.input_radio_buttons(
            "letter",
            "Choose a letter (Store in Bookmark 'input')",
            choices=["A", "B", "C"],
        ),
        ui.input_radio_buttons(
            "letter_values",
            "Choose a letter (Stored in Bookmark 'values' as lowercase)",
            choices=["A", "B", "C"],
        ),
        "Selection:",
        ui.output_code("letters"),
    )

def server(input: Inputs, output: Outputs, session: Session):
    # Exclude "letter_values" from being saved automatically
    session.bookmark.exclude.append("letter_values")

    lowercase_letter = reactive.value()

    @reactive.effect
    @reactive.event(input.letter_values)
    async def _():
        lowercase_letter.set(input.letter_values().lower())

    @render.code
    def letters():
        return str([input.letter(), lowercase_letter()])

    # Bookmark when inputs change
    @reactive.effect
    @reactive.event(input.letter, lowercase_letter, ignore_init=True)
    async def _():
        await session.bookmark()

    # Store custom values before bookmarking
    @session.bookmark.on_bookmark
    async def _(state: BookmarkState):
        with reactive.isolate():
            state.values["lowercase"] = lowercase_letter()

    # Update URL after bookmarking
    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)

    # Restore custom values
    @session.bookmark.on_restore
    def _(state: RestoreState):
        if "lowercase" in state.values:
            uppercase = state.values["lowercase"].upper()
            ui.update_radio_buttons("letter_values", selected=uppercase)

app = App(app_ui, server, bookmark_store="url")
```


---------------------------------------------------------------

# Input Serialization for Bookmarking in Shiny for Python

Input serialization is a critical aspect of Shiny's bookmarking system that determines how input values are converted to a format that can be stored and later restored. Here's how input serialization works in Shiny for Python's bookmarking system:

## Basic Serialization Process

When a bookmark is created, Shiny:

1. Collects all input values from `session.input`
2. Filters out any inputs listed in `session.bookmark.exclude`
3. Serializes each input value to a JSON-compatible format
4. Stores the serialized values either in the URL or on the server

## Default Serialization Behavior

By default, Shiny uses the following rules for serializing inputs:

- **Simple types** (strings, numbers, booleans): Serialized directly as JSON
- **Lists and dictionaries**: Serialized as JSON arrays and objects
- **Complex objects**: Converted to JSON using their default representation
- **Unserializable objects**: Excluded from bookmarking

## Custom Input Serializers

For inputs that require special handling, Shiny allows you to register custom serializers:

```python
def custom_serializer(value: Any = None, state_dir: Path | None = None):
    # Transform the value into a serializable format
    transformed_value = transform(info.value))
    return transformed_value

# Register the serializer for a specific input
session.input.set_serializer("input_id", custom_serializer)
```

The serializer function receives:
- `value`: The current input value
- `state_dir`: The directory path where bookmark files are stored (for server bookmarking)

It should return a JSON-serializable object or a special `shiny.bookmark.Unserializable` value to exclude the input.

## File Input Serialization

File inputs require special handling since they reference local files:

```python
def serializer_file_input(value, state_dir):
    if state_dir is None:
        # For URL bookmarking, files can't be serialized
        return Unserializable()

    # For server bookmarking, copy the file to the bookmark directory
    datapath = Path(value["datapath"])
    new_path = state_dir / datapath.name

    # Copy the file to the bookmark directory
    copyfile(datapath, new_path)

    # Update the path in the value to be relative
    value["datapath"] = new_path.name

    return value
```

## Module-Aware Serialization

Input serialization is module-aware:

- Input IDs are fully qualified with their namespace
- Each module can exclude its own inputs using `session.bookmark.exclude`
- Custom serializers can be registered within module server functions

## URL vs. Server Serialization

The serialization process differs slightly based on the bookmark storage method:

- **URL bookmarking**:
  - All values must be serializable to JSON
  - Size limitations apply (browser URL length limits)
  - File inputs and large data structures are typically excluded

- **Server bookmarking**:
  - Values are serialized to JSON files stored on the server
  - File inputs can be copied to the bookmark directory
  - Larger data structures can be accommodated

## Handling Unserializable Inputs

For inputs that cannot or should not be serialized:

1. Add them to the exclude list:
   ```python
   session.bookmark.exclude.append("large_data_input")
   ```

2. Return `Unserializable()` from a custom serializer:
   ```python
   def my_serializer(value, state_dir):
       if some_condition:
           return Unserializable()
       return processed_value
   ```

3. For transient inputs like file uploads, consider storing metadata instead:
   ```python
   @session.bookmark.on_bookmark
   def _(state):
       # Store just the filename instead of the file content
       if input.file_upload() is not None:
           state.values["uploaded_filename"] = input.file_upload()["name"]
   ```

## Best Practices for Input Serialization

1. **Exclude transient inputs** that don't make sense to restore (like file uploads)
2. **Register custom serializers** for complex input types
3. **Keep serialized data compact** for URL bookmarking
4. **Test bookmark restoration** to ensure inputs are properly serialized and deserialized
5. **Consider security implications** when serializing sensitive data

By understanding and properly implementing input serialization, you can create robust bookmarking functionality that preserves the important state of your Shiny application.


---------------------------------------------------------------

Cadence of Bookmarking in Shiny for Python

* User: requests app
* Server: process UI and return HTML
  * If Query string, create restore context for UI use during reconstruction
    * Bookmark Input values will be used
* User: Receives HTML and JS
* User: Initializes app inputs
* User: Creates web socket
* Server: Process inputs and return outputs
  * If Query string, create restore context for server use during reconstruction
  * Bookmark Input values will be used when creating dynamic UI
  * All `on_restore` callbacks will be invoked before any reactive expression runs
    * Bookmark Values should be used here for `update_input(name, value)` calls
  * All reactive expressions run
  * All `on_restored` callbacks will be invoked after all reactive expressions have been run
    * Bookmark Values could be used here if necessary
  * Session is initialized
* User: Requests bookmark
* Server: Saves bookmark
  * All `on_bookmark` callbacks will be invoked
    * Bookmark Values should be set here
  * Bookmark is saved
  * All `on_bookmarked` callbacks will be invoked
    * Utilize the Bookmark URL here



# Shiny Bookmarking Lifecycle

## 1. Initial Request & UI Generation
1. **User requests app**
2. **Server processes request**
   - Processes UI and returns HTML
   - If query string exists:
     - Creates RestoreContext for UI reconstruction
     - Uses bookmark input values during UI generation
3. **User receives response**
   - Receives HTML and JS
   - Initializes app inputs
   - Creates WebSocket connection

## 2. Server Initialization
1. **Process inputs and setup**
   - If query string exists:
     - Creates RestoreContext for server use
     - Applies bookmark input values to dynamic UI
   - Inputs are sent through `@input_handlers` for processing
     - Inputs can have their Bookmark serialier set here
        ```python
        @input_handlers.add("shiny.password")
        def _(value: str, name: ResolvedId, session: Session) -> str:
            # Never bookmark passwords
            session.input.set_serializer(name, serializer_unserializable)

            return value
        ```

2. **Restoration sequence**
   ```python
   # 1. on_restore callbacks execute first
   @session.bookmark.on_restore
   def _(state):
       # Use bookmark values to update inputs
       ui.update_input("input_id", state.values["some_value"])

   # 2. Reactive expressions run

   # 3. on_restored callbacks execute last
   @session.bookmark.on_restored
   def _(state):
       # Handle any post-restoration tasks
       pass
   ```

3. **Session initialization completes**

## 3. Bookmark Creation
1. **User requests bookmark**

  ```python
  session.bookmark()
  ```

2. **Server processes bookmark request**
   ```python
   # 1. All on_bookmark callbacks execute
   @session.bookmark.on_bookmark
   def _(state):
       # Set bookmark values
       state.values["some_value"] = compute_value()

   # 2. Bookmark state is saved to disk/url

   # 3. All on_bookmarked callbacks execute
   @session.bookmark.on_bookmarked
   async def _(url):
       # Handle the bookmark URL
       await session.bookmark.update_query_string(url)
   ```

## Key Points
- RestoreContext is created twice (independently): once for UI and once for server
- Callbacks execute in their registration order during restoration and bookmarking
- Bookmark `.values` should be:
  - Set during `on_bookmark`
  - Used during `on_restore` for updating inputs
  - Optionally used during `on_restored` if needed
