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
            }

        def evaluate(self, expression):
            return "https://example.org/article"

        def act(self, *args):
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
    engine = "https://en.wikipedia.org/wiki/Analytical_Engine"
    records = {
        "portal": {"event": "observation", "page": {"url": "https://www.wikipedia.org/", "text": ""}},
        "search": {"event": "executed", "from_url": "https://www.wikipedia.org/", "action": {"kind": "click"}},
        "ada": {"event": "observation", "page": {"url": ada, "text": ""}},
        "link": {"event": "executed", "from_url": ada, "href": engine, "action": {"kind": "click"}},
        "destination": {"event": "observation", "page": {"url": engine, "text": "Charles Babbage designed it."}},
    }
    assert assess_workflow(list(records.values()), "Charles Babbage", [ada, engine])["passed"]
    if removed == "passage":
        records["destination"]["page"]["text"] = "No relevant text observed"
    else:
        del records[removed]
    assert not assess_workflow(list(records.values()), "Charles Babbage", [ada, engine])["passed"]
