from __future__ import annotations

import ast
import difflib
import functools
import importlib
import inspect
import json
import operator
import pkgutil
import sys
import textwrap
import warnings
from collections.abc import Iterator
from types import ModuleType
from typing import Any, Literal

import click
from click.shell_completion import CompletionItem

from .._typing_extensions import TypedDict


class _ParameterInfo(TypedDict):
    name: str
    type: str | None
    default: str | None
    kind: Literal[
        "POSITIONAL_ONLY",
        "POSITIONAL_OR_KEYWORD",
        "VAR_POSITIONAL",
        "KEYWORD_ONLY",
        "VAR_KEYWORD",
    ]


class _MethodInfo(TypedDict):
    name: str
    signature: str
    return_type: str | None
    parameters: list[_ParameterInfo]
    docstring: str


class _RoutineInfo(_MethodInfo):
    type: Literal["function"]


class _ClassInfo(_MethodInfo):
    type: Literal["class"]
    bases: list[str]
    methods: list[_MethodInfo]


class _ModuleInfo(TypedDict):
    name: str
    signature: str
    type: Literal["module"]
    docstring: str
    members: list[str]


_DocInfo = _RoutineInfo | _ClassInfo | _ModuleInfo

# Errors raised by `inspect.getsource()` (no source available, e.g. builtins or
# objects defined interactively) and by `ast.parse()` on the dedented snippet.
_SOURCE_ERRORS = (OSError, TypeError, SyntaxError)


def _iter_public_modules(package: ModuleType) -> Iterator[ModuleType]:
    yield package
    for module_info in pkgutil.iter_modules(
        getattr(package, "__path__", []), prefix=f"{package.__name__}."
    ):
        if module_info.name.rsplit(".", 1)[-1].startswith("_"):
            continue
        try:
            with warnings.catch_warnings():
                # Deprecated import paths (e.g. `shiny.express.layout`) warn with
                # ImportWarning; treat that as "not a public module".
                warnings.simplefilter("error", ImportWarning)
                module = importlib.import_module(module_info.name)
        except (ImportError, ImportWarning):
            # Skip unavailable optional modules and deprecated import paths.
            continue
        if module_info.ispkg:
            yield from _iter_public_modules(module)
        else:
            yield module


def _defining_package(obj: Any) -> str | None:
    """Top-level package of the module that defines ``obj``, if known."""
    module = getattr(inspect.unwrap(obj), "__module__", None)
    return module.split(".")[0] if module else None


def _public_names(mod: ModuleType) -> list[str]:
    """Public attribute names of a module, honoring ``__all__`` when defined.

    Without ``__all__``, only objects defined inside the ``shiny`` package count
    as public; names like ``Path`` that a module merely imports are skipped.
    """
    # Read `__dict__` directly: modules with a module-level `__getattr__` (e.g.
    # `shiny.express.app`) may raise on an unknown dunder lookup.
    all_names = vars(mod).get("__all__")
    if all_names is not None:
        return [str(name) for name in all_names]
    return [
        name
        for name, obj in vars(mod).items()
        if not name.startswith("_") and _defining_package(obj) == "shiny"
    ]


def _is_documentable_method(obj: Any) -> bool:
    """Whether a class attribute is a method worth listing.

    Methods inherited from builtins or the standard library (e.g. the ``str``
    methods of :class:`~shiny.ui.HTML`, via ``UserString``) are excluded: they
    carry no Shiny documentation and drown out the useful entries in completion
    and "did you mean" suggestions.
    """
    if not callable(obj):
        return False
    package = _defining_package(obj)
    return package is not None and package not in sys.stdlib_module_names


def _public_methods(cls: type) -> list[tuple[str, Any]]:
    methods: list[tuple[str, Any]] = []
    for m_name in dir(cls):
        if m_name.startswith("_"):
            continue
        try:
            m_obj = getattr(cls, m_name)
        except AttributeError:
            # `dir()` can list names whose descriptor refuses class-level access.
            continue
        if _is_documentable_method(m_obj):
            methods.append((m_name, m_obj))
    return methods


@functools.lru_cache(maxsize=1)
def _get_all_documentable_symbols() -> list[str]:
    symbols: set[str] = set()
    for mod in _iter_public_modules(importlib.import_module("shiny")):
        full_mod = mod.__name__
        short_mod = full_mod.removeprefix("shiny").lstrip(".")
        short_prefix = f"{short_mod}." if short_mod else ""
        symbols.add(full_mod)
        if short_mod:
            symbols.add(short_mod)
        for attr in _public_names(mod):
            obj = getattr(mod, attr, None)
            if obj is None or not (inspect.isroutine(obj) or inspect.isclass(obj)):
                continue
            symbols.add(f"{full_mod}.{attr}")
            symbols.add(f"{short_prefix}{attr}")
            if inspect.isclass(obj):
                for m_name, _ in _public_methods(obj):
                    symbols.add(f"{full_mod}.{attr}.{m_name}")
                    symbols.add(f"{short_prefix}{attr}.{m_name}")
    return sorted(symbols)


