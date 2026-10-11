"""Model-free checks for travel completion and irreversible-action safeguards."""

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from jev_ultrafast.browser import StalePage
from travel_demo.contracts import FlightRequest, shortlist
from travel_demo.observe import form_checks, inspect, parse_flight
from travel_demo.session import finish, run_session
from travel_demo.workflow import next_step

REQUEST = FlightRequest.load(Path(__file__).parents[1] / "request.json")
ROW = (
    "From 250 US dollars. Nonstop flight with Delta. "
    "Leaves San Francisco International Airport at 7:00 AM on Monday, November 16 and arrives at "
    "Boston Logan International Airport at 3:30 PM on Monday, November 16. "
    "Total duration 5 hr 30 min. Select flight"
)


def page(*rows, query="", fingerprint="same", text=""):
    actions = [
        {"id": name, "node": index, "kind": "fill", "label": label, "value": value,
         "current_value": value}
        for index, (name, label, value) in enumerate([
            ("origin", "Origin", "SFO"), ("destination", "Destination", "BOS"),
            ("departure", "Departure date YYYY-MM-DD", REQUEST.departure_date),
            ("adults", "Adults", "1"), ("cabin", "Cabin", "Economy"),
            ("trip_type", "Trip type", "One way"),
        ], 1)
    ]
    actions.extend({"id": f"row{index}", "node": 20 + index, "kind": "click", "label": row}
                   for index, row in enumerate(rows))
    actions.append({"id": "wait", "kind": "wait", "label": "Wait for the page to update"})
    return {"url": "http://127.0.0.1:8766/fixture.html?origin=SFO&destination=BOS&"
                   "date=2026-11-16&adults=1&cabin=Economy&trip_type=One%20way&currency=USD" + query,
            "fingerprint": fingerprint, "actions": actions, "text": text, "title": "Flight search"}


class Browser:
    def __init__(self, pages, errors=()):
        self.pages = list(pages)
        self.errors = list(errors)
        self.actions = []

    def observe(self, screenshot=False):
        current = self.pages.pop(0) if len(self.pages) > 1 else self.pages[0]
        if isinstance(current, Exception):
            raise current
        return deepcopy(current)

    def act(self, action, observed, text=None):
        self.actions.append(action["id"])
        if self.errors:
            error = self.errors.pop(0)
            if error:
                raise error


def choose(target):
    return lambda *_: {"choice": target, "operation": "CLICK", "usage": {}}


def test_final_source_change_discards_previous_rows():
    result = finish([page(ROW), page(ROW.replace("250", "350"), query="&new_search=1")], REQUEST, fixture=True)
    assert [row["price"] for row in result["shortlist"]] == [350]


def test_unknown_final_rows_cannot_inherit_previous_success():
    result = finish([page(ROW), page("Unknown result. Select flight")], REQUEST, fixture=True)
    assert not result["outcome_verified"]
    assert result["shortlist"] == []


def test_unknown_only_rows_fail_closed():
    result = run_session(Browser([page("Unknown result. Select flight")]), REQUEST,
                         fixture=True, decide=choose("DONE"))
    assert not result["successful_run"]
    assert not result["outcome_verified"]
    assert result["inspected_rows"] == 1
    assert result["unparsed_rows"] == 1


def test_observed_empty_result_is_success_without_filler():
    result = run_session(Browser([page(text="No matching flights found.")]), REQUEST, fixture=True)
    assert result["successful_run"]
    assert result["shortlist"] == []
    assert result["inspected_rows"] == 0


def test_verified_rows_without_matches_are_inspected_no_match():
    result = run_session(Browser([page(ROW.replace("250", "450"))]), REQUEST, fixture=True)
    assert result["successful_run"]
    assert result["shortlist"] == []


def test_model_done_never_establishes_completion():
    result = run_session(Browser([page(), page(ROW)]), REQUEST, mode="local", fixture=True, decide=choose("DONE"))
    assert not result["successful_run"]
    assert result["shortlist"] == []
    assert result["metrics"]["model_decisions"] == 1


@pytest.mark.parametrize("label", ["Select flight", "Select departing flight", "Choose flight", "Book", "Pay",
                                    "Log in", "Sign in", "Hotels", "Visit sponsor"])
def test_booking_and_out_of_scope_targets_rejected(label):
    current = page()
    current["actions"].append({"id": "unsafe", "node": 88, "kind": "click", "label": label})
    browser = Browser([current])
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("unsafe"))
    assert not browser.actions
    assert not result["successful_run"]


def test_terminal_error_cannot_inherit_results():
    current = page()
    current["actions"].append({"id": "safe", "node": 90, "kind": "click", "label": "Search"})
    browser = Browser([current, page(ROW)], errors=[RuntimeError("Execution uncertain")])
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("safe"))
    assert browser.actions == ["safe"]
    assert not result["successful_run"]
    assert result["shortlist"] == []


def test_preaction_stale_rejection_reobserves():
    current = page()
    current["actions"].append({"id": "safe", "node": 90, "kind": "click", "label": "Search"})
    browser = Browser([current, current, page(ROW)], errors=[StalePage("Rejected before mutation"), None])
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("safe"))
    assert result["successful_run"]
    assert result["metrics"]["rejected_stale_actions"] == 1
    assert result["metrics"]["actions_executed"] == 1


def test_challenge_stops_before_model():
    current = page(ROW, text="Verify you are human")
    calls = []
    result = run_session(Browser([current]), REQUEST, mode="local", fixture=True,
                         decide=lambda *_: calls.append("called"))
    assert not calls
    assert not result["successful_run"]
    assert not result["outcome_verified"]


def test_forged_expanded_autocomplete_never_submits():
    current = page()
    current["actions"][0].update(value="San Francisco", current_value="San Francisco", expanded="true")
    current["actions"].append({"id": "search", "node": 90, "kind": "click", "label": "Search"})
    history = [{"field": "origin", "kind": "fill", "text": "San Francisco"}]
    assert next_step(current, REQUEST, history) is None
    assert not form_checks(current, REQUEST)["origin"]


