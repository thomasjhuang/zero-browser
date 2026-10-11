from types import SimpleNamespace

import pytest

from jev_ultrafast.bounded_worker import permitted_candidates, run_bounded, target_actions, validate_task


def task():
    return {"outcome": "Set City to Lima", "kind": "fill", "target": "City", "value": "Lima",
            "permitted_actions": ["fill"],
            "stopping_conditions": ["outcome_observed", "human_required", "boundary_violation"],
            "deadline_seconds": 10, "action_budget": 2}


def test_missing_or_ambiguous_target_never_reaches_the_model():
    for actions in ([], [{"id": str(i), "node": i, "label": "City", "kind": "fill"} for i in (1, 2)]):
        browser = SimpleNamespace(observe=lambda **kw: {"actions": actions, "text": ""})
        result = run_bounded(browser, task(), lambda *args: pytest.fail("model called"),
                             SimpleNamespace(write=lambda *args, **kw: None))
        assert result["status"] == "uncertainty"
        assert not result["executed_actions"]


def test_uncertain_mutation_is_never_repeated():
    actions = [{"id": "e1", "node": 1, "label": "City", "kind": "fill", "value": ""}]
    calls = []

    def act(*args, **kwargs):
        calls.append(1)
        raise RuntimeError("Connection lost after input")

    browser = SimpleNamespace(observe=lambda **kw: {"actions": actions, "text": ""}, act=act,
                              evaluate=lambda code: {"value": "", "expanded": None, "option_nodes": []})
    result = run_bounded(browser, task(), lambda *args: {"choice": "e1"},
                         SimpleNamespace(write=lambda *args, **kw: None))
    assert calls == [1]
    assert result["status"] == "uncertainty"
    assert result["unresolved_execution"] is True
    assert result["first_failure"]["step"] == 1


def test_limits_and_target_type_fail_closed():
    invalid = {**task(), "action_budget": 100}
    with pytest.raises(ValueError):
        validate_task(invalid)
    assert target_actions({"actions": [{"label": "City", "node": 1, "kind": "select"}]}, task())[1]


def test_candidate_menu_excludes_forbidden_and_unchanged_field_actions():
    fill = {"id": "e1", "node": 1, "label": "City", "kind": "fill"}
    click = {"id": "e2", "node": 1, "label": "Open City", "kind": "click"}
    other = {"id": "e3", "node": 2, "label": "Other city", "kind": "fill"}
    page = {"actions": [fill, click, other]}
    assert permitted_candidates(page, task(), 1, {"value": ""}, []) == [fill]
    assert permitted_candidates(page, task(), 1, {"value": "Lima"}, []) == []
