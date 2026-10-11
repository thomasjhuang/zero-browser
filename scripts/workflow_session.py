"""File transport for hosted benchmark agents using the same persistent worker."""

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.milestone_record import save_json  # noqa: E402
from scripts.run_cli import isolated_browser  # noqa: E402
from scripts.runtime_guard import (  # noqa: E402
    cancellation_signals,
    process_memory,
    single_run,
    supervise,
    worker_memory_limit,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["serve", "child", "request"])
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--request")
    args = parser.parse_args()
    folder = args.folder.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    if args.operation == "request":
        request = json.loads(args.request)
        token = str(time.time_ns())
        temporary = folder / (token + ".tmp")
        save_json(temporary, request)
        temporary.rename(folder / (token + ".request"))
        deadline = time.monotonic() + 45
        response = folder / (token + ".response")
        while not response.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not response.exists():
            raise TimeoutError("Request result is uncertain. Do not repeat a mutation.")
        print(response.read_text())
        return
    if args.operation == "child":
        from scripts.workflow_browser import Workflow

        worker = Workflow({"folder": str(folder), "method": "persistent"})
        (folder / "ready").write_text(str(os.getpid()))
        try:
            while True:
                requests = sorted(folder.glob("*.request"))
                if not requests:
                    time.sleep(0.02)
                    continue
                path = requests[0]
                request = json.loads(path.read_text())
                if request["method"] not in {"observe", "delegate", "assess", "close"}:
                    raise ValueError("Unsupported session operation")
                path.rename(path.with_suffix(".processing"))
                stop = request["method"] == "close"
                try:
                    result = (
                        {"closed": True} if stop else getattr(worker, request["method"])(**request.get("params", {}))
                    )
                except Exception as error:
                    result = {"error": str(error), "stop": True}
                save_json(path.with_suffix(".response"), result)
                if stop:
                    break
        finally:
            worker.close()
        return
    stats = {}
    with cancellation_signals(), single_run(), isolated_browser():
        os.environ.update(
            JEV_LOCAL="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", ZB_RECORD_PATH=str(folder / "replay.jsonl")
        )

        def memory(pid):
            deadline = folder / "active_deadline"
            if deadline.exists() and time.monotonic() >= float(deadline.read_text()):
                raise TimeoutError("Subtask deadline ended")
            total = process_memory(pid)
            model = folder / "model.pid"
            if model.exists():
                try:
                    total += process_memory(int(model.read_text()))
                except (FileNotFoundError, ProcessLookupError):
                    pass
            return total

        try:
            supervise(
                [sys.executable, str(Path(__file__).resolve()), "child", "--folder", str(folder)],
                timeout=180,
                memory_limit=worker_memory_limit(),
                memory_reader=memory,
                stats=stats,
            )
        finally:
            save_json(folder / "runtime.json", stats)


if __name__ == "__main__":
    main()
