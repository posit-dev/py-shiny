# GitHub Copilot Instructions for py-shiny

This document provides GitHub Copilot with comprehensive context about the Shiny for Python repository to help generate high-quality, context-aware code and suggestions.

## 1. Project Overview

**Shiny for Python** is a framework for building fast, beautiful web applications in Python. It enables data scientists and developers to create interactive visualizations and applications quickly while remaining extensible enough to power large, mission-critical applications.

### Key Principles
- **Reactive Programming**: Automatic dependency tracking and efficient updates
- **Extensibility**: Build simple prototypes or complex production applications
- **Performance**: Optimized for speed and efficiency
- **Developer Experience**: Intuitive APIs with both Express (simple) and Core (powerful) modes

### Documentation
- Main documentation: https://shiny.posit.co/py/
- API reference: https://shiny.posit.co/py/api/
- Learn more: https://shiny.posit.co/py/docs/overview.html

## 2. Repository Structure

```
py-shiny/
├── shiny/                  # Core library code
│   ├── express/           # Express API (decorator-based, simpler syntax)
│   ├── ui/                # UI components and page layouts
│   ├── render/            # Rendering functions (@render.plot, @render.table, etc.)
│   ├── reactive/          # Reactive programming primitives (@reactive.calc, @reactive.effect)
│   ├── session/           # Session management
│   ├── experimental/      # Experimental features
│   ├── api-examples/      # API documentation examples
│   └── templates/         # Project templates
├── tests/                 # Test suite
│   ├── pytest/           # Unit tests
│   └── playwright/       # End-to-end integration tests
├── examples/              # Example applications
├── docs/                  # Documentation source (Quartodoc + Quarto)
├── js/                    # JavaScript/TypeScript code
└── scripts/               # Development and build scripts
```

## 3. Code Style & Standards

### Python Version Support
- **Minimum**: Python 3.10+ (as of current version)
- Code must work across supported Python versions (3.10, 3.11, 3.12, 3.13, 3.14)

### Type Hints
- **Required** for all public APIs
- Use `typing` module or `typing_extensions` for compatibility
- Example:
  ```python
  from typing import Optional
  from htmltools import Tag, TagList
  
  def my_component(id: str, label: Optional[str] = None) -> Tag:
      ...
  ```

### Code Formatting
- **Black**: Code formatter (configuration in `pyproject.toml`)
- **isort**: Import sorting
- **flake8**: Linting (with specific ignore rules in `pyproject.toml`)
- **pyright**: Type checking

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Hooks automatically run black, isort, and flake8
```

### Development Commands
```bash
# Check everything (formatting, linting, types, tests)
make check

# Auto-fix formatting issues
make check-fix

# Individual checks
make check-format    # Check black and isort
make check-lint      # Check flake8
make check-types     # Check pyright
make check-tests     # Run pytest
```

### Documentation Standards
- **Comprehensive docstrings** for all public functions and classes
- Use Google-style or NumPy-style docstrings
- Include **examples** in docstrings when helpful
- Use the `@add_example()` decorator to link to runnable examples in `shiny/api-examples/`

## 4. Reactive Programming Patterns

Shiny uses reactive programming for automatic dependency tracking and efficient updates.

### Core Reactive Decorators

#### `@reactive.calc`
For computed values that depend on other reactive sources:
```python
@reactive.calc
def filtered_data():
    # Automatically re-executes when input.filter() changes
    return df[df['category'] == input.filter()]
```

#### `@reactive.effect`
For side effects (e.g., logging, file I/O):
```python
@reactive.effect
def _():
    # Runs when dependencies change
    print(f"Current value: {input.slider()}")
```

#### `@render.*` decorators
For rendering outputs:
```python
@render.plot
def my_plot():
    return create_plot(filtered_data())

@render.table
def my_table():
    return filtered_data()
