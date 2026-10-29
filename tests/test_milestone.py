"""Exercise milestone evidence and guards without local inference."""

import base64
import copy
import json
import os
import signal
import subprocess
import sys
import time
from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from scripts import milestone, runtime_guard
from scripts.milestone_record import Journal, read_events, summarize
from scripts.milestone_verify import verify_flights, verify_local

MANIFEST = json.loads(milestone.MANIFEST.read_text())


@pytest.mark.parametrize("requirement", list(MANIFEST["tasks"]["local_search"]["expected"]))
def test_each_local_requirement_fails_independently(requirement):
    expected = MANIFEST["tasks"]["local_search"]["expected"]
    actual = {"submitted": dict(expected), "results_visible": True, "selected": False}
    assert verify_local(actual, expected)["passed"]
    actual["submitted"][requirement] = "wrong"
    result = verify_local(actual, expected)
    assert not result["passed"]
    assert [key for key, ok in result["checks"].items() if not ok] == [requirement]


def test_local_completion_requires_submission_results_and_no_selection():
    expected = MANIFEST["tasks"]["local_search"]["expected"]
    assert not verify_local({}, expected)["passed"]
    for key, value in [("submitted", None), ("results_visible", False), ("selected", True)]:
        actual = {"submitted": dict(expected), "results_visible": True, "selected": False, key: value}
        assert not verify_local(actual, expected)["passed"]


def flight_page():
    expected = MANIFEST["tasks"]["sfo_bos"]["expected"]
    encoded = base64.urlsafe_b64encode(expected["date"].encode()).decode()
    return {"url": "https://www.google.com/travel/flights/search?tfs=" + encoded, "text": "",
            "actions": [{"label": label, "value": value} for label, value in [
                ("Where from?", "San Francisco"), ("Where to?", "Boston"),
                ("Departure", "Mon, Nov 16"), ("Change ticket type. One way", "One way"),
                ("1 passenger. 1 adult", ""), ("Change cabin class. Economy", "Economy"),
                ("Select flight departing Monday, November 16", ""),
            ]]}


@pytest.mark.parametrize("index,requirement", [(0, "origin"), (1, "destination"), (2, "departure"),
                                              (3, "trip_type"), (4, "adults"), (5, "cabin"),
                                              (6, "results_visible")])
def test_flight_verifier_rejects_each_missing_control(index, requirement):
    expected = MANIFEST["tasks"]["sfo_bos"]["expected"]
    page = flight_page()
    assert verify_flights(page, expected)["passed"]
    page["actions"].pop(index)
    result = verify_flights(page, expected)
    assert not result["passed"]
    assert not result["checks"][requirement]


def test_flight_verifier_rejects_wrong_year_date_and_generic_passenger_count():
    expected = MANIFEST["tasks"]["sfo_bos"]["expected"]
    page = flight_page()
    page["url"] = page["url"].split("?")[0]
    assert not verify_flights(page, expected)["checks"]["year"]
    page = flight_page()
    page["actions"][-1]["label"] = "Select flight departing Tuesday, November 17"
    assert not verify_flights(page, expected)["checks"]["result_dates"]
    page = flight_page()
    page["actions"][4]["label"] = "1 passenger"
    assert not verify_flights(page, expected)["checks"]["adults"]


def test_verifier_ignores_control_order_and_unrelated_controls():
    page = flight_page()
    page["actions"].reverse()
    page["actions"].extend({"label": f"Help {index}", "value": ""} for index in range(80))
    assert verify_flights(page, MANIFEST["tasks"]["sfo_bos"]["expected"])["passed"]


def test_done_is_separate_from_independent_success():
    events = [{"event": "decision", "step": 4, "operation": "DONE", "latency_ms": 100}]
    assert summarize(events)["model_done"]
    assert not summarize(events)["outcome_verified"]
    events.append({"event": "outcome", "result": {"passed": False}})
    assert summarize(events)["first_observed_failure"]["category"] == "premature_completion"
    events[-1]["result"]["passed"] = True
    events[0]["operation"] = "CLICK"
    assert summarize(events)["outcome_verified"]
    assert not summarize(events)["model_done"]


