"""A passed action list replays on the same controls without a model."""

from jev_ultrafast.replay_cache import load_actions, replay, save_actions, steps_from_history


def page(title="Notes"):
    return {
        "url": "http://127.0.0.1:9/notes",
        "title": title,
        "actions": [
            {"kind": "fill", "label": "Note", "value": "", "node": 1},
            {"kind": "click", "label": "Save note", "node": 2},
        ],
    }


def test_matching_page_reloads_the_action_list(tmp_path):
    steps = [{"operation": "fill", "target": "Note", "value": "Ship the crate"},
             {"operation": "click", "target": "Save note"}]
    save_actions(tmp_path, "Save the note", page(), steps)
    assert load_actions(tmp_path, "Save the note", page()) == steps
    moved = page()
    moved["actions"] = [{**action, "node": 50 + action["node"]} for action in moved["actions"]]
    assert load_actions(tmp_path, "Save the note", moved) == steps
    assert load_actions(tmp_path, "Save the note", page(title="Other")) is None
    assert load_actions(tmp_path, "Different goal", page()) is None


def test_replay_uses_the_browser_and_not_a_model():
    seen = []

    class Browser:
        def observe(self, screenshot=False):
            assert screenshot is False
            return page()

        def act(self, action, _page, text=None):
            seen.append((action["label"], text))

    result = replay(Browser(), [{"operation": "click", "target": "Save note"}])
    assert result["error"] is None
    assert result["executed"] == [None]
    assert seen == [("Save note", None)]


def test_history_becomes_a_general_action_list():
    history = [
        {"kind": "fill", "action": "Note", "text": "Ship the crate"},
        {"kind": "select", "action": "Count → 1", "text": None},
        {"kind": "click", "action": "Save note", "text": None},
        {"kind": "wait", "action": "Wait"},
    ]
    assert steps_from_history(history) == [
        {"operation": "fill", "target": "Note", "value": "Ship the crate"},
        {"operation": "select", "target": "Count", "value": "1"},
        {"operation": "click", "target": "Save note"},
    ]