```

### Key Concepts
- **Reactive invalidation**: When inputs change, dependent calculations automatically re-execute
- **Dependency tracking**: The reactive system automatically tracks which reactive sources are read
- **Lazy evaluation**: Reactive calculations only run when their outputs are needed
- **Avoid blocking operations**: Don't use `time.sleep()` or blocking I/O in reactive contexts

### Common Patterns
```python
# Reactive value with isolation
@reactive.calc
def expensive_computation():
    with reactive.isolate():
        # This won't create a dependency
        config = input.config()
    # But this will
    return process(input.data(), config)

# Conditional reactivity with req()
@render.text
def output():
    req(input.file())  # Only proceed if file is uploaded
    return f"Uploaded: {input.file()[0]['name']}"
```

## 5. UI Components

Shiny provides two complementary APIs for building user interfaces:

### Express API
**Best for**: Quick prototypes, simple apps, learning Shiny

```python
from shiny.express import input, render, ui

ui.page_opts(title="My App")

ui.input_slider("n", "N", min=1, max=100, value=50)

@render.text
def result():
    return f"n = {input.n()}"
```

### Core API
**Best for**: Complex applications, full control, modules

```python
from shiny import App, ui, render

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", min=1, max=100, value=50),
    ui.output_text("result")
)

def server(input, output, session):
    @render.text
    def result():
        return f"n = {input.n()}"

app = App(app_ui, server)
```

### UI Guidelines
- UI functions should return `Tag`, `TagList`, or `HTML` objects (from `htmltools`)
- Both Express and Core APIs should be **supported and tested**
- Use semantic, accessible HTML when possible
- Leverage UI helper functions like `ui.row()`, `ui.column()`, `ui.card()`, etc.

## 6. Development Workflow

### Setup
```bash
# Clone repository
git clone https://github.com/posit-dev/py-shiny.git
cd py-shiny

# Install with development dependencies
pip install -e ".[dev,test,doc]"

# Install pre-commit hooks
pre-commit install
```

### Development Cycle
```bash
# 1. Run tests before making changes
make check

# 2. Make your changes

# 3. Run formatting and tests
make check-fix

# 4. Run your app with auto-reload
shiny run app.py --reload --launch-browser

# 5. Debug with verbose logging
SHINY_LOG_LEVEL=DEBUG shiny run app.py
```

### Building Documentation
```bash
cd docs
make quartodoc  # Generate API docs
make serve      # Preview locally
```

### Testing During Development
```bash
# Run specific test file
pytest tests/pytest/test_module.py

# Run with verbose output
pytest -v tests/pytest/

# Run integration tests
pytest tests/playwright/
```

## 7. Contributing Guidelines

### Branch and PR Guidelines
- **Target branch**: `main`
- **Branch naming**: Use descriptive names (e.g., `feature/add-xyz`, `fix/issue-123`)
- **Commit messages**: Clear, concise, imperative mood ("Add feature" not "Added feature")

### Pull Request Checklist
- [ ] Include tests for new features
- [ ] Update documentation for user-facing changes
- [ ] Add changelog entries when appropriate (see `CHANGELOG.md`)
- [ ] Follow existing code organization patterns
- [ ] Ensure `make check` passes
- [ ] Add type hints to public APIs
- [ ] Include docstrings with examples

### Code Organization
- Place related functionality together
- Use modules for organization (see `shiny/ui/`, `shiny/render/`)
- Keep public API surface clean
- Mark internal functions with leading underscore (`_internal_func`)

## 8. Key Dependencies

### Core Dependencies
- **htmltools** (>=0.6.0): HTML generation and tag manipulation
- **starlette**: ASGI web framework (routing, middleware)
- **uvicorn** (>=0.16.0): ASGI server
- **websockets** (>=13.0): WebSocket support for reactive communication
- **packaging** (>=20.9): Version parsing and requirements
- **asgiref** (>=3.5.2): ASGI utilities

### Supporting Libraries
- **markdown-it-py**: Markdown parsing
- **watchfiles**: File watching for auto-reload
- **questionary**: Interactive CLI prompts
- **python-multipart**: File upload handling
- **narwhals** (>=1.10.0): DataFrame abstraction layer
- **orjson** (>=3.10.7): Fast JSON serialization

### Development Dependencies
- **black** (>=26.1.0): Code formatting
- **isort** (>=5.10.1): Import sorting
- **flake8** (>=6.0.0): Linting
- **pyright** (>=1.1.407): Type checking
- **pytest** (>=6.2.4): Testing framework
- **playwright** (>=1.48.0): Browser automation for E2E tests

## 9. Testing Considerations

### Test Structure
```
tests/
├── pytest/              # Unit tests
│   ├── test_*.py       # Test modules
│   └── fixtures/       # Test fixtures and utilities
└── playwright/          # End-to-end tests
    └── shiny/
        ├── inputs/     # Input component tests
        ├── outputs/    # Output rendering tests
        └── examples/   # Example app tests
