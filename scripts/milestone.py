"""Run one fixed local-model benchmark with durable evidence and external limits."""

import argparse
import functools
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.coordinator_handoff import CoordinatorHandoff, CoordinatorStop  # noqa: E402
from scripts.milestone_record import Journal, compare_runs, read_events, save_json, summarize  # noqa: E402
from scripts.milestone_verify import (  # noqa: E402
    LOCAL_READ,
    diagnose_local,
    verify_flights,
    verify_local,
    verify_selection,
)
from scripts.run_cli import FixtureHandler, isolated_browser  # noqa: E402
from scripts.runtime_guard import (  # noqa: E402
    cancellation_signals,
    challenge_reason,
    single_run,
    supervise,
    worker_memory_limit,
)

MANIFEST = ROOT / "fixtures/milestone_tasks.json"
FORBIDDEN = re.compile(
    r"\b(log\s*in|sign\s*in|sign\s*up|register|password|captcha|select flight|book|booking|"
    r"reserve|buy|purchase|pay|payment|checkout|send|message|delete|account|subscribe)\b", re.I,
)


class HumanRequired(RuntimeError):
    pass


def require_allowed(action):
    if action.get("kind") not in {"click", "fill", "select", "scroll", "wait"}:
        raise HumanRequired("The action is outside the supported search operations.")
    if FORBIDDEN.search(" ".join(str(action.get(k, "")) for k in ("label", "href", "type"))):
        raise HumanRequired("The observed target requires human involvement.")


def require_page(page):
    reason = challenge_reason(page)
    if reason:
        raise HumanRequired(reason)
    if any(a.get("type") == "password" for a in page.get("actions", [])):
        raise HumanRequired("Login requires human involvement.")


def require_selection_action(action, page, events, expected):
    """Keep a supplied field-selection task inside that field and its option dialog."""
    target = expected["target_label"].strip().casefold()
    fields = [a for a in page.get("actions", []) if a.get("kind") == "fill"]
    targets = [a for a in fields if a.get("label", "").strip().casefold() == target]
    started, target_nodes = False, set()
    for event in events:
        if event.get("event") == "observation":
            target_nodes = {a.get("node") for a in event["page"].get("actions", [])
                            if a.get("kind") == "fill" and a.get("label", "").strip().casefold() == target}
        elif event.get("event") == "executed":
            prior = event["action"]
            started |= (prior.get("label", "").strip().casefold() == target
                        or prior.get("node") in target_nodes)
    same_field = len(targets) == 1 and action.get("node") == targets[0].get("node")
    popup_field = started and not targets and len(fields) == 1 and action.get("node") == fields[0].get("node")
    matching_option = (started and action.get("role") == "option"
                       and re.search(r"(?<!\w)" + re.escape(expected["option_text"]) + r"(?!\w)",
                                     action.get("label", ""), re.I))
    permitted = (action.get("kind") in {"wait", "scroll"}
                 or (action.get("kind") == "fill" and (same_field or popup_field))
                 or (action.get("kind") == "click" and (same_field or matching_option)))
    if not permitted:
        raise HumanRequired("The action is outside the supplied field-selection boundary.")


@contextmanager
def local_page(layout):
    handler = functools.partial(FixtureHandler, directory=str(ROOT / "fixtures"))
    port = json.loads(MANIFEST.read_text())["conditions"]["local_port"]
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/milestone.html?layout={layout}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@contextmanager
def measured_model(journal, step):
    """Measure actual score and text calls inside this single owned worker."""
    import mlx_lm

    from jev_ultrafast import local_policy

    score, generate = local_policy.score_decision, mlx_lm.generate
    count = 0

    def wrap(function, kind):
        def measured(*args, **kwargs):
            nonlocal count
            count += 1
            if count > 160:
                raise RuntimeError("The run reached its model-call budget.")
            journal.write("model_call_started", kind=kind, call=count, step=step[0])
            started = time.monotonic()
            result = function(*args, **kwargs)
            fields = {k: result[k] for k in ("prompt_tokens", "peak_mlx_bytes", "candidate_order") if k in result} \
                if isinstance(result, dict) else {}
            journal.write("model_call_finished", kind=kind, call=count, step=step[0],
                          latency_ms=round((time.monotonic() - started) * 1000), **fields)
            return result
        return measured

    local_policy.score_decision = wrap(score, "decision_menu")
    mlx_lm.generate = wrap(generate, "field_text")
    try:
        yield
    finally:
        local_policy.score_decision, mlx_lm.generate = score, generate


