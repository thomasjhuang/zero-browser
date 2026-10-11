"""One bounded browser session with injected decisions and shared outcome checking."""

import json
import re
import time
from dataclasses import asdict, dataclass
from urllib.parse import parse_qsl, urlparse

from scripts.runtime_guard import challenge_reason

from .contracts import normalized, shortlist
from .observe import (
    Observation,
    PassengerVerification,
    field_name,
    field_value,
    form_checks,
    inspect,
    parse_flight,
    passenger_context,
    passenger_control,
    passenger_done,
    passenger_popup_counts,
)
from .workflow import Step, next_step


def require_search_action(action, page=None, request=None, *, verification=None, check_submission=True):
    label = normalized(action.get("label", ""))
    forbidden = (
        r"\b(?:(?:select|choose)(?: \w+){0,3} flights?|book|booking|reserve|checkout|pay|purchase|"
        r"log in|sign in|password|subscribe|hotels?|sponsors?|advertisement)\b"
    )
    if re.search(forbidden, label) or action.get("kind") not in {"click", "fill", "select", "scroll", "wait"}:
        raise ValueError("This target is outside the flight-search demo boundary.")
    if check_submission and is_search(action):
        valid = page is not None and request is not None and \
            all(form_checks(page, request, verification=verification).values())
        if not valid or \
                any(a.get("expanded") == "true" for a in page.get("actions", [])) or page.get("omitted_actions", 0):
            raise ValueError("Search submission requires the currently committed, unambiguous requested form.")


def is_search(action):
    return action.get("kind") == "click" and normalized(action.get("label", "")) in {
        "search", "search flights", "find flights"
    }


def other_checks_pass(checks):
    return bool(checks) and all(value for key, value in checks.items() if key != "adults")


def context_ready(page, observed):
    return observed.search_verified or (other_checks_pass(observed.checks) and passenger_control(page) is not None)


def search_scope(page):
    """Current committed source, excluding fragment and query ordering changes."""
    parsed = urlparse(page.get("url", ""))
    return parsed.scheme, parsed.netloc, parsed.path, tuple(sorted(parse_qsl(parsed.query)))


def document_epoch(page):
    key = page.get("page_key")
    return key[0] if isinstance(key, (list, tuple)) and key else None


@dataclass(frozen=True)
class ViewportAnchor:
    """Session evidence that collection started with the requested current search visible."""
    epoch: float
    scope: tuple


def viewport_matches(page, request, anchor, *, fixture=False):
    if anchor is None or document_epoch(page) != anchor.epoch or search_scope(page) != anchor.scope or \
            challenge_reason(page) or page.get("omitted_actions", 0) or \
            any(a.get("expanded") == "true" for a in page.get("actions", [])):
        return False
    observed = inspect(page, request, fixture=fixture, allow_unverified_passengers=True)
    if not observed.checks["source"] or not observed.checks["submitted"]:
        return False
    # Absence may result from viewport clipping. A present contradictory control never may.
    present = {field_name(a) for a in page.get("actions", [])}
    passenger = passenger_control(page)
    passenger_valid = passenger is not None and normalized(passenger["label"]).split()[0] == str(request.adults) and \
        all(field_value(a) == str(request.adults) for a in page.get("actions", [])
            if field_name(a) == "adults" and a is not passenger)
    return all(observed.checks[name] or (name == "adults" and passenger_valid)
               for name in present if name in observed.checks)


def inspect_viewport(page, request, anchor, *, fixture=False, verification=None):
    observed = inspect(page, request, fixture=fixture, verification=verification,
                       allow_unverified_passengers=True)
    if not viewport_matches(page, request, anchor, fixture=fixture):
        return observed
    labels = list(dict.fromkeys(" ".join(a.get("label", "").split()) for a in page.get("actions", [])
                               if "select flight" in " ".join(a.get("label", "").split()).casefold()))
    flights = [parse_flight(label, request) for label in labels]
    return Observation(observed.checks, [f for f in flights if f is not None],
                       sum(f is None for f in flights), len(labels))


def blank_snapshot(page, *, fixture=False):
    """Only a genuinely empty current search surface permits this settling wait."""
    parsed = urlparse(page.get("url", ""))
    source = parsed.scheme == "https" and parsed.hostname == "www.google.com" and \
        parsed.path in {"/travel/flights", "/travel/flights/search"}
    source = source or (fixture and parsed.hostname in {"127.0.0.1", "localhost"}
                        and parsed.path == "/fixture.html")
    synthetic = {"scroll_down": ("scroll", "scroll down"), "scroll_up": ("scroll", "scroll up"),
                 "wait": ("wait", "wait for the page to update")}
    return bool(source and not page.get("text", "").strip() and not page.get("omitted_actions", 0) and
                all(a.get("node") is None and
                    synthetic.get(a.get("id")) == (a.get("kind"), normalized(a.get("label", "")))
                    for a in page.get("actions", [])))


