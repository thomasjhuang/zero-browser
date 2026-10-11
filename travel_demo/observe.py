"""Conservative English flight observations, independent of model completion."""

import base64
import binascii
import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from urllib.parse import parse_qs, urlparse

from .contracts import Flight, normalized

FIELD_LABELS = {
    "origin": {"origin", "where from", "departure airport", "from"},
    "destination": {"destination", "where to", "arrival airport", "to"},
    "departure": {"departure", "departure date", "departure date yyyy mm dd"},
    "adults": {"adults", "passengers", "travelers"},
    "cabin": {"cabin", "cabin class", "travel class"},
    "trip_type": {"trip type", "ticket type"},
}


def field_name(action):
    label = normalized(action.get("label", "").split(" → ")[0])
    if label.startswith("open "):
        label = label[5:]
    for field, labels in FIELD_LABELS.items():
        if label in labels:
            return field
    if action.get("role") == "combobox":
        if re.fullmatch(r"where from .+", label):
            return "origin"
        if re.fullmatch(r"where to .+", label):
            return "destination"
    if re.fullmatch(r"(?:change ticket type|select your ticket type) (round trip|one way|multi city)", label):
        return "trip_type"
    if re.fullmatch(r"change (?:cabin|seating) class (economy(?: include basic)?|business|first|premium economy)",
                    label):
        return "cabin"
    if label in {"economy", "business", "first", "premium economy"} and action.get("role") == "combobox":
        return "cabin"
    if (action.get("role") == "button" and
            re.fullmatch(r"\d+ passengers?(?: change number of passengers)?", label)):
        return "adults"
    if re.fullmatch(r"\d+ passengers? change number of passengers", label):
        return "adults"
    if re.fullmatch(r"\d+ passengers? \d+ adults?", label):
        return "adults"
    return None


def field_value(action):
    # A passenger total is not an adult count, even if the button carries a numeric value.
    if (action.get("role") == "button" and
            re.fullmatch(r"\d+ passengers?(?: change number of passengers)?", normalized(action.get("label", "")))):
        return ""
    value = str(action.get("current_value", action.get("value", "")))
    if value:
        if field_name(action) != "cabin":
            return value
        canonical = "Economy" if normalized(value) == "economy include basic" else value
        label = normalized(action.get("label", "")).removeprefix("open ")
        declared = re.fullmatch(
            r"change (?:cabin|seating) class (economy(?: include basic)?|business|first|premium economy)", label,
        )
        label_class = declared[1] if declared else label if label in {
            "economy", "business", "first", "premium economy",
        } else None
        if label_class == "economy include basic":
            label_class = "economy"
        if label_class is not None and normalized(canonical) != label_class:
            return ""
        return canonical
    label = normalized(action.get("label", ""))
    for prefix in ("change ticket type ", "select your ticket type ", "change cabin class ", "change seating class "):
        if label.startswith(prefix):
            extracted = label[len(prefix):]
            return "Economy" if field_name(action) == "cabin" and extracted == "economy include basic" else extracted
    if field_name(action) == "adults" and label in {"1 passenger 1 adult", "1 passengers 1 adults"}:
        return "1"
    if field_name(action) == "cabin" and label == "economy":
        return "Economy"
    return ""


def fields(page):
    """Conflicting current field values stay unknown, including duplicate controls."""
    groups = {}
    for action in page.get("actions", []):
        name = field_name(action)
        if name:
            groups.setdefault(name, set()).add(field_value(action))
    return {name: next(iter(values)) for name, values in groups.items() if len(values) == 1}



def _unique_control(actions):
    if not actions or any(not a.get("id") for a in actions):
        return None
    nodes = {a.get("node") or a["id"]: a for a in actions}
    return next(iter(nodes.values())) if len(nodes) == 1 else None


def passenger_control(page):
    """Discover a passenger TOTAL button; it never proves adult composition."""
    if page.get("omitted_actions", 0):
        return None
    candidates = []
    for action in page.get("actions", []):
        label = normalized(action.get("label", ""))
        match = re.fullmatch(r"(?P<count>\d+) passengers?(?: change number of passengers)?", label)
        if action.get("kind") != "click" or action.get("role") != "button" or not match:
            continue
        value = str(action.get("current_value", action.get("value", "")))
        if value and normalized(value) not in {match["count"], f"{match['count']} passenger",
                                               f"{match['count']} passengers"}:
            return None
        candidates.append(action)
    return _unique_control(candidates)


