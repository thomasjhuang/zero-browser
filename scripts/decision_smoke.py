"""Offline next-token decision scoring; never calls generate or a hosted model."""

import argparse
import importlib.metadata
import json
import platform
import shutil
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

from jev_ultrafast.local_model import LABELS as LABELS
from jev_ultrafast.local_model import SYSTEM as SYSTEM
from jev_ultrafast.local_model import get_model, get_model_info
from jev_ultrafast.local_model import make_prompt as make_prompt
from jev_ultrafast.local_model import score_decision as score_decision

ROOT = Path(__file__).resolve().parents[1]


def package_versions():
    versions = {}
    for name in ("mlx", "mlx-lm", "huggingface-hub", "transformers", "tokenizers", "numpy"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def run(args, report):
    disk = shutil.disk_usage(ROOT)
    report["disk"] = {"total_bytes": disk.total, "free_bytes_before_run": disk.free}
    model, tokenizer, mx = get_model()
    report["hardware"] = mx.device_info()
    report.update(get_model_info())
    cases = json.loads(args.cases.read_text())
    measurements = report["measurements"]
    for case in cases:
        actions = case["candidates"]
        for rotation in range(len(actions)):
            rotated = actions[rotation:] + actions[:rotation]
            for repetition in range(args.repeats + 1):
                result = score_decision(model, tokenizer, mx, case["goal"], case["observation"], rotated)
                result.update(
                    case=case["name"], rotation=rotation, repetition=repetition,
                    expected_action=case["expected_action"],
                    correct=result["selected_action"]["id"] == case["expected_action"],
                    phase="cold_first_forward" if not measurements else "warm_forward",
                )
                measurements.append(result)
    warm = [m["inference_ms"] for m in measurements if m["phase"] == "warm_forward"]
    firsts = [m for m in measurements if m["repetition"] == 0]
    report.update(
        status="completed", forward_passes=len(measurements),
        correct_unique_prompts=sum(m["correct"] for m in firsts), unique_prompts=len(firsts),
        cold_first_forward_ms=measurements[0]["inference_ms"],
        warm_median_ms=statistics.median(warm) if warm else None,
        warm_min_ms=min(warm) if warm else None, warm_max_ms=max(warm) if warm else None,
        peak_mlx_bytes=max(report["model_load_peak_mlx_bytes"], *(m["peak_mlx_bytes"] for m in measurements)),
        prompt_tokens_min=min(m["prompt_tokens"] for m in measurements),
        prompt_tokens_max=max(m["prompt_tokens"] for m in measurements),
        rotation_checks={case["name"]: {
            "all_rotations_correct": all(m["correct"] for m in firsts if m["case"] == case["name"]),
            "selected_actions": [m["selected_action"]["id"] for m in firsts if m["case"] == case["name"]],
        } for case in cases},
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / "fixtures/decision_cases.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/decision-smoke.json")
    parser.add_argument("--repeats", type=int, default=3, help="Warm repeats per prompt after its first measurement")
    parser.add_argument("--offline", action="store_true", help="Accepted for clarity; offline is always enforced")
    args = parser.parse_args()
    if args.repeats < 0:
        parser.error("--repeats must be nonnegative")
    report = {
        "status": "started", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": "mlx-community/Qwen3-4B-Instruct-2507-4bit", "model_revision": None,
        "python": platform.python_version(), "platform": platform.platform(),
        "dependencies": package_versions(), "measurements": [],
        "notes": [
            "Scores are uncalibrated restricted-label softmax scores, not guaranteed confidence estimates.",
            "These synthetic cases do not establish browser-task reliability.",
            "Cold means first forward pass in this process after model loading; disk/OS caches are not cleared.",
            "Warm runs still prefill the full prompt; no KV cache or prefix reuse.",
            "Latency excludes tokenization; load time is separate. Peak MLX excludes other applications and OS memory.",
            "Candidate rotations move each action across all four labels and positions; they are a limited bias check.",
        ],
    }
    exit_code = 0
    try:
        run(args, report)
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
        exit_code = 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "measurements"}, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
