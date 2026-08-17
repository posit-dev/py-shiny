from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import subprocess
import time
from pathlib import Path

from shiny.mcp import simulate_shiny_app, validate_shiny_code

PROMPT = """Inspect and fix app.py. Ensure all KPI cards and the load table calculate cleanly without reactive or runtime errors. Once fixed, verify that the application computes correctly."""

REPO_ROOT = Path(__file__).parent.parent.resolve()
SOURCE_APP = REPO_ROOT / "examples" / "mcp_test_app" / "app.py"
EXP_DIR = REPO_ROOT / "examples" / "ab_experiment_workspace" / "opencode"

OPENCODE_MODELS = [
    ("Kimi K2.7 Code", "opencode-go/kimi-k2.7-code"),
    ("MiniMax - M2.7", "opencode-go/minimax-m2.7"),
    ("MiniMax - M3", "opencode-go/minimax-m3"),
    ("Qwen3.6 Plus", "opencode-go/qwen3.6-plus"),
    ("Qwen3.7 Max", "opencode-go/qwen3.7-max"),
]


def setup_workspace(tag: str) -> tuple[Path, Path]:
    work_dir = EXP_DIR / tag
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    ctrl_dir = work_dir / "control"
    treat_dir = work_dir / "treatment"
    ctrl_dir.mkdir()
    treat_dir.mkdir()

    shutil.copy(SOURCE_APP, ctrl_dir / "app.py")
    shutil.copy(SOURCE_APP, treat_dir / "app.py")

    # Control has empty MCP config
    (ctrl_dir / "opencode.json").write_text(
        json.dumps(
            {
                "$schema": "https://opencode.ai/config.json",
                "mcp": {},
            },
            indent=2,
        )
    )

    # Treatment has Shiny MCP config
    (treat_dir / "opencode.json").write_text(
        json.dumps(
            {
                "$schema": "https://opencode.ai/config.json",
                "mcp": {
                    "shiny": {
                        "type": "local",
                        "command": [
                            "uv",
                            "run",
                            "--directory",
                            str(REPO_ROOT),
                            "shiny",
                            "mcp",
                        ],
                        "enabled": True,
                    }
                },
            },
            indent=2,
        )
    )

    return ctrl_dir, treat_dir


def run_opencode_agent(workspace_dir: Path, model_name: str) -> dict[str, object]:
    start_time = time.time()
    try:
        proc = subprocess.run(
            [
                "opencode",
                "run",
                PROMPT,
                "-m",
                model_name,
                "--dir",
                str(workspace_dir),
                "--dangerously-skip-permissions",
            ],
            cwd=str(workspace_dir),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=240,
        )
        elapsed = round(time.time() - start_time, 2)
        stdout = proc.stdout
        stderr = proc.stderr
        exit_code = proc.returncode
    except subprocess.TimeoutExpired:
        elapsed = 240.0
        stdout = ""
        stderr = "Timeout expired (240s)"
        exit_code = -1
    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        stdout = ""
        stderr = str(e)
        exit_code = -1

    return {
        "elapsed_secs": elapsed,
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
    }


async def evaluate_app(app_path: Path) -> dict[str, object]:
    if not app_path.exists():
        return {
            "exists": False,
            "valid": False,
            "duplicate_id_fixed": False,
            "uncalled_input_fixed": False,
            "simulation_success": False,
            "error": "app.py not found",
        }

    code = app_path.read_text()
    val_res = validate_shiny_code(code)

    sim_res = await simulate_shiny_app(
        file_path=str(app_path),
        inputs={
            "bed_capacity": 200,
            "patient_volume": 150,
            "staff_ratio": 0.25,
            "surge_multiplier": 1.2,
            "fixed_overhead": 45,
        },
    )

    has_duplicate_id = any(
        w.get("code") == "DUPLICATE_ID" for w in val_res.get("warnings", [])
    )
    has_uncalled_input = any(
        w.get("code") == "UNCALLED_INPUT" for w in val_res.get("warnings", [])
    )

    return {
        "exists": True,
        "valid": val_res.get("valid", False),
        "duplicate_id_fixed": not has_duplicate_id,
        "uncalled_input_fixed": not has_uncalled_input,
        "simulation_success": sim_res.get("success", False),
        "outputs": sim_res.get("outputs", {}),
        "errors": sim_res.get("errors", {}),
    }


