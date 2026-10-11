import pytest

from jev_ultrafast.structured_policy import parse_decision


@pytest.mark.parametrize("output", ['{"unmet":"Fill city","action_id":"invented"}',
                                    '{"unmet":"Fill city","action_id":"e1","selector":"input"}',
                                    '{"unmet":[],"action_id":"e1"}', 'not JSON'])
def test_structured_decision_rejects_unsupported_output(output):
    with pytest.raises(ValueError, match="No action executed"):
        parse_decision(output, [{"id": "e1"}])


def test_structured_decision_retains_claim_separately_from_action():
    assert parse_decision('{"unmet":"City is empty","action_id":"e1"}', [{"id": "e1"}]) == {
        "unmet": "City is empty", "action_id": "e1",
    }
