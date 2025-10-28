# Porting Components from bslib to py-shiny

This guide explains how to port new UI components from the R bslib package to py-shiny. It assumes you're an experienced developer familiar with Python, R, and JavaScript/TypeScript, but may be new to the specifics of these repositories.

## Background

The bslib R package serves as the primary development location for new Bootstrap 5 components in the Shiny ecosystem. Components developed in bslib are then ported to py-shiny to maintain feature parity between Shiny for R and Shiny for Python.

**Key relationship**: bslib provides both the R implementation and the compiled JavaScript/CSS assets that py-shiny vendors and uses directly.

## Overview of the Porting Process

The porting process involves three main phases:

1. **Understanding the source** - Study the bslib implementation (R, TypeScript, SCSS)
2. **Implementing the port** - Create Python equivalents and add client-side bindings
3. **Testing and documentation** - Ensure correctness with unit and end-to-end tests

## Phase 1: Understanding the Source Implementation

### Step 1.1: Locate the bslib PR

Find the bslib PR that introduced the feature. The py-shiny PR description should reference it (e.g., `Related https://github.com/rstudio/bslib/pull/...`).

**Checklist:**
- [ ] Located the bslib PR
- [ ] Reviewed the PR description and any design discussions

### Step 1.2: Identify the core source files

In the bslib PR, locate these key files:

1. **R implementation**: `R/[feature-name].R` - The main component function(s)
2. **TypeScript bindings**: `srcts/src/components/[featureName].ts` - Client-side behavior
3. **SCSS styles**: `inst/components/scss/[feature_name].scss` - Component styles
4. **Unit tests**: `tests/testthat/test-[feature-name].R` - R unit tests

**Note**: Generated files (compiled JS/CSS, documentation) can be ignored - focus on source files.

**Checklist:**
- [ ] Found the R implementation file(s)
- [ ] Found the TypeScript source file(s)
- [ ] Found the SCSS source file
- [ ] Found the unit test file(s)
- [ ] Reviewed how TypeScript is registered in `srcts/src/components/index.ts`

### Step 1.3: Understand the component structure

Study the bslib implementation to understand:

1. **API design**: Function signature, parameters, defaults
2. **HTML structure**: The DOM elements created by the R function
3. **Client-side behavior**: How the TypeScript binding handles interactions
4. **Shiny communication**: How the component sends/receives values from the server
5. **Dependencies**: What other components or utilities it relies on

**Key patterns to note:**
- Is the component an input binding? If so, how does the binding register (typically via a CSS class)?
- What markup structure does it generate on the server side?
- How does the component integrate with Bootstrap classes?
- How are configuration options passed from R to JavaScript -- data attributes, embedded JSON, etc.?
- How does the component receive data from the server -- via `sendInputMessage()` or `sendCustomMessage()`?
- How does the component receive data from the client -- via `receiveMessage()` or small inputs set with `Shiny.setInputValue()`?

**Checklist:**
- [ ] Documented the component's API surface
- [ ] Understood the HTML structure and CSS classes
- [ ] Identified client-side event handlers and state management
- [ ] Noted any dependencies on other components

## Phase 2: Implementing the Port

### Step 2.1: Create the Python implementation

Create a new file in `shiny/ui/` for the component implementation.

**File naming**: Use snake_case matching the R function name:
- R: `input_submit_textarea()` → Python: `_input_submit_textarea.py`

**Implementation notes:**
- Translate R's htmltools to Python's htmltools
- Use `@add_example()` decorator for documentation examples (examples are created in a later step)
- Follow existing patterns for parameter validation
- Use `resolve_id()` for module namespace support
- Use `restore_input()` for bookmarking support
- Include both the main component function and any `update_*()` functions

**Common translations:**
- R `tags$div()` → Python `div()` or `tags.div()`
- R `!!!args` (splicing) → Python `*args`+`**kwargs`
- R `NULL` → Python `None`
- R lists → Python dicts or lists as appropriate
- R `paste0()` → Python f-strings or `.format()`

