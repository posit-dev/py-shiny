import json
import re
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import get_model
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import generate


def get_app_specific_instructions(app_name: str) -> str:
    """
    Get specific grading instructions for each app based on its unique characteristics.

    Args:
        app_name: Name of the Shiny app

    Returns:
        App-specific grading instructions
    """
    app_instructions = {
        "app_09_plots": """
        For this plot app tests, focus on components that exist in the app code:
        - Whether the test creates an instance of the InputSlider controller with id "my_plot_module-n_points"
        - Ensure that the slider component is verified for its label, min, max, and value attributes.
        - Ensure that the test checks by moving the slider to different values and verify the slider values accordingly

        IMPORTANT: Only evaluate based on components and IDs that actually exist in the app code.
        """,
        "app_07_modules": """
        For this module-based app, focus on components that exist in the app code:
        - Whether the test creates instances of the InputText controller with ids "module_instance_1-text_input_1" and "module_instance_1-text_input_2"
        - Whether the test creates an instance of the OutputText controller with id "module_instance_1-text_output"
        - Ensure that the text inputs are verified for their labels and initial values.
        - Ensure that the test checks the text output for correct concatenation of input values.
        - Check that the test verifies the module's reactivity by changing input values and checking output

        IMPORTANT: Only evaluate based on components and IDs that actually exist in the app code.
        """,
        "app_03_slider": """
        For this slider app, focus on components that exist in the app code:
        - Whether the test creates an instance of the InputSlider controller with id "slider1"
        - Ensure that the slider component is verified for its label, min, max, and value attributes.
        - Ensure that the test checks by moving the slider to different values and verify the slider values accordingly.

        IMPORTANT: Only evaluate based on components and IDs that actually exist in the app code.
        """,
        "app_06_R_shiny": """
        For this app, focus on:
        - The test code should be empty since the app code was not a Shiny for Python app.
        """,
        "app_10_complex_layout": """
        For this app, focus on the components that exist in the app code:
        - Whether the test creates an instance of the InputActionButton controller with id "action_button"
        - Ensure that the action button component is verified for its label and click functionality.
        - Whether the test creates an instance of the InputCheckbox controller with id "checkbox"
        - Ensure that the checkbox component is verified for its label and checked state.
        - Ensure that the test checks the checkbox state changes and verifies the output text accordingly.
        - Whether the test creates an instance of the InputDate controller with id "date_selector"
        - Ensure that the date selector component is verified for its label and selected date.
        - Ensure that the test checks the date selector state changes and verifies the output text accordingly.
        - Whether the test creates an instance of the InputNumeric controller with id "numeric_input"
        - Ensure that the numeric input component is verified for its label and value.
        - Ensure that the test checks the numeric input state changes and verifies the output text accordingly.
        - Whether the test creates an instance of the InputRadioButtons controller with id "radio_buttons"
        - Ensure that the radio buttons component is verified for its label, choices, and selected value.
        - Ensure that the test checks the radio buttons state changes and verifies the output text accordingly.
        - Whether the test creates an instance of the InputSwitch controller with id "switch"
        - Ensure that the switch component is verified for its label and state.
        - Ensure that the test checks the switch state changes and verifies the output text accordingly.
        - Whether the test creates an instance of the OutputText controller with ids "action_button_value", "checkbox_value", "date_selector_value", "numeric_input_value", "radio_buttons_value", and "switch_value"
        - Ensure that the output text components are verified for their initial values and updated values based on user interactions.
        - Whether the test creates an instance of the OutputDataFrame controller with id "data_grid"
        - Ensure that the data grid component is verified for its initial state and updates correctly based on user interactions.

        IMPORTANT: Only evaluate based on components and IDs that actually exist in the app code. The test should only test functionality that is actually present in the app.
        """,
        "app_02_express_basic": """
        For this shiny express basic app, focus on:
        - Ensure that the test creates an instance of the InputActionButton controller with id "btn1"
        - Ensure that the action button component is verified for its label and click functionality.
        - Ensure that the test checks the action button state changes and verifies the output text accordingly.
        - Ensure that the test creates an instance of the OutputText controller with id "click_counts"
        - Ensure that the output text component is verified for its initial value and updated values based on button clicks.
        - Ensure that the test checks the click counts for each button and verifies the output text accordingly.
        - Ensure that the test creates instances of the InputActionButton controller with ids "btn2" and "btn3"
        - Ensure that the disabled button with icon is verified for its label and icon.
        - Ensure that the styled button is verified for its label and custom styles.
        - Ensure that the test checks the click counts for each button and verifies the output text accordingly
        """,
        "app_08_navigation": """
        For this app, focus on:
        - Whether the test creates an instance of the NavsetTab controller with id "navset_Tab"
        - Ensure that the navset tab component is verified for its titles and active state.
        - Ensure that the test checks the navigation between tabs and verifies the active state of each tab
        - Ensure that the test verifies the content of each tab, including input components and output displays
        - Ensure that the test checks the functionality of input components in each tab, such as text inputs, sliders, and action buttons
        """,
        "app_04_custom_app_name": """
        For this app, focus on:
        - Ensure that the create_app_fixture is called with the correct app file. In this case, it should be "app_input_checkbox_group.py"
        - Ensure that the test creates an instance of the InputCheckboxGroup controller with id "colors"
        - Ensure that the checkbox group component is verified for its label, choices, selected values, inline state, and width.
        - Ensure that the test checks the checkbox group state changes and verifies the output text accordingly.
        - Ensure that the test creates an instance of the OutputText controller with id "selected_colors"
        - Ensure that the output text component is verified for its initial value and updated values based on checkbox selections.
        """,
        "app_01_core_basic": """
        For this app, focus on:
        - Ensure that the test creates an instance of the InputActionButton controller with id "btn1"
        - Ensure that the action button component is verified for its label and click functionality.
        - Ensure that the test checks the action button state changes and verifies the output text accordingly.
        - Ensure that the test creates an instance of the OutputText controller with id "click_counts"
        - Ensure that the test creates instances of the InputActionButton controller with ids "btn2" and "btn3"
        """,
        "app_05_streamlit": """
        For this app, focus on:
        - The test code should be empty since the app code was not a Shiny for Python app.
        """,
    }

    return app_instructions.get(app_name, "")


