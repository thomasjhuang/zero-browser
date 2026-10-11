"""Return control to the coordinator after each guarded browser action."""

import json
import math
import os
import sys
import time
import uuid
from pathlib import Path

from jev_ultrafast.browser import Browser, StalePage
from scripts.coordinator_handoff import ERROR_TEXT, visible_state
from scripts.milestone import (
    instrument_browser,
    measured_model,
    require_allowed,
    require_page,
    require_selection_action,
    show_task_tab,
)
from scripts.milestone_record import Journal, read_events, save_json
from scripts.milestone_verify import verify_round_trip, verify_selection


class PreInputStale(StalePage):
    """The executor conclusively rejected the request before input."""


def check_deadline(deadline):
    if time.monotonic() >= deadline:
        raise TimeoutError("The shared deadline ended")


def resolve(page, target):
    if not isinstance(target, dict) or set(target) != {"id", "node", "kind", "label"}:
        raise ValueError("Supply an exact observed id, node, kind, and label")
    matches = [a for a in page["actions"] if all(a.get(k) == v for k, v in target.items())]
    semantic = [a for a in page["actions"] if a.get("kind") == target["kind"]
                and a.get("label", "").strip().casefold() == target["label"].strip().casefold()]
    if len(matches) != 1 or len(semantic) != 1:
        raise ValueError("The target is missing or ambiguous")
    return matches[0]


def require_task_action(action, page, events, task, purpose):
    require_allowed(action)
    if task["kind"] == "selection":
        require_selection_action(action, page, events, task["expected"])
        return
    purposes = {"origin", "destination", "departure", "return", "trip_type", "passengers", "cabin", "search"}
    if task["kind"] != "round_trip" or purpose not in purposes:
        raise ValueError("Supply a permitted search-control purpose")
    # Codex authorizes the exact observed target for one form action. Links are outside this boundary.
    if action.get("role") not in {"button", "combobox", "textbox", "searchbox", "spinbutton",
                                  "option", "gridcell", "radio", "checkbox", "menuitemradio", "menuitem"}:
        raise ValueError("Only observed search form controls are permitted")
    if purpose == "search" and (action["kind"] != "click" or action.get("role") != "button"
                               or "search" not in action["label"].casefold()):
        raise ValueError("Search requires an observed search button")


def assess(page, events, task):
    if task["kind"] == "round_trip":
        return verify_round_trip(page, events, task["expected"])
    return verify_selection(page, events, task["expected"])


def dispatch_one(browser, page, request, task, journal, step, deadline):
    """There is one act call and no retry or recursive dispatch in this function."""
    from jev_ultrafast import local_policy
    from jev_ultrafast.local_model import begin_decision_group, get_model

    if request.get("fingerprint") != page["fingerprint"]:
        raise ValueError("The request does not match its issued observation")
    require_page(page)
    mode = request.get("mode")
    extra = {"purpose"} if task["kind"] == "round_trip" else set()
    purpose = request.get("purpose")
    if mode == "exact":
        if set(request) != {"request_id", "fingerprint", "mode", "target", "value"} | extra:
            raise ValueError("Invalid exact action request")
        action = resolve(page, request["target"])
        # Click/select use Browser.act's page-key and target guard, without a whole-page veto.
        if action["kind"] not in {"click", "select"} and not browser.fresh(page):
            raise PreInputStale("The request observation is stale before input")
        text = request["value"]
        if action["kind"] == "fill":
            if not isinstance(text, str) or not 1 <= len(text) <= 1000:
                raise ValueError("Supply a bounded field value")
        elif text is not None:
            raise ValueError("Only fill actions accept a value")
    elif mode == "choose":
        if not browser.fresh(page):
            raise PreInputStale("The local selection observation is stale before inference")
        if set(request) != {"request_id", "fingerprint", "mode", "instruction", "permitted"} | extra:
            raise ValueError("Invalid local selection request")
        if not isinstance(request["instruction"], str) or not 1 <= len(request["instruction"]) <= 2000:
            raise ValueError("Supply one bounded action instruction")
        if not isinstance(request["permitted"], list) or not 1 <= len(request["permitted"]) <= 20:
            raise ValueError("Supply between one and twenty observed permitted actions")
        actions = [resolve(page, a) for a in request["permitted"]]
        if len({a["id"] for a in actions}) != len(actions):
            raise ValueError("Repeated permitted action")
        events = read_events(journal.path)
        for candidate in actions:
            require_task_action(candidate, page, events, task, purpose)
            if candidate["kind"] != "click":
                raise ValueError("Local selection accepts observed click choices only")
        candidates = [{"id": a["id"], "operation": "CLICK", "target": str(a["node"]),
                       "description": a["label"]} for a in actions]
        begin_decision_group()
        started = time.monotonic()
        result = local_policy.score_decision(
            *get_model(), request["instruction"],
            json.dumps({"url": page["url"], "text": page["text"][:3000],
                        "permitted_actions": candidates}), candidates,
        )
        choice = result["selected_action"]["id"]
        journal.write("decision", step=step, choice=choice, operation="CLICK",
                      latency_ms=round((time.monotonic()-started)*1000), result=result)
        matches = [a for a in actions if a["id"] == choice]
        if len(matches) != 1:
            raise ValueError("The model chose an unsupported target")
        action, text = matches[0], None
    else:
        raise ValueError("Use exact or choose mode")
    require_task_action(action, page, read_events(journal.path), task, purpose)
    check_deadline(deadline)
    journal.write("action_source", step=step, source="deterministic" if mode == "exact" else "local_model")
    try:
        browser.act(action, page, text=text)
    except StalePage as error:
        # Browser.act raises StalePage only before input. Select uncertainty uses RuntimeError.
        raise PreInputStale(str(error)) from error
    # Execution is journaled by instrument_browser before this observation. Never retry.
    after = browser.observe(screenshot=False)
    check_deadline(deadline)
    return after


