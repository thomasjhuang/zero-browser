import json
from types import SimpleNamespace

import pytest

from jev_ultrafast import local_policy, model


def scored(candidates, selected):
    return {
        "selected_action": next(c for c in candidates if c["id"] == selected),
        "scores": {c["id"]: float(c["id"] == selected) for c in candidates},
        "prompt_tokens": 10,
    }


def test_local_choice_uses_only_the_selected_operations_targets(monkeypatch):
    state = {"url": "https://example.test", "title": "Search", "text": "City Search", "actions": [
        {"id": "click-button", "kind": "click", "node": 1, "label": "Search"},
        {"id": "fill-city", "kind": "fill", "node": 2, "label": "City", "value": "",
         "context": "Destination", "empty": "true", "required": "true", "placeholder": "Enter a city"},
    ]}
    state["actions"].extend({"id": f"extra-{i}", "kind": "click", "node": i + 3, "label": f"Help {i}"}
                           for i in range(24))
    calls = []

    def score(goal, observation, candidates):
        calls.append(candidates)
        return scored(candidates, "TYPE_TEXT" if len(calls) == 1 else "2")

    monkeypatch.setattr(local_policy, "_score", score)
    answer = local_policy.local_choose(state, "Search Lisbon", [])
    assert answer["choice"] == "fill-city"
    assert answer["operation"] == "TYPE_TEXT"
    assert answer["target"] == "2"
    assert {c["id"] for c in calls[1]} == {"2"}
    assert answer["probabilities"] == {"fill-city": 1.0}
    assert answer["usage"]["prompt_tokens"] == 20
    assert json.loads(calls[1][0]["description"]) == {
        "label": "City", "current_value": "", "context": "Destination", "empty": "true",
        "required": "true", "placeholder": "Enter a city",
    }


@pytest.mark.parametrize("selected,operation,target", [("type", "TYPE_TEXT", "1"), ("option", "SELECT", "2:1")])
def test_joint_menu_executes_only_its_concrete_observed_action(monkeypatch, selected, operation, target):
    state = {"url": "https://example.test", "title": "Search", "text": "", "actions": [
        {"id": "type", "kind": "fill", "node": 1, "label": "City", "value": "",
         "context": "Destination", "empty": "true", "required": "true", "placeholder": "Enter a city"},
        {"id": "open", "kind": "click", "node": 1, "label": "Open City", "value": ""},
        {"id": "option", "kind": "select", "node": 2, "label": "Count → 1", "current_value": "2", "value": "1"},
        {"id": "search", "kind": "click", "node": 3, "role": "button", "label": "Search", "value": ""},
    ]}
    calls = []

    def score(goal, observation, candidates):
        calls.append(candidates)
        return scored(candidates, selected)

    monkeypatch.setattr(local_policy, "_score", score)
    answer = local_policy.local_choose(state, "Search a city", [])
    assert len(calls) == 1
    assert (answer["choice"], answer["operation"], answer["target"]) == (selected, operation, target)
    assert answer["usage"]["prompt_tokens"] == 10
    assert {c["id"] for c in calls[0]} == {"type", "open", "option", "search", "DONE", "BLOCKED"}
    assert next(c["description"] for c in calls[0] if c["id"] == "search") == "Search"
    description = calls[0][0]["description"]
    assert '"context": "Destination"' in description
    assert '"empty": "true"' in description
    assert '"required": "true"' in description
    assert '"placeholder": "Enter a city"' in description


def test_large_target_groups_rescore_winners_together(monkeypatch):
    candidates = [{"id": str(i)} for i in range(45)]
    calls = []

    def score(goal, observation, group):
        calls.append([c["id"] for c in group])
        return scored(group, group[-1]["id"])

    monkeypatch.setattr(local_policy, "_score", score)
    records = []
    answer = local_policy._select("Goal", "Page", candidates, records)
    assert calls == [list(map(str, range(20))), list(map(str, range(20, 40))),
                     list(map(str, range(40, 45))), ["19", "39", "44"]]
    assert answer["selected_action"]["id"] == "44"
    assert len(records) == 4


@pytest.mark.parametrize("bad", ['{"text":null}', '{"text":""}', '{"text":7}',
                                 '{"text":"City","extra":true}', 'not JSON', '["City"]'])
def test_text_helper_retries_invalid_output_once_then_stops(monkeypatch, bad):
    import mlx_lm

    calls = []
    tokenizer = SimpleNamespace(apply_chat_template=lambda *a, **k: "prompt",
                                encode=lambda text, **k: list(text))
    monkeypatch.setattr(local_policy, "get_model", lambda: (None, tokenizer, None))
    monkeypatch.setattr(mlx_lm, "generate", lambda *a, **k: calls.append(k) or bad)
    with pytest.raises(ValueError, match="Nothing typed"):
        local_policy.local_field_text({"goal": "Search Lisbon"})
    assert len(calls) == 2
    assert all(call["max_tokens"] == 128 for call in calls)


def test_text_helper_can_recover_without_an_extra_model_load(monkeypatch):
    import mlx_lm

    outputs = iter(['{"text":null}', json.dumps({"text": "Lisbon"})])
    loads = []
    prompts = []

    def template(messages, **kwargs):
        prompts.append(messages)
        assert kwargs["enable_thinking"] is False
        return "prompt"

    tokenizer = SimpleNamespace(apply_chat_template=template, encode=lambda text, **k: list(text))
    monkeypatch.setattr(local_policy, "get_model", lambda: loads.append(1) or (None, tokenizer, None))
    monkeypatch.setattr(mlx_lm, "generate", lambda *a, **k: next(outputs))
    text, info = local_policy.local_field_text({"goal": "Find Design stays in Lisbon", "field": "Destination"})
    assert text == "Lisbon"
    assert len(loads) == 1
    assert len(prompts) == 2
    assert info["usage"]["completion_tokens"] > 0


def test_local_mode_cannot_call_hosted_models_even_with_credentials(monkeypatch):
    monkeypatch.setenv("JEV_LOCAL", "1")
    monkeypatch.setenv("TYPESAFE_API_KEY", "synthetic-key")
    monkeypatch.setenv("TEXT_MODEL_API_KEY", "synthetic-key")
    monkeypatch.setattr(model, "post_json", lambda *a: pytest.fail("A hosted model was called"))
    monkeypatch.setattr(local_policy, "local_choose", lambda *a: {"choice": "DONE"})
    monkeypatch.setattr(local_policy, "local_field_text", lambda *a: ("Lisbon", {}))
    assert model.choose({}, "Goal", [])["choice"] == "DONE"
    assert model.field_text({}) == ("Lisbon", {})
