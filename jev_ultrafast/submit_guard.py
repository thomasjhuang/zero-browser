"""Keep a form submit out of the decision menu while required fields are empty."""

import re


def field_names(expected):
    if not isinstance(expected, dict):
        return []
    return [key for key in expected if isinstance(key, str) and key]


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


def unset_required_fields(actions, fields):
    missing = []
    for field in fields:
        observed = [action for action in actions
                    if action.get("kind") in {"fill", "select"} and _matches(_label(action), field)]
        if observed and any(_unset(action) for action in observed):
            missing.append(field)
    return missing


def is_submit(action):
    return action.get("kind") == "click" and action.get("submits") in {True, "true"}


def without_premature_submit(actions, fields):
    if not unset_required_fields(actions, fields):
        return actions
    return [action for action in actions if not is_submit(action)]
