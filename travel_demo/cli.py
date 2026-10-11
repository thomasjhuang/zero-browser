"""Bounded terminal travel demo. The default workflow uses no inference model."""

import argparse
import functools
import hashlib
import json
import os
import sys
import tempfile
import threading
import time
from contextlib import ExitStack, contextmanager
from dataclasses import replace
from datetime import datetime
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode

from scripts.milestone_record import Journal, read_events, save_json
from scripts.run_cli import FixtureHandler, isolated_browser
from scripts.runtime_guard import cancellation_signals, single_run, supervise, worker_memory_limit

from .contracts import FlightRequest
from .format import render_result

ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = ("normal", "reverse", "renamed", "ambiguous", "empty", "challenge", "passengers")
GOOGLE_FLIGHTS = "https://www.google.com/travel/flights?hl=en&curr=USD"


def default_request(airlines=()):
    return replace(FlightRequest.load(Path(__file__).with_name("request.json")), airlines=tuple(airlines))


def source_sha256():
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.iterdir()):
        if path.suffix in {".py", ".html", ".json"}:
            digest.update(path.name.encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


@contextmanager
def fixture_url(layout="normal"):
    """Serve the fixture in the parent so it remains available during user review."""
    handler = functools.partial(FixtureHandler, directory=str(Path(__file__).parent))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/fixture.html?{urlencode({'layout': layout})}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def execute_worker(path):
    """Inference modules are imported only on an opted-in callback inside this worker."""
    from jev_ultrafast.browser import Browser

    from .session import run_session

    data = json.loads(Path(path).read_text())
    request = FlightRequest.load(data["request_path"])
    directory = Path(data["artifacts"])
    journal = Journal(directory / "events.jsonl")
    browser = None
    result = None
    started = time.monotonic()
    with ExitStack() as stack:
        model_step = [0]
        model_ready = False

        def prepare_model():
            nonlocal model_ready
            if not model_ready:
                os.environ["JEV_LOCAL"] = "1"
                from scripts.milestone import measured_model

                stack.enter_context(measured_model(journal, model_step))
                model_ready = True

        def decide(page, goal, history):
            prepare_model()
            from jev_ultrafast.local_policy import local_choose

            model_step[0] += 1
            return local_choose(page, goal, history)

        def write_text(context):
            prepare_model()
            from jev_ultrafast.local_policy import local_field_text

            return local_field_text(context)

        try:
            browser = Browser(data["url"])
            if not data["headless"]:
                browser.call("Page.bringToFront")
            result = run_session(
                browser, request, mode=data["mode"],
                decide=decide if data["allow_model"] else None,
                write_text=write_text if data["allow_model"] else None,
                fixture=data["fixture"], max_steps=data["max_steps"],
                max_model_decisions=data["max_model_decisions"], timeout=data["timeout"], journal=journal,
            )
            events = read_events(journal.path)
            result["metrics"].update(
                model_calls_started=sum(e["event"] == "model_call_started" for e in events),
                model_calls_finished=sum(e["event"] == "model_call_finished" for e in events),
            )
            result.update(artifacts=str(directory), worker_elapsed_ms=round((time.monotonic() - started) * 1000))
            result["evidence_kind"] = "synthetic browser fixture" if data["fixture"] else "live browser observation"
            # The parent's Chrome context owns this target's final lifetime.
            keep = result["successful_run"] and data["review"] and not data["headless"]
            result["browser_held_for_review"] = bool(keep)
            if keep:
                browser.call("Page.bringToFront")
                result["review_target"] = browser.target
            save_json(directory / "result.json", result)
            return 0 if result["successful_run"] else 1
        finally:
            if browser and not (result and result.get("browser_held_for_review")):
                browser.close()


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", action="store_true",
                        help="Use synthetic browser results; no network or model needed.")
    parser.add_argument("--layout", choices=LAYOUTS, default="normal", help="Fixture control/result variation.")
    parser.add_argument("--headless", action="store_true", help="Hide Chrome; always close it when the run ends.")
    parser.add_argument("--review", action=argparse.BooleanOptionalAction, default=True,
                        help="Keep a successful visible browser open until Enter (default: on).")
    parser.add_argument("--mode", choices=("workflow", "local"), default="workflow",
                        help="Deterministic workflow, or local model decisions at each step.")
    parser.add_argument("--allow-model", "--ready-model", dest="allow_model", action="store_true",
                        help="Enable cached local model fallback or local-mode decisions.")
    parser.add_argument("--airline", action="append", default=[], metavar="NAME",
                        help="Optional strict airline restriction; repeat for several. Omit for all airlines.")
    parser.add_argument("--max-steps", type=int, default=40)
    parser.add_argument("--max-model-decisions", type=int, default=12)
    parser.add_argument("--timeout", type=float, default=90,
                        help="Worker seconds, including startup and model loading.")
    parser.add_argument("--artifacts", type=Path, default=ROOT / "artifacts/travel-demo",
                        help="Local ignored evidence root; each run gets a new subdirectory.")
    parser.add_argument("--_worker", type=Path, help=argparse.SUPPRESS)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args._worker:
        return execute_worker(args._worker)
    if args.mode == "local" and not args.allow_model:
        parser.error("--mode local requires --allow-model (or --ready-model).")
    if args.max_steps < 1 or args.max_model_decisions < 1 or not 0 < args.timeout <= 600:
        parser.error("Use positive action/model budgets and a timeout of at most 600 seconds.")
    request = default_request(airline.strip() for airline in args.airline if airline.strip())
    directory = args.artifacts.expanduser().resolve() / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    directory.mkdir(parents=True, exist_ok=False)
    save_json(directory / "request.json", request.to_dict())
    journal = Journal(directory / "events.jsonl")
    stats = {}
    started = time.monotonic()
    try:
        # Model-free workers still get deadline, ownership, and memory supervision.
        budget = worker_memory_limit() if args.allow_model else 512 * 2**20
        with cancellation_signals(), single_run(), ExitStack() as stack:
            url = stack.enter_context(fixture_url(args.layout)) if args.fixture else GOOGLE_FLIGHTS
            stack.enter_context(isolated_browser(headless=args.headless))
            data = {**vars(args), "artifacts": str(directory), "request_path": str(directory / "request.json"),
                    "url": url, "_worker": None}
            save_json(directory / "conditions.json", {**data, "memory_limit_bytes": budget,
                                                     "request": request.to_dict(), "source_sha256": source_sha256()})
            journal.write("worker_started", mode=args.mode, allow_model=args.allow_model,
                          memory_limit_bytes=budget, timeout=args.timeout, fixture=args.fixture)
            with tempfile.TemporaryDirectory(prefix="travel-demo-worker-") as temporary:
                worker_path = Path(temporary) / "worker.json"
                save_json(worker_path, data)
                code = supervise([sys.executable, "-m", "travel_demo", "--_worker", str(worker_path)],
                                 timeout=args.timeout, memory_limit=budget, stats=stats)
            result_path = directory / "result.json"
            if not result_path.exists():
                raise RuntimeError(f"Worker exited with code {code} without a verified outcome record.")
            result = json.loads(result_path.read_text())
            result.update(runtime=stats, supervised_elapsed_ms=round((time.monotonic() - started) * 1000))
            save_json(result_path, result)
            print(render_result(result), flush=True)
            if result.get("browser_held_for_review"):
                # User review happens after the timed worker and does not enter its benchmark metrics.
                try:
                    input("\nChrome is open for review. Press Enter to close this isolated browser: ")
                except EOFError:
                    print("No interactive input available; closing the isolated browser.", flush=True)
            return code
    except KeyboardInterrupt:
        journal.write("worker_cancelled", runtime=stats)
        print(f"Stopped by user. Local evidence: {directory}", file=sys.stderr)
        return 130
    except Exception as error:
        journal.write("worker_failure", cause=f"{type(error).__name__}: {error}", runtime=stats)
        print(f"Stopped: {error}\nLocal evidence: {directory}", file=sys.stderr)
        return 1