def instrument_browser(browser, journal, step):
    observe, act = browser.observe, browser.act

    def observed(*args, **kwargs):
        page = observe(*args, **kwargs)
        journal.write("observation", step=step[0], page={k: v for k, v in page.items() if k != "screenshot"})
        require_page(page)
        return page

    def acted(action, page, text=None):
        require_allowed(action)
        journal.write("mutation_started", step=step[0], action=action, text=text)
        try:
            result = act(action, page, text=text)
        except Exception as error:
            from jev_ultrafast.browser import StalePage

            event = "rejected" if isinstance(error, StalePage) else "mutation_uncertain"
            journal.write(event, step=step[0], category="execution_failure", cause=str(error))
            raise
        # Persist execution before the agent performs the next observation.
        journal.write("executed", step=step[0], action=action, text=text)
        return result

    browser.observe, browser.act = observed, acted


def show_task_tab(browser):
    """Remove the unused startup tab from this run's isolated browser."""
    targets = browser.call("Target.getTargets")["targetInfos"]
    closed = 0
    for target in targets:
        if target["type"] == "page" and target["url"] == "about:blank" and target["targetId"] != browser.target:
            browser.call("Target.closeTarget", targetId=target["targetId"])
            closed += 1
    browser.call("Target.activateTarget", targetId=browser.target)
    return closed


def run_task(task, url, journal, max_decisions, *, visible=False, coordinator=None):
    from jev_ultrafast.agent import Agent
    from jev_ultrafast.browser import StalePage
    from jev_ultrafast.local_model import get_model, get_model_info

    step = [0]
    with Agent(url, task["goal"]) as agent:
        if visible:
            journal.write("task_tab_shown", closed_startup_tabs=show_task_tab(agent.browser))
        journal.write("observation", step=0, page=agent.state["page"])
        require_page(agent.state["page"])
        instrument_browser(agent.browser, journal, step)
        handoff = CoordinatorHandoff(coordinator, journal, agent.state["page"]) if coordinator else None
        if handoff:
            handoff.check_deadline()
        journal.write("model_loading", step=0)
        get_model()
        loaded_at = time.monotonic()
        journal.write("model_loaded", **get_model_info(), monotonic=loaded_at, worker_pid=os.getpid())
        rejected = 0
        with measured_model(journal, step):
            for number in range(1, max_decisions + 1):
                step[0] = number
                try:
                    if handoff:
                        handoff.check_deadline()
                    agent.command("predict")
                    decision = agent.state["decisions"][-1]
                    journal.write("decision", step=number, **decision)
                    choice = decision["choice"]
                    if choice not in {"DONE", "BLOCKED"}:
                        action = next((a for a in agent.state["page"]["actions"] if a["id"] == choice), None)
                        if action is None:
                            journal.write("failure", step=number, category="wrong_decision",
                                          cause="The selected target is absent from the observed actions.")
                            break
                        require_allowed(action)
                        if task["kind"] == "selection":
                            require_selection_action(action, agent.state["page"],
                                                     read_events(journal.path), task["expected"])
                    agent.command("act", {"fingerprint": agent.state["page"]["fingerprint"]})
                    rejected = 0
                    if task["kind"] == "selection":
                        result = verify_selection(agent.state["page"], read_events(journal.path), task["expected"])
                        if result["passed"]:
                            journal.write("outcome", step=number, result=result)
                            return 0
                    if handoff:
                        handoff.after_step(agent, number, max_decisions, loaded_at)
                except CoordinatorStop as error:
                    journal.write("failure", step=number, category=error.category, cause=str(error))
                    break
                except StalePage as error:
                    if (handoff and agent.state["history"]
                            and agent.state["history"][-1].get("page_changed") is None):
                        journal.write("failure", step=number, category="unresolved_observation",
                                      cause="Input executed but its resulting observation failed. Stop without replay.")
                        break
                    rejected += 1
                    journal.write("rejected", step=number, category="stale_decision", cause=str(error))
                    if rejected >= 3:
                        journal.write("failure", step=number, category="rejected_decisions",
                                      cause="Three consecutive decisions did not finish.")
                        break
                    agent.state["decision"] = None
                    agent.state["status"] = "ready"
                    agent.state["page"] = agent.browser.observe(screenshot=False)
                print(f"Decision {number}: {agent.state['status']}", flush=True)
                if agent.state["status"] in {"done", "blocked"}:
                    if agent.state["status"] == "blocked" and choice != "BLOCKED":
                        journal.write("failure", step=number, category="no_progress",
                                      cause="Three executed actions produced no observed page change.")
                    break
            else:
                journal.write("failure", step=step[0], category="decision_budget",
                              cause="The fixed decision budget ended.")
        # Read again independently. Never use the model's request or DONE as proof.
        if task["kind"] == "local":
            result = verify_local(agent.browser.evaluate(LOCAL_READ), task["expected"])
        elif task["kind"] == "selection":
            result = verify_selection(agent.browser.observe(screenshot=False),
                                      read_events(journal.path), task["expected"])
        else:
            result = verify_flights(agent.browser.observe(screenshot=False), task["expected"])
        journal.write("outcome", step=step[0], result=result)
        return 0 if result["passed"] else 1


