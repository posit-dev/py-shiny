# Shiny Testing Framework

This directory contains the comprehensive testing framework for Shiny applications, including AI-powered test generation, evaluation tools, and utility scripts.

## Components

### 1. Generator (`generator/`)

The core AI-powered test generation system that creates comprehensive test files for Shiny applications.

**Key Features:**

- Support for multiple AI providers (Anthropic, OpenAI)
- Model selection and configuration
- Template-based test generation
- File and code-based input processing

**Usage:**

```python
from shiny.testing import ShinyTestGenerator

generator = ShinyTestGenerator(provider="anthropic")
test_code, test_file = generator.generate_test_from_file("app.py")
```

### 2. Evaluation (`evaluation/`)

Framework for evaluating the performance and quality of the test generator.

**Components:**

- **apps/**: Collection of diverse Shiny applications for testing
- **scripts/**: Evaluation execution and metadata management
- **results/**: Storage for evaluation outcomes and analysis

**Usage:**

```bash
python evaluation/scripts/evaluation.py
```

### 3. Utils (`utils/`)

Utility tools for processing documentation, analyzing results, and quality gating.

**Key Scripts:**

- `process_docs.py`: Convert XML documentation to JSON format
- `process_results.py`: Analyze evaluation results and generate summaries
- `quality_gate.py`: Validate performance against quality thresholds

## CLI Integration

The test generator is integrated into the Shiny CLI:

```bash
# Generate test with interactive prompts
shiny generate test

# Generate test with specific parameters
shiny generate test --app app.py --output test_app.py --provider anthropic

# Use different models
shiny generate test --app app.py --provider openai --model gpt-4.1-nano
```

## Getting Started

1. **Install Dependencies**: Ensure you have the required AI provider SDKs and API keys
2. **Generate Tests**: Use the CLI or Python API to generate tests
3. **Run Evaluations**: Use the evaluation framework to assess generator performance
4. **Quality Control**: Use utility scripts for processing and validation

## Development Workflow

1. **Add Test Apps**: Place new evaluation apps in `evaluation/apps/`
2. **Update Documentation**: Modify `generator/data/docs/` for API changes
3. **Run Evaluations**: Execute evaluation scripts to test performance
4. **Process Results**: Use utility scripts to analyze outcomes
5. **Quality Gate**: Validate results meet quality standards
