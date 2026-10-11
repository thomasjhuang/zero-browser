"""Optional travel rules over current observations. Unknown controls defer to the model."""

from dataclasses import dataclass
from datetime import date, datetime

from .contracts import normalized
from .observe import field_name, fields, form_checks, passenger_control


@dataclass(frozen=True)
class Step:
    action: dict
    text: str | None
    reason: str


def unique(actions):
    """Node identities are used only to collapse variants from the current snapshot."""
    if any(not a.get("id") for a in actions):
        return None
    matches = {a.get("node") or a["id"]: a for a in actions}
    return next(iter(matches.values())) if len(matches) == 1 else None


def _calendar_date(action):
    if action.get("kind") != "click" or action.get("role") not in {"button", "gridcell"}:
        return None
    label = " ".join(action.get("label", "").split())
    for fmt in ("%A, %B %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            value = datetime.strptime(label, fmt).date()
            if fmt.startswith("%A") and value.strftime("%A").casefold() != label.split(",")[0].casefold():
                return None
            return value
        except ValueError:
            pass
    return None


def _date_step(actions, request, checked, history=None):
    controls = [a for a in actions if field_name(a) == "departure"]
    days = [(a, _calendar_date(a)) for a in actions]
    days = [(a, value) for a, value in days if value is not None]
    active = bool(controls) and (any(a.get("expanded") == "true" for a in controls) or len(days) >= 2)
    if active:
        wanted = date.fromisoformat(request.departure_date)
        values = fields({"actions": actions})
        compatible_dates = {
            request.departure_date, f"{wanted:%a}, {wanted:%b} {wanted.day}",
            f"{wanted:%A}, {wanted:%B} {wanted.day}",
            f"{wanted:%A}, {wanted:%B} {wanted.day}, {wanted.year}",
            f"{wanted:%b} {wanted.day}, {wanted.year}",
        }
        expected_done = normalized(f"Done. Search for one-way flights, departing on {wanted:%B} "
                                   f"{wanted.day}, {wanted.year}")
        described_done = [a for a in actions if a.get("kind") == "click" and a.get("role") == "button" and
                          normalized(a.get("label", "")).startswith("done search for one way flights departing on ")]
        done = unique(described_done)
        if (done and all(normalized(a["label"]) == expected_done for a in described_done) and
                values.get("departure") in compatible_dates and normalized(values.get("trip_type", "")) == "one way"):
            recent = next((entry for entry in reversed(history or []) if entry.get("kind") != "wait"), {})
            if (recent.get("kind") == "click" and recent.get("source") in {"deterministic", "model"} and
                    normalized(recent.get("action", "")) == expected_done):
                # Executed history permits only waiting for this still-coherent transition. It
                # never proves date commitment or outcome success, and never retries this click.
                wait = unique([a for a in actions if a.get("kind") == "wait"])
                return Step(wait, None, "Wait for the executed date Done transition to settle") if wait else None
            return Step(done, None, "Apply the departure date proved by the current full-year Done label and field")
        candidate = unique([a for a, value in days if value == wanted])
        if candidate and candidate.get("selected") != "true":
            return Step(candidate, None, "Choose the uniquely observed departure date, including its year")
        if checked or (candidate and candidate.get("selected") == "true"):
            done = unique([a for a in actions if a.get("kind") == "click" and a.get("role") == "button"
                           and normalized(a.get("label", "")) in {
                               "done", "apply dates",
                               normalized(f"Done. Search for one-way flights, departing on {wanted:%B} "
                                          f"{wanted.day}, {wanted.year}"),
                           }])
            if done:
                return Step(done, None, "Apply the currently verified departure date")
        if days:
            months = {(value.year, value.month) for _, value in days}
            target = (wanted.year, wanted.month)
            direction = "next" if target > max(months) else "previous" if target < min(months) else None
            if direction:
                candidate = unique([a for a in actions if a.get("kind") == "click" and a.get("role") == "button"
                                    and normalized(a.get("label", "")) == f"{direction} month"])
                if candidate:
                    return Step(candidate, None, "Navigate the calendar using explicitly observed month/year dates")
        return None
    if checked:
        return None
    candidate = unique([a for a in controls if a.get("kind") == "fill"
                        and "yyyy mm dd" in normalized(a.get("label", ""))])
    if candidate:
        return Step(candidate, request.departure_date, "Enter the explicitly formatted departure date")
    candidate = unique([a for a in controls if a.get("kind") == "click"])
    if candidate:
        return Step(candidate, None, "Open the observed departure-date control")
    return None



def _airport_popup_step(actions, request):
    markers = [a for a in actions if a.get("kind") == "click" and a.get("role") == "button" and
               normalized(a.get("label", "")) in {
                   "origin select multiple airports", "destination select multiple airports",
               }]
    marker = unique(markers)
    if marker is None or len({normalized(a["label"]) for a in markers}) != 1:
        return None
    key = normalized(marker["label"]).split()[0]
    query_labels = {"where else", "where from" if key == "origin" else "where to"}
    queries = [a for a in actions if a.get("kind") == "fill" and a.get("role") == "combobox" and
               a.get("expanded") == "true" and normalized(a.get("label", "")) in query_labels]
    query = unique(queries)
    if query is None:
        return None
    query_node = query.get("node") or query["id"]
    for action in actions:
        if action.get("expanded") != "true" or (action.get("node") or action.get("id")) == query_node:
            continue
        label = normalized(action.get("label", ""))
        if (action.get("kind") != "click" or action.get("role") != "button" or
                not label.startswith("toggle nearby airports for ")):
            return None
    query_values = {str(a.get("current_value", a.get("value", ""))) for a in queries}
    if len(query_values) != 1 or ("current_value" in query and "value" in query and
                                 str(query["current_value"]) != str(query["value"])):
        return None
    airport = getattr(request, key)
    options = [a for a in actions if a.get("kind") == "click" and a.get("role") == "option"]
    candidate = unique([a for a in options if airport.identifies(a.get("label", ""))])
    if candidate:
        return Step(candidate, None, f"Commit the uniquely matching {key} airport suggestion")
    if options:
        return None
    value = str(query.get("current_value", query.get("value", "")))
    if normalized(value) != normalized(airport.code):
        return Step(query, airport.code, f"Enter the exact {key} airport code in the explicitly identified popup")
    wait = unique([a for a in actions if a.get("kind") == "wait"])
    return Step(wait, None, "Wait for the airport-code suggestions to appear") if wait else None

def next_step(page, request, history, *, verification=None):
    """History never proves commitment. Every selected target comes from this observation."""
    actions = page.get("actions", [])
    if page.get("omitted_actions", 0):
        return None
    # The live airport popup names its context separately from its generic editable input.
    if any(normalized(a.get("label", "")) in {"origin select multiple airports", "destination select multiple airports"}
           or (a.get("expanded") == "true" and normalized(a.get("label", "")) in {"where else", "open where else"})
           for a in actions):
        return _airport_popup_step(actions, request)
    expanded_fields = {field_name(a) for a in actions if a.get("expanded") == "true"}
    # A calendar modal hides the other form fields. Its explicitly observed full dates can be
    # handled directly without treating those hidden settings as previously verified.
    if (any(field_name(a) == "departure" for a in actions) and
            sum(_calendar_date(a) is not None for a in actions) >= 2):
        if expanded_fields - {"departure"}:
            return None
        return _date_step(actions, request, form_checks(page, request, verification=verification)["departure"], history)
    checks = form_checks(page, request, verification=verification)
    options = [a for a in actions if a.get("role") == "option" and a.get("kind") == "click"]
    # A selected menu can remain visible during its closing animation. Wait only for this exact
    # coherent state; unfamiliar options or conflicting selection never authorize a mutation.
    trip_controls = [a for a in actions if field_name(a) == "trip_type"]
    trip_option_labels = {"round trip", "one way", "multi city"}
    if (options and not expanded_fields and checks["trip_type"] and unique(trip_controls) is not None and
            all(a.get("expanded") == "false" for a in trip_controls) and len(options) == 3 and
            len({a.get("node") or a.get("id") for a in options}) == 3 and
            {normalized(a.get("label", "")) for a in options} == trip_option_labels and
            all(a.get("selected") == ("true" if normalized(a["label"]) == "one way" else "false")
                for a in options)):
        wait = unique([a for a in actions if a.get("kind") == "wait"])
        return Step(wait, None, "Wait for the coherently selected One way menu to finish closing") if wait else None
    # An open airport query takes precedence. An option with mixed airport codes is ambiguous.
    active_airports = expanded_fields & {"origin", "destination"}
    if active_airports:
        if len(active_airports) != 1 or expanded_fields - active_airports:
            return None
        key = next(iter(active_airports))
        airport = getattr(request, key)
        candidate = unique([a for a in options if airport.identifies(a.get("label", ""))])
        return Step(candidate, None, f"Commit the uniquely matching {key} airport suggestion") if candidate else None

    for key, wanted in (("trip_type", "One way"), ("adults", "1"), ("cabin", "Economy")):
        if checks[key] and key not in expanded_fields:
            continue
        if key == "adults" and not expanded_fields and passenger_control(page) is not None:
            # Configure the other fields first. A separate fresh popup transaction must prove adults
            # immediately before submission; the passenger total alone never permits Search.
            continue
        if expanded_fields and expanded_fields != {key}:
            return None
        if key in expanded_fields:
            candidate = unique([a for a in actions if a.get("role") in {"option", "menuitemradio", "radio"}
                                and a.get("kind") == "click" and normalized(a.get("label", "")) == normalized(wanted)])
            if candidate and candidate.get("selected") != "true" and candidate.get("checked") != "true":
                return Step(candidate, None, f"Choose the observed {key} option")
            return None
        if options:
            return None
        candidate = unique([a for a in actions if field_name(a) == key and a.get("kind") == "select"
                            and normalized(a.get("label", "").split(" → ")[-1]) == normalized(wanted)])
        if candidate:
            return Step(candidate, None, f"Set {key} to the requested value")
        candidate = unique([a for a in actions if field_name(a) == key and a.get("kind") == "click"
                            and a.get("role") in {"button", "combobox"}])
        if candidate:
            return Step(candidate, None, f"Open the observed {key} control")
        return None

    if expanded_fields and expanded_fields != {"departure"}:
        return None
    if options:
        return None
    if expanded_fields == {"departure"} or sum(_calendar_date(a) is not None for a in actions) >= 2:
        return _date_step(actions, request, checks["departure"], history)
    if any(a.get("role") == "gridcell" for a in actions):
        return None

    for key in ("origin", "destination"):
        if checks[key]:
            continue
        airport = getattr(request, key)
        value = fields(page).get(key, "")
        if not airport.matches(value) and not airport.identifies(value):
            candidate = unique([a for a in actions if field_name(a) == key and a.get("kind") == "fill"])
            if candidate:
                return Step(candidate, airport.city, f"Enter the requested {key} query")
        candidate = unique([a for a in actions if field_name(a) == key and a.get("kind") == "click"])
        if candidate:
            return Step(candidate, None, f"Open the observed {key} airport control")
        return None

    if not checks["departure"]:
        return _date_step(actions, request, False, history)
    # Optional GUI filtering is safe only for an explicit unchecked nonstop control.
    if request.nonstop:
        candidate = unique([a for a in actions if a.get("kind") == "click" and a.get("role") == "checkbox"
                            and a.get("checked") == "false"
                            and normalized(a.get("label", "")) in {"nonstop", "nonstop only"}])
        if candidate:
            return Step(candidate, None, "Enable the explicitly observed nonstop filter")
    if expanded_fields:
        return None
    candidate = unique([a for a in actions if a.get("kind") == "click" and a.get("role") == "button"
                        and normalized(a.get("label", "")) in {"search", "search flights", "find flights"}])
    if candidate and all(checks.values()):
        return Step(candidate, None, "Submit the currently verified search form")
    return None
