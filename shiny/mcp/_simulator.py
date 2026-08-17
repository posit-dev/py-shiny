from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, cast

from .._app import App
from .._connection import MockConnection
from ..express import is_express_app
from ..express._run import wrap_express_app
from ..session._session import AppSession


async def simulate_shiny_app(
    code: Optional[str] = None,
    file_path: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    timeout_secs: float = 3.0,
) -> Dict[str, Any]:
    old_testmode = os.environ.get("SHINY_TESTMODE")
    os.environ["SHINY_TESTMODE"] = "1"

    temp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
    try:
        if code is not None:
            temp_dir = tempfile.TemporaryDirectory()
            temp_path = Path(temp_dir.name) / "app.py"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(code)
            target_path = temp_path
        elif file_path is not None:
            target_path = Path(file_path).resolve()
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "traceback": "",
                    "outputs": {},
                    "errors": {},
                    "exports": {},
                    "rendered_ui": None,
                }
        else:
            return {
                "success": False,
                "error": "Either 'code' or 'file_path' must be provided.",
                "traceback": "",
                "outputs": {},
                "errors": {},
                "exports": {},
                "rendered_ui": None,
            }

        app_obj: Optional[App] = None
        try:
            if is_express_app(str(target_path), app_dir=None):
                app_obj = wrap_express_app(target_path)
            else:
                module_name = f"_shiny_mcp_sim_{os.path.basename(str(target_path)).replace('.', '_')}_{id(target_path)}"
                import importlib.util

                spec = importlib.util.spec_from_file_location(module_name, target_path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Cannot load module from {target_path}")
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)

                if hasattr(mod, "app") and isinstance(mod.app, App):
                    app_obj = mod.app
                elif hasattr(mod, "app_ui") and hasattr(mod, "server"):
                    app_obj = App(mod.app_ui, mod.server)
                else:
                    for val in mod.__dict__.values():
                        if isinstance(val, App):
                            app_obj = val
                            break

                if app_obj is None:
                    return {
                        "success": False,
                        "error": "No Shiny 'App' instance found in module (expected 'app' or 'app_ui' + 'server').",
                        "traceback": "",
                        "outputs": {},
                        "errors": {},
                        "exports": {},
                        "rendered_ui": None,
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed during app load: {type(e).__name__}: {e}",
                "traceback": traceback.format_exc(),
                "outputs": {},
                "errors": {},
                "exports": {},
                "rendered_ui": None,
            }

        conn = MockConnection()
        session: AppSession = app_obj._create_session(conn)

        initial_inputs = dict(inputs or {})

        async def driver():
            conn.cause_receive(json.dumps({"method": "init", "data": initial_inputs}))
            await asyncio.sleep(0.05)

            unhide_data: Dict[str, Any] = {}
            for out_name in session.output._outputs.keys():
                unhide_data[f".clientdata_output_{out_name}_hidden"] = False

            if unhide_data:
                conn.cause_receive(
                    json.dumps({"method": "update", "data": unhide_data})
                )
                await asyncio.sleep(0.05)

            conn.cause_disconnect()

        try:
            await asyncio.wait_for(
                asyncio.gather(driver(), session._run()),
                timeout=timeout_secs,
            )
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Simulation timed out after {timeout_secs}s. The app may have blocking operations or an infinite loop.",
                "traceback": "",
                "outputs": {},
                "errors": {},
                "exports": {},
                "rendered_ui": None,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Runtime error during session execution: {type(e).__name__}: {e}",
                "traceback": traceback.format_exc(),
                "outputs": {},
                "errors": {},
                "exports": {},
                "rendered_ui": None,
            }

        outputs = dict(session._outbound_message_queues.test_values)
        errors = dict(session._outbound_message_queues.test_errors)
        exports: Dict[str, Any] = {}
        test_values_dict: Any = getattr(session, "_test_values", None)
        if isinstance(test_values_dict, dict):
            typed_values: Dict[str, Any] = cast(Dict[str, Any], test_values_dict)
            for k, fn in typed_values.items():
                try:
                    exports[k] = fn() if callable(fn) else fn
                except Exception as e:
                    exports[k] = f"<Error evaluating export {k}: {e}>"

        rendered_ui: Optional[str] = None
        rendered_attr = getattr(app_obj, "_rendered_ui", None)
        if rendered_attr is not None:
            try:
                rendered_ui = str(rendered_attr)
            except Exception:
                pass

        return {
            "success": len(errors) == 0,
            "error": (
                None
                if len(errors) == 0
                else f"{len(errors)} reactive error(s) occurred"
            ),
            "traceback": "",
            "outputs": outputs,
            "errors": errors,
            "exports": exports,
            "rendered_ui": rendered_ui,
        }

    finally:
        if old_testmode is None:
            os.environ.pop("SHINY_TESTMODE", None)
        else:
            os.environ["SHINY_TESTMODE"] = old_testmode

        if temp_dir is not None:
            try:
                temp_dir.cleanup()
            except Exception:
                pass