def empty_results(page, observed, *, provisional=False):
    # An unknown parser response or a blank loading page cannot establish an empty result.
    text = normalized(page.get("text", ""))
    verified = context_ready(page, observed) if provisional else observed.search_verified
    return verified and observed.result_rows == 0 and bool(re.search(
        r"\b(?:no matching flights found|no flights found|no flights available|no results found)\b", text))


def finish(pages, request, *, fixture=False, verification=None, collection_only=False, viewport_anchor=None):
    """Present only rows from consecutive verified observations of the final committed search."""
    flights, labels, unparsed, itineraries = [], set(), set(), set()
    last = inspect_viewport(pages[-1], request, viewport_anchor, fixture=fixture,
                            verification=verification) if pages else None
    current_ready = bool(last and (last.search_verified or
                         (collection_only and (context_ready(pages[-1], last) or
                          viewport_matches(pages[-1], request, viewport_anchor, fixture=fixture)))))
    if viewport_anchor is not None and pages and not viewport_matches(
            pages[-1], request, viewport_anchor, fixture=fixture):
        current_ready = False
    eligible = bool(current_ready and not challenge_reason(pages[-1]) and
                    (last.flights or empty_results(pages[-1], last, provisional=collection_only)))
    if current_ready and not challenge_reason(pages[-1]):
        scope = search_scope(pages[-1])
        for page in reversed(pages):
            observed = inspect_viewport(page, request, viewport_anchor, fixture=fixture, verification=verification)
            ready = observed.search_verified or ((collection_only or verification is not None) and
                                                 context_ready(page, observed))
            anchored = viewport_matches(page, request, viewport_anchor, fixture=fixture)
            ready = ready or anchored
            if search_scope(page) != scope or not ready or challenge_reason(page):
                break
            if verification is not None and not anchored and passenger_context(page) != verification.context:
                break
            # An explicit empty response supersedes earlier rows, rather than reviving stale fares.
            if empty_results(page, observed, provisional=collection_only or verification is not None):
                break
            for flight in observed.flights:
                identity = (normalized(flight.airline), normalized(flight.origin),
                            normalized(flight.destination), flight.departure,
                            flight.arrival, flight.stops, flight.currency)
                if identity not in itineraries:
                    itineraries.add(identity)
                    flights.append(flight)
            current = {" ".join(a.get("label", "").split()) for a in page.get("actions", [])
                       if "select flight" in " ".join(a.get("label", "").casefold().split())}
            labels.update(current)
            parsed = {" ".join(f.evidence.split()) for f in observed.flights}
            unparsed.update(current - parsed)
        unparsed.difference_update(" ".join(f.evidence.split()) for f in flights)
    selected = shortlist(flights, request) if eligible else []
    eligible = bool(eligible and (selected or (flights and not unparsed) or
                    empty_results(pages[-1], last, provisional=collection_only)))
    return {
        "outcome_verified": eligible and not collection_only,
        "search_checks": last.checks if last else {},
        "shortlist": [asdict(f) for f in selected],
        "inspected_rows": len(labels), "unparsed_rows": len(unparsed),
        "coverage": "Inspected results only; global cheapest and exhaustive coverage are not established.",
        "source_url": pages[-1].get("url", "") if pages else "",
        "price_scope": "Observed USD fare; additional fees and subsequent price changes may apply.",
    }


