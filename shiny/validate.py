"""Static Shiny validation, including typed results and extensible AST visitors.

Subclass ``ShinyCodeValidator`` and pass it as ``validator_class`` to
``validate_shiny_code`` or ``validate_shiny_file`` to include project rules::

    import ast
    from shiny.validate import ShinyCodeValidator, validate_shiny_code

    class ProjectValidator(ShinyCodeValidator):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                self.result.add_warning(node.lineno, "Use logging", "PROJECT_LOGGING")
            super().visit_Call(node)

    result = validate_shiny_code(source, validator_class=ProjectValidator)
    report = result.to_dict()

For intentional exceptions, use ``# shiny: ignore`` on the diagnostic line or
``# shiny: ignore-next-line`` on the preceding line. Add comma-separated rule
codes to ignore only those rules (for example, ``# shiny: ignore UNCALLED_INPUT``).
These directives work in ``shiny validate``, startup validation, and the Shiny
VS Code extension. Runtime errors still enforce Shiny's input/output contracts.
"""

from ._validate import (
    ShinyCodeValidator,
    ValidateResult,
    ValidationIssue,
    ValidationReport,
    validate_shiny_code,
    validate_shiny_file,
)

__all__ = [
    "ShinyCodeValidator",
    "ValidateResult",
    "ValidationIssue",
    "ValidationReport",
    "validate_shiny_code",
    "validate_shiny_file",
]