**Checklist:**
- [ ] Created `shiny/ui/_[component_name].py`
- [ ] Implemented the main component function with full docstring
- [ ] Implemented any `update_*()` functions
- [ ] Added parameter validation
- [ ] Added support for modules (`resolve_id`)
- [ ] Added support for bookmarking (`restore_input`)
- [ ] Used `components_dependencies()` for client-side deps

### Step 2.2: Export the new functions

Update `shiny/ui/__init__.py` to export the new component:

```python
from ._input_submit_textarea import input_submit_textarea, update_submit_textarea

__all__ = (
    # ... existing exports ...
    "input_submit_textarea",
    "update_submit_textarea",
)
```

If the component is suitable for express mode, also export from `shiny/express/ui/__init__.py`.

**Checklist:**
- [ ] Added imports to `shiny/ui/__init__.py`
- [ ] Added to `__all__` tuple in `shiny/ui/__init__.py`
- [ ] (If applicable) Exported from `shiny/express/ui/__init__.py`

### Step 2.3: Vendor assets from bslib

The TypeScript in bslib is compiled to JavaScript and bundled, and SCSS is compiled to CSS. Py-shiny vendors these compiled assets along with the SCSS source files from bslib.

**Process:**
1. Ensure bslib PR is merged and the feature is in the branch referenced in `scripts/_pkg-sources.R` (usually `@main`)
2. If vendoring from a non-default branch or specific commit, update `scripts/_pkg-sources.R` temporarily
3. Run `make upgrade-html-deps` to vendor the latest assets from bslib, shiny, sass, and htmltools

**What `make upgrade-html-deps` does:**
- Copies SCSS source files from bslib to `shiny/www/shared/sass/bslib/components/scss/`
- Updates all theme preset `_04_rules.scss` files to import the new SCSS
- Compiles SCSS to CSS for all themes
- Vendors compiled JavaScript bundles (`components.min.js`, etc.)
- Updates other shared assets from upstream packages

**Files updated by this process** (examples):
- `shiny/www/shared/sass/bslib/components/scss/[feature_name].scss` (SCSS source)
- `shiny/www/shared/sass/preset/*/04_rules.scss` (27 theme preset files with new imports)
- `shiny/www/shared/bslib/components/components.min.js` (compiled JavaScript)
- `shiny/www/shared/bslib/components/components.min.js.map` (source map)
- `shiny/www/shared/bslib/components/components.css` (compiled CSS)
- Other theme-specific CSS files

**Note**: This is a manual process that's not part of CI. The vendored files are committed to the repository.

**Checklist:**
- [ ] Verified bslib PR is merged (or adjusted `scripts/_pkg-sources.R` if needed)
- [ ] Ran `make upgrade-html-deps`
- [ ] Reviewed changes to vendored files (SCSS, CSS, JS)
- [ ] Verified new SCSS imports in theme preset files
- [ ] Restored `scripts/_pkg-sources.R` if temporarily modified

### Step 2.4: Create API examples

Create example applications demonstrating the component's usage.

**Location**: `shiny/api-examples/[component_name]/`

**Files to create**:
- `app-core.py` - Core mode example
- `app-express.py` - Express mode example (if applicable)

**Example structure**:
```python
# app-express.py
from shiny.express import input, render, ui

ui.input_submit_textarea("text", placeholder="Enter some input...")

@render.text
def value():
    if "text" in input:
        return f"You entered: {input.text()}"
    else:
        return "Submit some input to see it here."
```

**Best practices**:
- Keep examples simple and focused
- Demonstrate the primary use case
- Show server-side value handling patterns
- Include any important parameter variations
- Re-use examples from bslib where possible
- Always include an Express version unless there's a strong reason not to
- A human reviewer should test the examples locally