def test_ambiguous_controls_defer():
    current = page()
    current["actions"].extend([
        {"id": "search1", "node": 90, "kind": "click", "role": "button", "label": "Search"},
        {"id": "search2", "node": 91, "kind": "click", "role": "button", "label": "Search"},
    ])
    assert next_step(current, REQUEST, []) is None


@pytest.mark.parametrize("key,value", [("origin", "OAK"), ("destination", "PVD"),
                                       ("departure", "2027-11-16"), ("adults", "2"), ("cabin", "Business")])
def test_final_state_must_match_route_year_adults_and_cabin(key, value):
    current = page(ROW)
    next(a for a in current["actions"] if a["id"] == key).update(value=value, current_value=value)
    assert not inspect(current, REQUEST, fixture=True).search_verified
    assert not finish([current], REQUEST, fixture=True)["outcome_verified"]


@pytest.mark.parametrize("old,new", [("5 hr 30 min", "5 hr nonsense"), ("250", "2,50"),
                                      ("Monday, November 16", "Tuesday, November 16")])
def test_malformed_row_fails_closed(old, new):
    assert parse_flight(ROW.replace(old, new), REQUEST) is None


@pytest.mark.parametrize("old,new", [("3:30 PM", "6:00 PM"), ("250", "400"),
                                    ("3:30 PM on Monday, November 16", "3:30 PM on Tuesday, November 17")])
def test_strict_price_same_day_and_arrival_constraints(old, new):
    flight = parse_flight(ROW.replace(old, new), REQUEST)
    assert flight is not None
    assert shortlist([flight], REQUEST) == []


def test_optional_airline_restriction_and_no_filler():
    flight = parse_flight(ROW, REQUEST)
    assert shortlist([flight], replace(REQUEST, airlines=("United",))) == []
    assert shortlist([flight], replace(REQUEST, airlines=("Delta",))) == [flight]


def test_layout_changes_do_not_change_outcome():
    current = page(ROW)
    changed = deepcopy(current)
    changed["actions"].reverse()
    for action in changed["actions"]:
        action["label"] = "  \n".join(action["label"].split())
    changed["fingerprint"] = "layout changed"
    assert finish([current], REQUEST, fixture=True)["shortlist"] == \
        finish([changed], REQUEST, fixture=True)["shortlist"]


def test_latest_fare_supersedes_old_price_before_filtering():
    result = finish([page(ROW), page(ROW.replace("250", "450"))], REQUEST, fixture=True)
    assert result["outcome_verified"]
    assert result["shortlist"] == []
    assert result["inspected_rows"] == 2


def test_model_cannot_submit_forged_autocomplete():
    current = page()
    current["actions"][0]["expanded"] = "true"
    current["actions"].append({"id": "search", "node": 90, "kind": "click", "label": "Search"})
    browser = Browser([current])
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("search"))
    assert browser.actions == []
    assert not result["successful_run"]


def test_loading_after_submit_waits_without_redecision():
    current = page()
    current["actions"].append({"id": "search", "node": 90, "kind": "click", "label": "Search"})
    browser = Browser([current, page(text="Loading..."), page(ROW)])
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("search"))
    assert result["successful_run"]
    assert browser.actions == ["search", "wait"]
    assert result["metrics"]["model_decisions"] == 1
    assert result["metrics"]["wait_actions"] == 1


def test_wait_budget_is_bounded_and_unknown_results_fail():
    current = page(text="Loading...")
    browser = Browser([current])
    result = run_session(browser, REQUEST, fixture=True, max_wait_steps=2)
    assert browser.actions == ["wait", "wait"]
    assert not result["successful_run"]
    assert "wait budget" in result["stop_reason"]


def test_failed_decision_invocation_has_count_and_latency():
    def fail(*_):
        raise RuntimeError("Decision unavailable")

    result = run_session(Browser([page()]), REQUEST, mode="local", fixture=True, decide=fail)
    assert result["metrics"]["model_decisions"] == 1
    assert len(result["metrics"]["decision_latency_ms"]) == 1
    assert not result["successful_run"]


def test_failed_text_invocation_has_count_and_latency():
    def fail(*_):
        raise RuntimeError("Text unavailable")

    browser = Browser([page()])
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("origin"), write_text=fail)
    assert not browser.actions
    assert result["metrics"]["text_calls"] == 1
    assert len(result["metrics"]["text_latency_ms"]) == 1


def test_final_observation_failure_discards_verified_rows():
    result = run_session(Browser([page(ROW), RuntimeError("Final read failed")]), REQUEST, fixture=True)
    assert not result["successful_run"]
    assert not result["outcome_verified"]
    assert result["shortlist"] == []


def test_wrong_committed_route_cannot_be_hidden_by_correct_editable_values():
    current = page(ROW)
    current["url"] = current["url"].replace("origin=SFO", "origin=OAK")
    assert not finish([page(ROW), current], REQUEST, fixture=True)["outcome_verified"]


def test_compact_date_without_year_evidence_rejected():
    current = page()
    current["url"] = "https://www.google.com/travel/flights/search"
    current["actions"][2].update(value="Mon, Nov 16", current_value="Mon, Nov 16")
    assert not form_checks(current, REQUEST)["departure"]


def test_unparsed_results_prevent_no_match_claim():
    result = run_session(Browser([page(ROW.replace("250", "450"), "Unknown result. Select flight")]),
                         REQUEST, fixture=True)
    assert not result["successful_run"]
    assert result["unparsed_rows"] == 1
    assert result["inspected_rows"] == 2


def test_qualifying_parsed_rows_can_be_reported_with_unknown_coverage():
    result = run_session(Browser([page(ROW, "Unknown result. Select flight")]), REQUEST, fixture=True)
    assert result["successful_run"]
    assert len(result["shortlist"]) == 1
    assert result["unparsed_rows"] == 1
    assert "Inspected results only" in result["coverage"]


