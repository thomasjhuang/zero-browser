import pytest

from jev_ultrafast.workflow_worker import observed_candidates, run_control
from scripts.workflow_browser import assess_workflow


def test_ambiguous_control_stops_before_decision():
    with pytest.raises(ValueError, match="ambiguous_target"):
        observed_candidates(
            {"actions": [{"kind": "click", "label": "Open"}, {"kind": "click", "label": "Open"}]}, "click", "Open"
        )


def test_uncertain_click_is_not_repeated():
    class Browser:
        calls = 0

        def observe(self, screenshot=False):
            return {
                "actions": [{"id": "C1", "kind": "click", "label": "Open", "node": 1}],
                "url": "https://example.org/",
                "title": "Example",
                "text": "",
            }

        def evaluate(self, expression):
            return "https://example.org/article"

        def act(self, *args, **kwargs):
            self.calls += 1
            raise RuntimeError("Connection lost after possible input")

    class Journal:
        def write(self, *args, **kwargs):
            pass

    browser = Browser()
    result = run_control(
        browser,
        {"kind": "click", "target": "Open", "outcome": "Open article", "allowed_hosts": ["example.org"]},
        lambda *args: {"choice": "C1"},
        Journal(),
    )
    assert result["unresolved_execution"] and browser.calls == 1


@pytest.mark.parametrize("removed", ["portal", "search", "ada", "link", "destination", "passage"])
def test_complete_answer_does_not_replace_route_evidence(removed):
    ada = "https://en.wikipedia.org/wiki/Ada_Lovelace"
    engine = "https://en.wikipedia.org/wiki/Analytical_engine"
    records = {
        "portal": {
            "event": "observation",
            "page": {
                "url": "https://www.wikipedia.org/",
                "text": "",
                "actions": [
                    {"node": 1, "kind": "fill", "label": "Search Wikipedia"},
                    {"node": 2, "kind": "click", "label": "Search", "role": "button"},
                ],
            },
        },
        "fill": {
            "event": "executed",
            "action": {"node": 1, "kind": "fill", "label": "Search Wikipedia"},
            "text": "Ada Lovelace",
        },
        "search": {
            "event": "executed",
            "from_url": "https://www.wikipedia.org/",
            "action": {"node": 2, "kind": "click", "label": "Search", "role": "button"},
        },
        "ada": {
            "event": "observation",
            "page": {
                "url": ada,
                "text": "",
                "actions": [{"node": 3, "kind": "click", "label": "analytical engine", "role": "link"}],
            },
        },
        "link": {
            "event": "executed",
            "from_url": ada,
            "href": engine,
            "action": {"node": 3, "kind": "click", "label": "analytical engine", "role": "link"},
        },
        "destination": {
            "event": "observation",
            "page": {
                "url": engine,
                "title": "Analytical engine - Wikipedia",
                "text": "The machine was designed by Charles Babbage.",
            },
        },
    }
    assert assess_workflow(list(records.values()), "Charles Babbage", [ada, engine])["passed"]
    if removed == "passage":
        records["destination"]["page"]["text"] = "No relevant text observed"
    else:
        del records[removed]
    assert not assess_workflow(list(records.values()), "Charles Babbage", [ada, engine])["passed"]


def test_bounded_prompt_excludes_general_task_instructions():
    from jev_ultrafast.questions import NEXT_ACTION
    from jev_ultrafast.structured_policy import BOUNDED_SYSTEM, decision_system

    assert decision_system(True) == BOUNDED_SYSTEM
    assert NEXT_ACTION not in decision_system(True)
    assert "entire user request" not in decision_system(True)


