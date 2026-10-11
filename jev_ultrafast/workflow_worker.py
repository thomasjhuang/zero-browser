"""Bounded observed-control steps in one owned browser session."""

import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urldefrag, urlsplit

from scripts.milestone import require_allowed, require_page

from .bounded_worker import normalized, observe_field
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


class TargetResolutionError(ValueError):
    pass


def observed_candidates(page, kind, target):
    choices = [a for a in page["actions"] if a["kind"] == kind and normalized(a["label"]) == normalized(target)]
    if len(choices) != 1:
        raise TargetResolutionError("missing_target" if not choices else "ambiguous_target")
    return choices


def observation(browser, journal, allowed_hosts):
    page = browser.observe(screenshot=False)
    require_page(page)
    if urlsplit(page["url"]).hostname not in allowed_hosts:
        raise ValueError("boundary_violation: navigation left the permitted hosts")
    page["identity"] = browser.evaluate("""(() => ({
      page_url: location.href, headings: [...document.querySelectorAll('h1')].filter(e =>
        e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})).map(e => e.innerText.trim()),
      canonical_url: document.querySelector('link[rel="canonical"]')?.href || null
    }))()""")
    if isinstance(page["identity"], dict) and page["identity"].get("page_url", page["url"]) != page["url"]:
        raise StalePage("Page changed during identity observation")
    journal.write("observation", page=page, monotonic_ns=time.monotonic_ns())
    return page


def public_observation(page):
    return {k: page[k] for k in ("url", "title", "text", "actions", "identity") if k in page}


def exact_identity(page, expected):
    identity = page.get("identity") or {}
    return isinstance(identity, dict) and any(
        normalized(h) == normalized(expected) for h in identity.get("headings", [])
    )


def link_destination(page, href, label):
    if not href:
        return False
    if urldefrag(page["url"])[0] == urldefrag(href)[0]:
        return True
    identity = page.get("identity") or {}
    return (
        isinstance(identity, dict)
        and exact_identity(page, label)
        and identity.get("canonical_url") == urldefrag(page["url"])[0]
    )


def failure(category, cause, unresolved=False, page=None):
    return {
        "status": "uncertainty",
        "action_executed": None if unresolved else False,
        "page_changed": None if unresolved else False,
        "outcome_achieved": False,
        "unresolved_execution": unresolved,
        "first_failure": {"category": category, "cause": cause},
        "observation": public_observation(page) if page else None,
    }


def execute_observed(browser, page, action, text, journal, allowed_hosts, source):
    require_allowed(action)
    href = (
        browser.evaluate("(n => window.__jevFast.nodes.get(n)?.href || null)(" + json.dumps(action.get("node")) + ")")
        if action["kind"] == "click"
        else None
    )
    if href and urlsplit(href).hostname not in allowed_hosts:
        return failure("boundary_violation", "The observed link leaves the permitted hosts", page=page)
    details = {"action": action, "text": text, "href": href, "from_url": page["url"], "source": source}
    journal.write("mutation_started", **details, monotonic_ns=time.monotonic_ns())
    try:
        browser.act(action, page, text=text)
    except StalePage as error:
        journal.write("rejected", execution="not_executed", cause=str(error), monotonic_ns=time.monotonic_ns())
        return {"rejected": True, "action_executed": False}
    except Exception as error:
        journal.write("mutation_uncertain", cause=str(error), **details)
        return failure("execution_failure", "Unknown input result. Do not replay it", unresolved=True, page=page)
    journal.write("executed", **details, monotonic_ns=time.monotonic_ns())
    try:
        after = observation(browser, journal, allowed_hosts)
        deadline = time.monotonic() + 5
        while (
            after["fingerprint"] == page["fingerprint"] or (href and not link_destination(after, href, action["label"]))
        ) and time.monotonic() < deadline:
            time.sleep(0.1)
            after = observation(browser, journal, allowed_hosts)
    except Exception as error:
        result = failure("observation_failure", str(error))
        result.update(action_executed=True, page_changed=None)
        return result
    return {
        "action_executed": True,
        "page_changed": after["fingerprint"] != page["fingerprint"],
        "unresolved_execution": False,
        "observed_href": href,
        "page": after,
    }