def wire_bytes(field, value):
    # These small fixture fields need only one byte for each protobuf tag and length.
    return bytes([field * 8 + 2, len(value)]) + value


def google_page(payload):
    import base64

    current = page(ROW)
    token = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    current["url"] = "https://www.google.com/travel/flights/search?tfs=" + token
    return current


def google_leg(origin="SFO", destination="BOS", departure="2026-11-16"):
    return wire_bytes(2, departure.encode()) + wire_bytes(13, wire_bytes(2, origin.encode())) + \
        wire_bytes(14, wire_bytes(2, destination.encode()))


def test_directional_google_query_confirms_exact_route_and_year():
    assert inspect(google_page(wire_bytes(3, google_leg())), REQUEST).search_verified


@pytest.mark.parametrize("payload", [
    wire_bytes(3, google_leg("BOS", "SFO")),
    wire_bytes(3, google_leg(departure="2027-11-16")),
    wire_bytes(3, google_leg()) + wire_bytes(3, google_leg()),
    b"SFO BOS 2026-11-16",
    b"\x1a\xffincomplete",
])
def test_unverified_google_query_never_borrows_substring_evidence(payload):
    current = google_page(payload)
    assert not inspect(current, REQUEST).search_verified
    assert not finish([current], REQUEST)["outcome_verified"]


@pytest.mark.parametrize("selected,expected", [("false", "desired-day"), ("true", "apply")])
def test_calendar_requires_full_date_and_applies_selected_day(selected, expected):
    current = page()
    current["actions"][2]["expanded"] = "true"
    current["actions"].extend([
        {"id": "desired-day", "node": 90, "kind": "click", "role": "button",
         "label": "Monday, November 16, 2026", "selected": selected},
        {"id": "other-day", "node": 91, "kind": "click", "role": "button",
         "label": "Tuesday, November 17, 2026", "selected": "false"},
        {"id": "apply", "node": 92, "kind": "click", "role": "button", "label": "Done"},
    ])
    assert next_step(current, REQUEST, []).action["id"] == expected


def test_shortlist_limit_cannot_exceed_five():
    with pytest.raises(ValueError, match="1 to 5"):
        replace(REQUEST, limit=6)


@pytest.mark.parametrize("changed_context,expected_calls", [(False, 1), (True, 2)])
def test_stale_text_reuse_requires_identical_helper_context(changed_context, expected_calls):
    first = page()
    retry = page(text="New field hint" if changed_context else "")
    browser = Browser([first, retry, page(ROW)], errors=[StalePage("Preaction rejection"), None])
    calls = []

    def text(context):
        calls.append(context)
        return "San Francisco", {"usage": {}}

    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("origin"), write_text=text)
    assert result["successful_run"]
    assert len(calls) == expected_calls
    assert result["metrics"]["text_calls"] == expected_calls
    assert result["metrics"]["model_decisions"] == 2


def test_live_passenger_total_defers_to_transaction_without_proving_adult_count():
    current = page()
    current["actions"][3] = {"id": "passengers", "node": 4, "kind": "click", "role": "button",
                            "label": "1 passenger, change number of passengers.", "value": ""}
    assert not form_checks(current, REQUEST)["adults"]
    assert next_step(current, REQUEST, []) is None
    assert not inspect(current, REQUEST, fixture=True).search_verified


def test_live_observed_seating_class_uses_current_value():
    current = page()
    current["actions"][4] = {"id": "seating", "node": 5, "kind": "click", "role": "combobox",
                            "label": "Change seating class. Economy", "value": "Economy", "expanded": "false"}
    assert form_checks(current, REQUEST)["cabin"]
    current["actions"][4]["value"] = "Business"
    assert not form_checks(current, REQUEST)["cabin"]


@pytest.mark.parametrize("old,new", [("250", "0"), ("5 hr 30 min", "0 min"),
                                    ("5 hr 30 min", "24 hr"), ("5 hr 30 min", "5 hr 60 min")])
def test_malformed_price_or_duration_cannot_claim_inspected_no_match(old, new):
    malformed = ROW.replace(old, new)
    assert parse_flight(malformed, REQUEST) is None
    result = run_session(Browser([page(malformed)]), REQUEST, fixture=True, decide=choose("DONE"))
    assert not result["successful_run"]
    assert result["inspected_rows"] == 1
    assert result["unparsed_rows"] == 1


def test_live_passenger_popup_does_not_establish_committed_search_from_history():
    current = page(text="Adults\n1\nChildren\nAged 2 to 11\n0\nInfants\nIn seat\n0\nInfants\nOn lap\n0\nDone\nCancel")
    labels = ["Add adult", "Add child aged 2 to 11", "Add infant in seat", "Add infant on lap", "Done", "Cancel"]
    current["actions"] = [{"id": f"popup{index}", "node": 20 + index, "kind": "click", "role": "button",
                           "label": label, "value": ""} for index, label in enumerate(labels)]
    history = [{"action": "Done", "kind": "click", "field": "adults", "text": "1"}]
    assert next_step(current, REQUEST, history) is None
    assert not inspect(current, REQUEST, fixture=True).search_verified
    result = run_session(Browser([current]), REQUEST, fixture=True, decide=choose("DONE"))
    assert not result["successful_run"]
    assert result["metrics"]["actions_executed"] == 0


def transaction_form(*rows, fingerprint="start", epoch=100, suffix=True):
    current = page(*rows, fingerprint=fingerprint)
    label = "1 passenger, change number of passengers." if suffix else "1 passenger"
    current["actions"][3] = {"id": "passengers", "node": 4, "kind": "click", "role": "button",
                            "label": label, "value": ""}
    current["page_key"] = [epoch, current["url"]]
    current["actions"].append({"id": "search", "node": 90, "kind": "click", "role": "button", "label": "Search"})
    return current


