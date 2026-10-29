import json
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

from jev_ultrafast.replay_cache import load_actions, save_actions
from scripts.worker_benchmark import ROOT, execute_case, main, remember_pass, run_two


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


def test_open_casa_flora_is_registered_on_the_hotel_fixture():
    from jev_ultrafast.bounded_worker import validate_task
    from scripts.worker_benchmark import independent_outcome

    cases = json.loads((ROOT / "fixtures/worker_tasks.json").read_text())["cases"]
    case = next(item for item in cases if item["name"] == "open-casa-flora")
    assert case["page"] == "fixture.html"
    validate_task(case["task"])
    opened = {"url": "http://127.0.0.1/fixture.html?scenario=travel#casa-flora", "text": "Casa Flora"}
    result = {"status": "success", "unresolved_execution": False}
    assert independent_outcome(case, {}, opened, result)["passed"] is True


def test_two_cases_load_weights_once(monkeypatch):
    from jev_ultrafast import local_model

    loads = []
    monkeypatch.setattr(local_model, "_MODEL", None)
    monkeypatch.setattr(local_model, "_MODEL_INFO", None)
    monkeypatch.setattr(local_model, "_load_model",
                        lambda: loads.append("weights") or (("model", "tokenizer", None), {"model_load_ms": 1}))

    def run_case(_request):
        local_model.get_model()
        return 0

    monkeypatch.setattr("scripts.worker_benchmark.run_case", run_case)
    code = run_two({"cases": [{"name": "one"}, {"name": "two"}], "journals": ["one.jsonl", "two.jsonl"],
                    "method": "structured"})
    assert code == 0
    assert loads == ["weights"]


def test_pair_starts_one_process(monkeypatch, tmp_path):
    from scripts import worker_benchmark as bench

    names = [case["name"] for case in json.loads((ROOT / "fixtures/worker_tasks.json").read_text())["cases"][:2]]
    started = []

    def supervise(cmd, **_kwargs):
        started.append(cmd)
        return 0

    monkeypatch.setattr(bench, "supervise", supervise)
    monkeypatch.setattr(bench, "isolated_browser", lambda: nullcontext())
    monkeypatch.setattr(bench, "single_run", lambda: nullcontext())
    monkeypatch.setattr(bench, "cancellation_signals", lambda: nullcontext())
    monkeypatch.setattr(bench, "worker_memory_limit", lambda: 2**30)
    assert main(["--pair", *names, "--output", str(tmp_path / "out.json")]) == 0
    assert len(started) == 1
    request = json.loads(Path(started[0][-1]).read_text())
    assert [case["name"] for case in request["cases"]] == names
    assert started[0][-2] == "--worker"