@pytest.mark.parametrize("destination", ["https://example.org/article", "https://example.org/unrelated"])
def test_exact_link_needs_destination_and_returns_observation(monkeypatch, destination):
    from jev_ultrafast.workflow_worker import run_step

    class Browser:
        acted = False

        def observe(self, screenshot=False):
            return {
                "actions": [{"id": "C1", "kind": "click", "label": "Open", "node": 1}],
                "url": destination if self.acted else "https://example.org/",
                "title": "Example",
                "text": "Visible text",
                "fingerprint": str(self.acted),
            }

        def evaluate(self, expression):
            return "https://example.org/article"

        def act(self, *args, **kwargs):
            self.acted = True

    class Journal:
        def write(self, *args, **kwargs):
            pass

    # Make the bounded read-only settling deadline expire immediately in the unit test.
    ticks = iter(range(100))
    monkeypatch.setattr("jev_ultrafast.workflow_worker.time.monotonic", lambda: next(ticks) * 10)

    def forbidden_model(*args):
        pytest.fail("Exact control must not ask Qwen for approval")

    result = run_step(Browser(), "click", "Open", "", "Open link", ["example.org"], forbidden_model, Journal())
    assert result["action_executed"] and result["page_changed"]
    assert result["outcome_achieved"] == destination.endswith("/article")
    assert result["observation"]["url"] == destination


def test_exact_identity_rejects_same_name_variation_and_accepts_observed_redirect():
    from jev_ultrafast.workflow_worker import exact_identity, link_destination

    page = {
        "url": "https://example.org/canonical",
        "identity": {
            "headings": ["Ada Lovelace (microarchitecture)"],
            "canonical_url": "https://example.org/canonical",
        },
    }
    assert not exact_identity(page, "Ada Lovelace")
    page["identity"]["headings"] = ["Ada Lovelace"]
    assert exact_identity(page, "Ada Lovelace")
    assert link_destination(page, "https://example.org/redirect", "Ada Lovelace")


@pytest.mark.parametrize("choices", [[], [{"kind": "click", "label": "Open"}, {"kind": "click", "label": "Open"}]])
def test_known_missing_or_ambiguous_target_is_not_uncertain_execution(choices):
    from jev_ultrafast.workflow_worker import exact_step

    class Browser:
        def observe(self, screenshot=False):
            return {"url": "https://example.org/", "title": "Example", "text": "", "actions": choices}

        def evaluate(self, expression):
            return {"headings": [], "canonical_url": None}

        def act(self, *args, **kwargs):
            pytest.fail("Invalid target must stop before input")

    class Journal:
        def write(self, *args, **kwargs):
            pass

    result = exact_step(Browser(), "click", "Open", "", ["example.org"], Journal())
    assert result["action_executed"] is False and result["page_changed"] is False
    assert not result["outcome_achieved"] and not result["unresolved_execution"]
    assert result["observation"]["url"] == "https://example.org/"


def test_search_failure_preserves_completed_fill_and_latest_observation(monkeypatch):
    from jev_ultrafast.workflow_worker import search_open

    page = {
        "url": "https://example.org/",
        "title": "Search",
        "text": "query",
        "actions": [],
        "identity": {"headings": ["Search"], "canonical_url": None},
    }
    monkeypatch.setattr("jev_ultrafast.workflow_worker.observation", lambda *args: page)
    monkeypatch.setattr(
        "jev_ultrafast.workflow_worker.exact_step",
        lambda *args: {"outcome_achieved": True, "action_executed": True, "page_changed": True, "observation": page},
    )

    class Journal:
        def write(self, *args, **kwargs):
            pass

    result = search_open(None, "Search", "query", ["example.org"], lambda *args: {"choice": "DONE"}, Journal())
    assert result["action_executed"] and result["page_changed"]
    assert not result["outcome_achieved"] and not result["unresolved_execution"]
    assert result["observation"]["text"] == "query"