def transaction_popup(form, *, counts=(1, 0, 0, 0), epoch=100):
    current = deepcopy(form)
    current["fingerprint"] = "popup-" + form["fingerprint"]
    current["page_key"] = [epoch, form["url"]]
    current["text"] = (f"Adults\n{counts[0]}\nChildren\nAged 2 to 11\n{counts[1]}\nInfants\nIn seat\n{counts[2]}\n"
                       f"Infants\nOn lap\n{counts[3]}\nDone\nCancel")
    labels = ["Add adult", "Add child aged 2 to 11", "Add infant in seat", "Add infant on lap", "Done", "Cancel"]
    current["actions"] = [{"id": "popup-done" if label == "Done" else f"popup{index}", "node": 100 + index,
                           "kind": "click", "role": "button", "label": label, "value": ""}
                          for index, label in enumerate(labels)]
    return current


def transaction_pages():
    initial = transaction_form()
    closed = transaction_form(fingerprint="closed-pre", suffix=False)
    results = transaction_form(ROW, fingerprint="results", suffix=False)
    final = transaction_form(ROW, fingerprint="closed-final", suffix=False)
    return [initial, transaction_popup(initial), closed, results, transaction_popup(results), final]


class Journal:
    def __init__(self):
        self.events = []

    def write(self, event, **data):
        self.events.append((event, data))


@pytest.mark.parametrize("mode", ["local", "frontier", "workflow"])
def test_passengers_are_freshly_verified_before_submit_and_after_collection(mode):
    browser, journal = Browser(transaction_pages()), Journal()
    result = run_session(browser, REQUEST, mode=mode, fixture=True, decide=choose("search"), journal=journal)
    assert result["successful_run"]
    assert browser.actions == ["passengers", "popup-done", "search", "passengers", "popup-done"]
    assert result["metrics"]["verification_transactions"] == 2
    assert result["metrics"]["verification_actions"] == 4
    assert result["metrics"]["observations"] == 6
    assert result["metrics"]["actions_executed"] == 5
    assert result["metrics"]["model_decisions"] == (0 if mode == "workflow" else 1)
    assert [proof["phase"] for proof in result["passenger_verifications"]] == ["pre_submit", "final"]
    assert result["search_checks"]["adults"]
    assert sum(event == "observation" for event, _ in journal.events) == 6
    assert sum(event == "executed" for event, _ in journal.events) == 5


@pytest.mark.parametrize("counts", [(2, 0, 0, 0), (0, 1, 0, 0), (1, 1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1)])
def test_final_passenger_composition_must_be_observed_again(counts):
    pages = transaction_pages()
    pages[4] = transaction_popup(pages[3], counts=counts)
    browser = Browser(pages)
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("search"))
    assert not result["successful_run"]
    assert result["shortlist"] == []
    assert browser.actions == ["passengers", "popup-done", "search", "passengers"]
    assert [proof["phase"] for proof in result["passenger_verifications"]] == ["pre_submit"]


@pytest.mark.parametrize("change", ["url", "epoch", "route", "total"])
def test_terminal_transaction_rejects_context_changes(change):
    pages = transaction_pages()
    closed = pages[-1]
    if change == "url":
        closed["url"] += "&different_search=1"
    elif change == "epoch":
        closed["page_key"][0] = 999
    elif change == "route":
        closed["actions"][0]["current_value"] = "OAK"
    else:
        closed["actions"][3]["label"] = "2 passengers"
    browser = Browser(pages)
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("search"))
    assert not result["successful_run"]
    assert not result["outcome_verified"]
    assert result["shortlist"] == []
    assert result["metrics"]["verification_transactions"] == 2


def test_uncertain_verification_mutation_is_not_retried():
    browser = Browser(transaction_pages(), errors=[None, None, None, None, RuntimeError("Uncertain close")])
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("search"))
    assert not result["successful_run"]
    assert browser.actions == ["passengers", "popup-done", "search", "passengers", "popup-done"]
    assert result["metrics"]["actions_executed"] == 4
    assert result["metrics"]["verification_transactions"] == 2


def test_transaction_stale_rejection_does_not_reuse_or_retry_proof():
    browser = Browser(transaction_pages(), errors=[StalePage("Preaction rejection")])
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("search"))
    assert not result["successful_run"]
    assert browser.actions == ["passengers"]
    assert result["metrics"]["rejected_stale_actions"] == 1
    assert result["passenger_verifications"] == []


def test_verification_actions_consume_the_session_action_budget():
    browser = Browser(transaction_pages())
    result = run_session(browser, REQUEST, mode="local", fixture=True, decide=choose("search"), max_steps=4)
    assert not result["successful_run"]
    assert len(browser.actions) == 4
    assert result["metrics"]["actions_executed"] == 4
    assert "budget" in result["stop_reason"]


def test_arbitrary_page_flag_cannot_establish_adults():
    current = transaction_form(ROW)
    current["passengers_verified"] = True
    assert not inspect(current, REQUEST, fixture=True).search_verified
    assert not finish([current], REQUEST, fixture=True)["outcome_verified"]


def test_provisional_collection_never_reports_verified_outcome():
    current = transaction_form(ROW)
    inspected = inspect(current, REQUEST, fixture=True, allow_unverified_passengers=True)
    assert inspected.flights
    assert not inspected.search_verified
    provisional = finish([current], REQUEST, fixture=True, collection_only=True)
    assert provisional["shortlist"]
    assert not provisional["outcome_verified"]


def test_unchecked_nonstop_is_configured_before_pre_submit_passenger_transaction():
    pages = transaction_pages()
    configured = deepcopy(pages[0])
    configured["fingerprint"] = "nonstop-configured"
    nonstop = {"id": "nonstop", "node": 91, "kind": "click", "role": "checkbox",
               "label": "Nonstop only", "checked": "true"}
    configured["actions"].append(deepcopy(nonstop))
    pages[2]["actions"].append(deepcopy(nonstop))
    initial = deepcopy(configured)
    initial["fingerprint"] = "nonstop-unchecked"
    initial["actions"][-1]["checked"] = "false"
    pages = [initial, configured, transaction_popup(configured), *pages[2:]]
    browser = Browser(pages)
    result = run_session(browser, REQUEST, fixture=True)
    assert result["successful_run"]
    assert browser.actions == ["nonstop", "passengers", "popup-done", "search", "passengers", "popup-done"]
    assert result["metrics"]["verification_transactions"] == 2
    assert result["metrics"]["verification_actions"] == 4
    assert result["metrics"]["deterministic_actions"] == 2
    assert result["metrics"]["model_decisions"] == 0