async def run_model_benchmark(display_name: str, model_id: str) -> dict[str, object]:
    tag = (
        model_id.replace("/", "_").replace(":", "_").replace("-", "_").replace(".", "_")
    )
    ctrl_dir, treat_dir = setup_workspace(tag)

    print(f"\n[{display_name}] Running Control (Skills Only / No MCP)...")
    ctrl_run = run_opencode_agent(ctrl_dir, model_name=model_id)
    print(
        f"  Control finished in {ctrl_run['elapsed_secs']}s (Exit code: {ctrl_run['exit_code']})"
    )

    print(f"[{display_name}] Running Treatment (With Shiny MCP)...")
    treat_run = run_opencode_agent(treat_dir, model_name=model_id)
    print(
        f"  Treatment finished in {treat_run['elapsed_secs']}s (Exit code: {treat_run['exit_code']})"
    )

    ctrl_eval = await evaluate_app(ctrl_dir / "app.py")
    treat_eval = await evaluate_app(treat_dir / "app.py")

    return {
        "model_name": display_name,
        "model_id": model_id,
        "ctrl_time": ctrl_run["elapsed_secs"],
        "treat_time": treat_run["elapsed_secs"],
        "ctrl_sim_ok": ctrl_eval["simulation_success"],
        "treat_sim_ok": treat_eval["simulation_success"],
        "ctrl_dup_fixed": ctrl_eval["duplicate_id_fixed"],
        "treat_dup_fixed": treat_eval["duplicate_id_fixed"],
        "ctrl_uncalled_fixed": ctrl_eval["uncalled_input_fixed"],
        "treat_uncalled_fixed": treat_eval["uncalled_input_fixed"],
    }


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run A/B experiment for OpenCode Go models comparing with vs without Shiny MCP."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Specific OpenCode model ID (e.g. 'opencode-go/qwen3.7-max').",
    )
    parser.add_argument(
        "--all-models",
        action="store_true",
        help="Run benchmark across all 5 OpenCode Go models.",
    )
    args = parser.parse_args()

    if args.all_models:
        target_models = OPENCODE_MODELS
    elif args.model:
        target_models = [(args.model, args.model)]
    else:
        target_models = OPENCODE_MODELS

    print("=" * 80)
    print("OPENCODE GO A/B BENCHMARK: Control (No MCP) vs Treatment (With Shiny MCP)")
    print(f"Target Models: {', '.join(name for name, _ in target_models)}")
    print("=" * 80)

    results = []
    for disp_name, model_id in target_models:
        res = await run_model_benchmark(disp_name, model_id)
        results.append(res)

    print("\n" + "=" * 80)
    print("OPENCODE A/B BENCHMARK SUMMARY")
    print("=" * 80)
    header = f"{'Model':<18} | {'Time (Ctrl/Treat)':<20} | {'Duplicate ID Fixed':<20} | {'Sim Success (C/T)':<18}"
    print(header)
    print("-" * 80)

    for r in results:
        time_str = f"{r['ctrl_time']}s / {r['treat_time']}s"
        dup_str = f"{'✅' if r['ctrl_dup_fixed'] else '❌'} / {'✅' if r['treat_dup_fixed'] else '❌'}"
        sim_str = f"{'✅' if r['ctrl_sim_ok'] else '❌'} / {'✅' if r['treat_sim_ok'] else '❌'}"
        print(f"{r['model_name']:<18} | {time_str:<20} | {dup_str:<20} | {sim_str:<18}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
