"""One coordinator correction without replacing the live agent or its budgets."""

import json
import math
import os
import re
import time
import uuid
from pathlib import Path

from scripts.milestone_record import save_json

ERROR_TEXT = re.compile(
    r"\b(no\s+(?:matching\s+)?(?:locations|results|options|matches)\s+(?:found|available)|"
    r"invalid\s+(?:input|value|date)|something went wrong)\b", re.I,
)


class CoordinatorStop(RuntimeError):
    def __init__(self, category, message):
        super().__init__(message)
        self.category = category


def visible_state(page):
    """Ignore volatile node IDs and geometry, but retain visible values and controls."""
    controls = sorted(json.dumps({k: a[k] for k in (
        "kind", "label", "value", "checked", "selected", "expanded"
    ) if k in a}, sort_keys=True) for a in page.get("actions", []))
    return page.get("url"), page.get("text"), controls


class CoordinatorHandoff:
    def __init__(self, config, journal, initial_page):
        self.folder, self.deadline = Path(config["folder"]), config["deadline_monotonic"]
        if not isinstance(self.deadline, (float, int)) or not math.isfinite(self.deadline):
            raise ValueError("Supply the parent process deadline")
        self.journal, self.used, self.unchanged = journal, False, 0
        self.previous = visible_state(initial_page)
        self.folder.mkdir(parents=True, exist_ok=True)
        if any((self.folder / name).exists() for name in ("handoff.json", "correction.json")):
            raise ValueError("Use a fresh handoff folder without a preloaded correction")

    def check_deadline(self):
        if time.monotonic() >= self.deadline:
            raise CoordinatorStop("deadline", "The shared run deadline ended")

    def after_step(self, agent, step, max_decisions, loaded_at):
        self.check_deadline()
        page = agent.state["page"]
        current = visible_state(page)
        self.unchanged = self.unchanged + 1 if current == self.previous else 0
        self.previous = current
        error = ERROR_TEXT.search(page.get("text", ""))
        reason = {"category": "observed_error", "evidence": error.group(0)} if error else None
        if reason is None and self.unchanged >= 3:
            reason = {"category": "nonprogress", "evidence": "Three actions left the visible state unchanged"}
        if reason is None:
            return False
        self.journal.write("local_segment_stopped", step=step, reason=reason,
                           monotonic_ns=time.monotonic_ns())
        if self.used:
            raise CoordinatorStop("continued_nonprogress", "Further error or nonprogress after the one correction")
        if step >= max_decisions:
            raise CoordinatorStop("decision_budget", "No local decision budget remains for a correction")
        self.used = True
        handoff_id = uuid.uuid4().hex
        request = {
            "handoff_id": handoff_id, "original_goal": agent.state["goal"], "reason": reason,
            "observation": {k: page[k] for k in ("url", "title", "text", "actions", "fingerprint") if k in page},
            "last_action": agent.state["history"][-1] if agent.state["history"] else None,
            "last_action_execution": "completed", "unresolved_execution": False,
            "decisions_used": step, "decisions_remaining": max_decisions - step,
            "deadline_monotonic": self.deadline, "seconds_remaining": self.deadline - time.monotonic(),
            "worker_pid": os.getpid(), "browser_target": getattr(agent.browser, "target", None),
            "model_loaded_monotonic": loaded_at, "seconds_after_model_load": time.monotonic() - loaded_at,
        }
        self.journal.write("coordinator_handoff", step=step, **request, monotonic_ns=time.monotonic_ns())
        save_json(self.folder / "handoff.json", request)
        reply_path = self.folder / "correction.json"
        while not reply_path.exists():
            self.check_deadline()
            time.sleep(0.05)
        self.check_deadline()
        if reply_path.stat().st_size > 8192:
            raise CoordinatorStop("invalid_correction", "Coordinator reply exceeds the size limit")
        reply = json.loads(reply_path.read_text())
        correction = reply.get("correction")
        if (set(reply) != {"handoff_id", "correction"} or reply.get("handoff_id") != handoff_id
                or not isinstance(correction, str) or not 1 <= len(correction.strip()) <= 2000):
            raise CoordinatorStop("invalid_correction", "Supply one correction for the current handoff ID")
        self.journal.write("coordinator_correction", step=step, correction=correction,
                           handoff_id=handoff_id, monotonic_ns=time.monotonic_ns())
        # Observe after the pause. No action with an uncertain result reaches this path.
        agent.state["page"] = agent.browser.observe(screenshot=False)
        self.check_deadline()
        agent.state["goal"] = request["original_goal"] + (
            "\nCoordinator correction for the next decision: " + correction.strip()
            + "\nPreserve the original goal and all action and stopping boundaries."
        )
        agent.pending_text = None
        agent.state["decision"] = None
        agent.state.pop("confirm_done", None)
        agent.state["status"] = "ready"
        self.previous, self.unchanged = visible_state(agent.state["page"]), 0
        self.journal.write("coordinator_resumed", step=step, handoff_id=handoff_id,
                           worker_pid=os.getpid(), browser_target=getattr(agent.browser, "target", None),
                           decisions_remaining=max_decisions-step, seconds_remaining=self.deadline-time.monotonic(),
                           monotonic_ns=time.monotonic_ns())
        return True
