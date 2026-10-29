"""Extract visible fields and a short action list. No browser and no flight form."""

from jev_ultrafast.page_controls import extract_fields, prepare, run_controls


def note_page(saved=False):
    return {
        "title": "Crate note",
        "actions": [
            {"id": "note", "kind": "fill", "label": "Note", "value": "Ship the crate" if saved else "",
             "empty": "false" if saved else "true", "node": 1},
            {"id": "save", "kind": "click", "label": "Save note", "node": 2},
        ],
    }


def test_extract_and_act_on_a_note_page():
    prepared = prepare(note_page(), [
        {"operation": "fill", "target": "Note", "value": "Ship the crate"},
        {"operation": "click", "target": "Save note"},
    ])
    assert prepared["error"] is None
    assert prepared["fields"] == [{
        "id": "note", "node": 1, "label": "Note", "kind": "fill", "value": "", "empty": True,
    }]
    assert [step["id"] for step in prepared["actions"]] == ["note", "save"]
    assert prepared["actions"][0]["text"] == "Ship the crate"


def test_missing_or_ambiguous_fields_do_not_invent_an_action():
    assert prepare(note_page(), [{"operation": "fill", "target": "Missing", "value": "x"}])["error"] == "missing"
    page = note_page()
    page["actions"].append({"id": "note-2", "kind": "fill", "label": "Note", "value": "", "node": 3})
    assert prepare(page, [{"operation": "fill", "target": "Note", "value": "x"}])["error"] == "ambiguous"


def test_run_controls_observes_then_acts_without_a_hosted_crawler():
    class Browser:
        def __init__(self):
            self.pages = [note_page(), note_page(saved=True), note_page(saved=True)]
            self.calls = []

        def observe(self, screenshot=False):
            assert screenshot is False
            return self.pages.pop(0)

        def act(self, action, page, text=None):
            self.calls.append((action["id"], text))

    browser = Browser()
    result = run_controls(browser, [
        {"operation": "fill", "target": "Note", "value": "Ship the crate"},
        {"operation": "click", "target": "Save note"},
    ])
    assert result["error"] is None
    assert result["executed"] == ["note", "save"]
    assert browser.calls == [("note", "Ship the crate"), ("save", None)]
    assert extract_fields(note_page(saved=True))[0]["value"] == "Ship the crate"


def test_same_path_opens_an_observed_stay():
    page = {"actions": [
        {"id": "casa", "kind": "click", "label": "View Casa Flora", "node": 4},
        {"id": "other", "kind": "click", "label": "View Other Stay", "node": 5},
    ]}
    prepared = prepare(page, [{"operation": "click", "target": "View Casa Flora"}])
    assert prepared["error"] is None
    assert prepared["actions"][0]["id"] == "casa"


def test_same_path_fills_an_observed_reference_field():
    page = {"actions": [
        {"id": "reference", "kind": "fill", "label": "Reference", "value": "", "empty": "true", "node": 1},
    ]}
    prepared = prepare(page, [{"operation": "fill", "target": "Reference", "value": "Trip 42"}])
    assert prepared["error"] is None
    assert prepared["actions"][0]["id"] == "reference"
    assert prepared["actions"][0]["text"] == "Trip 42"