def _suggest_similar_symbols(name: str, max_suggestions: int = 3) -> list[str]:
    symbols = _get_all_documentable_symbols()
    candidates = (
        [s for s in symbols if s.startswith("shiny.")]
        if name.startswith("shiny.")
        else [s for s in symbols if not s.startswith("shiny.")]
    )

    name_lower = name.lower()
    name_parts = name_lower.split(".")
    target_attr = name_parts[-1]

    if len(name_parts) > 1:
        prefix_parts = name_parts[:-1]
        same_prefix = [
            c for c in candidates if c.lower().split(".")[:-1] == prefix_parts
        ]
        if same_prefix:
            scored_same: list[tuple[float, str]] = []
            for cand in same_prefix:
                cand_attr = cand.lower().split(".")[-1]
                score = difflib.SequenceMatcher(None, target_attr, cand_attr).ratio()
                if score >= 0.55:
                    scored_same.append((score, cand))
            if scored_same:
                scored_same.sort(key=operator.itemgetter(0), reverse=True)
                top = scored_same[0][0]
                if len(scored_same) == 1 or (
                    top >= 0.8 and (top - scored_same[1][0]) >= 0.12
                ):
                    return [scored_same[0][1]]
                filtered = [
                    cand for s, cand in scored_same if s >= max(0.6, top - 0.15)
                ]
                return filtered[:max_suggestions]

    scored: list[tuple[float, str]] = []
    for cand in candidates:
        cand_lower = cand.lower()
        cand_parts = cand_lower.split(".")
        cand_attr = cand_parts[-1]

        if len(name_parts) == 1:
            if cand_attr == target_attr:
                score = 1.0
            elif cand_lower.endswith(f".{name_lower}"):
                score = 0.95
            else:
                score = difflib.SequenceMatcher(None, name_lower, cand_attr).ratio()
        else:
            full_ratio = difflib.SequenceMatcher(None, name_lower, cand_lower).ratio()
            attr_ratio = difflib.SequenceMatcher(None, target_attr, cand_attr).ratio()

            if cand_lower.endswith(f".{name_lower}"):
                score = 0.95
            else:
                score = 0.5 * full_ratio + 0.5 * attr_ratio

        if score >= 0.55:
            scored.append((score, cand))

    if not scored:
        return []

    scored.sort(key=operator.itemgetter(0), reverse=True)

    top_score = scored[0][0]
    if len(scored) == 1 or (top_score >= 0.85 and (top_score - scored[1][0]) >= 0.12):
        return [scored[0][1]]

    filtered = [cand for s, cand in scored if s >= max(0.6, top_score - 0.15)]
    return filtered[:max_suggestions]


def _not_found(name: str) -> click.ClickException:
    suggestions = _suggest_similar_symbols(name)
    if not suggestions:
        return click.ClickException(f"Could not find documentation for '{name}'.")
    if len(suggestions) == 1:
        return click.ClickException(
            f"Could not find documentation for '{name}'. Did you mean '{suggestions[0]}'?"
        )
    formatted = ", ".join(f"'{s}'" for s in suggestions)
    return click.ClickException(
        f"Could not find documentation for '{name}'. Did you mean one of: {formatted}?"
    )


def _resolve_symbol(name: str) -> tuple[Any, str]:
    def _try_resolve(target_name: str) -> Any | None:
        parts = target_name.split(".")
        for i in range(len(parts), 0, -1):
            mod_name = ".".join(parts[:i])
            attr_parts = parts[i:]
            try:
                mod = importlib.import_module(mod_name)
                curr: Any = mod
                for attr in attr_parts:
                    curr = getattr(curr, attr)
                return curr
            except (ImportError, AttributeError):
                pass
        return None

    full_name = name if name.startswith("shiny.") else f"shiny.{name}"
    obj = _try_resolve(full_name)
    if obj is None:
        raise _not_found(name)
    if not (inspect.ismodule(obj) or inspect.isclass(obj) or callable(obj)):
        raise click.ClickException(
            f"'{name}' is not a function, class, or module "
            f"(it is an instance of {type(obj).__name__})."
        )
    return obj, full_name


