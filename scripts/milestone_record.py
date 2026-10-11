"""Durable local run evidence. This module does not import a model."""

import json
import os
import time
from pathlib import Path


class Journal:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.started = time.monotonic()

    def write(self, event, **data):
        record = {"event": event, "elapsed_ms": round((time.monotonic() - self.started) * 1000), **data}
        with self.path.open("a") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())


def read_events(path):
    events = []
    if not Path(path).exists():
        return events
    for line in Path(path).read_text().splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            # A killed writer can leave an incomplete final line.
            break
    return events


def summarize(events):
    decisions = [e for e in events if e["event"] == "decision"]
    calls = [e for e in events if e["event"] == "model_call_started"]
    finished = [e for e in events if e["event"] == "model_call_finished"]
    outcomes = [e for e in events if e["event"] == "outcome"]
    failures = [e for e in events if e["event"] in {"failure", "human_required", "rejected", "mutation_uncertain"}]
    result = outcomes[-1]["result"] if outcomes else None
    pending = set()
    for event in events:
        if event["event"] == "mutation_started":
            pending.add(event["step"])
        elif event["event"] in {"executed", "rejected"}:
            pending.discard(event.get("step"))
    # Never infer a cause from the final status alone.
    first_failure = failures[0] if failures else None
    if first_failure is None and result and not result["passed"]:
        terminal = next((e for e in reversed(decisions) if e.get("operation") == "DONE"), None)
        if terminal:
            first_failure = {"step": terminal["step"], "category": "premature_completion",
                             "cause": "DONE preceded independent outcome success."}
    return {
        "outcome_verified": bool(result and result["passed"]),
        "verification": result,
        "model_done": any(e.get("operation") == "DONE" for e in decisions),
        "first_observed_failure": first_failure,
        "decision_latency_ms": [e["latency_ms"] for e in decisions],
        "decision_count": len(decisions),
        "model_calls_started": len(calls),
        "model_calls_finished": len(finished),
        "model_call_coverage": "complete" if len(calls) == len(finished) else "interrupted",
        "actions_executed": sum(e["event"] == "executed" for e in events),
        "execution_outcome_unknown": bool(pending) or any(e["event"] == "mutation_uncertain" for e in events),
        "peak_mlx_bytes": max((e.get("peak_mlx_bytes", 0) for e in finished), default=0) or None,
    }


def compare_runs(folder):
    """Group fixed conditions. Keep interrupted runs in the denominator."""
    groups = {}
    for path in sorted(Path(folder).glob("*/conditions.json"), key=lambda p: p.parent.name.rsplit("-", 1)[-1]):
        conditions = json.loads(path.read_text())
        if conditions["pilot"]:
            continue
        summary_path = path.parent / "summary.json"
        summary = json.loads(summary_path.read_text()) if summary_path.exists() else {
            **summarize(read_events(path.parent / "events.jsonl")), "successful_run": False,
            "task": conditions["task"], "total_elapsed_ms": None, "runtime": {},
        }
        key_data = {k: conditions[k] for k in ("task", "manifest", "timeout", "max_decisions", "headless")}
        key = json.dumps(key_data, sort_keys=True)
        group = groups.setdefault(key, {"task": summary["task"], "runs": [], "consecutive_successes": 0,
                                        "best_consecutive_successes": 0})
        success = summary["successful_run"]
        if group["runs"] and group["runs"][-1]["source_sha256"] != conditions["source_sha256"]:
            group["consecutive_successes"] = 0
        group["consecutive_successes"] = group["consecutive_successes"] + 1 if success else 0
        group["best_consecutive_successes"] = max(group["best_consecutive_successes"],
                                                  group["consecutive_successes"])
        group["runs"].append({"record": path.parent.name, "successful_run": success,
                              "revision": conditions["revision"], "source_sha256": conditions["source_sha256"],
                              **{k: summary[k] for k in ("total_elapsed_ms", "decision_latency_ms",
                                                        "model_calls_started", "runtime")}})
    return list(groups.values())


def save_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)
