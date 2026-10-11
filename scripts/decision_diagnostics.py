"""Compare decision methods on fixed saved states, without a browser."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.milestone_record import Journal, read_events, save_json  # noqa: E402
from scripts.runtime_guard import cancellation_signals, single_run, supervise, worker_memory_limit  # noqa: E402


def worker(case, method, path):
    from jev_ultrafast import local_policy
    from jev_ultrafast.local_model import get_model, get_model_info
    from jev_ultrafast.structured_policy import structured_choose

    journal = Journal(path)
    journal.write("started", case=case["name"], method=method)
    calls = []
    original = local_policy.score_decision

    def score(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    local_policy.score_decision = score
    try:
        get_model()
        journal.write("loaded", **get_model_info())
        started = time.perf_counter()
        choose = local_policy.local_choose if method == "label" else structured_choose
        answer = choose(case["page"], case["goal"], case["history"])
        elapsed = round((time.perf_counter() - started) * 1000)
        journal.write("result", choice=answer["choice"], operation=answer["operation"],
                      correct=answer["choice"] in case["acceptable_action_ids"],
                      model_claims=answer.get("model_claims"), decision_ms=elapsed,
                      model_calls=len(calls) if method == "label" else 1,
                      usage=answer["usage"], peak_mlx_bytes=answer.get("peak_mlx_bytes"))
        return 0
    except Exception as error:
        journal.write("failure", error=str(error), error_type=type(error).__name__)
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--method", choices=["label", "structured"], required=True)
    parser.add_argument("--case")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--worker", type=Path)
    args = parser.parse_args()
    args.cases = args.cases.resolve()
    cases = json.loads(args.cases.read_text())["cases"]
    cases = [c for c in cases if args.case is None or c["name"] == args.case]
    if not cases:
        parser.error("No matching saved case")
    if args.worker:
        return worker(cases[0], args.method, args.worker)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    folder = ROOT / "artifacts/diagnostics" / str(time.time_ns())
    folder.mkdir(parents=True)
    paths = [*sorted((ROOT / "jev_ultrafast").glob("*.py")), Path(__file__), args.cases,
             ROOT / "scripts/runtime_guard.py", ROOT / "model-lock.json", ROOT / "uv.lock"]
    evidence = {"method": args.method, "cases_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest(),
                "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in paths},
                "limits": ["Saved-state diagnostics do not prove task completion.",
                           "Worker memory excludes browser memory. No browser runs in this comparison.",
                           "Methods receive the same goal, saved observation, history, and available actions.",
                           "Prompt serialization differs. Label retains its existing two-stage path on crowded pages."],
                "runs": []}
    save_json(args.output, evidence)
    with cancellation_signals(), single_run():
        for case in cases:
            path = folder / (case["name"] + ".jsonl")
            stats, error, code = {}, None, None
            started = time.monotonic()
            try:
                code = supervise([sys.executable, str(Path(__file__).resolve()), "--cases", str(args.cases),
                                  "--method", args.method, "--case", case["name"], "--output", str(args.output),
                                  "--worker", str(path)], timeout=90, memory_limit=worker_memory_limit(), stats=stats)
            except (Exception, KeyboardInterrupt) as problem:
                error = str(problem) or "cancelled"
            events = read_events(path)
            result = next((e for e in events if e["event"] == "result"), None)
            row = {"case": case["name"], "result": result, "events": events, "runtime": stats,
                   "exit_code": code, "error": error, "total_ms": round((time.monotonic()-started)*1000)}
            evidence["runs"].append(row)
            save_json(args.output, evidence)
            print(json.dumps({k: row[k] for k in ("case", "result", "error", "runtime")}), flush=True)
            if error:
                return 1
    return 0


if __name__ == "__main__":
    os.environ.update(JEV_LOCAL="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    raise SystemExit(main())
