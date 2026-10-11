"""Render only independently verified observed flights for terminal review."""

from datetime import datetime


def render_result(result):
    request = result.get("request", {})
    synthetic = result.get("fixture", False)
    lines = ["SYNTHETIC FIXTURE — these are invented fares." if synthetic else "Observed Google Flights fares."]
    if request:
        origin, destination = request.get("origin", {}), request.get("destination", {})
        lines.append(f"{origin.get('code')} → {destination.get('code')} | {request.get('departure_date')} | "
                     f"One way | {request.get('adults')} adult | {request.get('cabin')}")
        lines.append(f"Nonstop | Under ${request.get('max_price'):g} USD | "
                     f"Arrive same day before {request.get('arrive_before')}")
        lines.append("Airline restriction: " + (", ".join(request.get("airlines", [])) or "all airlines"))
    lines.append(f"Mode: {result.get('mode', 'workflow')} | Verified run: "
                 f"{'yes' if result.get('successful_run') else 'no'}")
    if result.get("stop_reason"):
        lines.append(f"Stopped: {result['stop_reason']}")
    rows = result.get("shortlist", []) if result.get("successful_run") else []
    if rows:
        lines.extend(["", "Verified shortlist (lowest observed price first):",
                      " #  Airline                 Price USD   Depart    Arrive    Duration   Stops"])
        for index, row in enumerate(rows, 1):
            departure, arrival = (datetime.fromisoformat(row[key]) for key in ("departure", "arrival"))
            hours, minutes = divmod(row["duration_minutes"], 60)
            lines.append(f" {index}  {row['airline'][:22]:22}  ${row['price']:8.2f}   "
                         f"{departure:%H:%M}     {arrival:%H:%M}     {hours}h {minutes:02d}m    {row['stops']}")
        lines.append(f"All rows arrive on {request.get('departure_date')} before "
                     f"{request.get('arrive_before')} local destination time.")
    elif result.get("successful_run"):
        lines.append("No qualifying flights in the inspected results.")
    else:
        lines.append("No verified shortlist is presented.")
    metrics = result.get("metrics", {})
    lines.extend(["", result.get("coverage", "Only inspected results are covered."),
                  result.get("price_scope", "Observed fares may change."),
                  f"Observed rows: {result.get('inspected_rows', 0)} | "
                  f"Unparsed rows: {result.get('unparsed_rows', 0)}",
                  f"Actions: {metrics.get('actions_executed', 0)} | "
                  f"Model decisions: {metrics.get('model_decisions', 0)} | "
                  f"Text requests: {metrics.get('text_calls', 0)} | "
                  f"Low-level model calls started/finished: "
                  f"{metrics.get('model_calls_started', 0)}/{metrics.get('model_calls_finished', 0)}",
                  f"Elapsed: {result.get('elapsed_ms', 0) / 1000:.2f}s"])
    if result.get("source_url"):
        lines.append(f"Review URL: {result['source_url']}")
    if result.get("artifacts"):
        lines.append(f"Local evidence: {result['artifacts']}")
    return "\n".join(lines)