def test_oracle_accepts_observed_canonical_destination_and_rejects_negated_answer():
    ada = "https://en.wikipedia.org/wiki/Ada_Lovelace"
    final = "https://en.wikipedia.org/wiki/Observed_canonical_article"
    field = {"node": 1, "kind": "fill", "label": "Search Wikipedia"}
    result = {"node": 2, "kind": "click", "label": "Ada Lovelace", "role": "link"}
    link = {"node": 3, "kind": "click", "label": "analytical engine", "role": "link"}
    events = [
        {"event": "observation", "page": {"url": "https://www.wikipedia.org/", "text": "", "actions": [field, result]}},
        {"event": "executed", "action": field, "text": "Ada Lovelace"},
        {"event": "executed", "action": result, "from_url": "https://www.wikipedia.org/", "href": ada},
        {"event": "observation", "page": {"url": ada, "text": "", "actions": [link]}},
        {
            "event": "executed",
            "action": link,
            "from_url": ada,
            "href": "https://en.wikipedia.org/wiki/Analytical_engine",
        },
        {
            "event": "observation",
            "page": {
                "url": final,
                "text": "The machine was designed by Charles Babbage.",
                "identity": {"headings": ["Analytical engine"], "canonical_url": final},
            },
        },
    ]
    assert assess_workflow(events, "The inventor was Charles Babbage.", [ada, final])["passed"]
    for answer in [
        "Not Charles Babbage",
        "The inventor was Ada Lovelace.",
        "Charles Babbage. The inventor was Ada Lovelace.",
    ]:
        assert not assess_workflow(events, answer, [ada, final])["passed"]


@pytest.mark.parametrize(
    "executed,unresolved,used,allowed",
    [(False, False, False, True), (None, True, False, False), (True, False, False, False), (False, False, True, False)],
)
def test_recovery_requires_confirmed_non_execution(executed, unresolved, used, allowed):
    from jev_ultrafast.workflow_worker import recovery_allowed

    result = {
        "first_failure": {"category": "missing_target"},
        "action_executed": executed,
        "unresolved_execution": unresolved,
        "observation": {"actions": []},
    }
    assert recovery_allowed(result, "click", used) is allowed


@pytest.mark.parametrize("target_returns,unknown", [(True, False), (False, False), (True, True)])
def test_one_recovery_action_continues_only_after_unique_target_returns(monkeypatch, target_returns, unknown):
    from jev_ultrafast.workflow_worker import recover_missing

    recovery = {"id": "s1", "kind": "scroll", "label": "Scroll down", "delta": 500}
    original = {"kind": "click", "target": "Destination", "value": "", "outcome": "Open the observed destination"}
    page = {"url": "https://example.org/", "title": "Example", "text": "", "actions": [recovery]}
    after = {
        **page,
        "actions": [{"id": "e2", "kind": "click", "label": "Destination", "node": 2}] if target_returns else [],
    }
    calls = []
    monkeypatch.setattr("jev_ultrafast.workflow_worker.observation", lambda *args: page)

    def execute(*args):
        calls.append("recovery")
        if unknown:
            return {
                "status": "uncertainty",
                "unresolved_execution": True,
                "first_failure": {"category": "execution_failure"},
            }
        return {"action_executed": True, "page_changed": True, "unresolved_execution": False, "page": after}

    def resume(*args, **kwargs):
        calls.append("original")
        return {"status": "success", "outcome_achieved": True, "unresolved_execution": False}

    monkeypatch.setattr("jev_ultrafast.workflow_worker.execute_observed", execute)
    monkeypatch.setattr("jev_ultrafast.workflow_worker.run_step", resume)
    result = recover_missing(None, page, original, "s1", ["example.org"], None, None)
    assert calls == (["recovery", "original"] if target_returns and not unknown else ["recovery"])
    assert result["unresolved_execution"] is unknown


def test_workflow_recovery_cannot_repeat(tmp_path, monkeypatch):
    from scripts.workflow_browser import Workflow

    worker = Workflow({"folder": str(tmp_path), "method": "persistent"})
    worker.pending_recovery = {"observation": {}, "original": {}}
    monkeypatch.setattr(
        "scripts.workflow_browser.recover_missing",
        lambda *args: {"status": "uncertainty", "unresolved_execution": False},
    )
    worker.recover("s1")
    with pytest.raises(ValueError, match="allowed once"):
        worker.recover("s1")
