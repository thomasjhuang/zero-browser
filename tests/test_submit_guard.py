"""Submit stays out of the menu while a required field is empty. No browser."""

from jev_ultrafast import local_policy
from jev_ultrafast.agent import Agent
from jev_ultrafast.submit_guard import (
    actions_for_unset_required,
    completion_allowed,
    field_names,
    without_premature_submit,
)


def actions(origin="", cabin="Economy"):
    return [
        {"id": "origin", "kind": "fill", "label": "Origin", "value": origin, "node": 1,
         "empty": "false" if origin else "true"},
        {"id": "open-origin", "kind": "click", "label": "Open Origin", "value": origin, "node": 1},
        {"id": "cabin", "kind": "select", "label": "Cabin → Other", "current_value": cabin, "value": "Other",
         "node": 2},
        {"id": "submit", "kind": "click", "role": "button", "label": "Search flights", "submits": "true", "node": 3},
        {"id": "help", "kind": "click", "role": "button", "label": "Help topic 1", "node": 4},
    ]


def test_field_names_do_not_include_answers():
    assert field_names({"origin": "Hidden City", "adults": "9"}) == ["origin", "adults"]
    assert field_names(None) == []


def test_submit_is_hidden_while_a_required_field_is_empty():
    visible = without_premature_submit(actions(), ["origin", "cabin"])
    assert [item["id"] for item in visible] == ["origin", "open-origin", "cabin", "help"]


def test_submit_remains_when_required_fields_have_values():
    visible = without_premature_submit(actions(origin="filled"), ["origin", "cabin"])
    assert any(item["id"] == "submit" for item in visible)


def test_done_is_hidden_while_a_required_field_is_empty(monkeypatch):
    state = {"url": "http://fixture", "title": "Form", "text": "", "actions": actions()}
    seen = {}

    def score(_goal, _observation, candidates):
        seen["ids"] = {item["id"] for item in candidates}
        return {"selected_action": candidates[0], "scores": {item["id"]: float(item is candidates[0])
                                                             for item in candidates}, "prompt_tokens": 1}

    monkeypatch.setattr(local_policy, "_score", score)
    local_policy.local_choose(state, "Complete the form", [], required_fields=["origin"])
    assert "DONE" not in seen["ids"]
    assert "BLOCKED" not in seen["ids"]
    assert completion_allowed(actions(origin="filled"), ["origin"]) is True


def test_done_returns_after_required_fields_are_filled(monkeypatch):
    state = {"url": "http://fixture", "title": "Form", "text": "", "actions": actions(origin="filled")}
    seen = {}

    def score(_goal, _observation, candidates):
        seen["ids"] = {item["id"] for item in candidates}
        return {"selected_action": next(item for item in candidates if item["id"] == "DONE"),
                "scores": {item["id"]: float(item["id"] == "DONE") for item in candidates}, "prompt_tokens": 1}

    monkeypatch.setattr(local_policy, "_score", score)
    answer = local_policy.local_choose(state, "Complete the form", [], required_fields=["origin", "cabin"])
    assert answer["choice"] == "DONE"
    assert "DONE" in seen["ids"]


def test_unset_required_fields_are_the_only_menu_actions(monkeypatch):
    menu = actions() + [
        {"id": "wait", "kind": "wait", "label": "Wait"},
        {"id": "adults", "kind": "select", "label": "Adults → 1", "current_value": "2", "value": "1", "node": 5},
    ]
    state = {"url": "http://fixture", "title": "Form", "text": "", "actions": menu}
    seen = {}

    def score(_goal, _observation, candidates):
        seen["ids"] = {item["id"] for item in candidates}
        return {"selected_action": candidates[0],
                "scores": {item["id"]: float(item is candidates[0]) for item in candidates},
                "prompt_tokens": 1}

    monkeypatch.setattr(local_policy, "_score", score)
    local_policy.local_choose(state, "Complete the form", [], required_fields=["origin", "adults", "cabin"])
    assert seen["ids"] == {"origin", "open-origin"}
    assert actions_for_unset_required(menu, ["origin"]) == [menu[0], menu[1]]


def test_non_submit_controls_stay_when_fields_are_empty():
    visible = without_premature_submit(actions(), ["origin"])
    assert any(item["id"] == "help" for item in visible)


def test_predict_does_not_offer_submit_while_the_field_is_empty(monkeypatch):
    runner = Agent.__new__(Agent)
    runner.screenshots = False
    runner.pending_text = None
    page = {"actions": actions(), "fingerprint": "same", "title": "Form", "url": "http://fixture", "text": ""}
    runner.state = {
        "browser": type("B", (), {"fresh": lambda self, _page: True, "observe": lambda self, **_k: page})(),
        "page": page,
        "goal": "Complete the form",
        "history": [],
        "decisions": [],
        "status": "ready",
        "started_at": 0,
        "required_fields": ["origin"],
        "record": False,
        "text_calls": [],
    }
    seen = {}

    def choose(offered, _goal, _history, _fields=None):
        seen["ids"] = [item["id"] for item in offered["actions"]]
        return {"choice": "origin", "confidence": 1, "probabilities": {"origin": 1},
                "operation": "TYPE_TEXT", "target": "1", "usage": {}}

    monkeypatch.setattr("jev_ultrafast.agent.choose", choose)
    runner.command("predict")
    assert seen["ids"] == ["origin", "open-origin"]
