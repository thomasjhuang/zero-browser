"""One explicit field outcome. Model choices never expand the supplied boundary."""

import json
import time
import unicodedata

from .browser import StalePage


def normalized(value):
    return " ".join(unicodedata.normalize("NFKC", str(value)).casefold().split())


def validate_task(task):
    required = {"outcome", "kind", "target", "value", "permitted_actions", "stopping_conditions",
                "deadline_seconds", "action_budget"}
    if not required <= set(task) or task["kind"] not in {"fill", "select", "autocomplete", "click"}:
        raise ValueError("Supply one supported field outcome and its limits")
    if task["kind"] == "click" and task["permitted_actions"] != ["click"]:
        raise ValueError("A click outcome permits only the click control")
    if any(not isinstance(task[k], str) or not task[k].strip() for k in ("outcome", "target", "value")):
        raise ValueError("Outcome, target, and supplied value must be nonempty strings")
    if (type(task["action_budget"]) is not int or not 1 <= task["action_budget"] <= 8
            or type(task["deadline_seconds"]) not in (int, float) or not 1 <= task["deadline_seconds"] <= 60):
        raise ValueError("The worker supports at most eight actions and a sixty-second deadline")
    if (not isinstance(task["permitted_actions"], list)
            or not set(task["permitted_actions"]) <= {"fill", "select", "click", "wait"}
            or task["stopping_conditions"] != ["outcome_observed", "human_required", "boundary_violation"]):
        raise ValueError("Unsupported action boundary or stopping conditions")


def goal_met(page, task, evidence=None, selected_suggestion=False):
    """Whether the task outcome is already visible, even if its control has gone."""
    if task["kind"] == "click":
        return task["value"] in str(page.get("url") or "")
    if not evidence:
        return False
    matches = normalized(evidence.get("value")) == normalized(task["value"])
    if task["kind"] == "select":
        matches = matches or normalized(evidence.get("selected_text")) == normalized(task["value"])
    if task["kind"] == "autocomplete":
        matches = matches and selected_suggestion and evidence.get("expanded") == "false"
    return matches


def target_actions(page, task):
    if task["kind"] == "click":
        actions = [a for a in page["actions"] if a["kind"] == "click"
                   and normalized(a.get("label", "")) == normalized(task["target"])]
    else:
        actions = [a for a in page["actions"] if a["kind"] in {"fill", "select"}
                   and normalized(a["label"].split(" → ")[0]) == normalized(task["target"])]
    nodes = {a["node"] for a in actions}
    if len(nodes) != 1:
        return [], "missing_target" if not nodes else "ambiguous_target"
    if task["kind"] == "click":
        return actions, None
    if task["kind"] == "select" and any(a["kind"] != "select" for a in actions):
        return [], "unsupported_target"
    if task["kind"] != "select" and any(a["kind"] != "fill" for a in actions):
        return [], "unsupported_target"
    return actions, None


def observe_field(browser, node):
    # The node comes from the browser observer. Neither the model nor the caller supplies a selector.
    return browser.evaluate(r"""(node => {
      const e=window.__jevFast?.nodes.get(node);
      if (!e?.isConnected) return null;
      const ids=(e.getAttribute('aria-controls')||e.getAttribute('aria-owns')||'').split(/\s+/).filter(Boolean);
      const roots=ids.map(id=>document.getElementById(id)).filter(Boolean);
      const optionNodes=[...window.__jevFast.nodes].filter(([id,n])=>
        n.getAttribute('role')==='option' && roots.some(root=>root.contains(n))).map(([id])=>id);
      return {value:e.value??e.innerText, expanded:e.getAttribute('aria-expanded'),
        selected_text:e.tagName==='SELECT' ? [...e.selectedOptions].map(o=>o.label).join(', ') : null,
        option_nodes:optionNodes};
    })(""" + json.dumps(node) + ")")


def permitted_candidates(page, task, node, evidence, options):
    """Expose only meaningful actions inside the caller's exact field contract."""
    candidates = []
    for action in page["actions"]:
        kind = action["kind"]
        if kind not in task["permitted_actions"]:
            continue
        if kind == "fill" and action.get("node") == node:
            if str(evidence["value"]) != task.get("query", task["value"]):
                candidates.append(action)
        elif kind == "select" and action.get("node") == node:
            if (normalized(action["value"]) == normalized(task["value"])
                    or normalized(action["label"].split(" → ")[-1]) == normalized(task["value"])):
                candidates.append(action)
        elif (kind == "click" and task["kind"] == "click"
              and normalized(action.get("label", "")) == normalized(task["target"])):
            candidates.append(action)
        elif kind == "click" and task["kind"] == "autocomplete" and action in options:
            candidates.append(action)
        elif (kind == "wait" and task["kind"] == "autocomplete" and evidence["expanded"] == "true"
              and not evidence["option_nodes"]):
            candidates.append(action)
    return candidates