def airport_popup(markers=("Origin",), *, query="San Francisco", options=()):
    current = page()
    current["url"] = "https://www.google.com/travel/flights?hl=en&curr=USD"
    current["text"] = ""
    current["actions"] = [
        {"id": "query", "node": 21, "kind": "fill", "role": "combobox", "label": "Where else?",
         "expanded": "true", "value": query},
        {"id": "open-query", "node": 21, "kind": "click", "role": "combobox", "label": "Open Where else?",
         "expanded": "true", "value": query},
        *[{"id": f"marker{index}", "node": 30 + index, "kind": "click", "role": "button",
           "label": f"{marker}, Select multiple airports", "value": ""} for index, marker in enumerate(markers)],
        *[{"id": f"option{index}", "node": 40 + index, "kind": "click", "role": "option", "label": label}
          for index, label in enumerate(options)],
        {"id": "wait", "kind": "wait", "label": "Wait for the page to update"},
    ]
    return current


@pytest.mark.parametrize("marker,code", [("Origin", "SFO"), ("Destination", "BOS")])
def test_current_airport_popup_marker_requests_exact_airport_code(marker, code):
    current = airport_popup((marker,))
    step = next_step(current, REQUEST, [])
    assert step.action["id"] == "query"
    assert step.text == code
    assert not form_checks(current, REQUEST)[marker.casefold()]


@pytest.mark.parametrize("marker,label", [("Origin", "San Francisco International Airport (SFO)"),
                                          ("Destination", "Boston Logan International Airport (BOS)")])
def test_current_airport_popup_marker_commits_unique_matching_option(marker, label):
    current = airport_popup((marker,), options=(label,))
    assert next_step(current, REQUEST, []).action["id"] == "option0"
    assert not inspect(current, REQUEST).search_verified


@pytest.mark.parametrize("markers", [(), ("Origin", "Destination"), ("Origin", "Origin")])
def test_airport_popup_marker_ambiguity_or_absence_defers(markers):
    current = airport_popup(markers, query="SFO", options=("San Francisco International Airport (SFO)",))
    current["text"] = "Origin San Francisco SFO"
    history = [{"action": "Origin", "field": "origin", "kind": "fill", "text": "SFO"}]
    assert next_step(current, REQUEST, history) is None
    assert not form_checks(current, REQUEST)["origin"]


def test_airport_popup_matching_option_ambiguity_defers():
    current = airport_popup(options=("San Francisco International Airport (SFO)", "SFO"))
    assert next_step(current, REQUEST, []) is None


def test_airport_query_loading_waits_repeat_without_model_and_are_bounded():
    browser = Browser([airport_popup(query="SFO")])
    result = run_session(browser, REQUEST, fixture=False, max_wait_steps=2)
    assert browser.actions == ["wait", "wait"]
    assert result["metrics"]["model_decisions"] == 0
    assert result["metrics"]["wait_actions"] == 2
    assert not result["successful_run"]
    assert "wait budget" in result["stop_reason"]


def closed_airport_form(key, suffix, *, value, expanded="false"):
    current = page()
    current["url"] = "https://www.google.com/travel/flights?hl=en&curr=USD"
    prefix = "Where from?" if key == "origin" else "Where to?"
    label = prefix + (" " + suffix if suffix else "")
    target = next(a for a in current["actions"] if a["id"] == key)
    target.update(role="combobox", label=label, value=value, current_value=value, expanded=expanded)
    opener = {**target, "id": "open-" + key, "kind": "click", "label": "Open " + label}
    current["actions"].append(opener)
    return current


@pytest.mark.parametrize("key,suffix,value", [("origin", "San Francisco SFO", "San Francisco"),
                                             ("destination", "Boston BOS", "Boston")])
def test_closed_airport_label_independently_identifies_requested_airport(key, suffix, value):
    current = closed_airport_form(key, suffix, value=value)
    assert form_checks(current, REQUEST)[key]
    assert not inspect(current, REQUEST).search_verified


@pytest.mark.parametrize("value", ["San Francisco", "SFO"])
def test_editable_airport_query_alone_is_not_closed_airport_proof(value):
    current = closed_airport_form("origin", "", value=value)
    assert not form_checks(current, REQUEST)["origin"]


@pytest.mark.parametrize("suffix,value,expanded", [
    ("San Francisco BOS", "San Francisco", "false"),
    ("San Francisco SFO BOS", "San Francisco", "false"),
    ("San Francisco SFO", "Oakland", "false"),
    ("San Francisco SFO", "San Francisco", "true"),
])
def test_closed_airport_label_rejects_wrong_mixed_open_or_contradictory_state(suffix, value, expanded):
    current = closed_airport_form("origin", suffix, value=value, expanded=expanded)
    assert not form_checks(current, REQUEST)["origin"]


def closing_trip_menu(*, selected=("false", "true", "false"), labels=("Round trip", "One way", "Multi-city")):
    current = page()
    trip = next(a for a in current["actions"] if a["id"] == "trip_type")
    trip.update(kind="click", role="combobox", label="Change ticket type. One way", expanded="false")
    current["actions"].extend([
        {"id": f"trip-option{index}", "node": 30 + index, "kind": "click", "role": "option",
         "label": label, "selected": checked}
        for index, (label, checked) in enumerate(zip(labels, selected, strict=True))
    ])
    return current


def test_coherent_selected_trip_menu_waits_for_closure():
    current = closing_trip_menu()
    step = next_step(current, REQUEST, [])
    assert step.action["id"] == "wait"
    assert step.action["kind"] == "wait"