```

### Testing Best Practices
- **Test both Express and Core APIs** when adding features
- **Unit tests** in `tests/pytest/` for logic and functionality
- **Integration tests** using Playwright for UI interactions
- **Type checking** with pyright (run via `make check-types`)
- **Consider edge cases**: empty inputs, None values, invalid data
- **Error handling**: Test that appropriate errors are raised

### Writing Tests
```python
# Unit test example
def test_reactive_calc():
    from shiny.reactive import Value, Calc
    
    x = Value(10)
    
    @Calc
    def doubled():
        return x() * 2
    
    assert doubled() == 20
    x.set(5)
    assert doubled() == 10

# Playwright test example
def test_slider_updates(page, local_app):
    page.goto(local_app.url)
    slider = page.locator("#my_slider")
    slider.fill("75")
    expect(page.locator("#output")).to_have_text("Value: 75")
```

### Running Tests
```bash
# All checks (formatting, linting, types, tests)
make check

# Only unit tests
make check-tests

# Specific test file
pytest tests/pytest/test_render.py -v

# With coverage
pytest --cov=shiny tests/pytest/

# Playwright tests
pytest tests/playwright/shiny/inputs/test_slider.py
```

## 10. Debugging Tips

### Logging
```bash
# Enable debug logging
SHINY_LOG_LEVEL=DEBUG shiny run app.py

# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

```python
# In your app
import logging
logger = logging.getLogger(__name__)

@reactive.calc
def data():
    logger.debug(f"Computing data with input: {input.x()}")
    return expensive_operation()
```

### Development Server
```bash
# Auto-reload on file changes
shiny run app.py --reload

# Launch browser automatically
shiny run app.py --reload --launch-browser

# Custom port
shiny run app.py --port 8080
```

### Debugging Techniques
1. **Print debugging**: Use `print()` in server functions (visible in console)
2. **Browser console**: Check for JavaScript errors (F12 in browser)
3. **Reactive graph**: Use `reactive.flush()` to force reactive updates
4. **Breakpoints**: Use Python debugger (`import pdb; pdb.set_trace()`)
5. **Network tab**: Inspect WebSocket messages in browser DevTools

### Common Issues
- **"Object not found"**: Accessing reactive value outside reactive context
- **Infinite loops**: Reactive cycles (A depends on B, B depends on A)
- **Stale data**: Forgetting to call reactive with `()` (use `input.x()` not `input.x`)
- **Module namespace errors**: Incorrect use of `session.ns()` in modules

## 11. Documentation

