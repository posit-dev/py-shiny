"""Static Shiny validation, including typed results and extensible rules.

Packages contribute rules by registering a ``ValidationRule`` subclass, or a
``(tree, result) -> None`` callable, under the ``shiny.validators`` entry-point
group. ``shiny validate``, ``shiny run`` and ``validate_shiny_code`` run every
installed rule over the same parsed tree::

    # pyproject.toml
    [project.entry-points."shiny.validators"]
    mypkg = "mypkg.validation:NoPrintRule"

    # mypkg/validation.py
    import ast
    from shiny.validate import ValidationRule

    class NoPrintRule(ValidationRule):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                self.result.add_warning(node.lineno, "Use logging", "MYPKG_PRINT")
            self.generic_visit(node)

For one-off rules, run ``shiny validate app.py --validator module:attr``.
Subclassing ``ShinyCodeValidator`` and passing it as ``validator_class`` still
customizes the built-in rules.

``shiny validate app.py`` and ``validate_shiny_file()`` also inspect local Python
imports within the entry file's directory, without executing the app or its
imports. Each diagnostic includes its source ``file`` and ``line``. Installed
packages, dynamic imports, and unresolved imports are not inspected.
``validate_shiny_code()`` inspects only the supplied source string.

The built-in checks cover Shiny semantics only, not general Python mistakes
that pyright, pylance, or a linter already report (syntax errors, unknown
imports, redeclared names, or attribute access on a reactive object). Errors
are reads of an input, ``reactive.value``, or ``reactive.calc`` outside any
reactive context (at module level or directly in a server function body),
reads inside extended tasks, uncalled inputs, assignment to inputs, multiple
render decorators, and ``@reactive.event`` placed above the effect, calc, or
renderer it should wrap. Warnings are duplicate input/output IDs within one
scope, a Core-mode ``ui.output_*()`` with no renderer or a renderer with no
placeholder, an effect that returns a value, an effect that reads and sets
the same value without ``reactive.event`` or ``reactive.isolate()``, a calc
that sets a value, mutating an object and setting it back into the same
reactive value, and broad exception handlers that swallow extended-task
result errors. The checks recognize reactive constructors, calc decorators,
``reactive.Value`` parameter annotations, ``@output(id=)``, and
``reactive.isolate()`` blocks, including import aliases. Use ``--strict`` to
fail on warnings too. Static checks do not replace running the app and
testing its interactions.

For intentional exceptions, use ``# shiny: ignore`` on the diagnostic line or
``# shiny: ignore-next-line`` on the preceding line. Add comma-separated rule
codes to ignore only those rules (for example, ``# shiny: ignore UNCALLED_INPUT``).
These directives work in ``shiny validate`` and startup validation. Runtime
errors still enforce Shiny's input/output contracts.
"""

from ._validate import (
    VALIDATOR_ENTRY_POINT_GROUP,
    ShinyCodeValidator,
    ValidateResult,
    ValidationIssue,
    ValidationReport,
    ValidationRule,
    ValidationRuleFunc,
    ValidationRuleLike,
    installed_validation_rules,
    load_validation_rule,
    validate_shiny_code,
    validate_shiny_file,
)

__all__ = [
    "VALIDATOR_ENTRY_POINT_GROUP",
    "ShinyCodeValidator",
    "ValidateResult",
    "ValidationIssue",
    "ValidationReport",
    "ValidationRule",
    "ValidationRuleFunc",
    "ValidationRuleLike",
    "installed_validation_rules",
    "load_validation_rule",
    "validate_shiny_code",
    "validate_shiny_file",
]
