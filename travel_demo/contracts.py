"""Fixed travel request and independently checked shortlist. No model imports."""

import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, time
from pathlib import Path


def normalized(value):
    return " ".join(re.sub(r"[^\w]+", " ", str(value).casefold()).split())


@dataclass(frozen=True)
class Airport:
    city: str
    code: str
    aliases: tuple[str, ...]

    def __post_init__(self):
        if not isinstance(self.city, str) or not self.city.strip() or not isinstance(self.code, str):
            raise ValueError("Each airport needs a city and a three-letter airport code.")
        if not re.fullmatch(r"[A-Z]{3}", self.code):
            raise ValueError("Use an uppercase three-letter airport code.")
        if not isinstance(self.aliases, tuple) or any(not isinstance(a, str) or not a.strip() for a in self.aliases):
            raise ValueError("Airport aliases must be nonempty strings.")

    def matches(self, value):
        return normalized(value) in {normalized(a) for a in (*self.aliases, self.city, self.code)}

    def identifies(self, value):
        """Require airport identity; a city alone can include other nearby airports."""
        text = str(value).strip()
        named = {normalized(a) for a in self.aliases if normalized(a) != normalized(self.city)}
        if normalized(text) in named | {normalized(self.code)}:
            return True
        # Google's airport suggestions combine city/name and code. Mixed airport codes are ambiguous.
        codes = re.findall(r"\b[A-Z]{3}\b", text)
        if codes != [self.code]:
            return False
        without_code = re.sub(r"\b" + re.escape(self.code) + r"\b", "", text)
        return normalized(without_code) in named | {normalized(self.city)}


@dataclass(frozen=True)
class FlightRequest:
    origin: Airport
    destination: Airport
    departure_date: str
    trip_type: str = "One way"
    adults: int = 1
    cabin: str = "Economy"
    currency: str = "USD"
    max_price: float = 400
    nonstop: bool = True
    arrive_before: str = "18:00"
    airlines: tuple[str, ...] = ()
    limit: int = 5

    def __post_init__(self):
        if not isinstance(self.departure_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.departure_date):
            raise ValueError("Use a departure date in YYYY-MM-DD format.")
        date.fromisoformat(self.departure_date)
        if not isinstance(self.arrive_before, str) or not re.fullmatch(r"\d{2}:\d{2}", self.arrive_before):
            raise ValueError("Use an arrival cutoff in HH:MM format.")
        time.fromisoformat(self.arrive_before)
        if self.trip_type != "One way" or type(self.adults) is not int or self.adults != 1 or self.cabin != "Economy":
            raise ValueError("This demo supports one-way flights, one adult, and economy only.")
        if self.currency != "USD" or type(self.nonstop) is not bool:
            raise ValueError("Use USD and a boolean nonstop constraint.")
        if (type(self.max_price) not in {int, float} or not math.isfinite(self.max_price)
                or self.max_price <= 0 or type(self.limit) is not int or not 1 <= self.limit <= 5):
            raise ValueError("Use a positive finite price and a shortlist limit from 1 to 5.")
        for airport in (self.origin, self.destination):
            if not re.fullmatch(r"[A-Z]{3}", airport.code) or not airport.city.strip():
                raise ValueError("Each airport needs a city and a three-letter airport code.")
        if self.origin.code == self.destination.code:
            raise ValueError("Origin and destination must differ.")
        if not isinstance(self.airlines, tuple) or any(not isinstance(a, str) or not a.strip() for a in self.airlines):
            raise ValueError("Airlines must be nonempty names, or an empty list for any airline.")

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        for key in ("origin", "destination"):
            data[key] = Airport(**{**data[key], "aliases": tuple(data[key]["aliases"])})
        data["airlines"] = tuple(data.get("airlines", []))
        return cls(**data)

    def to_dict(self):
        return asdict(self)

    @property
    def goal(self):
        stop = "nonstop" if self.nonstop else "with any number of stops"
        airlines = f"Only consider these marketing airlines: {', '.join(self.airlines)}. " if self.airlines else ""
        return (
            f"Find one-way flights from {self.origin.city} ({self.origin.code}) to "
            f"{self.destination.city} ({self.destination.code}) on {self.departure_date}, "
            f"for one adult in economy. Find {stop} options under {self.max_price:g} USD "
            f"arriving on {self.departure_date} before {self.arrive_before} local destination time. "
            f"{airlines}"
            f"Inspect flight results for up to {self.limit} qualifying options, cheapest first. "
            "Stop with flight options visible. Do not select a flight, book, log in, or pay."
        )


@dataclass(frozen=True)
class Flight:
    airline: str
    origin: str
    destination: str
    departure: str
    arrival: str
    duration_minutes: int
    stops: int
    price: float
    currency: str
    evidence: str


def check_flight(flight, request):
    try:
        departure = datetime.fromisoformat(flight.departure)
        arrival = datetime.fromisoformat(flight.arrival)
    except (TypeError, ValueError):
        return {"valid_datetimes": False}
    return {
        "origin": request.origin.identifies(flight.origin),
        "destination": request.destination.identifies(flight.destination),
        "departure_date": departure.date().isoformat() == request.departure_date,
        "arrival_date": arrival.date().isoformat() == request.departure_date,
        "arrival_time": arrival.time() < time.fromisoformat(request.arrive_before),
        "price": type(flight.price) in {int, float} and math.isfinite(flight.price) and
        0 < flight.price < request.max_price,
        "currency": flight.currency == request.currency,
        "stops": type(flight.stops) is int and (flight.stops == 0 if request.nonstop else flight.stops >= 0),
        "duration": type(flight.duration_minutes) is int and 0 < flight.duration_minutes < 24 * 60,
        "airline": not request.airlines or normalized(flight.airline) in {normalized(a) for a in request.airlines},
        "evidence": bool(flight.evidence),
    }


def shortlist(flights, request):
    # Later observations replace earlier fares for the same itinerary, even if no longer qualifying.
    latest = {}
    for flight in flights:
        key = (normalized(flight.airline), normalized(flight.origin), normalized(flight.destination),
               flight.departure, flight.arrival, flight.stops, flight.currency)
        latest[key] = flight
    matches = [flight for flight in latest.values() if all(check_flight(flight, request).values())]
    return sorted(matches, key=lambda f: (f.price, f.duration_minutes, f.departure))[:request.limit]