### API Documentation
- Generated with **Quartodoc** (https://machow.github.io/quartodoc/)
- Source files in `docs/` directory
- Configuration in `docs/_quarto.yml`
- Built with Quarto (https://quarto.org/)

### Documentation Structure
```
docs/
├── _quarto.yml           # Quarto configuration
├── api/                  # API reference (generated)
│   ├── core/            # Core API docs
│   └── express/         # Express API docs
├── docs/                 # User guides and tutorials
└── examples/             # Featured examples
```

### Writing Good Documentation
- **Examples are essential**: Every public function should have usage examples
- **Runnable examples**: Use `@add_example()` to link to `shiny/api-examples/`
- **Clear descriptions**: Explain *what*, *why*, and *how*
- **Link related functions**: Use references to connect related functionality
- **Simple → Advanced**: Start with simple examples, progress to complex

### Example Documentation Pattern
```python
from shiny import ui
from shiny._docstring import add_example

@add_example()
def input_slider(
    id: str,
    label: str,
    min: float,
    max: float,
    value: float,
    *,
    step: Optional[float] = None,
) -> Tag:
    """
    Create a slider input control.
    
    Parameters
    ----------
    id
        An input id.
    label
        Label for the slider.
    min
        Minimum value.
    max
        Maximum value.
    value
        Initial value.
    step
        Increment step size.
        
    Returns
    -------
    :
        A UI element for a slider input.
        
    See Also
    --------
    * ~shiny.ui.input_numeric
    * ~shiny.ui.update_slider
    """
    ...
```

## 12. Community Resources

### Getting Help
- **Discord**: https://discord.gg/yMGCamUMnS (main community hub)
- **GitHub Discussions**: https://github.com/posit-dev/py-shiny/discussions
- **Documentation**: https://shiny.posit.co/py/
- **GitHub Issues**: https://github.com/posit-dev/py-shiny/issues

### Learning Resources
- **Gallery**: https://shiny.posit.co/py/gallery/
- **Templates**: https://shiny.posit.co/py/docs/templates.html
- **Tutorials**: https://shiny.posit.co/py/docs/overview.html
- **Reactive Programming Guide**: https://shiny.posit.co/py/docs/reactive-programming.html
- **Modules Guide**: https://shiny.posit.co/py/docs/workflow-modules.html

### Deployment Options
- **Posit Connect**: https://posit.co/products/enterprise/connect/
- **Connect Cloud**: https://docs.posit.co/connect-cloud/
- **shinyapps.io**: https://www.shinyapps.io/
- **Hugging Face**: https://huggingface.co/spaces
- **Shinylive** (WASM): https://shiny.posit.co/py/docs/shinylive.html

## 13. Code Generation Guidelines for Copilot

When generating code for py-shiny, prioritize:

### 1. Type Safety
```python
# Good: Type hints on public APIs
def my_function(data: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    ...

# Avoid: Missing type hints on public functions
def my_function(data, threshold=0.5):
    ...
```

### 2. Reactive Patterns Over Imperative Code
```python
# Good: Reactive pattern
@reactive.calc
def filtered_data():
    return df[df['value'] > input.threshold()]

@render.table
def table():
    return filtered_data()

# Avoid: Imperative, non-reactive
def update_table():
    global current_data
    current_data = df[df['value'] > threshold]
```

### 3. Express vs. Core API
```python
# Express: For simple, quick examples
from shiny.express import input, render, ui

ui.input_slider("n", "N", 1, 100, 50)

@render.text
def txt():
    return f"n = {input.n()}"

# Core: For complex, modular applications
from shiny import App, ui, render, module

@module.ui
def counter_ui():
    return ui.card(
        ui.input_action_button("increment", "+1"),
        ui.output_text("count")
    )
```

### 4. Clear Variable Naming
```python
# Good: Clear, descriptive names following Shiny conventions
@reactive.calc
def filtered_penguins():
    return penguins[penguins.species == input.species_filter()]

# Avoid: Unclear abbreviations
@reactive.calc
def filt_peng():
    return p[p.s == input.sf()]
```

### 5. Proper Error Handling
```python
# Good: Graceful handling of missing inputs
@render.plot
def scatter():
    req(input.file())  # Require file to be uploaded
    df = pd.read_csv(input.file()[0]["datapath"])
    return create_plot(df)

# Avoid: Unhandled errors
@render.plot
def scatter():
    df = pd.read_csv(input.file()[0]["datapath"])  # May crash
    return create_plot(df)
```

### 6. Performance Considerations
```python
# Good: Minimize reactive dependencies
@reactive.calc
def expensive_calc():
    # Only depends on necessary inputs
    return complex_computation(input.data())

@render.text
def summary():
    # Reuses cached calculation
    result = expensive_calc()
    return f"Result: {result}"

# Avoid: Unnecessary reactivity
@render.text
def summary():
    # Recalculates every time
    return f"Result: {complex_computation(input.data())}"
```

## 14. Common Gotchas

### 1. Calling Reactives Outside Reactive Context
```python
# Wrong: Calling reactive outside reactive context
filtered_data = filtered_data()  # Error!

# Right: Call reactives inside reactive contexts
@render.table
def table():
    return filtered_data()  # OK: inside render decorator
```

### 2. Using `req()` for Graceful Handling
```python
# Good: Use req() to handle missing inputs
@render.plot
def plot():
    req(input.x_var(), input.y_var())
    return create_scatter(df, input.x_var(), input.y_var())

# Avoid: Manual checks that don't stop execution
@render.plot
def plot():
    if not input.x_var():
        return  # Might still cause errors
    return create_scatter(df, input.x_var(), input.y_var())
```

### 3. Automatic UI Updates
```python
# Remember: UI updates are automatic with reactive programming
# Don't try to manually update output

# Good: Reactive pattern handles updates automatically
@reactive.calc
def data():
    return load_data(input.dataset())

@render.table
def table():
    return data()  # Automatically updates when input.dataset() changes

# Avoid: Trying to manually trigger updates
# (Not necessary in Shiny!)
```

### 4. Module Namespacing
```python
# Modules require proper namespacing

@module.ui
def counter_ui():
    return ui.div(
        ui.input_action_button("button", "Click"),
        ui.output_text("count")
    )

@module.server
def counter_server(input, output, session):
    count = reactive.value(0)
    
    @reactive.effect
    @reactive.event(input.button)
    def _():
        count.set(count() + 1)
    
    @render.text
    def count():
        return str(count())

# In app: use session.ns() for module IDs
counter_ui("counter1")  # Creates inputs with IDs "counter1-button", "counter1-count"
```

### 5. File Paths in Deployed Apps
```python
# Good: Use Path(__file__).parent for relative paths
from pathlib import Path

app_dir = Path(__file__).parent
data_path = app_dir / "data" / "dataset.csv"

# Avoid: Hardcoded absolute paths
data_path = "/home/user/my_app/data/dataset.csv"  # Won't work when deployed
```

### 6. Reactive Value Access
```python
# Wrong: Forgetting to call reactive (missing parentheses)
def some_function():
    threshold = input.threshold  # This is a function, not the value!
    
# Right: Always call reactive values with ()
def some_function():
    threshold = input.threshold()  # Gets the actual value
```

---

## Quick Reference

### Most Common Patterns

**Simple Express App:**
```python
from shiny.express import input, render, ui

ui.input_slider("n", "N", 1, 100, 50)

@render.text
def result():
    return f"n*2 = {input.n() * 2}"
```

**Core App with Reactive Calc:**
```python
from shiny import App, render, ui, reactive

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 1, 100, 50),
    ui.output_text("result")
)

def server(input, output, session):
    @reactive.calc
    def doubled():
        return input.n() * 2
    
    @render.text
    def result():
        return f"n*2 = {doubled()}"

app = App(app_ui, server)
```

**Module Pattern:**
```python
from shiny import module, ui, render, reactive

@module.ui
def my_module_ui():
    return ui.div(
        ui.input_text("name", "Name"),
        ui.output_text("greeting")
    )

@module.server
def my_module_server(input, output, session):
    @render.text
    def greeting():
        return f"Hello, {input.name()}!"
```

---

**Version Info**: This document is for py-shiny >= 1.0.0 supporting Python 3.10+