def _complete_symbol_names(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[CompletionItem]:
    symbols = _get_all_documentable_symbols()
    inc = incomplete.lower()
    return [CompletionItem(s) for s in symbols if s.lower().startswith(inc)]


def _format_signature(
    prefix: str,
    name: str,
    parameters: list[_ParameterInfo],
    return_type: str | None,
) -> str:
    """Render a PEP 8 style signature line from parsed parameters.

    ``ast.unparse`` writes ``x: int=None``; this writes ``x: int = None`` (and
    ``x=None`` when there is no annotation), inserting the ``/`` and ``*``
    markers where they belong.
    """
    parts: list[str] = []
    kinds = [p["kind"] for p in parameters]
    for idx, p in enumerate(parameters):
        if p["kind"] == "KEYWORD_ONLY" and (
            "VAR_POSITIONAL" not in kinds and "KEYWORD_ONLY" not in kinds[:idx]
        ):
            parts.append("*")
        part = p["name"]
        if p["type"] is not None:
            part += f": {p['type']}"
        if p["default"] is not None:
            part += (
                f" = {p['default']}" if p["type"] is not None else f"={p['default']}"
            )
        parts.append(part)
        if p["kind"] == "POSITIONAL_ONLY" and (
            idx + 1 == len(kinds) or kinds[idx + 1] != "POSITIONAL_ONLY"
        ):
            parts.append("/")
    ret_str = f" -> {return_type}" if return_type else ""
    return f"{prefix}{name}({', '.join(parts)}){ret_str}:"


def _extract_parameters(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[_ParameterInfo]:
    def annotation(a: ast.arg) -> str | None:
        return ast.unparse(a.annotation) if a.annotation else None

    parameters: list[_ParameterInfo] = []
    args = node.args

    positional = [*args.posonlyargs, *args.args]
    defaults_offset = len(positional) - len(args.defaults)
    for idx, a in enumerate(positional):
        default = (
            ast.unparse(args.defaults[idx - defaults_offset])
            if idx >= defaults_offset
            else None
        )
        parameters.append(
            {
                "name": a.arg,
                "type": annotation(a),
                "default": default,
                "kind": (
                    "POSITIONAL_ONLY"
                    if idx < len(args.posonlyargs)
                    else "POSITIONAL_OR_KEYWORD"
                ),
            }
        )

    if args.vararg:
        parameters.append(
            {
                "name": "*" + args.vararg.arg,
                "type": annotation(args.vararg),
                "default": None,
                "kind": "VAR_POSITIONAL",
            }
        )

    for a, d_node in zip(args.kwonlyargs, args.kw_defaults):
        parameters.append(
            {
                "name": a.arg,
                "type": annotation(a),
                "default": ast.unparse(d_node) if d_node else None,
                "kind": "KEYWORD_ONLY",
            }
        )

    if args.kwarg:
        parameters.append(
            {
                "name": "**" + args.kwarg.arg,
                "type": annotation(args.kwarg),
                "default": None,
                "kind": "VAR_KEYWORD",
            }
        )

    return parameters


def _source_node(obj: Any) -> ast.stmt | None:
    """The AST node of ``obj``'s own definition, or ``None`` if unavailable."""
    try:
        source = textwrap.dedent(inspect.getsource(inspect.unwrap(obj)))
        tree = ast.parse(source)
    except _SOURCE_ERRORS:
        return None
    return tree.body[0] if tree.body else None


def _parse_callable(
    func: Any, display_name: str
) -> tuple[str, str | None, list[_ParameterInfo]]:
    """Signature line, return type, and parameters of a function or method.

    Parsed from source so annotations and defaults read as written; falls back
    to :func:`inspect.signature` for callables without Python source.
    """
    node = _source_node(func)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
        return_type = ast.unparse(node.returns) if node.returns else None
        parameters = _extract_parameters(node)
        return (
            _format_signature(prefix, node.name, parameters, return_type),
            (return_type),
            parameters,
        )

    try:
        sig = inspect.signature(func)
    except (TypeError, ValueError):
        return f"def {display_name}(...):", None, []
    return f"def {display_name}{sig}:", None, []


def _docstring(obj: Any) -> str:
    return inspect.getdoc(inspect.unwrap(obj)) or inspect.getdoc(obj) or ""


def _parse_method_info(method: Any, method_name: str) -> _MethodInfo:
    sig_str, return_type, parameters = _parse_callable(method, method_name)
    return {
        "name": method_name,
        "signature": sig_str,
        "return_type": return_type,
        "parameters": parameters,
        "docstring": _docstring(method),
    }


def _parse_class_info(cls: type, full_name: str) -> _ClassInfo:
    node = _source_node(cls)
    bases = (
        [ast.unparse(b) for b in node.bases] if isinstance(node, ast.ClassDef) else []
    )

    # The class signature is its constructor's, minus `self`, so that
    # `render.plot(alt=..., width=...)` and `Accordion(page, id)` read as called.
    parameters: list[_ParameterInfo] = []
    init = getattr(cls, "__init__", None)
    if init is not None and init is not object.__init__:
        _, _, parameters = _parse_callable(init, "__init__")
        parameters = parameters[1:] if parameters else []
    sig_str = _format_signature("class ", cls.__name__, parameters, None)

    return {
        "name": full_name,
        "signature": sig_str,
        "type": "class",
        "bases": bases,
        "return_type": None,
        "parameters": parameters,
        "docstring": _docstring(cls),
        "methods": [
            _parse_method_info(m, m_name) for m_name, m in _public_methods(cls)
        ],
    }


def _parse_routine_info(func: Any, full_name: str) -> _RoutineInfo:
    sig_str, return_type, parameters = _parse_callable(func, full_name.split(".")[-1])
    return {
        "name": full_name,
        "signature": sig_str,
        "type": "function",
        "return_type": return_type,
        "parameters": parameters,
        "docstring": _docstring(func),
    }


def _parse_module_info(mod: ModuleType, full_name: str) -> _ModuleInfo:
    members = [
        name
        for name in _public_names(mod)
        if (obj := getattr(mod, name, None)) is not None
        and (inspect.isroutine(obj) or inspect.isclass(obj) or inspect.ismodule(obj))
    ]
    return {
        "name": full_name,
        "signature": f"module {mod.__name__}:",
        "type": "module",
        "docstring": inspect.getdoc(mod) or "",
        "members": members,
    }


def _get_doc_info(obj: Any, full_name: str) -> _DocInfo:
    if inspect.ismodule(obj):
        return _parse_module_info(obj, full_name)
    if inspect.isclass(obj):
        return _parse_class_info(obj, full_name)
    return _parse_routine_info(obj, full_name)


def _format_text_doc(info: _DocInfo) -> str:
    lines: list[str] = [info["signature"]]
    if info["type"] == "class" and info["bases"]:
        lines[0] += f"  # bases: {', '.join(info['bases'])}"
    if info["docstring"]:
        lines.append(info["docstring"])

    if info["type"] == "module" and info["members"]:
        lines.append("\nMembers\n-------\n" + "\n".join(info["members"]))

    if info["type"] == "class" and info["methods"]:
        method_lines: list[str] = []
        for m in info["methods"]:
            m_doc = m["docstring"].strip()
            if m_doc:
                first_para = m_doc.split("\n\n")[0]
                method_lines.append(f"{m['signature']}\n    {first_para}")
            else:
                method_lines.append(m["signature"])
        lines.append("\nMethods\n-------\n" + "\n\n".join(method_lines))

    return "\n".join(lines)


@click.command(
    "docs",
    help="Look up documentation and signatures for Shiny functions and controllers.",
)
@click.argument(
    "names",
    nargs=-1,
    required=False,
    shell_complete=_complete_symbol_names,
)
@click.option(
    "--complete",
    "complete_prefix",
    type=str,
    default=None,
    help="Return autocomplete symbol matches for a prefix.",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Output documentation or completions in JSON format.",
)
@click.pass_context
def docs(
    ctx: click.Context,
    names: tuple[str, ...],
    complete_prefix: str | None,
    as_json: bool,
) -> None:
    if complete_prefix is not None:
        all_syms = _get_all_documentable_symbols()
        inc = complete_prefix.lower()
        prefix_matches = [s for s in all_syms if s.lower().startswith(inc)]
        other_matches = [
            s for s in all_syms if inc in s.lower() and not s.lower().startswith(inc)
        ]
        matches = prefix_matches + other_matches
        if as_json:
            click.echo(json.dumps(matches, indent=2))
        else:
            for m in matches:
                click.echo(m)
        return

    if not names:
        raise click.UsageError("Missing argument 'NAMES...'.")

    results: list[_DocInfo] = []
    errors: list[str] = []
    for name in names:
        try:
            obj, full_name = _resolve_symbol(name)
        except click.ClickException as e:
            errors.append(e.format_message())
            continue
        results.append(_get_doc_info(obj, full_name))

    for err_msg in errors:
        click.echo(f"Error: {err_msg}", err=True)

    if as_json:
        # Always emit valid JSON on stdout, even when every lookup failed.
        click.echo(json.dumps(results, indent=2))
    elif results:
        text_blocks = [_format_text_doc(r) for r in results]
        click.echo("\n\n---\n\n".join(text_blocks))

    if errors:
        ctx.exit(1)
