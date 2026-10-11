"""Coordinator pause/resume guards, with fake pages and no inference."""
import copy
import json
from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from scripts import coordinator_handoff as bridge
from scripts import milestone
from scripts.milestone_record import Journal, read_events, save_json

PAGE = {"url": "https://example.test/search", "title": "Search", "text": "Search",
        "fingerprint": "initial", "actions": [{"id": "e1", "node": 1, "kind": "fill",
                                               "label": "Query", "value": ""}]}
ERROR_PAGE = {**PAGE, "text": "No matching results found", "fingerprint": "error"}


def agent(page):
    return SimpleNamespace(state={"page": copy.deepcopy(page), "goal": "Find the supplied item. Do not buy.",
                                  "history": [{"action": "Query", "page_changed": True}],
                                  "decision": {}, "confirm_done": True, "status": "ready"},
                           pending_text=("old input", "old text"),
                           browser=SimpleNamespace(target="same-tab", observe=lambda **_: copy.deepcopy(page)))


def test_one_correction_preserves_agent_and_boundary_and_clears_old_text(tmp_path, monkeypatch):
    now = [0.0]
    monkeypatch.setattr(bridge.time, "monotonic", lambda: now[0])
    journal = Journal(tmp_path / "events")
    h = bridge.CoordinatorHandoff({"folder": str(tmp_path), "deadline_monotonic": 90}, journal, PAGE)
    a = agent(ERROR_PAGE)
    browser = a.browser

    def reply(_seconds):
        now[0] += 12
        request = json.loads((tmp_path / "handoff.json").read_text())
        assert request["decisions_remaining"] == 19
        save_json(tmp_path / "correction.json", {"handoff_id": request["handoff_id"],
                                                 "correction": "Use the supplied shorter item code."})

    monkeypatch.setattr(bridge.time, "sleep", reply)
    assert h.after_step(a, 1, 20, 0)
    assert a.browser is browser
    assert a.pending_text is None
    assert a.state["decision"] is None
    assert not a.state.get("confirm_done")
    assert a.state["goal"].startswith("Find the supplied item. Do not buy.")
    assert "shorter item code" in a.state["goal"]
    assert h.deadline == 90
    events = read_events(journal.path)
    resumed = next(e for e in events if e["event"] == "coordinator_resumed")
    assert resumed["seconds_remaining"] == 78
    assert resumed["decisions_remaining"] == 19
    with pytest.raises(bridge.CoordinatorStop, match="Further error"):
        h.after_step(a, 2, 20, 0)
    assert len([e for e in read_events(journal.path) if e["event"] == "coordinator_handoff"]) == 1


@pytest.mark.parametrize("late_reply", [False, True])
def test_wait_and_late_reply_cannot_extend_deadline(tmp_path, monkeypatch, late_reply):
    now = [0.0]
    monkeypatch.setattr(bridge.time, "monotonic", lambda: now[0])
    h = bridge.CoordinatorHandoff({"folder": str(tmp_path), "deadline_monotonic": 3},
                                  Journal(tmp_path / "events"), PAGE)

    def tick(_seconds):
        now[0] = 4
        if late_reply:
            request = json.loads((tmp_path / "handoff.json").read_text())
            save_json(tmp_path / "correction.json", {"handoff_id": request["handoff_id"], "correction": "Continue"})

    monkeypatch.setattr(bridge.time, "sleep", tick)
    a = agent(ERROR_PAGE)
    with pytest.raises(bridge.CoordinatorStop, match="deadline"):
        h.after_step(a, 1, 20, 0)
    assert a.state["goal"] == "Find the supplied item. Do not buy."


def test_preloaded_reply_and_exhausted_decisions_never_resume(tmp_path):
    (tmp_path / "correction.json").write_text('{}')
    config = {"folder": str(tmp_path), "deadline_monotonic": bridge.time.monotonic()+90}
    with pytest.raises(ValueError, match="preloaded"):
        bridge.CoordinatorHandoff(config, Journal(tmp_path / "events"), PAGE)
    (tmp_path / "correction.json").unlink()
    h = bridge.CoordinatorHandoff(config, Journal(tmp_path / "events"), PAGE)
    with pytest.raises(bridge.CoordinatorStop, match="No local decision budget"):
        h.after_step(agent(ERROR_PAGE), 20, 20, 0)
    assert not (tmp_path / "handoff.json").exists()


def test_three_unchanged_waits_detect_nonprogress_without_geometry_noise(tmp_path, monkeypatch):
    h = bridge.CoordinatorHandoff({"folder": str(tmp_path), "deadline_monotonic": bridge.time.monotonic()+90},
                                  Journal(tmp_path / "events"), PAGE)
    a = agent(PAGE)
    assert not h.after_step(a, 1, 20, 0)
    a.state["page"]["actions"][0].update(id="e99", node=99, rect={"y": 33})
    assert not h.after_step(a, 2, 20, 0)

    def stop_at_handoff(_seconds):
        request = json.loads((tmp_path / "handoff.json").read_text())
        assert request["reason"]["category"] == "nonprogress"
        raise KeyboardInterrupt

    monkeypatch.setattr(bridge.time, "sleep", stop_at_handoff)
    with pytest.raises(KeyboardInterrupt):
        h.after_step(a, 3, 20, 0)


