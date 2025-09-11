# Scripts Directory

This directory contains scripts for processing documentation, evaluation results, and quality gating for the Shiny test generator.

## Scripts Overview

### `process_docs.py`

Converts XML documentation to structured JSON format for use in test generation. This script extracts API documentation and formats it for consumption by the Shiny test generator's AI models.

**Usage:**

```bash
python process_docs.py input.xml output.json
python process_docs.py --input docs.xml --output result.json
```

**Purpose:**

- Parses XML documentation files
- Extracts method names, descriptions, and API details
- Converts to structured JSON format
- Prepares documentation data for AI model training/reference

### `process_results.py`

Processes evaluation results from Inspect AI and generates performance summaries for the Shiny test generator.

**Usage:**

```bash
python process_results.py <path_to_result_file.json>
```

**Purpose:**

- Analyzes test generation evaluation results
- Categorizes tests as complete, partial, or incomplete
- Calculates pass rates and performance metrics
- Generates summary reports in JSON format
- Provides detailed statistics on test generator performance

### `quality_gate.py`

Performs quality gate validation on evaluation results to ensure the Shiny test generator meets required performance standards.

**Usage:**

```bash
python quality_gate.py <results_dir>
```

**Purpose:**

- Checks if evaluation results meet minimum quality thresholds (default: 80%)
- Validates test generator performance against benchmarks
- Provides pass/fail status for CI/CD pipelines
- Ensures quality standards before deployment or release

## Workflow

The typical workflow for using these scripts:

1. **Documentation Processing**: Use `process_docs.py` to convert API documentation into structured format
2. **Evaluation**: Run test generation evaluations (external process)
3. **Results Processing**: Use `process_results.py` to analyze evaluation outcomes
4. **Quality Gate**: Use `quality_gate.py` to validate performance meets standards