def passenger_popup_counts(page):
    """Read only the complete currently observed passenger popup, including zero child/infant counts."""
    if page.get("omitted_actions", 0):
        return None
    text = " ".join(page.get("text", "").split())
    match = re.fullmatch(
        r"Adults (\d+) Children Aged 2 to 11 (\d+) Infants In seat (\d+) Infants On lap (\d+) Done Cancel",
        text,
    )
    if not match:
        return None
    expected = {"add adult", "add child aged 2 to 11", "add infant in seat", "add infant on lap", "done", "cancel"}
    clicks = [a for a in page.get("actions", []) if a.get("kind") not in {"scroll", "wait"}]
    if any(a.get("kind") != "click" or a.get("role") != "button" or
           normalized(a.get("label", "")) not in expected for a in clicks):
        return None
    if any(_unique_control([a for a in clicks if normalized(a.get("label", "")) == label]) is None
           for label in expected):
        return None
    counts = tuple(int(value) for value in match.groups())
    return counts if all(0 <= value <= 9 for value in counts) else None


def passenger_done(page):
    if passenger_popup_counts(page) is None:
        return None
    return _unique_control([a for a in page.get("actions", []) if a.get("kind") == "click" and
                            a.get("role") == "button" and normalized(a.get("label", "")) == "done"])


def passenger_context(page):
    """Context used within a fresh verification transaction; no browser history is consulted."""
    control = passenger_control(page)
    page_key = page.get("page_key", [])
    if (control is None or not isinstance(page_key, (list, tuple)) or not page_key or
            type(page_key[0]) not in {int, float} or not math.isfinite(page_key[0]) or page_key[0] <= 0):
        return None
    count = normalized(control["label"]).split()[0]
    values = fields(page)
    return (page_key[0], page.get("url", ""), tuple((key, values.get(key)) for key in
            ("origin", "destination", "departure", "cabin", "trip_type")), count)


@dataclass(frozen=True)
class PassengerVerification:
    """Session-produced proof from a fresh popup/read/close transaction; expires on any other mutation."""

    counts: tuple[int, int, int, int]
    popup_fingerprint: str
    closed_fingerprint: str
    context: tuple

    def matches(self, page, request):
        if (not isinstance(self.counts, tuple) or any(type(value) is not int for value in self.counts) or
                self.counts != (request.adults, 0, 0, 0) or self.context is None or
                not self.popup_fingerprint or
                not self.closed_fingerprint or self.popup_fingerprint == self.closed_fingerprint or
                self.closed_fingerprint != page.get("fingerprint") or self.context != passenger_context(page)):
            return False
        control = passenger_control(page)
        if control is None or normalized(control["label"]).split()[0] != str(request.adults):
            return False
        # A proof never overrides a contradictory or unknown additional adult control.
        return all(field_value(a) == str(request.adults) for a in page.get("actions", [])
                   if field_name(a) == "adults" and a is not control)

def _wire_fields(payload):
    """Read bounded protobuf wire fields; unfamiliar wire types fail closed."""
    offset, result = 0, {}

    def varint():
        nonlocal offset
        number = 0
        for shift in range(0, 70, 7):
            if offset >= len(payload):
                raise ValueError("Truncated query")
            byte = payload[offset]
            offset += 1
            number |= (byte & 127) << shift
            if byte < 128:
                return number
        raise ValueError("Oversized query integer")

    while offset < len(payload):
        tag = varint()
        field, wire = tag >> 3, tag & 7
        if field == 0:
            raise ValueError("Invalid query field")
        if wire == 0:
            value = varint()
        elif wire == 2:
            length = varint()
            if offset + length > len(payload):
                raise ValueError("Truncated query field")
            value = payload[offset:offset + length]
            offset += length
        else:
            raise ValueError("Unsupported query field")
        result.setdefault(field, []).append(value)
    return result