@pytest.mark.parametrize("selected,labels", [
    (("false", "false", "false"), ("Round trip", "One way", "Multi-city")),
    (("true", "true", "false"), ("Round trip", "One way", "Multi-city")),
    (("false", "true", "false"), ("Round trip", "One way", "Unfamiliar choice")),
])
def test_unverified_or_unfamiliar_trip_menu_defers(selected, labels):
    assert next_step(closing_trip_menu(selected=selected, labels=labels), REQUEST, []) is None


def nearby_destination_popup():
    current = airport_popup(("Destination",), query="Boston", options=(
        "Boston Logan International Airport (BOS)", "Manchester-Boston Regional Airport (MHT)"))
    current["actions"][0]["label"] = "Where to? "
    current["actions"][1]["label"] = "Open Where to? "
    current["actions"].append({"id": "nearby", "node": 70, "kind": "click", "role": "button",
                               "label": "Toggle nearby airports for Boston, Massachusetts", "expanded": "true"})
    return current


def test_destination_popup_selects_exact_bos_with_known_nearby_airport_expansion():
    current = nearby_destination_popup()
    step = next_step(current, REQUEST, [])
    assert step.action["id"] == "option0"
    assert step.action["label"] == "Boston Logan International Airport (BOS)"
    assert not form_checks(current, REQUEST)["destination"]


@pytest.mark.parametrize("change", ["mismatch", "unrelated_expanded", "duplicate_bos"])
def test_destination_nearby_popup_rejects_ambiguous_or_unrelated_controls(change):
    current = nearby_destination_popup()
    if change == "mismatch":
        current["actions"][0]["label"] = "Where from?"
        current["actions"][1]["label"] = "Open Where from?"
    elif change == "unrelated_expanded":
        current["actions"].append({"id": "unrelated", "node": 80, "kind": "click", "role": "button",
                                   "label": "Change passengers", "expanded": "true"})
    else:
        current["actions"].append({"id": "second-bos", "node": 80, "kind": "click", "role": "option",
                                   "label": "BOS"})
    assert next_step(current, REQUEST, []) is None


def current_calendar_modal():
    current = page()
    current["actions"] = [
        {"id": "departure", "node": 3, "kind": "fill", "role": "textbox", "label": "Departure", "value": ""},
        {"id": "open-departure", "node": 3, "kind": "click", "role": "textbox",
         "label": "Open Departure", "value": ""},
        {"id": "desired-day", "node": 90, "kind": "click", "role": "button",
         "label": "Monday, November 16, 2026", "selected": "false"},
        {"id": "other-day", "node": 91, "kind": "click", "role": "button",
         "label": "Tuesday, November 17, 2026", "selected": "false"},
        {"id": "apply", "node": 92, "kind": "click", "role": "button", "label": "Done"},
    ]
    return current


def test_current_calendar_selects_full_date_without_hidden_form_controls():
    current = current_calendar_modal()
    step = next_step(current, REQUEST, [])
    assert step.action["id"] == "desired-day"
    assert not inspect(current, REQUEST, fixture=True).search_verified


def test_current_calendar_with_conflicting_expanded_widget_defers():
    current = current_calendar_modal()
    current["actions"].append({"id": "unrelated", "node": 80, "kind": "click", "role": "button",
                               "label": "Main menu", "expanded": "true"})
    assert next_step(current, REQUEST, []) is None


def selected_current_date_modal(*, departure="Mon, Nov 16", done_year=2026, generic_done=False):
    current = current_calendar_modal()
    current["url"] = "https://www.google.com/travel/flights?hl=en&curr=USD"
    for action in current["actions"]:
        if action["id"] in {"departure", "open-departure"}:
            action["value"] = departure
        elif action["id"] == "desired-day":
            action["label"] = "Monday, November 16, 2026, departure date."
            action.pop("selected", None)
        elif action["id"] == "apply":
            action["label"] = "Done" if generic_done else \
                f"Done. Search for one-way flights, departing on November 16, {done_year}"
    current["actions"].extend([
        {"id": "another-day", "node": 93, "kind": "click", "role": "button",
         "label": "Wednesday, November 18, 2026"},
        {"id": "trip", "node": 94, "kind": "click", "role": "combobox",
         "label": "Select your ticket type. One way", "value": "One way", "expanded": "false"},
    ])
    return current


def test_exact_done_label_and_compatible_compact_date_prove_current_selected_date():
    current = selected_current_date_modal()
    step = next_step(current, REQUEST, [])
    assert step.action["id"] == "apply"
    assert not inspect(current, REQUEST).search_verified


@pytest.mark.parametrize("kwargs", [{"generic_done": True}, {"done_year": 2027}, {"departure": "Tue, Nov 17"}])
def test_date_commit_requires_exact_done_year_and_current_date_consistency(kwargs):
    assert next_step(selected_current_date_modal(**kwargs), REQUEST, []) is None


def settling_date_modal(**kwargs):
    current = selected_current_date_modal(**kwargs)
    current["actions"].append({"id": "wait", "kind": "wait", "label": "Wait for the page to update"})
    return current


def executed_date_done_history():
    return [{"action": "Done. Search for one-way flights, departing on November 16, 2026",
             "kind": "click", "text": None, "source": "deterministic"}]


def test_current_coherent_done_waits_after_its_execution_without_committed_date_claim():
    current = settling_date_modal()
    step = next_step(current, REQUEST, executed_date_done_history())
    assert step.action["id"] == "wait"
    assert not form_checks(current, REQUEST)["departure"]
    assert not inspect(current, REQUEST).search_verified


def test_calendar_done_settling_waits_repeat_without_model_within_budget():
    browser = Browser([settling_date_modal()])
    result = run_session(browser, REQUEST, max_wait_steps=2)
    assert browser.actions == ["apply", "wait", "wait"]
    assert result["metrics"]["model_decisions"] == 0
    assert result["metrics"]["wait_actions"] == 2
    assert not result["successful_run"]
    assert result["shortlist"] == []
    assert "wait budget" in result["stop_reason"]


