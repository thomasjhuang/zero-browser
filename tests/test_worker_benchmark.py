from types import SimpleNamespace

from jev_ultrafast.replay_cache import load_actions, save_actions
from scripts.worker_benchmark import execute_case, remember_pass


def city_page():
    return {
        "url": "http://127.0.0.1:9/form",
        "title": "Form",
        "text": "Form",
        "actions": [{"id": "city", "kind": "fill", "label": "City", "value": "", "node": 1}],
    }


def task():
    return {"outcome": "Set City to Lima", "kind": "fill", "target": "City", "value": "Lima",
            "permitted_actions": ["fill"],
            "stopping_conditions": ["outcome_observed", "human_required", "boundary_violation"],
            "deadline_seconds": 10, "action_budget": 2}


def test_a_missing_later_target_is_not_a_completed_hit(tmp_path, monkeypatch):
    page = city_page()
    save_actions(tmp_path, task()["outcome"], page, [
        {"operation": "fill", "target": "City", "value": "Lima"},
        {"operation": "click", "target": "Lima port"},
    ])
    acted = []
    calls = []

    def run_bounded(*_args, **_kwargs):
        calls.append("model")
        return {"status": "failure", "executed_actions": [], "unresolved_execution": False}

    monkeypatch.setattr("jev_ultrafast.bounded_worker.run_bounded", run_bounded)
    browser = SimpleNamespace(observe=lambda **_k: page, act=lambda *_a, **_k: acted.append(1))
    _page, replayed, result = execute_case(browser, task(), None, SimpleNamespace(write=lambda *_a, **_k: None),
                                           tmp_path)
    assert replayed is None
    assert calls == ["model"]
    assert acted == []
    assert result["status"] == "failure"


def test_a_complete_action_list_skips_the_model(tmp_path, monkeypatch):
    page = city_page()
    steps = [{"operation": "fill", "target": "City", "value": "Lima"}]
    save_actions(tmp_path, task()["outcome"], page, steps)
    acted = []

    def run_bounded(*_args, **_kwargs):
        raise AssertionError("model called")

    monkeypatch.setattr("jev_ultrafast.bounded_worker.run_bounded", run_bounded)
    browser = SimpleNamespace(
        observe=lambda **_k: page,
        act=lambda action, _observed, text=None: acted.append((action["label"], text)),
    )
    _page, replayed, result = execute_case(browser, task(), None, SimpleNamespace(write=lambda *_a, **_k: None),
                                           tmp_path)
    assert replayed == steps
    assert acted == [("City", "Lima")]
    assert result["unresolved_execution"] is False
    assert remember_pass(tmp_path, task()["outcome"], page, replayed, result, False) is None
    history = [{"kind": "fill", "action": "City", "text": "Lima"}]
    assert remember_pass(tmp_path, "Set City to Lima", page, None, {"executed_actions": history}, True)
    assert load_actions(tmp_path, "Set City to Lima", page) == steps
