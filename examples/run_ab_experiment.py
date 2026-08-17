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
EXP_DIR = REPO_ROOT / "examples" / "ab_experiment_workspace"

DEFAULT_MODELS = [
    ("Sonnet 5", "claude-sonnet-5"),
    ("Opus 5", "claude-opus-5"),
    ("Haiku 4.5", "claude-haiku-4-5"),
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

    # Control has empty MCP config (skills only)
    (ctrl_dir / ".mcp.json").write_text(json.dumps({"mcpServers": {}}, indent=2))

    # Treatment has Shiny MCP config pointing to current repo
    (treat_dir / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "shiny": {
                        "command": "uv",
                        "args": [
                            "run",
                            "--directory",
                            str(REPO_ROOT),
                            "shiny",
                            "mcp",
                        ],
                    }
                }
            },
            indent=2,
        )
    )

    return ctrl_dir, treat_dir


def run_claude_agent(workspace_dir: Path, model_name: str) -> dict[str, object]:
    start_time = time.time()
    try:
        proc = subprocess.run(
            [
                "claude",
                "-p",
                PROMPT,
                "--model",
                model_name,
                "--dangerously-skip-permissions",
                "--output-format",
                "json",
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
        result_text = ""
        num_turns = 0
        total_cost = 0.0

        if stdout:
            try:
                data = json.loads(stdout)
                result_text = data.get("result", "")
                num_turns = data.get("num_turns", 0)
                total_cost = data.get("total_cost_usd", 0.0)
            except Exception:
                pass

    except subprocess.TimeoutExpired:
        elapsed = 240.0
        stdout = ""
        stderr = "Timeout expired (240s)"
        exit_code = -1
        result_text = ""
        num_turns = 0
        total_cost = 0.0
    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        stdout = ""
        stderr = str(e)
        exit_code = -1
        result_text = ""
        num_turns = 0
        total_cost = 0.0

    return {
        "elapsed_secs": elapsed,
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "result_text": result_text,
        "num_turns": num_turns,
        "total_cost": total_cost,
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
    tag = model_id.replace("/", "_").replace(":", "_").replace("-", "_")
    ctrl_dir, treat_dir = setup_workspace(tag)

    print(f"\n[{display_name}] Running Control (Skills Only)...")
    ctrl_run = run_claude_agent(ctrl_dir, model_name=model_id)
    print(
        f"  Control finished in {ctrl_run['elapsed_secs']}s (Turns: {ctrl_run['num_turns']}, Cost: ${ctrl_run['total_cost']:.4f})"
    )

    print(f"[{display_name}] Running Treatment (With Shiny MCP)...")
    treat_run = run_claude_agent(treat_dir, model_name=model_id)
    print(
        f"  Treatment finished in {treat_run['elapsed_secs']}s (Turns: {treat_run['num_turns']}, Cost: ${treat_run['total_cost']:.4f})"
    )

    ctrl_eval = await evaluate_app(ctrl_dir / "app.py")
    treat_eval = await evaluate_app(treat_dir / "app.py")

    return {
        "model_name": display_name,
        "model_id": model_id,
        "ctrl_time": ctrl_run["elapsed_secs"],
        "treat_time": treat_run["elapsed_secs"],
        "ctrl_turns": ctrl_run["num_turns"],
        "treat_turns": treat_run["num_turns"],
        "ctrl_cost": ctrl_run["total_cost"],
        "treat_cost": treat_run["total_cost"],
        "ctrl_sim_ok": ctrl_eval["simulation_success"],
        "treat_sim_ok": treat_eval["simulation_success"],
        "ctrl_dup_fixed": ctrl_eval["duplicate_id_fixed"],
        "treat_dup_fixed": treat_eval["duplicate_id_fixed"],
        "ctrl_uncalled_fixed": ctrl_eval["uncalled_input_fixed"],
        "treat_uncalled_fixed": treat_eval["uncalled_input_fixed"],
    }


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run A/B experiment comparing Claude Code with vs without Shiny MCP server."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Specific model to run (e.g. 'claude-sonnet-5', 'claude-opus-5', 'haiku').",
    )
    parser.add_argument(
        "--all-models",
        action="store_true",
        help="Run benchmark across all default models (Sonnet 5, Opus 5, Haiku 4.5).",
    )
    args = parser.parse_args()

    if args.all_models:
        target_models = DEFAULT_MODELS
    elif args.model:
        target_models = [(args.model, args.model)]
    else:
        target_models = [("Sonnet 5", "claude-sonnet-5")]

    print("=" * 80)
    print("A/B EXPERIMENT: Skills-Only (Control) vs Skills + Shiny MCP (Treatment)")
    print(f"Target Models: {', '.join(name for name, _ in target_models)}")
    print("=" * 80)

    results = []
    for disp_name, model_id in target_models:
        res = await run_model_benchmark(disp_name, model_id)
        results.append(res)

    print("\n" + "=" * 80)
    print("FINAL A/B BENCHMARK SUMMARY")
    print("=" * 80)
    header = f"{'Model':<12} | {'Time (Ctrl/Treat)':<18} | {'Turns (C/T)':<12} | {'Cost (C/T)':<18} | {'Sim Success (C/T)':<18}"
    print(header)
    print("-" * 80)

    for r in results:
        time_str = f"{r['ctrl_time']}s / {r['treat_time']}s"
        turns_str = f"{r['ctrl_turns']} / {r['treat_turns']}"
        cost_str = f"${float(r['ctrl_cost']):.3f} / ${float(r['treat_cost']):.3f}"
        sim_str = f"{'✅' if r['ctrl_sim_ok'] else '❌'} / {'✅' if r['treat_sim_ok'] else '❌'}"
        print(
            f"{r['model_name']:<12} | {time_str:<18} | {turns_str:<12} | {cost_str:<18} | {sim_str:<18}"
        )
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