def test_interrupted_journal_preserves_calls_and_uncertain_mutation(tmp_path):
    path = tmp_path / "events.jsonl"
    journal = Journal(path)
    journal.write("model_call_started", step=1)
    journal.write("mutation_started", step=1)
    with path.open("a") as stream:
        stream.write('{"event":')
    result = summarize(read_events(path))
    assert result["model_calls_started"] == 1
    assert result["model_call_coverage"] == "interrupted"
    assert result["execution_outcome_unknown"]
    assert not result["outcome_verified"]


@pytest.mark.parametrize("label", ["Sign in", "Pay", "Select flight", "Book now", "Send message", "Account settings"])
def test_human_boundary_prevents_execution(label):
    with pytest.raises(milestone.HumanRequired):
        milestone.require_allowed({"kind": "click", "label": label})


def test_execution_is_durable_before_a_failed_observation(tmp_path):
    path = tmp_path / "events.jsonl"
    browser = SimpleNamespace(act=lambda *_a, **_k: {"executed": "search"},
                              observe=lambda **_k: (_ for _ in ()).throw(RuntimeError("observation failed")))
    milestone.instrument_browser(browser, Journal(path), [1])
    browser.act({"id": "search", "kind": "click", "label": "Search"}, {})
    with pytest.raises(RuntimeError, match="observation failed"):
        browser.observe()
    result = summarize(read_events(path))
    assert result["actions_executed"] == 1
    assert not result["execution_outcome_unknown"]


def test_execution_error_is_not_retried(tmp_path):
    calls = []

    def act(*_args, **_kwargs):
        calls.append(1)
        raise RuntimeError("Transport ended after input")

    path = tmp_path / "events.jsonl"
    browser = SimpleNamespace(act=act, observe=lambda **_k: {})
    milestone.instrument_browser(browser, Journal(path), [1])
    with pytest.raises(RuntimeError):
        browser.act({"kind": "click", "label": "Search"}, {})
    assert calls == [1]
    assert summarize(read_events(path))["execution_outcome_unknown"]


def test_challenge_after_observation_stops_before_more_inference(tmp_path):
    browser = SimpleNamespace(act=lambda: None, observe=lambda: {"text": "Verify you are human"})
    milestone.instrument_browser(browser, Journal(tmp_path / "events"), [1])
    with pytest.raises(milestone.HumanRequired):
        browser.observe()


def test_pilot_requires_explicit_readiness(monkeypatch):
    monkeypatch.setattr(milestone, "run", lambda *_a: pytest.fail("Inference started"))
    with pytest.raises(SystemExit) as error:
        milestone.main(["--pilot"])
    assert error.value.code == 2


def _note_page():
    return {
        "url": "http://127.0.0.1:9/notes",
        "title": "Notes",
        "text": "Notes",
        "fingerprint": "abc",
        "actions": [{"id": "note", "kind": "fill", "label": "Note", "value": "", "node": 1}],
    }