def committed_query(page, request):
    """Verify one current directional leg, never raw airport/date substrings."""
    parsed = urlparse(page.get("url", ""))
    query = parse_qs(parsed.query)
    if parsed.hostname in {"127.0.0.1", "localhost"} and parsed.path.endswith("fixture.html"):
        return {key: query.get(key) == [wanted] for key, wanted in {
            "origin": request.origin.code, "destination": request.destination.code,
            "departure": request.departure_date,
        }.items() if key != "departure"} | {"departure": query.get("date") == [request.departure_date]}
    unknown = dict.fromkeys(("origin", "destination", "departure"), False)
    if parsed.hostname != "www.google.com" or parsed.path not in {"/travel/flights", "/travel/flights/search"}:
        return unknown
    tokens = query.get("tfs", [])
    if len(tokens) != 1 or len(tokens[0]) > 16000:
        return unknown
    try:
        token = tokens[0]
        payload = base64.b64decode(token + "=" * (-len(token) % 4), altchars=b"-_", validate=True)
        root = _wire_fields(payload)
        legs = root.get(3, [])
        if len(legs) != 1 or not isinstance(legs[0], bytes):
            return unknown
        leg = _wire_fields(legs[0])

        def airport(field):
            places = leg.get(field, [])
            if len(places) != 1 or not isinstance(places[0], bytes):
                return None
            codes = _wire_fields(places[0]).get(2, [])
            return codes[0] if len(codes) == 1 else None

        return {
            "origin": airport(13) == request.origin.code.encode(),
            "destination": airport(14) == request.destination.code.encode(),
            "departure": leg.get(2) == [request.departure_date.encode()],
        }
    except (ValueError, TypeError, binascii.Error):
        return unknown


def _airport_committed(page, key, airport, value, submitted):
    controls = [a for a in page.get("actions", []) if field_name(a) == key]
    if not controls or any(a.get("expanded") == "true" for a in controls):
        return False
    tails = []
    for control in controls:
        label = " ".join(control.get("label", "").split())
        match = re.fullmatch(r"(?:Open )?Where (?:from|to)\? (.+)", label, re.I)
        if match:
            tails.append((control, match[1]))
    if tails and any(not airport.identifies(tail) for _, tail in tails):
        return False
    compatible = airport.matches(value) or airport.identifies(value)
    if tails and compatible and all(control.get("expanded") == "false" for control, _ in tails):
        return True
    if submitted:
        return compatible
    # An editable value is text, not proof of selecting the airport autocomplete result.
    return not any(a.get("kind") == "fill" for a in controls) and airport.identifies(value)


def form_checks(page, request, *, verification=None):
    values = fields(page)
    committed = committed_query(page, request)
    expected_date = date.fromisoformat(request.departure_date)
    compact = {f"{expected_date:%a}, {expected_date:%b} {expected_date.day}",
               f"{expected_date:%A}, {expected_date:%B} {expected_date.day}"}
    full_dates = {request.departure_date,
                  f"{expected_date:%A}, {expected_date:%B} {expected_date.day}, {expected_date.year}",
                  f"{expected_date:%b} {expected_date.day}, {expected_date.year}"}
    return {
        "origin": _airport_committed(page, "origin", request.origin, values.get("origin", ""), committed["origin"]),
        "destination": _airport_committed(page, "destination", request.destination,
                                          values.get("destination", ""), committed["destination"]),
        "departure": values.get("departure") in full_dates or
        (values.get("departure") in compact and committed["departure"]),
        "adults": values.get("adults") == "1" or
        (isinstance(verification, PassengerVerification) and verification.matches(page, request)),
        "cabin": normalized(values.get("cabin", "")) == "economy",
        "trip_type": normalized(values.get("trip_type", "")) == "one way",
    }


def search_checks(page, request, *, fixture=False, verification=None):
    checks = form_checks(page, request, verification=verification)
    parsed = urlparse(page.get("url", ""))
    query = parse_qs(parsed.query)
    committed = committed_query(page, request)
    if fixture:
        checks["submitted"] = all(query.get(k) == [str(v)] for k, v in {
            "origin": request.origin.code, "destination": request.destination.code,
            "date": request.departure_date, "adults": "1", "cabin": "Economy", "trip_type": "One way",
            "currency": request.currency,
        }.items())
        checks["source"] = parsed.hostname in {"127.0.0.1", "localhost"} and parsed.path.endswith("fixture.html")
    else:
        checks["source"] = (parsed.scheme == "https" and parsed.hostname == "www.google.com"
                            and parsed.path == "/travel/flights/search")
        # Current visible passenger/cabin/trip controls are checked separately above.
        checks["submitted"] = all(committed.values())
    return checks


