"""Independent outcome tests. Expected answers never enter policy prompts."""

import base64
import re
from urllib.parse import parse_qs, urlparse


def verify_local(actual, expected):
    submitted = actual.get("submitted") or {}
    checks = {key: str(submitted.get(key, "")).strip().casefold() == value.casefold()
              for key, value in expected.items()}
    checks["search_submitted"] = actual.get("submitted") is not None
    checks["results_visible"] = actual.get("results_visible") is True
    checks["no_flight_selected"] = actual.get("selected") is False
    return {"passed": all(checks.values()), "checks": checks}


LOCAL_READ = """(() => ({
  submitted: window.submittedSearch || null,
  results_visible: !!document.querySelector('#results:not([hidden]) article'),
  selected: window.flightSelected === true
}))()"""


def diagnose_local(events, expected):
    """Classify observed fixture failures after the run. Do not direct the policy."""
    fields = {"Origin": "origin", "Destination": "destination", "Departure date (YYYY-MM-DD)": "departure"}
    selections = {"Adults": "adults", "Cabin": "cabin", "Trip type": "trip_type"}
    observed = {}
    for event in events:
        if event["event"] == "observation":
            observed = {a.get("label"): a.get("value", "") for a in event["page"].get("actions", [])
                        if a.get("kind") == "fill"}
            observed.update({a["label"].split(" → ")[0]: a.get("current_value", "")
                             for a in event["page"].get("actions", []) if a.get("kind") == "select"})
        if event["event"] == "observation" and event.get("step") == 0:
            actions = event["page"].get("actions", [])
            missing = [label for label in fields if not any(a.get("label") == label for a in actions)]
            if missing:
                return {"step": 0, "category": "missing_control", "cause": "Required fields were not observed.",
                        "fields": missing, "inference": False}
        if event["event"] == "executed":
            action = event["action"]
            field = selections.get(action.get("label", "").split(" → ")[0])
            if (field and action.get("kind") == "select"
                    and action.get("value", "").casefold() != expected[field].casefold()):
                return {"step": event["step"], "category": "wrong_decision", "field": field,
                        "cause": "The selected dropdown value contradicts the fixed requirement.", "inference": False}
            if action.get("label") == "Search flights":
                mismatched = [key for label, key in (fields | selections).items()
                              if observed.get(label, "").strip().casefold() != expected[key].casefold()]
                if mismatched:
                    return {"step": event["step"], "category": "wrong_decision", "fields": mismatched,
                            "cause": "The submitted controls did not satisfy all fixed requirements.",
                            "inference": False}
            field = fields.get(action.get("label"))
            if field and action.get("kind") == "fill":
                if str(event.get("text", "")).strip().casefold() != expected[field].casefold():
                    return {"step": event["step"], "category": "incorrect_field_text",
                            "cause": "The entered field text differs from the fixed requirement.",
                            "field": field, "inference": False}
            if action.get("label", "").startswith("Help topic "):
                return {"step": event["step"], "category": "wrong_decision",
                        "cause": "The action opened an unrelated fixture help topic.", "inference": False}
    return None


def verify_flights(page, expected):
    parsed = urlparse(page.get("url", ""))
    actions = page.get("actions", [])
    values = {a.get("label", "").strip(): a.get("value", "") for a in actions}
    labels = [a.get("label", "") for a in actions]
    flights = [label for label in labels if "Select flight" in label]
    encoded = parse_qs(parsed.query).get("tfs", [""])[0]
    try:
        url_bytes = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
    except ValueError:
        url_bytes = b""
    # These are verifier adapters, not instructions or targets for the decision model.
    checks = {
        "search_page": parsed.hostname == "www.google.com" and parsed.path == "/travel/flights/search",
        "origin": values.get("Where from?") in expected["origin_labels"],
        "destination": values.get("Where to?") in expected["destination_labels"],
        "departure": values.get("Departure") == expected["date_label"],
        "year": expected["date"].encode() in url_bytes,
        "trip_type": values.get("Change ticket type. One way") == "One way",
        "adults": any(re.fullmatch(r"1 passenger[,.]? 1 adult[.]?", label, re.I) for label in labels),
        "cabin": any(values.get(label) == "Economy" for label in ("Economy", "Change cabin class. Economy")),
        "results_visible": bool(flights),
        "result_dates": bool(flights) and all(expected["result_date"] in label for label in flights),
    }
    return {"passed": all(checks.values()), "checks": checks, "visible_result_count": len(flights),
            "limitations": "Unknown control labels fail closed. Live adapter validation is pending."}