def run_session(browser, request, *, mode="workflow", decide=None, write_text=None,
                fixture=False, max_steps=40, max_model_decisions=12, timeout=90, journal=None,
                max_wait_steps=30):
    """All arms share collection, waits, boundaries, and independent outcome checking.

    decide(page, goal, history) follows choose(); write_text(context) follows field_text().
    A frontier adapter can implement these externally; this module makes no hosted calls.
    The parent CLI supervises calls against a hard deadline; this loop checks between calls.
    """
    if mode not in {"local", "workflow", "frontier"}:
        raise ValueError("Unknown comparison mode.")
    from jev_ultrafast.browser import StalePage
    from jev_ultrafast.model import field_context

    started = time.monotonic()
    pages, history = [], []
    metrics = {"model_decisions": 0, "text_calls": 0, "deterministic_actions": 0,
               "collection_actions": 0, "wait_actions": 0, "verification_actions": 0,
               "verification_transactions": 0,
               "actions_executed": 0, "observations": 0, "rejected_stale_actions": 0,
               "decision_latency_ms": [], "text_latency_ms": [], "model_usage": []}
    status, cause, stopped_by_model = "incomplete", None, False
    last_rule_key, no_progress, last_mutation = None, 0, None
    scrolls, waiting, pending_search = 0, 0, False
    viewport_anchor, restoring, restore_steps = None, False, 0
    cached_text = None
    budget_used, terminal_proof, terminal_final = 0, None, None
    verification_phases, proofs = set(), []

    def record(event, **data):
        if journal:
            journal.write(event, **data)

    def check_deadline():
        if time.monotonic() - started >= timeout:
            raise RuntimeError("Session deadline reached.")

    def execute(action, page, *, text=None, source, number, verification=None):
        nonlocal budget_used, cached_text
        check_deadline()
        if budget_used >= max_steps:
            raise RuntimeError("Browser action budget reached.")
        require_search_action(action, page, request, verification=verification)
        budget_used += 1
        record("mutation_started", step=number, source=source, action=action, text=text)
        try:
            browser.act(action, page, text=text)
        except StalePage:
            metrics["rejected_stale_actions"] += 1
            record("rejected_stale", step=number, source=source)
            raise
        record("executed", step=number, source=source, action=action, text=text)
        cached_text = None
        metrics["actions_executed"] += 1
        metrics["deterministic_actions"] += source == "deterministic"
        metrics["collection_actions"] += source == "collection"
        metrics["verification_actions"] += source == "verification"
        metrics["wait_actions"] += action["kind"] == "wait"
        history.append({"action": action["label"], "kind": action["kind"], "text": text,
                        "field": field_name(action), "source": source})

    def observe_verification(number, phase):
        check_deadline()
        current = browser.observe(screenshot=False)
        metrics["observations"] += 1
        record("observation", step=number, phase=phase, source="verification", page=current)
        check_deadline()
        if challenge_reason(current):
            raise RuntimeError(challenge_reason(current))
        return current

    def verify_passengers(page, number, phase):
        """Two guarded actions; proof is consumed with the resulting fresh closed observation."""
        if phase in verification_phases:
            raise RuntimeError("The bounded passenger verification attempt was already used.")
        verification_phases.add(phase)
        metrics["verification_transactions"] += 1
        context, opener, epoch = passenger_context(page), passenger_control(page), document_epoch(page)
        if context is None or opener is None or epoch is None:
            raise ValueError("No unambiguous passenger control and document lifecycle for fresh verification.")
        record("passenger_verification_started", step=number, phase=phase, context=context)
        try:
            execute(opener, page, source="verification", number=number)
            popup = observe_verification(number, phase)
            if document_epoch(popup) != epoch or search_scope(popup) != search_scope(page):
                raise ValueError("Passenger verification changed the document or search source.")
            counts, done = passenger_popup_counts(popup), passenger_done(popup)
            if counts != (request.adults, 0, 0, 0) or done is None:
                raise ValueError("The current passenger popup does not prove one adult and no children or infants.")
            execute(done, popup, source="verification", number=number)
            closed = observe_verification(number, phase)
            if document_epoch(closed) != epoch or passenger_context(closed) != context:
                raise ValueError("Passenger verification changed the document or requested form context.")
            proof = PassengerVerification(counts, popup.get("fingerprint", ""), closed.get("fingerprint", ""), context)
            if not proof.matches(closed, request):
                raise ValueError("The passenger verification is not bound to the current closed form.")
        except StalePage as error:
            # These internal actions get one attempt; never resume an uncertain transaction.
            raise RuntimeError("Passenger verification target became stale; no transaction retry.") from error
        proofs.append({"phase": phase, **asdict(proof)})
        record("passenger_verification", step=number, phase=phase, proof=asdict(proof))
        return closed, proof

    record("task_started", mode=mode, request=request.to_dict(), goal=request.goal, fixture=fixture)
    try:
        for number in range(max_steps):
            if time.monotonic() - started >= timeout:
                cause = "Session deadline reached."
                break
            page = browser.observe(screenshot=False)
            metrics["observations"] += 1
            pages.append(page)
            record("observation", step=number, page=page)
            if challenge_reason(page):
                cause = challenge_reason(page)
                break
            verification = None
            observed = inspect_viewport(page, request, viewport_anchor, fixture=fixture)
            full_context = context_ready(page, observed)
            anchored = viewport_matches(page, request, viewport_anchor, fixture=fixture)
            if viewport_anchor is not None and not anchored:
                cause = "The result viewport changed the committed search, document, or visible constraints."
                break
            if full_context and (observed.flights or empty_results(page, observed, provisional=True)) and \
                    viewport_anchor is None:
                epoch = document_epoch(page)
                if type(epoch) in {int, float} and 0 < epoch < float("inf"):
                    viewport_anchor = ViewportAnchor(epoch, search_scope(page))
            if blank_snapshot(page, fixture=fixture):
                wait = next((a for a in page.get("actions", []) if a.get("id") == "wait"), None)
                if wait is None:
                    cause = "The blank search snapshot has no observed wait action."
                    break
                step, source = Step(wait, None, "Wait for the empty search snapshot to settle"), "wait"
            elif (full_context and (observed.flights or empty_results(page, observed, provisional=True))) or anchored:
                pending_search, waiting = False, 0
                # The exact same collector and sorter are used by every comparison arm.
                options = finish(pages, request, fixture=fixture, collection_only=True,
                                 viewport_anchor=viewport_anchor)["shortlist"]
                scroll = next((a for a in page.get("actions", []) if a.get("id") == "scroll_down"), None)
                done = restoring or empty_results(page, observed, provisional=True) or \
                    len(options) >= request.limit or not scroll or scrolls >= 3
                if done and not full_context:
                    restoring = True
                    up = [a for a in page.get("actions", [])
                          if a.get("id") == "scroll_up" and a.get("kind") == "scroll"]
                    if len(up) != 1 or restore_steps >= 3:
                        cause = "The requested search controls could not be restored within the scroll budget."
                        break
                    step = Step(up[0], None, "Restore current search controls for final verification")
                    source = "collection"
                elif done:
                    if not observed.checks["adults"]:
                        terminal_final, terminal_proof = verify_passengers(page, number, "final")
                        pages.append(terminal_final)
                    status = "complete"
                    break
                else:
                    step = Step(scroll, None, "Inspect another viewport of results")
                    source = "collection"
            elif pending_search or re.search(
                    r"\b(?:loading|searching for flights)\b", normalized(page.get("text", ""))):
                wait = next((a for a in page.get("actions", []) if a.get("kind") == "wait"), None)
                if waiting >= max_wait_steps or not wait:
                    cause = "Search results did not become verifiable within the wait budget."
                    break
                step, source = Step(wait, None, "Wait for the submitted search to settle"), "wait"
            else:
                if last_mutation is not None:
                    no_progress = no_progress + 1 if page.get("fingerprint") == last_mutation else 0
                    last_mutation = None
                if no_progress >= 3:
                    cause = "Three actions made no observed progress."
                    break
                step = next_step(page, request, history) if mode == "workflow" else None
                checks = form_checks(page, request)
                if mode == "workflow" and step is None and not checks["adults"] and other_checks_pass(checks) and \
                        passenger_control(page) is not None and \
                        not any(a.get("expanded") == "true" for a in page.get("actions", [])):
                    page, verification = verify_passengers(page, number, "pre_submit")
                    pages.append(page)
                    step = next_step(page, request, history, verification=verification)
                    if step is None or not is_search(step.action):
                        raise ValueError("The verified passenger transaction must be followed immediately by Search.")
                source = "deterministic" if step else "model"
                key = (page.get("fingerprint"), step.action["id"], step.text) if step else None
                if step and step.action["kind"] != "wait" and key == last_rule_key:
                    step, source = None, "model"
                if step and step.action["kind"] != "wait":
                    last_rule_key = key
                if step is None:
                    if decide is None:
                        cause = "No unambiguous rule applies; a model fallback is required."
                        break
                    if metrics["model_decisions"] >= max_model_decisions:
                        cause = "Model decision budget reached."
                        break
                    before = time.monotonic()
                    metrics["model_decisions"] += 1
                    record("decision_started", step=number)
                    try:
                        decision = decide(page, request.goal, history)
                    finally:
                        latency = round((time.monotonic() - before) * 1000)
                        metrics["decision_latency_ms"].append(latency)
                    metrics["model_usage"].append(decision.get("usage", {}))
                    record("decision", step=number, decision=decision, latency_ms=latency)
                    if decision["choice"] in {"DONE", "BLOCKED"}:
                        stopped_by_model = True
                        cause = "The model stopped before independent shortlist verification."
                        break
                    matches = [a for a in page.get("actions", []) if a["id"] == decision["choice"]]
                    if len(matches) != 1:
                        raise ValueError("Model selected a target absent or ambiguous in the current observation.")
                    action = matches[0]
                    require_search_action(action, page, request, check_submission=False)
                    text = None
                    if action["kind"] == "fill":
                        if write_text is None:
                            raise ValueError("The selected field requires a text model.")
                        context = field_context(request.goal, action, page, history)
                        cache_key = json.dumps(context, sort_keys=True)
                        if cached_text and cached_text[0] == cache_key:
                            text = cached_text[1]
                        else:
                            before = time.monotonic()
                            metrics["text_calls"] += 1
                            try:
                                text, usage = write_text(context)
                            finally:
                                metrics["text_latency_ms"].append(round((time.monotonic() - before) * 1000))
                            metrics["model_usage"].append(usage.get("usage", {}))
                            if not isinstance(text, str) or not text.strip() or len(text) > 2000:
                                raise ValueError("No valid field text. Nothing entered.")
                            cached_text = (cache_key, text)
                    step = Step(action, text, "Model fallback" if mode == "workflow" else "Model decision")
            if is_search(step.action) and verification is None:
                checks = form_checks(page, request)
                if not checks["adults"] and other_checks_pass(checks) and passenger_control(page) is not None and \
                        not any(a.get("expanded") == "true" for a in page.get("actions", [])):
                    original = step.action
                    page, verification = verify_passengers(page, number, "pre_submit")
                    pages.append(page)
                    current = [a for a in page.get("actions", []) if is_search(a) and
                               a.get("node") == original.get("node") and
                               normalized(a.get("label", "")) == normalized(original.get("label", ""))]
                    if len(current) != 1:
                        raise ValueError("The selected search target changed during passenger verification.")
                    step = Step(current[0], step.text, step.reason)
            if step.action["kind"] == "wait":
                if waiting >= max_wait_steps:
                    cause = "The page did not become verifiable within the wait budget."
                    break
                waiting += 1
            try:
                execute(step.action, page, text=step.text, source=source, number=number, verification=verification)
            except StalePage:
                # Browser rejects these before any mutation; an uncertain execution is never retried.
                last_rule_key = None
                if verification is not None:
                    cause = "The verified submission target became stale; the passenger proof expired."
                    break
                if metrics["rejected_stale_actions"] >= 3:
                    cause = "Three stale targets were rejected."
                    break
                continue
            if source == "collection":
                scrolls += step.action.get("id") == "scroll_down"
                restore_steps += step.action.get("id") == "scroll_up"
            if step.action["kind"] != "wait":
                last_mutation = page.get("fingerprint")
                waiting = 0
            if step.action["kind"] == "click" and normalized(step.action["label"]) in {
                "search", "search flights", "find flights"
            }:
                pending_search, waiting = True, 0
        else:
            cause = "Browser action budget reached."
    except Exception as error:
        cause = f"{type(error).__name__}: {error}"
        record("failure", cause=cause)
    # The terminal transaction's fresh closed read is the final observation; its proof expires on another action.
    try:
        if terminal_final is None:
            final = browser.observe(screenshot=False)
            metrics["observations"] += 1
            pages.append(final)
            record("observation", source="final", page=final)
        else:
            final = terminal_final
        if challenge_reason(final):
            cause = challenge_reason(final)
    except Exception as error:
        pages = []
        cause = f"Final observation failed: {error}"
    outcome = finish(pages, request, fixture=fixture, verification=terminal_proof, viewport_anchor=viewport_anchor)
    if time.monotonic() - started >= timeout and cause is None:
        cause = "Session deadline reached."
    if status == "complete" and not outcome["outcome_verified"] and cause is None:
        cause = "Final search and shortlist verification failed."
    result = {**outcome, "mode": mode, "fixture": fixture, "request": request.to_dict(),
              "metrics": metrics, "elapsed_ms": round((time.monotonic() - started) * 1000),
              "status": status, "stop_reason": cause, "model_stopped": stopped_by_model,
              "passenger_verifications": proofs}
    result["successful_run"] = outcome["outcome_verified"] and cause is None and status == "complete"
    if not result["successful_run"]:
        result["shortlist"] = []
        result["outcome_verified"] = False
        result["status"] = "incomplete"
    record("outcome", result=result)
    return result