def test_cache_miss_runs_the_model_and_a_hit_does_not(tmp_path, monkeypatch):
    from jev_ultrafast import agent as agent_module
    from jev_ultrafast import local_model
    from jev_ultrafast.browser import StalePage
    from jev_ultrafast.replay_cache import load_actions, save_actions

    loads = []
    page = _note_page()
    save_actions(tmp_path, "Save the note", page, [{"operation": "fill", "target": "Note", "value": "Ship the crate"}])

    class Agent:
        def __init__(self, *_args):
            self.state = {"page": page, "status": "ready", "history": [], "decisions": []}
            passed = {"submitted": {"note": "Ship the crate"}, "results_visible": True, "selected": False}
            self.browser = SimpleNamespace(
                observe=lambda **_k: page,
                act=lambda *_a, **_k: None,
                evaluate=lambda _e: passed,
            )

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def command(self, name, *_args):
            if name == "predict":
                self.state["decisions"].append({"choice": "DONE", "operation": "DONE", "latency_ms": 1})
                self.state["status"] = "predicted"
                return
            self.state["history"].append({"kind": "fill", "action": "Note", "text": "Ship the crate"})
            self.state["status"] = "done"

    monkeypatch.setattr(milestone, "REPLAY_CACHE", tmp_path)
    monkeypatch.setattr(agent_module, "Agent", Agent)
    monkeypatch.setattr(local_model, "get_model", lambda: loads.append(1))
    monkeypatch.setattr(local_model, "get_model_info", lambda: {})
    monkeypatch.setattr(milestone, "measured_model", lambda *_a: nullcontext())
    task = {"kind": "local", "goal": "Save another note", "expected": {"note": "Ship the crate"}}
    journal = Journal(tmp_path / "miss")
    assert milestone.run_task(task, "http://127.0.0.1:9/notes", journal, 2) == 0
    assert loads == [1]
    stored = load_actions(tmp_path, "Save another note", page)
    assert stored == [{"operation": "fill", "target": "Note", "value": "Ship the crate"}]

    loads.clear()
    ran = {}

    class ReplayAgent(Agent):
        def __init__(self, *_args):
            super().__init__()

            def act(action, _observed, text=None):
                ran.setdefault("seen", []).append((action["label"], text))

            self.browser = SimpleNamespace(observe=lambda **_k: page, act=act, evaluate=self.browser.evaluate)

        def command(self, *_args):
            raise StalePage("The model loop ran on a cache hit")

    monkeypatch.setattr(agent_module, "Agent", ReplayAgent)
    journal = Journal(tmp_path / "hit")
    hit = {"kind": "local", "goal": "Save the note", "expected": {"note": "Ship the crate"}}
    assert milestone.run_task(hit, "http://127.0.0.1:9/notes", journal, 2) == 0
    assert loads == []
    assert ran["seen"] == [("Note", "Ship the crate")]


def test_missing_replay_target_runs_the_model(tmp_path, monkeypatch):
    from jev_ultrafast import agent as agent_module
    from jev_ultrafast import local_model
    from jev_ultrafast.replay_cache import save_actions

    page = _note_page()
    save_actions(tmp_path, "Save the note", page, [
        {"operation": "fill", "target": "Note", "value": "Ship the crate"},
        {"operation": "click", "target": "Save note"},
    ])
    acted = []
    loads = []

    class Agent:
        def __init__(self, *_args):
            self.state = {"page": page, "status": "ready", "history": [], "decisions": []}
            passed = {"submitted": {"note": "Ship the crate"}, "results_visible": True, "selected": False}

            def act(*_args, **_kwargs):
                acted.append(1)

            self.browser = SimpleNamespace(observe=lambda **_k: page, act=act, evaluate=lambda _e: passed)

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def command(self, name, *_args):
            if name == "predict":
                self.state["decisions"].append({"choice": "DONE", "operation": "DONE", "latency_ms": 1})
                return
            self.state["history"].append({"kind": "fill", "action": "Note", "text": "Ship the crate"})
            self.state["status"] = "done"

    monkeypatch.setattr(milestone, "REPLAY_CACHE", tmp_path)
    monkeypatch.setattr(agent_module, "Agent", Agent)
    monkeypatch.setattr(local_model, "get_model", lambda: loads.append(1))
    monkeypatch.setattr(local_model, "get_model_info", lambda: {})
    monkeypatch.setattr(milestone, "measured_model", lambda *_a: nullcontext())
    task = {"kind": "local", "goal": "Save the note", "expected": {"note": "Ship the crate"}}
    assert milestone.run_task(task, page["url"], Journal(tmp_path / "events"), 2) == 0
    assert loads == [1]
    assert acted == []


