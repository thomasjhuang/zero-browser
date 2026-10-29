"""Observe a page, extract visible fields, then run a short action list.

The caller supplies the already observed page or an object with observe and act.
This module does not call a hosted crawler.
"""


def _label(action):
    return str(action.get("label", "")).split("→")[0].strip()


def _same(left, right):
    return " ".join(str(left).casefold().split()) == " ".join(str(right).casefold().split())


def extract_fields(page):
    fields = []
    seen = set()
    for action in page.get("actions") or []:
        if action.get("kind") not in {"fill", "select"}:
            continue
        label = _label(action)
        key = (action.get("node"), label.casefold(), action["kind"])
        if key in seen:
            continue
        seen.add(key)
        if action["kind"] == "select":
            value = action.get("current_value", "")
        else:
            value = action.get("value", "")
        text = "" if value is None else str(value)
        fields.append({
            "id": action.get("id"),
            "node": action.get("node"),
            "label": label,
            "kind": action["kind"],
            "value": text,
            "empty": action.get("empty") in {True, "true"} or not text.strip(),
        })
    return fields


def _matches(page, step):
    operation = step.get("operation")
    target = step.get("target", "")
    value = step.get("value")
    found = []
    for action in page.get("actions") or []:
        if operation == "fill" and action.get("kind") == "fill" and _same(_label(action), target):
            found.append(action)
        elif operation == "click" and action.get("kind") == "click" and _same(action.get("label", ""), target):
            found.append(action)
        elif operation == "select" and action.get("kind") == "select" and _same(_label(action), target):
            option = str(action.get("label", "")).split("→")[-1].strip()
            if value is None or _same(option, value) or _same(action.get("value", ""), value):
                found.append(action)
    return found


def prepare(page, steps):
    fields = extract_fields(page)
    actions = []
    for step in steps:
        matches = _matches(page, step)
        if len(matches) != 1:
            return {"fields": fields, "actions": actions,
                    "error": "ambiguous" if len(matches) > 1 else "missing", "target": step.get("target")}
        chosen = matches[0]
        actions.append({
            "operation": step["operation"],
            "id": chosen.get("id"),
            "label": chosen.get("label"),
            "text": step.get("value") if step["operation"] == "fill" else None,
            "observed": chosen,
        })
    return {"fields": fields, "actions": actions, "error": None}


def run_controls(browser, steps):
    page = browser.observe(screenshot=False)
    prepared = prepare(page, steps)
    executed = []
    if prepared["error"]:
        return {**prepared, "executed": executed}
    for step in prepared["actions"]:
        browser.act(step["observed"], page, text=step["text"])
        executed.append(step["id"])
        page = browser.observe(screenshot=False)
    return {"fields": extract_fields(page), "actions": prepared["actions"], "executed": executed, "error": None}