def worker(request_path):
    os.environ.update(JEV_LOCAL="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    request = json.loads(Path(request_path).read_text())
    journal = Journal(request["journal"])
    task = request["task"]
    try:
        if task["kind"] == "local":
            with local_page(task["layout"]) as url:
                return run_task(task, url, journal, request["max_decisions"], visible=request.get("visible", False))
        return run_task(task, task["url"], journal, request["max_decisions"], visible=request.get("visible", False),
                        coordinator=request.get("coordinator"))
    except HumanRequired as error:
        events = read_events(journal.path)
        step = max((e.get("step", 0) for e in events), default=0)
        journal.write("human_required", step=step, category="human_required", cause=str(error))
        return 1
    except Exception as error:
        events = read_events(journal.path)
        step = max((e.get("step", 0) for e in events), default=0)
        journal.write("failure", step=step, category="unresolved", cause=str(error), error_type=type(error).__name__)
        return 1


def run(args):
    manifest = json.loads(MANIFEST.read_text())
    task = manifest["tasks"][args.task]
    if args.pilot and task["kind"] != "local":
        raise ValueError("The first pilot must use a local task.")
    timeout = 20 if args.pilot else manifest["conditions"]["timeout_seconds"]
    max_decisions = 2 if args.pilot else manifest["conditions"]["max_decisions"]
    run_dir = args.output / f"{args.task}-{time.time_ns()}"
    run_dir.mkdir(parents=True)
    journal_path = run_dir / "events.jsonl"
    request_path = run_dir / "request.json"
    save_json(request_path, {"task": task, "journal": str(journal_path), "max_decisions": max_decisions,
                             "visible": not args.headless})
    started = time.monotonic()
    stats, error, code = {}, None, 1
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    sources = [*sorted((ROOT / "jev_ultrafast").glob("*.py")), ROOT / "jev_ultrafast/snapshot.js", MANIFEST,
               *sorted((ROOT / "scripts").glob("milestone*.py")), ROOT / "scripts/runtime_guard.py",
               ROOT / "scripts/run_cli.py", ROOT / "fixtures/milestone.html",
               ROOT / "model-lock.json", ROOT / "uv.lock"]
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    save_json(run_dir / "conditions.json", {"task": args.task, "manifest": manifest, "revision": revision,
                                           "source_sha256": hashes, "pilot": args.pilot,
                                           "headless": args.headless,
                                           "timeout": timeout, "max_decisions": max_decisions,
                                           "cancel_after_seconds": 3 if args.pilot else None})
    try:
        with cancellation_signals(), single_run(), isolated_browser(headless=args.headless):
            limit = worker_memory_limit()
            stats["memory_limit_bytes"] = limit
            code = supervise([sys.executable, str(Path(__file__).resolve()), "--worker", str(request_path)],
                             timeout=timeout, memory_limit=limit, stats=stats,
                             cancel_after=3 if args.pilot else None)
    except KeyboardInterrupt:
        error, code = "cancelled", 130
    except Exception as problem:
        error = str(problem)
    events = read_events(journal_path)
    summary = {**summarize(events), "task": args.task, "pilot": args.pilot, "exit_code": code,
               "parent_stop": error, "total_elapsed_ms": round((time.monotonic() - started) * 1000),
               "runtime": stats, "memory_scope": "Sampled worker footprint. Browser memory is excluded."}
    summary["successful_run"] = summary["outcome_verified"] and error is None and code == 0
    if task["kind"] == "local":
        diagnosis = diagnose_local(events, task["expected"])
        first = summary["first_observed_failure"]
        if diagnosis and (first is None or diagnosis["step"] < first.get("step", 0)):
            summary["first_observed_failure"] = diagnosis
    if error and not summary["first_observed_failure"]:
        summary["first_observed_failure"] = {
            "step": max((e.get("step", 0) for e in events), default=0),
            "category": "interrupted" if code == 130 else "runtime_stop", "cause": error,
        }
    save_json(run_dir / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    print(f"Private records: {run_dir}", flush=True)
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=list(json.loads(MANIFEST.read_text())["tasks"]), default="local_search")
    parser.add_argument("--pilot", action="store_true",
                        help="Two decisions, 20-second deadline, cancel after 3 seconds.")
    parser.add_argument("--ready", action="store_true", help="Use only after the user confirms readiness for this run.")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--report", action="store_true", help="Compare saved runs without inference.")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/milestone")
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        return worker(args.worker)
    if args.report:
        print(json.dumps(compare_runs(args.output), indent=2))
        return 0
    if not args.ready:
        parser.error("Wait for user readiness before local inference. Use --ready only after that response.")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