@pytest.mark.parametrize("failure", [None, "uncertain", "post_input_stale", "human"])
def test_milestone_resumes_same_agent_once_and_never_hands_off_uncertain_input(tmp_path, monkeypatch, failure):
    from jev_ultrafast import agent as agent_module
    from jev_ultrafast import local_model
    from jev_ultrafast.browser import StalePage

    instances, loads = [], []

    class FakeAgent:
        def __init__(self, _url, goal):
            instances.append(self)
            self.pending_text = ("old", "old")
            self.state = {"page": copy.deepcopy(PAGE), "goal": goal, "history": [], "decisions": [],
                          "status": "ready"}
            self.browser = SimpleNamespace(act=self.act, observe=lambda **_: self.state["page"], target="same-tab")

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def act(self, *_args, **_kwargs):
            if failure == "uncertain":
                raise RuntimeError("Input outcome unknown")

        def command(self, name, _body=None):
            if name == "predict":
                if len(self.state["decisions"]) == 1:
                    assert "shorter item code" in self.state["goal"]
                    assert self.pending_text is None
                self.state["decisions"].append({"choice": "e1", "operation": "TYPE_TEXT", "latency_ms": 1})
                return
            action = self.state["page"]["actions"][0]
            self.browser.act(action, self.state["page"], text="value")
            self.state["history"].append({"action": "Query", "page_changed": None})
            if failure == "post_input_stale":
                raise StalePage("Observation lost after successful input")
            self.state["page"] = copy.deepcopy(ERROR_PAGE if len(self.state["decisions"]) == 1 else PAGE)
            if failure == "human":
                self.state["page"]["text"] = "Verify you are human"
            self.state["page"] = self.browser.observe(screenshot=False)
            self.state["history"][-1]["page_changed"] = True

    monkeypatch.setattr(agent_module, "Agent", FakeAgent)
    monkeypatch.setattr(local_model, "get_model", lambda: loads.append(1))
    monkeypatch.setattr(local_model, "get_model_info", lambda: {})
    monkeypatch.setattr(milestone, "measured_model", lambda *_: nullcontext())
    monkeypatch.setattr(milestone, "verify_flights", lambda *_: {"passed": False})

    def reply(_seconds):
        request = json.loads((tmp_path / "handoff.json").read_text())
        save_json(tmp_path / "correction.json", {"handoff_id": request["handoff_id"],
                                                 "correction": "Use the shorter item code."})

    monkeypatch.setattr(bridge.time, "sleep", reply)
    journal = Journal(tmp_path / "events")
    args = ({"kind": "flights", "goal": "Find item. Do not buy.", "expected": {}},
            PAGE["url"], journal, 2)
    config = {"folder": str(tmp_path), "deadline_monotonic": bridge.time.monotonic()+90}
    if failure in {"uncertain", "human"}:
        with pytest.raises((RuntimeError, milestone.HumanRequired)):
            milestone.run_task(*args, coordinator=config)
    else:
        assert milestone.run_task(*args, coordinator=config) == 1
    assert len(instances) == len(loads) == 1
    events = read_events(journal.path)
    assert sum(e["event"] == "coordinator_handoff" for e in events) == (0 if failure else 1)
    assert len(instances[0].state["decisions"]) == (1 if failure else 2)
    if failure == "post_input_stale":
        assert any(e.get("category") == "unresolved_observation" for e in events)


@pytest.mark.parametrize("problem", [None, "typed_only", "wrong_option", "unobserved_option",
                                     "open", "empty", "ambiguous", "later_fill"])
def test_selection_requires_each_observed_outcome_condition(problem):
    from scripts.milestone_verify import verify_selection

    option = {"id": "e2", "node": 2, "kind": "click", "role": "option", "label": "Requested airport JFK"}
    field = {"id": "e1", "node": 1, "kind": "fill", "label": "Destination", "value": "New York", "expanded": "false"}
    events = [{"event": "observation", "page": {"actions": [dict(option)]}},
              {"event": "executed", "step": 2, "action": option}]
    page = {"actions": [field]}
    if problem == "typed_only":
        events = []
        field["value"] = "JFK"
    elif problem == "wrong_option":
        option["label"] = "Another airport LGA"
        events[0]["page"]["actions"] = [dict(option)]
    elif problem == "unobserved_option":
        events[0]["page"]["actions"] = []
    elif problem == "open":
        field["expanded"] = "true"
    elif problem == "empty":
        field["value"] = ""
    elif problem == "ambiguous":
        page["actions"].append(dict(field))
    elif problem == "later_fill":
        events.append({"event": "executed", "action": field})
    result = verify_selection(page, events, {"target_label": "Destination", "option_text": "JFK"})
    assert result["passed"] is (problem is None)


@pytest.mark.parametrize("label,kind,role,allowed", [
    ("Destination", "fill", "combobox", True),
    ("Origin", "fill", "combobox", False),
    ("Departure", "fill", "textbox", False),
    ("Search", "click", "button", False),
    ("Choose multiple items", "click", "button", False),
    ("Requested airport JFK", "click", "option", True),
    ("Wrong airport LGA", "click", "option", False),
])
def test_selection_cannot_change_unrelated_fields_or_submit(label, kind, role, allowed):
    target = {"node": 1, "kind": "fill", "label": "Destination"}
    action = {"node": 1 if label == "Destination" else 2, "kind": kind, "role": role, "label": label}
    page = {"actions": [target, action] if label != "Destination" else [target]}
    events = [{"event": "executed", "action": target}]
    expected = {"target_label": "Destination", "option_text": "JFK"}
    if allowed:
        milestone.require_selection_action(action, page, events, expected)
    else:
        with pytest.raises(milestone.HumanRequired):
            milestone.require_selection_action(action, page, events, expected)


def test_popup_field_requires_previous_target_entry():
    field = {"node": 2, "kind": "fill", "label": "Query"}
    page = {"actions": [field]}
    expected = {"target_label": "Destination", "option_text": "JFK"}
    with pytest.raises(milestone.HumanRequired):
        milestone.require_selection_action(field, page, [], expected)
    milestone.require_selection_action(field, page,
                                       [{"event": "executed", "action": {"label": "Destination"}}], expected)