@pytest.mark.parametrize("kwargs", [{"generic_done": True}, {"done_year": 2027}, {"departure": "Tue, Nov 17"}])
def test_old_done_history_cannot_replace_current_date_or_year_evidence(kwargs):
    current = settling_date_modal(**kwargs)
    assert next_step(current, REQUEST, executed_date_done_history()) is None
    assert not form_checks(current, REQUEST)["departure"]
    assert not finish([current], REQUEST)["outcome_verified"]


@pytest.mark.parametrize("label,value,expected", [
    ("Economy (include Basic)", "Economy (include Basic)", True),
    ("Premium Economy", "Premium Economy", False),
    ("Business", "Business", False),
    ("Economy (include Basic)", "Business", False),
    ("Business", "Economy (include Basic)", False),
    ("Business", "Economy", False),
    ("Premium Economy", "Economy", False),
])
def test_live_cabin_basic_economy_and_current_label_value_coherence(label, value, expected):
    current = page()
    current["actions"][4] = {"id": "seating", "node": 5, "kind": "click", "role": "combobox",
                            "label": "Change seating class. " + label, "value": value, "expanded": "false"}
    assert form_checks(current, REQUEST)["cabin"] is expected


@pytest.mark.parametrize("airline,depart,arrive,duration,bags,qualifies", [
    ("Delta", "7:00 AM", "3:30 PM", "5 hr 30 min", "1 carry-on bag", True),
    ("JetBlue", "7:30 AM", "4:05 PM", "5 hr 35 min", "1 carry-on bag", True),
    ("United", "12:45 PM", "9:24 PM", "5 hr 39 min", "0 carry-on bags", False),
])
def test_actual_flight_rows_with_numeric_baggage_preserve_itinerary_facts(
        airline, depart, arrive, duration, bags, qualifies):
    bare = (
        f"From 169 US dollars. Nonstop flight with {airline}. "
        f"Leaves San Francisco International Airport at {depart} on Monday, November 16 and arrives at "
        f"Boston Logan International Airport at {arrive} on Monday, November 16. "
        f"Total duration {duration}. Select flight"
    )
    observed = bare.replace(" Select flight", f"   {bags} included. 0 checked bags included.  Select flight")
    flight = parse_flight(observed, REQUEST)
    original = parse_flight(bare, REQUEST)
    assert flight is not None and original is not None
    assert replace(flight, evidence=original.evidence) == original
    assert flight.price == 169
    assert flight.airline == airline
    assert bool(shortlist([flight], REQUEST)) is qualifies
    assert shortlist([flight], replace(REQUEST, airlines=("Other Airline",))) == []


@pytest.mark.parametrize("suffix", [
    "1 carry-on bag included.",
    "2 checked bags included.",
    "0 carry-on bags included. 1 checked bag included.",
])
def test_optional_numeric_baggage_does_not_change_strict_price_or_arrival(suffix):
    for original in (ROW, ROW.replace("250", "400"), ROW.replace("3:30 PM", "6:00 PM")):
        bare = parse_flight(original, REQUEST)
        flight = parse_flight(original.replace("Select flight", suffix + " Select flight"), REQUEST)
        assert flight is not None and bare is not None
        assert replace(flight, evidence=bare.evidence) == bare
        assert bool(shortlist([flight], REQUEST)) == bool(shortlist([bare], REQUEST))


@pytest.mark.parametrize("suffix", [
    "Premium baggage benefits included.",
    "1 carry-on bag included. Additional fare restrictions apply.",
    "1 carry-on bag included. 1 carry-on bag included.",
    "1 checked bag included. 1 carry-on bag included.",
    "-1 carry-on bag included.",
    "1.5 checked bags included.",
])
def test_unrecognized_or_malformed_baggage_suffix_fails_closed(suffix):
    label = ROW.replace("Select flight", suffix + " Select flight")
    assert parse_flight(label, REQUEST) is None
    result = finish([page(label)], REQUEST, fixture=True)
    assert not result["outcome_verified"]
    assert result["shortlist"] == []


def test_baggage_suffix_cannot_join_two_flight_rows_into_one_itinerary():
    first = ROW.replace("Select flight", "1 carry-on bag included. 0 checked bags included. Select flight")
    second = first.replace("250", "169").replace("Delta", "JetBlue").replace("3:30 PM", "9:30 PM")
    assert parse_flight(first + " " + second, REQUEST) is None
    assert parse_flight(first.replace(" Select flight", "") + " " + second, REQUEST) is None


def scrolling_result_pages():
    top = transaction_form(ROW, fingerprint="top", suffix=False)
    top["actions"].append({"id": "scroll_down", "kind": "scroll", "label": "Scroll down"})
    rows = [ROW.replace("Delta", "JetBlue").replace("250", "180"),
            ROW.replace("Delta", "United").replace("250", "200"),
            ROW.replace("Delta", "JetBlue").replace("250", "450")]
    viewports = []
    for index, row in enumerate(rows):
        current = deepcopy(top)
        current["fingerprint"] = f"viewport{index}"
        current["page_key"] = [100, current["url"], 0, 560 * (index + 1)]
        current["actions"] = [
            {"id": "row", "kind": "click", "label": row},
            {"id": "scroll_down", "kind": "scroll", "label": "Scroll down"},
            {"id": "scroll_up", "kind": "scroll", "label": "Scroll up"},
            {"id": "wait", "kind": "wait", "label": "Wait for the page to update"},
        ]
        viewports.append(current)
    restored = deepcopy(top)
    restored["fingerprint"] = "restored"
    final = deepcopy(restored)
    final["fingerprint"] = "closed-final"
    returning = deepcopy(viewports[0])
    returning["actions"][0]["label"] = rows[2]
    return [top, *viewports, viewports[1], returning, restored, transaction_popup(restored), final]