def run(request):
    from jev_ultrafast.local_model import get_model, get_model_info

    folder = Path(request["coordinator"]["folder"])
    deadline = request["coordinator"]["deadline_monotonic"]
    if not isinstance(deadline, (int, float)) or not math.isfinite(deadline):
        raise ValueError("Supply the external shared deadline")
    budget = request["max_decisions"]
    if type(budget) is not int or not 1 <= budget <= (60 if request["task"]["kind"] == "round_trip" else 20):
        raise ValueError("Supply a bounded action budget")
    if list(folder.glob("action-*.json")) or (folder / "ready.json").exists():
        raise ValueError("Use a fresh request folder")
    journal, step = Journal(request["journal"]), [0]
    browser = None
    try:
        check_deadline(deadline)
        browser = Browser(request["task"]["url"])
        instrument_browser(browser, journal, step)
        journal.write("task_tab_shown", closed_startup_tabs=show_task_tab(browser))
        page = browser.observe(screenshot=False)
        journal.write("model_loading", step=0)
        get_model()
        journal.write("model_loaded", **get_model_info(), worker_pid=os.getpid(), monotonic=time.monotonic())
        with measured_model(journal, step):
            for number in range(1, budget + 1):
                check_deadline(deadline)
                step[0] = number
                request_id = uuid.uuid4().hex
                ready = {"request_id": request_id, "sequence": number, "observation": page,
                         "actions_remaining": budget-number+1, "seconds_remaining": deadline-time.monotonic(),
                         "worker_pid": os.getpid(), "browser_target": browser.target}
                journal.write("coordinator_ready", **ready, monotonic_ns=time.monotonic_ns())
                save_json(folder / "ready.json", ready)
                path = folder / f"action-{number}.json"
                while not path.exists():
                    check_deadline(deadline)
                    time.sleep(0.05)
                check_deadline(deadline)
                if path.stat().st_size > 16384:
                    raise ValueError("Action request exceeds size limit")
                command = json.loads(path.read_text())
                if command.get("request_id") != request_id:
                    raise ValueError("The request does not match the current observation")
                journal.write("coordinator_request", step=number, request=command, monotonic_ns=time.monotonic_ns())
                before = page
                try:
                    page = dispatch_one(browser, page, command, request["task"], journal, number, deadline)
                except PreInputStale as error:
                    # This catch excludes failures in the observation after completed input.
                    page = browser.observe(screenshot=False)
                    check_deadline(deadline)
                    response = {"request_id": request_id, "sequence": number,
                                "status": "stale_not_executed", "action_executed": False,
                                "unresolved_execution": False, "observation": page,
                                "stop": False, "reason": str(error)}
                    journal.write("stale_returned", **response, monotonic_ns=time.monotonic_ns())
                    save_json(folder / f"result-{number}.json", response)
                    observed_error = ERROR_TEXT.search(page.get("text", ""))
                    if observed_error:
                        raise ValueError(observed_error.group(0))
                    # Consume the request budget. Only a NEW coordinator request can act.
                    continue
                outcome = assess(page, read_events(journal.path), request["task"])
                error = ERROR_TEXT.search(page.get("text", ""))
                stopped = bool(error or visible_state(page) == visible_state(before))
                response = {"request_id": request_id, "sequence": number, "action_executed": True,
                            "unresolved_execution": False, "observation": page, "outcome": outcome,
                            "stop": stopped or outcome["passed"],
                            "reason": error.group(0) if error else "no_progress" if stopped else None}
                journal.write("action_returned", **response, monotonic_ns=time.monotonic_ns())
                save_json(folder / f"result-{number}.json", response)
                if outcome["passed"]:
                    journal.write("outcome", step=number, result=outcome)
                    return 0
                if stopped:
                    raise ValueError(response["reason"])
                # The next iteration cannot act until a new matching request arrives.
            raise ValueError("The shared action budget ended")
    except Exception as error:
        events = read_events(journal.path)
        uncertain = any(e["event"] == "mutation_uncertain" for e in events)
        executed = any(e["event"] == "executed" and e.get("step") == step[0] for e in events)
        journal.write("failure", step=step[0], category=type(error).__name__, cause=str(error))
        save_json(folder / "stopped.json", {"step": step[0], "cause": str(error),
                  "action_executed": None if uncertain else executed, "unresolved_execution": uncertain,
                  "execution_evidence": "Read events.jsonl. Do not replay any action from this run."})
        return 1
    finally:
        if browser is not None:
            browser.close()


if __name__ == "__main__":
    os.environ.update(JEV_LOCAL="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    raise SystemExit(run(json.loads(Path(sys.argv[1]).read_text())))