def exact_step(browser, kind, target, value, allowed_hosts, journal):
    for _ in range(3):
        page = observation(browser, journal, allowed_hosts)
        try:
            action = observed_candidates(page, kind, target)[0]
        except TargetResolutionError as error:
            return failure(str(error), "The requested control is not uniquely observed", page=page)
        result = execute_observed(
            browser, page, action, value if kind == "fill" else None, journal, allowed_hosts, "deterministic"
        )
        if result.get("rejected"):
            continue
        if "page" not in result:
            return result
        after = result.pop("page")
        if kind == "fill":
            field = observe_field(browser, action["node"])
            achieved = bool(field and field["value"] == value)
        elif kind == "click":
            achieved = link_destination(after, result["observed_href"], action["label"])
        else:
            achieved = after["scroll"] != page["scroll"]
        result.update(
            status="success" if achieved else "uncertainty",
            outcome_achieved=achieved,
            observation=public_observation(after),
            evidence={
                "before_url": page["url"],
                "after_url": after["url"],
                "predicate": "exact_field_value"
                if kind == "fill"
                else "observed_link_destination"
                if kind == "click"
                else "scroll_position_changed",
            },
        )
        if not achieved:
            result["first_failure"] = {
                "category": "outcome_not_observed",
                "cause": "Input executed but the requested outcome was not observed",
            }
        return result
    return failure("rejected_decisions", "Three decisions were rejected before execution")


def run_control(browser, task, choose, journal):
    # Retain the existing internal entry point. Exact controls do not need model approval.
    return exact_step(browser, task["kind"], task["target"], "", task["allowed_hosts"], journal)


def search_open(browser, target, value, allowed_hosts, choose, journal):
    """Fill a supplied field, then open a result with the exact requested visible heading."""
    initial = observation(browser, journal, allowed_hosts)
    filled = exact_step(browser, "fill", target, value, allowed_hosts, journal)
    if not filled["outcome_achieved"]:
        return filled
    executed, changed, last = filled["action_executed"], filled["page_changed"], filled["observation"]
    history, rejected = [], 0

    def failed(category, cause, unresolved=False):
        result = failure(category, cause, unresolved=unresolved, page=last)
        result.update(action_executed=executed or (None if unresolved else False), page_changed=changed)
        return result

    def success(page):
        return {
            "status": "success",
            "action_executed": executed,
            "page_changed": changed,
            "outcome_achieved": True,
            "unresolved_execution": False,
            "observation": public_observation(page),
            "evidence": {
                "predicate": "new_page_exact_visible_heading",
                "query": value,
                "before_url": initial["url"],
                "after_url": page["url"],
                "identity": page["identity"],
            },
        }

    for step in range(3):
        try:
            page = observation(browser, journal, allowed_hosts)
            last = page
            if page["url"] != initial["url"] and exact_identity(page, value):
                return success(page)
            candidates = [a for a in page["actions"] if a["kind"] == "click"]
            goal = json.dumps(
                {
                    "outcome": "Search for the supplied query and open the exact matching result page",
                    "query": value,
                    "permitted_actions": ["click"],
                    "submission_permitted": True,
                    "stop_when": "A new page has a visible main heading exactly equal to the query",
                }
            )
            decision = choose({**page, "actions": candidates}, goal, history)
            journal.write("decision", source="qwen", **decision)
            action = next((a for a in candidates if a["id"] == decision["choice"]), None)
            if action is None:
                return failed("incorrect_decision", "The model stopped or selected an unavailable action")
            result = execute_observed(browser, page, action, None, journal, allowed_hosts, "qwen")
        except Exception as error:
            return failed("decision_or_observation_failure", str(error))
        if result.get("rejected"):
            rejected += 1
            if rejected == 3:
                return failed("rejected_decisions", "Three decisions were rejected before input")
            continue
        executed |= result.get("action_executed") is True
        changed |= result.get("page_changed") is True
        if "page" not in result:
            if result.get("observation"):
                last = result["observation"]
            issue = result["first_failure"]
            return failed(issue["category"], issue["cause"], result.get("unresolved_execution", False))
        last = result["page"]
        history.append({"action": action["label"], "kind": "click", "page_changed": result["page_changed"]})
        if last["url"] != initial["url"] and exact_identity(last, value):
            return success(last)
    return failed("action_budget", "The exact requested result was not observed within the action budget")


def run_step(browser, kind, target, value, outcome, allowed_hosts, choose, journal):
    if kind == "search_open":
        return search_open(browser, target, value, allowed_hosts, choose, journal)
    if kind not in {"fill", "click", "scroll"}:
        raise ValueError("Unsupported subtask kind")
    return exact_step(browser, kind, target, value, allowed_hosts, journal)


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
                result = structured_choose(request["state"], request["goal"], request["history"], bounded=True)
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