@pytest.mark.parametrize("mode", ["workflow", "local", "frontier"])
def test_offscreen_results_restore_controls_and_fresh_passenger_proof_before_success(mode):
    browser = Browser(scrolling_result_pages())
    result = run_session(browser, REQUEST, mode=mode, fixture=True)
    assert result["successful_run"]
    assert browser.actions == ["scroll_down"] * 3 + ["scroll_up"] * 3 + ["passengers", "popup-done"]
    assert result["metrics"]["collection_actions"] == 6
    assert result["metrics"]["model_decisions"] == 0
    assert [p["phase"] for p in result["passenger_verifications"]] == ["final"]
    # The later viewport's 450 fare supersedes JetBlue's earlier 180 fare.
    assert [(f["airline"], f["price"]) for f in result["shortlist"]] == [("United", 200), ("Delta", 250)]


@pytest.mark.parametrize("change", ["source", "epoch", "origin", "adults", "challenge", "expanded"])
def test_offscreen_collection_rejects_changed_context_or_present_contradiction(change):
    pages = scrolling_result_pages()
    current = pages[1]
    if change == "source":
        current["url"] += "&new_search=1"
    elif change == "epoch":
        current["page_key"][0] += 1
    elif change == "origin":
        current["actions"].append({"id": "wrong", "kind": "fill", "label": "Origin", "value": "OAK"})
    elif change == "adults":
        current["actions"].append({"id": "wrong", "kind": "fill", "label": "Adults", "value": "2"})
    elif change == "challenge":
        current["text"] = "Verify you are human"
    else:
        current["actions"].append({"id": "open", "kind": "click", "label": "Stops", "expanded": "true"})
    browser = Browser([pages[0], current])
    result = run_session(browser, REQUEST, fixture=True)
    assert browser.actions == ["scroll_down"]
    assert not result["successful_run"]
    assert result["shortlist"] == []
    assert result["metrics"]["model_decisions"] == 0


def test_offscreen_rows_never_succeed_without_restored_header_proof():
    pages = scrolling_result_pages()
    browser = Browser(pages[:4] + [pages[3]] * 5)
    result = run_session(browser, REQUEST, fixture=True)
    assert browser.actions == ["scroll_down"] * 3 + ["scroll_up"] * 3
    assert not result["successful_run"]
    assert result["shortlist"] == []
    assert "restored" in result["stop_reason"]


def test_final_restored_header_cannot_inherit_offscreen_search_proof():
    pages = scrolling_result_pages()
    pages[-1]["actions"][0].update(value="OAK", current_value="OAK")
    result = run_session(Browser(pages), REQUEST, fixture=True)
    assert not result["successful_run"]
    assert result["shortlist"] == []


def test_missing_observed_scroll_up_stops_without_model_or_invented_target():
    pages = scrolling_result_pages()
    pages[3]["actions"] = [a for a in pages[3]["actions"] if a["id"] != "scroll_up"]
    browser = Browser(pages[:4])
    result = run_session(browser, REQUEST, fixture=True)
    assert browser.actions == ["scroll_down"] * 3
    assert not result["successful_run"]
    assert result["shortlist"] == []
    assert result["metrics"]["model_decisions"] == 0
    assert "restored" in result["stop_reason"]


def blank_search_snapshot():
    current = page()
    current["actions"] = [
        {"id": "scroll_down", "kind": "scroll", "label": "Scroll down", "delta": 560},
        {"id": "wait", "kind": "wait", "label": "Wait for the page to update"},
    ]
    current["omitted_actions"] = 0
    return current


@pytest.mark.parametrize("mode", ["workflow", "local", "frontier"])
def test_truly_blank_search_snapshot_waits_then_uses_fresh_verified_results(mode):
    browser = Browser([blank_search_snapshot(), page(ROW)])
    result = run_session(browser, REQUEST, mode=mode, fixture=True)
    assert result["successful_run"]
    assert browser.actions == ["wait"]
    assert result["metrics"]["wait_actions"] == 1
    assert result["metrics"]["model_decisions"] == 0


def test_persistent_blank_search_snapshot_stops_at_shared_wait_budget():
    browser = Browser([blank_search_snapshot()])
    result = run_session(browser, REQUEST, fixture=True, max_wait_steps=2)
    assert browser.actions == ["wait", "wait"]
    assert not result["successful_run"]
    assert result["shortlist"] == []
    assert "wait budget" in result["stop_reason"]


@pytest.mark.parametrize("change", ["text", "element", "omitted", "challenge", "source"])
def test_blank_wait_does_not_hide_populated_ambiguous_or_challenged_pages(change):
    current = blank_search_snapshot()
    if change == "text":
        current["text"] = "Unknown flight search controls"
    elif change == "element":
        current["actions"].append({"id": "mystery", "node": 11, "kind": "click", "label": "Unknown control"})
    elif change == "omitted":
        current["omitted_actions"] = 1
    elif change == "challenge":
        current["text"] = "Verify you are human"
    else:
        current["url"] = "https://example.com/booking"
    browser = Browser([current])
    result = run_session(browser, REQUEST, fixture=True)
    assert browser.actions == []
    assert not result["successful_run"]
    assert result["shortlist"] == []


def test_preaction_stale_scroll_up_does_not_consume_successful_restoration_budget():
    pages = scrolling_result_pages()
    pages.insert(4, deepcopy(pages[3]))  # Preaction rejection leaves the current viewport unchanged.
    browser = Browser(pages, errors=[None, None, None, StalePage("Preaction rejected scroll")])
    result = run_session(browser, REQUEST, fixture=True)
    assert result["successful_run"]
    assert browser.actions == ["scroll_down"] * 3 + ["scroll_up"] * 4 + ["passengers", "popup-done"]
    assert result["metrics"]["rejected_stale_actions"] == 1
    assert result["metrics"]["collection_actions"] == 6
    assert result["metrics"]["actions_executed"] == 8
    assert result["metrics"]["model_decisions"] == 0
