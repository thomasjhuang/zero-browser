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


def verify_selection(page, events, expected):
    """Require an observed option click followed by a closed, populated target field."""
    target = expected["target_label"].strip().casefold()
    token = re.compile(r"(?<!\w)" + re.escape(expected["option_text"]) + r"(?!\w)", re.I)
    # Keep identity across a label update only within the same document.
    original = next((e["page"] for e in events if e.get("event") == "observation"
                     and any(a.get("kind") == "fill" and a.get("label", "").strip().casefold() == target
                             for a in e["page"].get("actions", []))), {})
    nodes = {a.get("node") for a in original.get("actions", []) if a.get("kind") == "fill"
             and a.get("label", "").strip().casefold() == target}
    same_document = (bool(page.get("page_key")) and bool(original.get("page_key"))
                     and page["page_key"][0] == original["page_key"][0])
    fields = [a for a in page.get("actions", []) if a.get("kind") == "fill"
              and (a.get("label", "").strip().casefold() == target
                   or (same_document and len(nodes) == 1 and a.get("node") in nodes
                       and a.get("label", "").strip().casefold().startswith(target + " ")
                       and token.search(a.get("label", ""))))]
    mutations = [(i, e) for i, e in enumerate(events)
                 if e.get("event") == "executed" and e["action"]["kind"] not in {"wait", "scroll"}]
    selection = None
    if mutations:
        index, last = mutations[-1]
        action = last["action"]
        before = next((e["page"] for e in reversed(events[:index]) if e.get("event") == "observation"), {})
        observed = any(all(a.get(k) == action.get(k) for k in ("node", "id", "kind", "label"))
                       for a in before.get("actions", []))
        if (observed and action.get("kind") == "click" and action.get("role") == "option"
                and token.search(action.get("label", ""))):
            selection = {"step": last.get("step"), "label": action["label"]}
    checks = {
        "matching_observed_option_clicked": selection is not None,
        "unique_target_field": len(fields) == 1,
        "selected_field_populated": len(fields) == 1 and bool(str(fields[0].get("value", "")).strip()),
        "selection_dialog_closed": len(fields) == 1 and fields[0].get("expanded") == "false",
    }
    return {"passed": all(checks.values()), "checks": checks, "selected_option": selection,
            "observed_field": fields[0] if len(fields) == 1 else None,
            "limitations": "Typed text alone is insufficient. Unrecognized option semantics fail closed."}


def verify_round_trip(page, events, expected):
    """Read provider output independently. This adapter never chooses actions."""
    parsed = urlparse(page.get("url", ""))
    actions = page.get("actions", [])
    encoded = parse_qs(parsed.query).get("tfs", [""])[0]
    try:
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
    except ValueError:
        payload = b""
    def field(prefix):
        matches = [a for a in actions if a.get("kind") == "fill"
                   and a.get("label", "").strip().casefold().startswith(prefix.casefold())]
        return matches[0] if len(matches) == 1 else None

    origin, destination = field("Where from?"), field("Where to?")
    departure, returning = field("Departure"), field("Return")
    def airport(control, code, names):
        if not control or control.get("expanded") != "false":
            return False
        label = control.get("label", "")
        value = control.get("value", "").strip().casefold()
        return (re.search(r"(?<!\w)" + re.escape(code) + r"(?!\w)", label) is not None
                or (code.encode() in payload and value in {n.casefold() for n in names}))

    def date_matches(control, date):
        from datetime import date as Date
        day = Date.fromisoformat(date)
        text = " ".join(str(control.get(k, "")) for k in ("label", "value")) if control else ""
        month_day = re.search(r"\b" + day.strftime("%b") + r"\s+" + str(day.day) + r"\b", text, re.I)
        return bool(control and (date in text or month_day) and date.encode() in payload)

    labels = [a.get("label", "") for a in actions]
    options = [label for label in labels if "select flight" in label.casefold()]
    adult_evidence = []
    for event in events:
        if event.get("event") != "observation":
            continue
        observed = event["page"]
        for a in observed.get("actions", []):
            if (re.search(r"\badults?\b", a.get("label", ""), re.I)
                    and str(a.get("value", "")).isdigit()):
                adult_evidence.append({"step": event.get("step"), "count": int(a["value"]),
                                       "label": a["label"]})
        count = re.search(r"\bAdults?\s*\n\s*(\d+)\b", observed.get("text", ""), re.I)
        if count:
            adult_evidence.append({"step": event.get("step"), "count": int(count.group(1)),
                                   "text": count.group(0)})
    explicit_adults = any(re.fullmatch(r"1 passenger[,.]? 1 adult[.]?", label, re.I) for label in labels)
    passenger_summary = any(re.match(r"1 passenger(?:\b|,)", label, re.I) for label in labels)
    adults = explicit_adults or (passenger_summary and bool(adult_evidence)
                                 and adult_evidence[-1]["count"] == expected["adults"])
    checks = {
        "results_page": parsed.hostname == "www.google.com" and parsed.path == "/travel/flights/search",
        "origin_SFO": airport(origin, expected["origin"], expected["origin_names"]),
        "destination_JFK": airport(destination, expected["destination"], expected["destination_names"]),
        "round_trip": any(a.get("value") == "Round trip" for a in actions),
        "departure_date_and_year": date_matches(departure, expected["departure"]),
        "return_date_and_year": date_matches(returning, expected["return"]),
        "one_adult": bool(adults),
        "economy": any(a.get("value") == expected["cabin"] for a in actions),
        "actual_flight_options": bool(options),
    }
    return {"passed": all(checks.values()), "checks": checks, "visible_result_count": len(options),
            "flight_options": options[:5], "fields": {"origin": origin, "destination": destination,
            "departure": departure, "return": returning}, "adult_evidence": adult_evidence[-1:],
            "limitations": "Unknown provider output fails closed. URL date evidence supports the explicit year."}