def run_bounded(browser, task, choose, journal):
    from scripts.milestone import HumanRequired, require_allowed, require_page

    validate_task(task)
    started = time.monotonic()
    history, claims, evidence = [], [], None
    selected_suggestion, rejected = False, 0

    def finish(status, category=None, cause=None):
        failure_step = len(history) if history and history[-1]["execution"] == "uncertain" else len(history)+1
        result = {"status": status, "evidence": evidence, "executed_actions": history,
                  "model_claims": claims, "unresolved_execution": any(h["execution"] == "uncertain" for h in history),
                  "elapsed_ms": round((time.monotonic()-started)*1000),
                  "first_failure": {"step": failure_step, "category": category, "cause": cause} if category else None}
        journal.write("worker_result", result=result)
        return result

    try:
        while True:
            if time.monotonic()-started >= task["deadline_seconds"]:
                return finish("uncertainty", "deadline", "The task deadline ended")
            page = browser.observe(screenshot=False)
            journal.write("observation", page=page)
            require_page(page)
            if goal_met(page, task, selected_suggestion=selected_suggestion):
                return finish("success")
            targets, problem = target_actions(page, task)
            if problem:
                return finish("uncertainty", problem, "The supplied target does not identify one editable control")
            node = targets[0]["node"]
            evidence = observe_field(browser, node)
            if evidence is None:
                if goal_met(page, task, selected_suggestion=selected_suggestion):
                    return finish("success")
                return finish("uncertainty", "missing_target", "The observed target disappeared")
            if goal_met(page, task, evidence, selected_suggestion):
                return finish("success")
            if len(history) >= task["action_budget"]:
                return finish("failure", "action_budget", "The supplied outcome was not observed")
            options = [a for a in page["actions"] if a.get("node") in evidence["option_nodes"]
                       and normalized(a["label"]) == normalized(task["value"])]
            if len({a["node"] for a in options}) > 1:
                return finish("uncertainty", "ambiguous_target", "Multiple matching suggestions are visible")
            candidates = permitted_candidates(page, task, node, evidence, options)
            if not candidates:
                return finish("uncertainty", "missing_target", "No supported action can reach the supplied value")
            supplied = json.dumps({"target": task["target"], "value": task["value"]})
            if task["kind"] == "click":
                limit = "Choose the named control. Do not submit."
            else:
                limit = ("Do not submit, navigate away, change other fields, or choose other values. "
                         "The supplied value will be used for text entry. Stop after this one field outcome.")
            goal = (task["outcome"] + "\nSupplied values: " + supplied
                    + "\nPermitted actions: " + json.dumps(task["permitted_actions"])
                    + "\n" + limit)
            try:
                decision = choose({**page, "actions": candidates}, goal, history)
            except ValueError as error:
                return finish("failure", "incorrect_decision", str(error))
            claims.append(decision.get("model_claims", {}))
            journal.write("decision", step=len(history)+1, **decision)
            if decision["choice"] in {"DONE", "BLOCKED"}:
                return finish("failure", "false_completion" if decision["choice"] == "DONE" else "wrong_decision",
                              "The model stopped before the supplied outcome was observed")
            action = next((a for a in page["actions"] if a["id"] == decision["choice"]), None)
            if action is None:
                return finish("failure", "wrong_decision", "The model selected an unsupported target")
            require_allowed(action)
            if action not in candidates:
                return finish("failure", "boundary_violation", "The action exceeds the supplied field boundary")
            text = task.get("query", task["value"]) if action["kind"] == "fill" else None
            journal.write("mutation_started", step=len(history)+1, action=action, text=text)
            try:
                browser.act(action, page, text=text)
            except StalePage as error:
                rejected += 1
                journal.write("rejected", step=len(history)+1, cause=str(error))
                if rejected >= 3:
                    return finish("uncertainty", "rejected_decisions", "Three decisions were rejected before execution")
                continue
            except Exception as error:
                history.append({"action": action["label"], "kind": action["kind"], "text": text,
                                "execution": "uncertain"})
                journal.write("mutation_uncertain", cause=str(error))
                return finish("uncertainty", "execution_failure", "The action result is unknown. Do not replay it")
            rejected = 0
            history.append({"action": action["label"], "kind": action["kind"], "text": text,
                            "execution": "executed", "page_changed": None})
            journal.write("executed", step=len(history), action=action, text=text)
            selected_suggestion |= action in options and action["kind"] == "click"
    except HumanRequired as error:
        return finish("uncertainty", "human_required", str(error))
    except Exception as error:
        return finish("uncertainty", "execution_failure", str(error))