ROW = re.compile(
    r"From (?P<price>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?) US dollars\.\s*.*?"
    r"(?P<stops>Nonstop|\d+ stops?) flight with (?P<airline>[^.]+)\.\s*.*?"
    r"Leaves (?P<origin>.+?) at (?P<depart_time>\d{1,2}:\d{2} [AP]M) on "
    r"(?P<depart_day>\w+, \w+ \d{1,2}(?:, \d{4})?) and arrives at (?P<destination>.+?) at "
    r"(?P<arrive_time>\d{1,2}:\d{2} [AP]M) on (?P<arrive_day>\w+, \w+ \d{1,2}(?:, \d{4})?)\. "
    r"Total duration (?P<duration>[^.]+)\.\s*"
    r"(?:\d+ carry-on bags? included\.\s*)?(?:\d+ checked bags? included\.\s*)?"
    r"Select flight\.?", re.I,
)
DURATION = re.compile(r"(?:(?P<hours>\d+)\s*hr(?:s|ours?)?(?:\s+|$))?(?:(?P<minutes>\d+)\s*min(?:s|utes?)?)?", re.I)


def parse_flight(label, request):
    """Unknown wording fails closed. Caller verifies the exact search year first."""
    label = " ".join(label.split())
    # A composite/malformed label must not bind the fare of one row to another itinerary.
    if any(len(re.findall(marker, label, re.I)) != 1 for marker in (
        r"\bFrom [\d,.]+ US dollars\.", r"\bflight with\b", r"\bLeaves\b",
        r"\bTotal duration\b", r"\bSelect flight\b",
    )):
        return None
    match = ROW.fullmatch(label)
    if not match:
        return None
    data = match.groupdict()
    try:
        year = date.fromisoformat(request.departure_date).year
        moments = []
        for prefix in ("depart", "arrive"):
            day = data[prefix + "_day"]
            explicit_year = bool(re.search(r", \d{4}$", day))
            stamp = f"{day} {data[prefix + '_time']}" if explicit_year else f"{day} {year} {data[prefix + '_time']}"
            fmt = "%A, %B %d, %Y %I:%M %p" if explicit_year else "%A, %B %d %Y %I:%M %p"
            moment = datetime.strptime(stamp, fmt)
            if moment.strftime("%A").casefold() != day.split(",")[0].casefold():
                return None
            moments.append(moment.isoformat(timespec="minutes"))
        duration = DURATION.fullmatch(data["duration"].strip())
        if not duration or not any(duration.groupdict().values()):
            return None
        hours, minutes = int(duration["hours"] or 0), int(duration["minutes"] or 0)
        price = float(data["price"].replace(",", ""))
        total_minutes = hours * 60 + minutes
        if minutes >= 60 or not 0 < total_minutes < 24 * 60 or not math.isfinite(price) or price <= 0:
            return None
        return Flight(
            data["airline"].strip(), data["origin"], data["destination"], *moments, total_minutes,
            0 if data["stops"].casefold() == "nonstop" else int(data["stops"].split()[0]),
            price, "USD", label,
        )
    except (ValueError, OverflowError):
        return None


@dataclass
class Observation:
    checks: dict
    flights: list
    unparsed_rows: int
    result_rows: int

    @property
    def search_verified(self):
        return bool(self.checks) and all(self.checks.values())


def inspect(page, request, *, fixture=False, verification=None, allow_unverified_passengers=False):
    checks = search_checks(page, request, fixture=fixture, verification=verification)
    labels = list(dict.fromkeys(" ".join(a.get("label", "").split()) for a in page.get("actions", [])
                               if "select flight" in " ".join(a.get("label", "").split()).casefold()))
    context_verified = all(value for key, value in checks.items() if key != "adults")
    parse_allowed = all(checks.values()) or (allow_unverified_passengers and context_verified)
    # Provisional collection can parse rows, but it cannot make search_verified true.
    flights = [parse_flight(label, request) for label in labels] if parse_allowed else []
    return Observation(checks, [f for f in flights if f is not None],
                       sum(f is None for f in flights), len(labels))
