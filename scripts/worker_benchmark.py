"""Run fixed bounded-worker contracts sequentially with independent fixture outcomes."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager, nullcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.milestone import HumanRequired, local_page, show_task_tab  # noqa: E402
from scripts.milestone_record import Journal, read_events, save_json  # noqa: E402
from scripts.run_cli import isolated_browser  # noqa: E402
from scripts.runtime_guard import cancellation_signals, single_run, supervise, worker_memory_limit  # noqa: E402

FIXTURE_READ = """(() => ({airport:document.getElementById('airport')?.value??null,
 reference:document.getElementById('reference').value,cabin:document.getElementById('cabin').value,
 selected:window.selectedAirport,submitted:window.submitted,help_opened:window.helpOpened}))()"""
PAGE_READ = "(() => ({url:location.href, text:document.body?document.body.innerText:''}))()"


def independent_outcome(case, before, after, result):
    task = case["task"]
    expected = case["expected_status"]
    if task["kind"] == "click":
        url = str((after or {}).get("url") or "")
        text = str((after or {}).get("text") or "")
        checks = {"expected_status": result["status"] == expected,
                  "opened": task["value"] in url,
                  "no_uncertain_execution": result["unresolved_execution"] is False}
        if case.get("expect_text"):
            checks["visible_text"] = case["expect_text"] in text
        return {"passed": all(checks.values()), "checks": checks, "observed": after}
    field = {"Reference": "reference", "Cabin": "cabin", "Departure airport": "airport"}[task["target"]]
    checks = {"expected_status": result["status"] == expected,
              "no_submission": after["submitted"] is False,
              "no_distractor_action": after["help_opened"] is False,
              "no_uncertain_execution": result["unresolved_execution"] is False,
              "other_fields_unchanged": all(before[k] == after[k] for k in ("airport", "reference", "cabin")
                                            if k != field)}
    if expected == "success":
        checks["supplied_value"] = after[field] == task["value"]
        if task["kind"] == "autocomplete":
            checks["suggestion_selected"] = after["selected"] == task["value"]
    else:
        checks["no_action"] = not result["executed_actions"]
        checks["page_unchanged"] = before == after
    return {"passed": all(checks.values()), "checks": checks, "observed": after}


def execute_case(browser, task, choose, journal, cache_dir):
    """Replay only when every stored target is on the page. Otherwise use the model."""
    from jev_ultrafast.bounded_worker import run_bounded
    from jev_ultrafast.replay_cache import cached_steps

    page = browser.observe(screenshot=False)
    replayed = None
    try:
        replayed = cached_steps(cache_dir, task["outcome"], page, browser)
    except HumanRequired:
        raise
    except Exception:
        replayed = None
    if not replayed:
        return page, None, run_bounded(browser, task, choose, journal)
    journal.write("replay", step=0, actions=len(replayed))
    result = {"status": "success", "evidence": None, "model_claims": [], "unresolved_execution": False,
              "first_failure": None, "executed_actions": [
                  {"action": step.get("target"), "kind": step.get("operation"), "text": step.get("value"),
                   "execution": "executed"} for step in replayed]}
    journal.write("worker_result", result=result)
    return page, replayed, result


def remember_pass(cache_dir, goal, page, replayed, result, passed):
    from jev_ultrafast.replay_cache import save_actions, steps_from_history

    if not passed:
        return None
    steps = replayed if replayed else steps_from_history((result or {}).get("executed_actions"))
    return save_actions(cache_dir, goal, page, steps)


def run_case(request):
    from jev_ultrafast import local_policy
    from jev_ultrafast.structured_policy import structured_choose

    case = request["case"]
    journal = Journal(request["journal"])
    counted = {"calls": 0}
    original = local_policy.score_decision

    def score(*args, **kwargs):
        counted["calls"] += 1
        journal.write("model_call_started", call=counted["calls"])
        answer = original(*args, **kwargs)
        journal.write("model_call_finished", call=counted["calls"])
        return answer

    def choose(*args):
        if request["method"] == "label":
            return local_policy.local_choose(*args)
        counted["calls"] += 1
        journal.write("model_call_started", call=counted["calls"])
        answer = structured_choose(*args)
        journal.write("model_call_finished", call=counted["calls"])
        return answer

    local_policy.score_decision = score
    try:
        return _finish_case(case, journal, choose, counted, request.get("replay_cache"))
    finally:
        local_policy.score_decision = original


@contextmanager
def hotel_fixture():
    """Serve the existing local hotel page. The fixture chooses its own controls."""
    import threading
    from functools import partial
    from http.server import ThreadingHTTPServer

    from scripts.milestone import MANIFEST
    from scripts.run_cli import FixtureHandler

    port = json.loads(MANIFEST.read_text())["conditions"]["local_port"]
    handler = partial(FixtureHandler, directory=str(ROOT / "jev_ultrafast" / "static"))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/fixture.html?scenario=travel"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _finish_case(case, journal, choose, counted, replay_cache=None):
    from jev_ultrafast.browser import Browser
    from scripts.milestone import REPLAY_CACHE

    cache = replay_cache or REPLAY_CACHE

    supplied_request = "url" in case
    hotel = case.get("page") == "fixture.html"
    if hotel:
        context = hotel_fixture()
    elif supplied_request:
        context = nullcontext(case["url"])
    else:
        context = local_page(case["layout"])
    with context as url:
        address = url if supplied_request or hotel else url.replace("milestone.html", "worker.html")
        browser = Browser(address)
        try:
            show_task_tab(browser)
            read = PAGE_READ if case["task"]["kind"] == "click" else FIXTURE_READ
            before = None if supplied_request else browser.evaluate(read)
            start_page, replayed, result = execute_case(browser, case["task"], choose, journal, cache)
            if supplied_request:
                assessment = {"passed": result["status"] == "success",
                              "scope": "Worker field predicate only. No independent site adapter was supplied."}
            else:
                after = browser.evaluate(read)
                assessment = independent_outcome(case, before, after, result)
            journal.write("outcome", assessment=assessment, model_calls=counted["calls"])
            remember_pass(cache, case["task"]["outcome"], start_page, replayed, result,
                          assessment.get("passed"))
            code = 0 if assessment["passed"] else 1
            journal.write("case_exit", code=code)
            return code
        finally:
            browser.close()


def run_two(request):
    """Run exactly two cases in this process. The weight load stays in memory."""
    cases, journals = request.get("cases"), request.get("journals")
    if not isinstance(cases, list) or len(cases) != 2 or not isinstance(journals, list) or len(journals) != 2:
        raise ValueError("The shared process runs exactly two existing cases")
    codes = [run_case({"case": case, "journal": journal, "method": request["method"],
                       "replay_cache": request.get("replay_cache")})
             for case, journal in zip(cases, journals)]
    return 0 if codes == [0, 0] else 1


def worker(request_path):
    request = json.loads(Path(request_path).read_text())
    if "cases" in request:
        return run_two(request)
    return run_case(request)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=["label", "structured"], default="structured")
    parser.add_argument("--case")
    parser.add_argument("--pair", nargs=2, metavar=("FIRST", "SECOND"),
                        help="Run two existing cases in one process. The model loads once.")
    parser.add_argument("--request", type=Path, help="JSON with url and one bounded task contract")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replay-cache", type=Path,
                        help="Replay cache directory. Defaults to artifacts/replay-cache.")
    parser.add_argument("--worker", type=Path)
    args = parser.parse_args(argv)
    if args.worker:
        return worker(args.worker)
    from scripts.milestone import REPLAY_CACHE

    replay_cache = str(args.replay_cache) if args.replay_cache else str(REPLAY_CACHE)
    args.output = args.output or ROOT / "artifacts/worker-result.json"
    manifest = ROOT / "fixtures/worker_tasks.json"
    if args.pair and (args.case or args.request):
        parser.error("--pair runs two manifest cases and cannot be combined with --case or --request")
    if args.request:
        from urllib.parse import urlparse

        from jev_ultrafast.bounded_worker import validate_task

        supplied = json.loads(args.request.read_text())
        validate_task(supplied["task"])
        if urlparse(supplied["url"]).scheme not in {"http", "https"}:
            parser.error("The worker requires an HTTP or HTTPS starting page")
        cases = [{"name": "supplied-request", "task": supplied["task"], "url": supplied["url"]}]
    else:
        cases = json.loads(manifest.read_text())["cases"]
    if args.pair:
        by_name = {case["name"]: case for case in cases}
        missing = [name for name in args.pair if name not in by_name]
        if missing:
            parser.error("No matching bounded task: " + ", ".join(missing))
        cases = [by_name[name] for name in args.pair]
    else:
        cases = [c for c in cases if args.case is None or c["name"] == args.case]
        if not cases:
            parser.error("No matching bounded task")
    folder = ROOT / "artifacts/worker" / str(time.time_ns())
    folder.mkdir(parents=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sources = [*sorted((ROOT / "jev_ultrafast").glob("*.py")), ROOT / "jev_ultrafast/snapshot.js",
               Path(__file__), ROOT / "scripts/runtime_guard.py", ROOT / "scripts/run_cli.py",
               ROOT / "scripts/milestone.py", ROOT / "scripts/milestone_record.py", manifest,
               ROOT / "fixtures/worker.html", ROOT / "model-lock.json", ROOT / "uv.lock"]
    results = {"method": args.method, "revision": subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                                         text=True).strip(),
               "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sources}, "manifest": {"cases": cases},
               "scope": "Bounded subtasks. No coordinator, full flight search, or savings proof.", "runs": []}
    save_json(args.output, results)
    with cancellation_signals(), single_run():
        if args.pair:
            journals = [folder / f"{index}-{case['name']}.jsonl" for index, case in enumerate(cases)]
            request = folder / "pair-request.json"
            save_json(request, {"cases": cases, "journals": [str(path) for path in journals],
                                "method": args.method, "replay_cache": replay_cache})
            started = time.monotonic()
            stats, error, code = {}, None, None
            try:
                with isolated_browser():
                    limit = worker_memory_limit()
                    stats["memory_limit_bytes"] = limit
                    timeout = sum(case["task"]["deadline_seconds"] for case in cases)
                    code = supervise([sys.executable, str(Path(__file__).resolve()), "--worker", str(request)],
                                     timeout=timeout, memory_limit=limit, stats=stats)
            except (Exception, KeyboardInterrupt) as problem:
                error = str(problem) or "cancelled"
            for case, journal in zip(cases, journals):
                append_case(results, args.output, case, journal, code, error, stats, started)
            return 1 if error else 0
        for case in cases:
            journal = folder / (case["name"] + ".jsonl")
            request = folder / (case["name"] + "-request.json")
            save_json(request, {"case": case, "journal": str(journal), "method": args.method,
                                "replay_cache": replay_cache})
            started = time.monotonic()
            stats, error, code = {}, None, None
            try:
                with isolated_browser():
                    limit = worker_memory_limit()
                    stats["memory_limit_bytes"] = limit
                    code = supervise([sys.executable, str(Path(__file__).resolve()), "--worker", str(request)],
                                     timeout=case["task"]["deadline_seconds"], memory_limit=limit, stats=stats)
            except (Exception, KeyboardInterrupt) as problem:
                error = str(problem) or "cancelled"
            if append_case(results, args.output, case, journal, code, error, stats, started):
                return 1
    return 0


def append_case(results, output, case, journal, code, error, stats, started):
    events = read_events(journal)
    calls = [e for e in events if e["event"] == "model_call_started"]
    outcome = next((e for e in events if e["event"] == "outcome"), None)
    result = next((e["result"] for e in events if e["event"] == "worker_result"), None)
    pending = set()
    for event in events:
        if event["event"] == "mutation_started":
            pending.add(event["step"])
        elif event["event"] in {"executed", "rejected"}:
            pending.discard(event.get("step"))
    if result is None:
        result = {"status": "uncertainty", "evidence": None,
                  "executed_actions": [e for e in events if e["event"] == "executed"],
                  "unresolved_execution": bool(pending),
                  "first_failure": {"category": "runtime_stop", "cause": error or "Worker exited"}}
    case_exit = next((e.get("code") for e in reversed(events) if e["event"] == "case_exit"), None)
    exit_code = case_exit if isinstance(case_exit, int) and not isinstance(case_exit, bool) else code
    row = {"case": case["name"], "result": result, "outcome": outcome,
           "passed": bool(outcome and outcome["assessment"]["passed"] and exit_code == 0 and error is None),
           "model_calls": len(calls),
           "model_calls_finished": sum(e["event"] == "model_call_finished" for e in events),
           "decision_ms": [e["latency_ms"] for e in events if e["event"] == "decision"],
           "unresolved_execution": bool(pending), "runtime": stats, "exit_code": exit_code, "error": error,
           "total_ms": round((time.monotonic()-started)*1000), "private_record": journal.name,
           "private_record_sha256": hashlib.sha256(journal.read_bytes()).hexdigest()
           if journal.exists() else None}
    results["runs"].append(row)
    save_json(output, results)
    print(json.dumps({k: row[k] for k in ("case", "passed", "result", "model_calls", "total_ms", "error")}),
          flush=True)
    return error is not None


if __name__ == "__main__":
    os.environ.update(JEV_LOCAL="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    raise SystemExit(main())