**Checklist:**
- [ ] Created `shiny/api-examples/[component]/app-core.py`
- [ ] Created `shiny/api-examples/[component]/app-express.py` (unless not warranted)
- [ ] Tested examples locally

### Step 2.5: Add Playwright controller (if input component)

If the component is an input component, create a Playwright controller for end-to-end testing.

**Location**: `shiny/playwright/controller/_input_fields.py` (or create new file if needed)

**Implementation**:
1. Create a new class inheriting from appropriate mixins
2. Implement required methods: `__init__`, `set`, interaction methods
3. Add expectation methods for testing (e.g., `expect_value`, `expect_placeholder`)
4. Follow existing patterns for locator initialization

**Example pattern**:
```python
class InputSubmitTextarea(
    _SetTextM,
    WidthContainerStyleM,
    _ExpectTextInputValueM,
    _ExpectPlaceholderAttrM,
    _ExpectRowsAttrM,
    UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_submit_textarea`."""

    loc_button: Locator

    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"textarea#{id}.form-control",
        )
        self.loc_button = self.loc_container.locator(".bslib-submit-textarea-btn")

    def set(self, value: str, *, submit: bool = False, timeout: Timeout = None) -> None:
        # Implementation
        pass
```

**Don't forget to export**: Update `shiny/playwright/controller/__init__.py` to export the new controller class.

**Checklist:**
- [ ] Created Playwright controller class
- [ ] Implemented core interaction methods
- [ ] Implemented expectation methods for testing
- [ ] Exported from `shiny/playwright/controller/__init__.py`
- [ ] Added to `__all__` in the same file

## Phase 3: Testing and Documentation

### Step 3.1: Port unit tests from bslib

Port the relevant unit tests from bslib's testthat tests to pytest.

**Translation patterns**:
- R `test_that()` → Python `def test_[name]():`
- R `expect_snapshot()` → Python snapshot testing (if applicable)
- R `expect_error()` → Python `with pytest.raises()`

**Focus on**:
- Parameter validation
- Error messages
- Edge cases
- HTML structure (snapshot tests if helpful)

**Note**: Python has better tooling for end-to-end tests, so unit tests here focus on correctness of the Python API and generated markup.

**Checklist:**
- [ ] Ported relevant unit tests
- [ ] Tests pass locally (`pytest tests/`)

### Step 3.2: Create end-to-end Playwright tests

Create comprehensive end-to-end tests using Playwright. It is likely that these tests do not exist in the R package, so you will need to use your knowledge of the component and its documented behavior to create them. Collaborate with the human reviewer if there are any uncertainties around expected behavior.

**Location**: `tests/playwright/shiny/inputs/[component_name]/`

**Files to create**:
- `app.py` - Test application with multiple variants
- `test_[component_name].py` - Playwright test cases

**Test coverage should include**:
- Initial state verification
- User interactions (typing, clicking, keyboard shortcuts)
- Server updates (via `update_*()` functions)
- Edge cases (empty values, disabled states, etc.)
- Multiple submissions and state changes

**Example test structure**:
```python
def test_input_submit_textarea_initial_state(page: Page, local_app: ShinyAppProc):
    page.goto(local_app.url)

    basic = controller.InputSubmitTextarea(page, "basic")
    basic.expect_label("Enter text")
    basic.expect_placeholder("Type something here...")
    basic.expect_value("Initial value")

    value_output = controller.OutputCode(page, "basic_value")
    value_output.expect_value("No value submitted yet")
```

**Best practices**:
- Use the Playwright controller for interactions
- Test both user interactions and programmatic updates
- Use clear, descriptive test names
- Verify both input state and output state
- Output state can be checked by rendering text outputs in the test app

**Checklist:**
- [ ] Created test app with multiple component variations
- [ ] Created comprehensive test cases
- [ ] Tests pass locally (`pytest tests/playwright/`)
- [ ] Covered key interaction patterns and edge cases

### Step 3.3: Update CHANGELOG

Add an entry to `CHANGELOG.md` under the `[UNRELEASED]` section.

**Format**:
```markdown
### New features

* Added `input_new_feature()` [description of function, new features and salient details in 1-3 sentences]. (#[PR_NUMBER])
```

**Checklist:**
- [ ] Added CHANGELOG entry under appropriate section
- [ ] Entry includes clear description and PR reference

### Step 3.4: Run quality checks

Run the various quality checks to ensure your code meets project standards.

**Recommended workflow**:
1. `make formatting` - Fix formatting and linting issues automatically
2. `make check-types` - Run type checking (pyright)
3. `make check-tests` - Run the test suite
4. `make playwright` - Run Playwright end-to-end tests (see `Makefile` for alternate make commands to run subsets of tests)
5. `make check` - Comprehensive checks (slower, runs everything)

**Common issues**:
- Type errors: Ensure proper type hints on all functions
- Format errors: Run `make format` to auto-fix
- Missing imports: Ensure all new modules are properly imported
- Test failures: Debug and fix any failing tests

**Checklist:**
- [ ] `make format` applied successfully
- [ ] `make check-types` passes
- [ ] `make check-tests` passes (or at least your new tests pass)
- [ ] `make playwright` passes (or at least new end-to-end tests pass)
- [ ] Addressed any other linting/quality issues

### Step 3.5: Update API reference configuration

Add the new component functions to the quartodoc YAML configuration files so they appear in the generated documentation.

**Files to update**:
- `docs/_quartodoc-core.yml` - Add component function and update function (if applicable)
- `docs/_quartodoc-express.yml` - Add express versions (if applicable)
- `docs/_quartodoc-testing.yml` - Add Playwright controller (if applicable)

**Where to add entries**:
- Find the appropriate section (e.g., "Inputs" for input components, "Update" for update functions)
- Add entries in alphabetical order within the section
- Use the full module path (e.g., `ui.input_submit_textarea`)

**Example additions**:
```yaml
# In _quartodoc-core.yml under inputs section:
- ui.input_submit_textarea

# In _quartodoc-core.yml under update section:
- ui.update_submit_textarea

# In _quartodoc-express.yml:
- express.ui.input_submit_textarea
- express.ui.update_submit_textarea

# In _quartodoc-testing.yml:
- playwright.controller.InputSubmitTextarea
```

**Checklist:**
- [ ] Added entries to `docs/_quartodoc-core.yml`
- [ ] Added entries to `docs/_quartodoc-express.yml` (if applicable)
- [ ] Added entries to `docs/_quartodoc-testing.yml` (if applicable)
- [ ] Verified alphabetical ordering within sections

### Step 3.6: Build documentation (final step)

Only build documentation at the very end, as it's slow and resource-intensive.

**Command**: `make docs`

**This will**:
- Generate API reference documentation from the quartodoc YAML files
- Build example applications
- Create the documentation website

**Note**: You don't need to run this frequently during development. It's primarily for final verification before PR submission. A human reviewer can handle this entire step, just remind them to run it before merging.

**Checklist:**
- [ ] `make docs` completes successfully
- [ ] Reviewed the generated documentation for your component
- [ ] API reference appears correctly in the appropriate sections
- [ ] Examples are properly linked

## Phase 4: Final Review and Submission

### Step 4.1: Self-review the changes

Before submitting, review all changes:

**Python code**:
- [ ] Functions have comprehensive docstrings
- [ ] Parameter types and defaults match or improve on bslib's API
- [ ] Code follows existing project patterns
- [ ] Error messages are clear and helpful

**Tests**:
- [ ] Unit tests cover parameter validation and edge cases
- [ ] End-to-end tests cover user workflows
- [ ] All tests pass locally

**Styles**:
- [ ] SCSS is imported in all theme presets
- [ ] Styles match the bslib implementation

**Documentation**:
- [ ] CHANGELOG is updated
- [ ] API examples are clear and working
- [ ] Docstrings are complete

### Step 4.2: Create the PR

Create a pull request with:

1. **Title**: `feat: Add [component_name]` or similar
2. **Description**:
   - Link to the source bslib PR
   - Brief description of the component
   - Any implementation notes or decisions
   - Example usage

**PR description template**:
```markdown
Related https://github.com/rstudio/bslib/pull/[NUMBER]

Adds `[component_name]`, a new [input/output/UI] component that [brief description].

## Example

Here is a hello world example:

[code block with example]

## Implementation notes

[Any important notes about the implementation, decisions made, etc. or open questions for reviewers.]
```

**Checklist:**
- [ ] PR title follows project conventions
- [ ] PR description links to bslib source
- [ ] PR description includes example usage
- [ ] All quality checks pass in CI

---

## Quick Reference Checklist

Use this high-level checklist to track your progress through the porting process:

### Preparation
- [ ] Located and reviewed the bslib PR
- [ ] Identified all source files (R, TypeScript, SCSS, tests)
- [ ] Understood the component's API and behavior

### Implementation
- [ ] Created Python implementation in `shiny/ui/_[name].py`
- [ ] Exported from `shiny/ui/__init__.py` (and express if applicable)
- [ ] Ran `make upgrade-html-deps` to vendor assets from bslib (SCSS, CSS, JavaScript)
- [ ] Created API examples (core and express)
- [ ] Created Playwright controller (if input component)

### Testing
- [ ] Ported unit tests from bslib
- [ ] Created comprehensive Playwright tests
- [ ] Updated CHANGELOG

### Documentation
- [ ] Updated quartodoc YAML files to include new functions
- [ ] Ran `make format`
- [ ] Passed `make check-types`
- [ ] Passed `make check-tests`
- [ ] Built docs with `make docs`

### Submission
- [ ] Self-reviewed all changes
- [ ] Created PR with proper description
- [ ] All CI checks passing

---

## Common Patterns and Tips

### Handling component dependencies

If the component depends on other components:
- Use `components_dependencies()` for bslib components (automatic)
- For other dependencies, add them explicitly in the component function

### Testing with different themes

The component should work with all Bootstrap themes. The `make upgrade-html-deps` process ensures SCSS is properly imported across all theme presets, but you may want to spot-check a few themes manually during development.

### Parameter naming conventions

Python style guide preferences:
- Use `snake_case` for parameter names
- Match bslib's parameter names when possible
- Use `Optional[T]` for user-facing parameters that can be `None`
- Use `Literal` rather than `Enum` for parameters with specific allowed values

### Working with htmltools

Key patterns:
- `Tag` objects are mutable by default, use `copy.copy()` if you need to modify
- Use `.add_class()`, `.add_style()`, `.attrs` to add CSS classes, styles, and HTML attributes
- Use `css()` helper for inline styles
- Tag children can be strings, Tags, TagLists, or None

---

## Troubleshooting

### "Tests fail with 'element not found'"

- Verify Playwright selectors match the actual HTML structure
- Check that the component is properly rendered before interaction
- Use `page.wait_for_selector()` if there are timing issues

### "SCSS not taking effect"

- Check that `make upgrade-html-deps` was run to vendor and compile SCSS/CSS
- Verify the SCSS file exists in `shiny/www/shared/sass/bslib/components/scss/`
- Verify the imports were added to preset `_04_rules.scss` files (should be automatic)
- Clear browser cache when testing

---

## Additional Resources

- **bslib repository**: https://github.com/rstudio/bslib
- **py-shiny repository**: https://github.com/posit-dev/py-shiny
- **Example PR (bslib)**: https://github.com/rstudio/bslib/pull/1204
- **Example PR (py-shiny)**: https://github.com/posit-dev/py-shiny/pull/2099

For questions or clarifications, consult with the Shiny team or reference previous component ports for patterns.