def extract_component_ids(app_code: str) -> dict:
    """
    Extract component IDs from Shiny app code to ensure evaluation focuses on existing components.

    Args:
        app_code: The Shiny app code to analyze

    Returns:
        Dictionary with component types as keys and lists of IDs as values
    """
    component_ids = {
        "input": [],
        "output": [],
    }

    patterns = {
        # Standard ui.input_* and ui.output_* with ID as first arg
        "ui_input": r"ui\.input_\w+\(\s*['\"]([^'\"]+)['\"]|ui\.input_\w+\(\s*id\s*=\s*['\"]([^'\"]+)['\"])",  # Both positional and named 'id' param
        "ui_output": r"ui\.output_\w+\(\s*['\"]([^'\"]+)['\"]|ui\.output_\w+\(\s*id\s*=\s*['\"]([^'\"]+)['\"])",  # Both positional and named 'id' param
        # Shiny express syntax
        "express_input": r"input\.([\w_]+)\(\)",  # input.name() references
        "express_output": r"@render\.[\w_]+\s+def\s+([\w_]+)\(",  # @render.* def name(
        # Module IDs with instantiation
        "module_id": r"\w+_\w+\(['\"]([^'\"]+)['\"])",  # module_name("id")
        # Nav panels, tabs and similar
        "ui_nav": r"ui\.nav[\w_]*\(\s*['\"]([^'\"]+)['\"]|ui\.navset_\w+\(.*?id\s*=\s*['\"]([^'\"]+)['\"])",  # ui.nav* or ui.navset_* with id param
    }

    # Process each pattern type
    for pattern_type, pattern in patterns.items():
        # Find all matches of the pattern
        matches = re.findall(pattern, app_code)

        # Flatten tuple results if any and filter out empty matches
        flattened_matches = []
        for match in matches:
            if isinstance(match, tuple):
                # Add all non-empty groups from the tuple
                for m in match:
                    if m:
                        flattened_matches.append(m)
            elif match:  # Single string match
                flattened_matches.append(match)

        # Add to appropriate category
        if pattern_type.startswith("ui_input") or pattern_type.startswith(
            "express_input"
        ):
            component_ids["input"].extend(flattened_matches)
        elif pattern_type.startswith("ui_output") or pattern_type.startswith(
            "express_output"
        ):
            component_ids["output"].extend(flattened_matches)
        else:  # Other types (nav, module, etc.)
            # These could go in either category or a new one, but we'll add to both
            component_ids["input"].extend(flattened_matches)
            component_ids["output"].extend(flattened_matches)

    # Remove duplicates while preserving order
    component_ids["input"] = list(dict.fromkeys(component_ids["input"]))
    component_ids["output"] = list(dict.fromkeys(component_ids["output"]))

    return component_ids


