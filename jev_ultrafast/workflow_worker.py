"""Bounded observed-control steps in one owned browser session."""

import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

from scripts.milestone import require_allowed, require_page

from .bounded_worker import normalized, run_bounded
from .browser import StalePage


class LocalDecisions:
    """Keep model lifetime separate from browser lifetime. No prompt cache is retained."""

    def __init__(self, folder, mode, journal):
        self.folder, self.mode, self.journal = Path(folder), mode, journal
        self.process = None
        self.error_stream = None

    def choose(self, state, goal, history):
        if self.process is None:
            self.error_stream = (self.folder / "model.stderr").open("a")
            self.process = subprocess.Popen(
                [sys.executable, "-m", "jev_ultrafast.workflow_worker", "--model"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=self.error_stream,
                text=True,
            )
            (self.folder / "model.pid").write_text(str(self.process.pid))
        started = time.monotonic_ns()
        self.journal.write("model_call_started", monotonic_ns=started, pid=self.process.pid)
        self.process.stdin.write(json.dumps({"state": state, "goal": goal, "history": history}) + "\n")
        self.process.stdin.flush()
        if not select.select([self.process.stdout], [], [], 30)[0]:
            raise TimeoutError("Local decision deadline ended")
        reply = json.loads(self.process.stdout.readline())
        if "error" in reply:
            self.journal.write("model_call_failed", **reply, monotonic_ns=time.monotonic_ns())
            raise ValueError(reply["error"])
        result = reply["decision"]
        self.journal.write(
            "model_call_finished",
            monotonic_ns=time.monotonic_ns(),
            pid=self.process.pid,
            wrapper_ms=(time.monotonic_ns() - started) / 1e6,
            timing=result["timing"],
            usage=result["usage"],
            load=reply["load"],
        )
        return result

    def end_subtask(self):
        if self.mode == "reload":
            self.close()

    def close(self):
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=1)
            self.process = None
            (self.folder / "model.pid").unlink(missing_ok=True)
            self.error_stream.close()


def observed_candidates(page, kind, target):
    choices = [a for a in page["actions"] if a["kind"] == kind and normalized(a["label"]) == normalized(target)]
    if len(choices) != 1:
        raise ValueError("missing_target" if not choices else "ambiguous_target")
    return choices


def run_control(browser, task, choose, journal):
    """Execute one uniquely identified observed control, then return fresh observed facts."""
    history = []
    for attempt in range(3):
        page = browser.observe(screenshot=False)
        require_page(page)
        journal.write("observation", page=page, monotonic_ns=time.monotonic_ns())
        actions = observed_candidates(page, task["kind"], task["target"])
        action = actions[0]
        require_allowed(action)
        decision = choose({**page, "actions": actions}, task["outcome"], history)
        journal.write("decision", **decision)
        if decision["choice"] != action["id"]:
            return {
                "status": "failure",
                "first_failure": {"category": "incorrect_decision", "step": attempt + 1},
                "unresolved_execution": False,
            }
        href = (
            browser.evaluate(
                "(n => window.__jevFast.nodes.get(n)?.href || null)(" + json.dumps(action.get("node")) + ")"
            )
            if task["kind"] == "click"
            else None
        )
        if href and urlsplit(href).hostname not in task["allowed_hosts"]:
            return {
                "status": "uncertainty",
                "first_failure": {"category": "boundary_violation"},
                "unresolved_execution": False,
            }
        journal.write(
            "mutation_started", action=action, href=href, from_url=page["url"], monotonic_ns=time.monotonic_ns()
        )
        try:
            browser.act(action, page)
        except StalePage as error:
            journal.write("rejected", cause=str(error), execution="not_executed", monotonic_ns=time.monotonic_ns())
            continue
        except Exception as error:
            journal.write("mutation_uncertain", cause=str(error))
            return {
                "status": "uncertainty",
                "unresolved_execution": True,
                "first_failure": {"category": "execution_failure", "cause": str(error)},
            }
        journal.write("executed", action=action, href=href, from_url=page["url"], monotonic_ns=time.monotonic_ns())
        # Observation can repeat. Browser input cannot repeat after possible execution.
        end = time.monotonic() + 5
        after = browser.observe(screenshot=False)
        while after["fingerprint"] == page["fingerprint"] and time.monotonic() < end:
            time.sleep(0.1)
            after = browser.observe(screenshot=False)
        require_page(after)
        journal.write("observation", page=after, monotonic_ns=time.monotonic_ns())
        return {
            "status": "success" if after["fingerprint"] != page["fingerprint"] else "uncertainty",
            "unresolved_execution": False,
            "evidence": {
                "before_url": page["url"],
                "after_url": after["url"],
                "changed": after["fingerprint"] != page["fingerprint"],
                "observed_href": href,
            },
        }
    return {
        "status": "uncertainty",
        "unresolved_execution": False,
        "first_failure": {"category": "rejected_decisions", "cause": "Three decisions rejected before execution"},
    }


def run_step(browser, kind, target, value, outcome, allowed_hosts, choose, journal):
    if kind == "fill":
        return run_bounded(
            browser,
            {
                "outcome": outcome,
                "kind": "fill",
                "target": target,
                "value": value,
                "permitted_actions": ["fill"],
                "stopping_conditions": ["outcome_observed", "human_required", "boundary_violation"],
                "deadline_seconds": 30,
                "action_budget": 2,
            },
            choose,
            journal,
        )
    if kind not in {"click", "scroll"}:
        raise ValueError("Unsupported subtask kind")
    return run_control(
        browser, {"kind": kind, "target": target, "outcome": outcome, "allowed_hosts": allowed_hosts}, choose, journal
    )


def model_main():
    import contextlib

    # Model libraries can print progress. Keep the JSON transport separate.
    with contextlib.redirect_stdout(sys.stderr):
        from . import local_model
        from .structured_policy import structured_choose
    for line in sys.stdin:
        request = json.loads(line)
        cold = local_model._MODEL is None
        started = time.monotonic_ns()
        try:
            with contextlib.redirect_stdout(sys.stderr):
                result = structured_choose(request["state"], request["goal"], request["history"])
                info = local_model.get_model_info()
            response = {
                "decision": result,
                "load": {
                    "actual_load": cold,
                    "pid": os.getpid(),
                    "call_started_monotonic_ns": started,
                    "model_load_ms": info["model_load_ms"] if cold else 0,
                },
            }
        except Exception as error:
            response = {"error": str(error)}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    model_main()
