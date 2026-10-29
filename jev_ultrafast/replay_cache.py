"""Replay a passed action list on a later page with the same controls. No model."""

import hashlib
import json
from pathlib import Path

from .page_controls import run_controls


def _norm(value):
    return " ".join(str(value or "").casefold().split())


def signature(goal, page):
    controls = []
    for action in page.get("actions") or []:
        kind = action.get("kind")
        label = _norm(action.get("label"))
        if kind == "select":
            current = _norm(action.get("current_value"))
        else:
            current = _norm(action.get("value"))
        controls.append([kind, label, current])
    controls.sort()
    return json.dumps({"goal": _norm(goal), "url": page.get("url") or "", "title": _norm(page.get("title")),
                       "controls": controls}, sort_keys=True)


def _path(directory, goal, page):
    digest = hashlib.sha256(signature(goal, page).encode()).hexdigest()
    return Path(directory) / f"{digest}.json"


def save_actions(directory, goal, page, steps):
    if not steps:
        return None
    path = _path(directory, goal, page)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"actions": steps}, indent=2) + "\n")
    return path


def load_actions(directory, goal, page):
    path = _path(directory, goal, page)
    if not path.is_file():
        return None
    data = json.loads(path.read_text())
    actions = data.get("actions")
    if not isinstance(actions, list) or not actions:
        return None
    return actions


def steps_from_history(history):
    steps = []
    for item in history or []:
        kind = item.get("kind")
        label = str(item.get("action") or "")
        if kind == "fill":
            steps.append({"operation": "fill", "target": label.split("→")[0].strip(), "value": item.get("text")})
        elif kind == "select":
            parts = [part.strip() for part in label.split("→")]
            steps.append({"operation": "select", "target": parts[0],
                          "value": parts[-1] if len(parts) > 1 else item.get("text")})
        elif kind == "click":
            steps.append({"operation": "click", "target": label})
    return steps


def replay(browser, steps):
    return run_controls(browser, steps)


def cached_steps(directory, goal, page, browser):
    """Replay a stored list. None means the caller must run the model."""
    steps = load_actions(directory, goal, page)
    if not steps:
        return None
    result = replay(browser, steps)
    if not isinstance(result, dict) or result.get("error") or not result.get("executed"):
        return None
    return steps
