from __future__ import annotations

import ast
import importlib
import inspect
import json
import textwrap
from typing import Any

import click


def _resolve_symbol(name: str) -> tuple[Any, str]:
    parts = name.split(".")
    for i in range(len(parts), 0, -1):
        mod_name = ".".join(parts[:i])
        attr_parts = parts[i:]
        try:
            mod = importlib.import_module(mod_name)
            curr: Any = mod
            for attr in attr_parts:
                curr = getattr(curr, attr)
            return curr, name
        except (ImportError, AttributeError):
            pass

    if not name.startswith("shiny."):
        try:
            return _resolve_symbol("shiny." + name)
        except Exception:
            pass

    for prefix in [
        "shiny.ui",
        "shiny.express.ui",
        "shiny.playwright.controller",
        "shiny.reactive",
        "shiny.render",
        "shiny.session",
        "shiny.types",
    ]:
        try:
            mod = importlib.import_module(prefix)
            if hasattr(mod, name):
                return getattr(mod, name), f"{prefix}.{name}"
        except Exception:
            pass

    raise click.ClickException(f"Could not find documentation for '{name}'.")


def _extract_function_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> tuple[str, str | None, list[dict[str, Any]]]:
    fn_prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
    args_str = ast.unparse(node.args)
    return_type = ast.unparse(node.returns) if node.returns else None
    ret_str = f" -> {return_type}" if return_type else ""
    sig_str = f"{fn_prefix}{node.name}({args_str}){ret_str}:"

    parameters: list[dict[str, Any]] = []
    for a in node.args.posonlyargs:
        parameters.append(
            {
                "name": a.arg,
                "type": ast.unparse(a.annotation) if a.annotation else None,
                "default": None,
                "kind": "POSITIONAL_ONLY",
            }
        )

    pos_args = node.args.args
    num_defaults = len(node.args.defaults)
    defaults_offset = len(pos_args) - num_defaults
    for idx, a in enumerate(pos_args):
        d_val = (
            ast.unparse(node.args.defaults[idx - defaults_offset])
            if idx >= defaults_offset
            else None
        )
        parameters.append(
            {
                "name": a.arg,
                "type": ast.unparse(a.annotation) if a.annotation else None,
                "default": d_val,
                "kind": "POSITIONAL_OR_KEYWORD",
            }
        )

    if node.args.vararg:
        parameters.append(
            {
                "name": "*" + node.args.vararg.arg,
                "type": (
                    ast.unparse(node.args.vararg.annotation)
                    if node.args.vararg.annotation
                    else None
                ),
                "default": None,
                "kind": "VAR_POSITIONAL",
            }
        )

    for idx, a in enumerate(node.args.kwonlyargs):
        d_node = node.args.kw_defaults[idx]
        d_val = ast.unparse(d_node) if d_node else None
        parameters.append(
            {
                "name": a.arg,
                "type": ast.unparse(a.annotation) if a.annotation else None,
                "default": d_val,
                "kind": "KEYWORD_ONLY",
            }
        )

    if node.args.kwarg:
        parameters.append(
            {
                "name": "**" + node.args.kwarg.arg,
                "type": (
                    ast.unparse(node.args.kwarg.annotation)
                    if node.args.kwarg.annotation
                    else None
                ),
                "default": None,
                "kind": "VAR_KEYWORD",
            }
        )

    return sig_str, return_type, parameters


def _parse_method_info(method: Any, method_name: str) -> dict[str, Any]:
    unwrapped = inspect.unwrap(method)
    sig_str: str | None = None
    return_type: str | None = None
    parameters: list[dict[str, Any]] = []

    try:
        source = textwrap.dedent(inspect.getsource(unwrapped))
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sig_str, return_type, parameters = _extract_function_signature(node)
                break
    except Exception:
        pass

    if not sig_str:
        try:
            sig = inspect.signature(method)
            sig_str = f"def {method_name}{sig}:"
        except Exception:
            sig_str = f"def {method_name}(...):"

    doc = inspect.getdoc(unwrapped) or inspect.getdoc(method) or ""
    return {
        "name": method_name,
        "signature": sig_str,
        "return_type": return_type,
        "parameters": parameters,
        "docstring": doc,
    }


def _parse_class_info(cls: Any, full_name: str) -> dict[str, Any]:
    unwrapped = inspect.unwrap(cls)
    bases_str = ""
    try:
        source = textwrap.dedent(inspect.getsource(unwrapped))
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = ", ".join(ast.unparse(b) for b in node.bases)
                bases_str = f"({bases})" if bases else ""
                break
    except Exception:
        pass

    sig_str = f"class {cls.__name__}{bases_str}:"
    doc = inspect.getdoc(unwrapped) or inspect.getdoc(cls) or ""

    methods: list[dict[str, Any]] = []
    for m_name in dir(cls):
        if not m_name.startswith("_"):
            try:
                m = getattr(cls, m_name)
                if callable(m):
                    methods.append(_parse_method_info(m, m_name))
            except Exception:
                pass

    return {
        "name": full_name,
        "signature": sig_str,
        "type": "class",
        "return_type": None,
        "parameters": [],
        "docstring": doc,
        "methods": methods,
    }


def _parse_routine_info(func: Any, full_name: str) -> dict[str, Any]:
    unwrapped = inspect.unwrap(func)
    sig_str: str | None = None
    return_type: str | None = None
    parameters: list[dict[str, Any]] = []

    try:
        source = textwrap.dedent(inspect.getsource(unwrapped))
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sig_str, return_type, parameters = _extract_function_signature(node)
                break
    except Exception:
        pass

    if not sig_str:
        try:
            sig = inspect.signature(func)
            prefix = "def " if inspect.isroutine(func) else "class "
            obj_name = getattr(func, "__name__", full_name.split(".")[-1])
            sig_str = f"{prefix}{obj_name}{sig}:"
        except Exception:
            sig_str = f"{full_name}:"

    doc = inspect.getdoc(unwrapped) or inspect.getdoc(func) or ""
    return {
        "name": full_name,
        "signature": sig_str,
        "type": "function",
        "return_type": return_type,
        "parameters": parameters,
        "docstring": doc,
    }


def _get_doc_info(obj: Any, full_name: str) -> dict[str, Any]:
    if inspect.isclass(obj):
        return _parse_class_info(obj, full_name)
    return _parse_routine_info(obj, full_name)


def _format_text_doc(info: dict[str, Any]) -> str:
    lines: list[str] = [info["signature"]]
    if info.get("docstring"):
        lines.append(info["docstring"])

    if info.get("methods"):
        method_lines: list[str] = []
        for m in info["methods"]:
            m_header = m["signature"]
            m_doc = m.get("docstring", "").strip()
            if m_doc:
                first_para = m_doc.split("\n\n")[0]
                method_lines.append(f"{m_header}\n    {first_para}")
            else:
                method_lines.append(m_header)
        if method_lines:
            lines.append("\nMethods\n-------\n" + "\n\n".join(method_lines))

    return "\n".join(lines)


@click.command(
    "docs",
    help="Look up documentation and signatures for Shiny functions and controllers.",
)
@click.argument("names", nargs=-1, required=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Output documentation in JSON format.",
)
def docs(names: tuple[str, ...], as_json: bool) -> None:
    results: list[dict[str, Any]] = []
    for name in names:
        obj, full_name = _resolve_symbol(name)
        info = _get_doc_info(obj, full_name)
        results.append(info)

    if as_json:
        click.echo(json.dumps(results, indent=2))
    else:
        text_blocks = [_format_text_doc(r) for r in results]
        click.echo("\n\n---\n\n".join(text_blocks))