@pytest.mark.parametrize("challenge", [True, False])
def test_runner_stops_initial_challenge_or_three_rejections(tmp_path, monkeypatch, challenge):
    from jev_ultrafast import agent as agent_module
    from jev_ultrafast import local_model
    from jev_ultrafast.browser import StalePage

    calls = []

    class Agent:
        def __init__(self, *_args):
            page = {"text": "Verify you are human" if challenge else "Search", "actions": []}
            self.state = {"page": page, "status": "ready"}
            self.browser = SimpleNamespace(observe=lambda **_k: page, act=lambda *_a: None, evaluate=lambda _e: {})

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def command(self, *_args):
            calls.append(1)
            raise StalePage("Page changed before input")

    monkeypatch.setattr(agent_module, "Agent", Agent)
    monkeypatch.setattr(local_model, "get_model", lambda: pytest.fail("Loaded on CAPTCHA") if challenge else None)
    monkeypatch.setattr(local_model, "get_model_info", lambda: {})
    monkeypatch.setattr(milestone, "measured_model", lambda *_a: nullcontext())
    journal = Journal(tmp_path / "events")
    if challenge:
        with pytest.raises(milestone.HumanRequired):
            milestone.run_task(MANIFEST["tasks"]["local_search"], "http://local.invalid", journal, 20)
        assert not calls
    else:
        assert milestone.run_task(MANIFEST["tasks"]["local_search"], "http://local.invalid", journal, 20) == 1
        assert len(calls) == 3
        assert any(e.get("category") == "rejected_decisions" for e in read_events(journal.path))


def test_timed_cancellation_preserves_measured_shutdown():
    stats = {}
    started = time.monotonic()
    with pytest.raises(KeyboardInterrupt):
        runtime_guard.supervise([sys.executable, "-c", "import time; time.sleep(30)"],
                                timeout=5, cancel_after=0.3, memory_limit=2**30, stats=stats)
    assert time.monotonic() - started < 3
    assert stats["memory_samples"] > 0
    assert stats["peak_worker_bytes"] > 0
    assert stats["worker_stopped_ms"] >= stats["cancel_requested_ms"]


def test_sigterm_cleans_up_worker_and_preserves_journal(tmp_path):
    path, pid_path = tmp_path / "events", tmp_path / "pid"
    child = ("import os,time; from pathlib import Path; from scripts.milestone_record import Journal; "
             f"Journal({str(path)!r}).write('model_call_started', step=1); "
             f"Path({str(pid_path)!r}).write_text(str(os.getpid())); time.sleep(30)")
    parent_code = (
        "import sys; from scripts.runtime_guard import cancellation_signals,supervise\n"
        "try:\n"
        " with cancellation_signals():\n"
        f"  supervise([sys.executable,'-c',{child!r}],timeout=30,memory_limit=2**30)\n"
        "except KeyboardInterrupt:\n sys.exit(130)\n"
    )
    parent = subprocess.Popen([sys.executable, "-c", parent_code], cwd=milestone.ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        deadline = time.monotonic() + 5
        while not pid_path.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert pid_path.exists()
        parent.send_signal(signal.SIGTERM)
        _, errors = parent.communicate(timeout=4)
        assert parent.returncode == 130
        assert b"Traceback" not in errors
        with pytest.raises(ProcessLookupError):
            os.kill(int(pid_path.read_text()), 0)
        assert summarize(read_events(path))["model_calls_started"] == 1
    finally:
        runtime_guard.stop_process_group(parent)


def test_fixed_variations_preserve_shared_requirements():
    tasks = MANIFEST["tasks"]
    assert tasks["sfo_bos_next_day"]["expected"]["date"] == "2026-11-17"
    assert tasks["sfo_sea"]["expected"]["destination_labels"] == ["Seattle"]
    for key in ("local_search_reordered", "local_search_crowded"):
        task = copy.deepcopy(tasks[key])
        task["layout"] = "normal"
        assert task == tasks["local_search"]
