"""Keep a form submit out of the decision menu while required fields are empty."""

import re


def field_names(expected):
    if not isinstance(expected, dict):
        return []
    return [key for key in expected if isinstance(key, str) and key]


def field_contract(expected):
    if not isinstance(expected, dict):
        return {}
    contract = {}
    for key, value in expected.items():
        if not isinstance(key, str) or not key or isinstance(value, bool):
            continue
        if isinstance(value, (str, int, float)):
            contract[key] = str(value)
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            contract[key] = value
    return contract


def _words(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text).casefold()).strip()


def _label(action):
    return _words(str(action.get("label", "")).split("→")[0])


def _matches(label, field):
    field_words = _words(field.replace("_", " "))
    if not field_words or not label:
        return False
    return label == field_words or label.startswith(field_words + " ")


def _unset(action):
    if action.get("kind") == "fill":
        if action.get("empty") in {True, "true"}:
            return True
        return not str(action.get("value", "")).strip()
    if action.get("kind") == "select":
        return not str(action.get("current_value", "")).strip()
    return False


def _observed_value(action):
    if action.get("kind") == "select":
        return action.get("current_value", "")
    return action.get("value", "")


def _same(observed, expected):
    left = str(observed).strip().casefold()
    if isinstance(expected, list):
        return left in {str(item).strip().casefold() for item in expected}
    return left == str(expected).strip().casefold()


def _requirements(fields):
    if isinstance(fields, dict):
        return list(fields.items())
    return [(name, None) for name in fields or []]


def unset_required_fields(actions, fields):
    missing = []
    for field, expected in _requirements(fields):
        observed = [action for action in actions
                    if action.get("kind") in {"fill", "select"} and _matches(_label(action), field)]
        if not observed:
            continue
        if expected is None:
            if any(_unset(action) for action in observed):
                missing.append(field)
        elif not any(_same(_observed_value(action), expected) for action in observed):
            missing.append(field)
    return missing


def is_submit(action):
    return action.get("kind") == "click" and action.get("submits") in {True, "true"}


def without_premature_submit(actions, fields):
    if not unset_required_fields(actions, fields):
        return actions
    return [action for action in actions if not is_submit(action)]


def completion_allowed(actions, fields):
    return not unset_required_fields(actions, fields)


def _field_nodes(actions, missing):
    nodes = set()
    for action in actions:
        if action.get("node") is None or action.get("kind") not in {"fill", "select"}:
            continue
        if any(_matches(_label(action), field) for field in missing):
            nodes.add(action["node"])
    return nodes


def actions_for_unset_required(actions, fields):
    missing = unset_required_fields(actions, fields)
    if not missing:
        return list(actions)
    nodes = _field_nodes(actions, missing)
    kept = []
    for action in actions:
        if action.get("kind") == "wait" or str(action.get("id", "")).casefold() == "wait":
            continue
        if is_submit(action):
            continue
        if action.get("node") in nodes:
            kept.append(action)
    return kept