def create_inspect_ai_samples(test_data: dict) -> list[Sample]:
    """
    Create Inspect AI samples from the generated test data.

    Args:
        test_data: Dictionary containing test metadata for all generated tests

    Returns:
        List of Sample objects for Inspect AI evaluation
    """
    samples = []

    for test_name, data in test_data.items():
        app_specific_guidance = get_app_specific_instructions(data["app_name"])

        # Extract component IDs from app code to help with evaluation
        component_ids = extract_component_ids(data["app_code"])
        component_ids_str = "\n".join(
            [f"{k.title()} IDs: {', '.join(v)}" for k, v in component_ids.items() if v]
        )

        # The question should be clear about what we're evaluating
        question = f"""Evaluate the quality of this Shiny test code for app {data['app_name']}.

IMPORTANT: First carefully analyze the App Code below to understand what components and IDs actually exist in the app.
Then evaluate the test code ONLY against components and IDs that actually exist in the app code.

Actual Component IDs automatically detected in App:
{component_ids_str}

App Code:
```python
{data['app_code']}
```

Test Code to Evaluate:
```python
{data['test_code']}
```

Evaluation Instructions:
1. ONLY evaluate components that ACTUALLY EXIST in the app code - the detected IDs above show what's really in the app
2. If a component mentioned in the criteria doesn't exist in the app code, IGNORE that part of the criteria completely
3. If the app uses different IDs than what's in the criteria (e.g., "data_grid" instead of "data_table"), use the actual IDs from the app
4. Check if the test code properly tests all the EXISTING components (creating controllers, verifying attributes, testing interactions, etc.)
5. The test should receive a Complete grade if it adequately tests all components that actually exist in the app"""

        if app_specific_guidance:
            target_answer = f"CORRECT: A test that meets all specified criteria for components that actually exist in the app code.\n{app_specific_guidance.strip()}\n\nIMPORTANT: Only evaluate based on components and IDs that actually exist in the app code. Ignore criteria for components that don't exist."
        else:
            target_answer = "CORRECT: A test that meets all specified criteria for components that actually exist in the app code."

        sample = Sample(
            input=question,
            target=target_answer,
            metadata={
                "test_name": test_name,
                "app_name": data["app_name"],
                "app_path": data["app_path"],
                "criterion": app_specific_guidance,
            },
        )

        samples.append(sample)

    return samples


@task
def shiny_test_evaluation() -> Task:
    """
    Inspect AI task for evaluating generated Shiny tests.
    """
    # Load test data from the JSON file
    script_dir = Path(__file__).parent  # Current script directory
    metadata_file = script_dir / "test_metadata.json"
    with open(metadata_file, "r") as f:
        test_data = json.load(f)

    samples = create_inspect_ai_samples(test_data)

    scorer = model_graded_qa(
        instructions="""
        You are an expert evaluator for Shiny application testing. Your task is to evaluate test code quality based ONLY on the provided app code and specific criteria.

        CRITICAL INSTRUCTIONS:
        1. FIRST, carefully analyze the app code to understand what components ACTUALLY exist in the app
        2. Extract a precise list of all component IDs present in the app code
        3. IGNORE any criteria that reference UI components or IDs that don't exist in the actual app code
        4. ONLY evaluate based on specific criteria that match components in the actual app
        5. DO NOT add your own criteria or suggestions beyond what is explicitly stated
        6. DO NOT penalize for missing features that are not mentioned in the criteria OR don't exist in the app
        7. For non-Shiny frameworks (R Shiny, Streamlit, etc.), the test code should be empty - grade as Complete if empty
        8. If test_code tests components that are actually in the app, it should get a 'C' grade even if it doesn't test components mentioned in the criteria that don't exist in the app

        EVALUATION PROCESS:
        - First carefully extract all component IDs from the app code (e.g., "action_button", "checkbox", etc.)
        - Compare these IDs with those mentioned in the criteria
        - ONLY evaluate criteria for components that actually exist in the app code
        - COMPLETELY IGNORE criteria about components that don't exist in the app
        - Grade based ONLY on how well the test code tests the components that actually exist

        MOST IMPORTANT:
        - If the app does not contain a component mentioned in the criteria, IGNORE that part of the criteria completely
        - If the app uses a different ID than what's in the criteria (e.g., "data_grid" instead of "data_table"), use the actual ID from the app

        GRADING SCALE:
        - C (Complete): ALL criteria for EXISTING components are met
        - P (Partial): MOST criteria for EXISTING components are met, with minor gaps
        - I (Incomplete): MAJOR criteria for EXISTING components are missing or incorrectly implemented

        Provide your evaluation in the following format:
        GRADE: [C/P/I]
        Explanation: [Brief explanation focusing ONLY on how well the specified criteria were met for EXISTING components]
        """,
        grade_pattern=r"GRADE:\s*([CPI])",
        model=get_model("openai/gpt-5-nano-2025-08-07"),
    )

    return Task(
        dataset=samples,
        solver=generate(),
        scorer=scorer,
        model=get_model("openai/gpt-5-nano-2025-08-07"),
    )
