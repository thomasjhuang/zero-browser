"""Run one browser goal with local Qwen and an isolated Chrome profile."""

import argparse
import functools
import json
import os
import platform
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.runtime_guard import (  # noqa: E402
    challenge_reason,
    cleanup_signals,
    single_run,
    stop_process_group,
    supervise,
    worker_memory_limit,
)

CACHED_CHROME = (ROOT / ".zero-browser/browser/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS"
                 / "Google Chrome for Testing")
CHROME_CANDIDATES = (
    CACHED_CHROME,
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    Path("/usr/bin/google-chrome-stable"),
    Path("/usr/bin/google-chrome"),
    Path("/usr/bin/chromium"),
    Path("/usr/bin/chromium-browser"),
)


def chrome_path():
    return next((p for p in CHROME_CANDIDATES if p.is_file() and os.access(p, os.X_OK)), None)


def install_browser(offline=False):
    if chrome_path():
        print("Chrome is available.", flush=True)
        return
    if offline:
        raise RuntimeError("Chrome is absent. Run bash install.sh with network access first.")
    endpoint = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    with urllib.request.urlopen(endpoint, timeout=30) as response:
        stable = json.load(response)["channels"]["Stable"]
    asset = next(a for a in stable["downloads"]["chrome"] if a["platform"] == "mac-arm64")
    if not asset["url"].startswith("https://storage.googleapis.com/chrome-for-testing-public/"):
        raise ValueError("Unexpected Chrome download address.")
    destination = ROOT / ".zero-browser/browser"
    destination.mkdir(parents=True, exist_ok=True)
    print(f"Downloading Chrome for Testing {stable['version']}.", flush=True)
    with tempfile.TemporaryDirectory(prefix="download-", dir=destination) as directory:
        archive = Path(directory) / "chrome.zip"
        with urllib.request.urlopen(asset["url"], timeout=60) as response, archive.open("wb") as output:
            import shutil

            shutil.copyfileobj(response, output)
        # ditto preserves the executable permissions and framework links in the macOS application.
        subprocess.run(["/usr/bin/ditto", "-x", "-k", str(archive), str(destination)], check=True)
    if not chrome_path():
        raise RuntimeError("The Chrome download contains no executable.")


@contextmanager
def isolated_browser(headless=False):
    executable = chrome_path()
    if not executable:
        raise RuntimeError("Chrome is absent. Run bash install.sh first.")
    with tempfile.TemporaryDirectory(prefix="zero-browser-") as directory:
        base = Path(directory)
        profile = base / "profile"
        # Set every harness path before importing its modules. Ignore inherited remote or cloud settings.
        os.environ.update({
            "JEV_LOCAL": "1", "BU_NAME": "zero_browser", "BU_BROWSER_ID": "", "BU_CDP_WS": "",
            "BH_HOME": str(base / "harness"), "BH_CONFIG_DIR": str(base / "harness"),
            "BH_RUNTIME_DIR": str(base / "harness/runtime"), "BH_TMP_DIR": str(base / "harness/tmp"),
            "BH_AGENT_WORKSPACE": str(base / "harness/workspace"),
        })
        command = [str(executable), f"--user-data-dir={profile}", "--remote-debugging-port=0",
                   "--remote-debugging-address=127.0.0.1", "--no-first-run", "--no-default-browser-check",
                   "--disable-background-networking", "about:blank"]
        if headless:
            command.insert(1, "--headless=new")
        with (base / "chrome.log").open("w") as log:
            process = subprocess.Popen(command, stdout=log, stderr=log, start_new_session=True)
            try:
                deadline = time.monotonic() + 20
                port_file = profile / "DevToolsActivePort"
                while not port_file.exists():
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError("Chrome did not start its local browser connection.")
                    time.sleep(0.05)
                port = int(port_file.read_text().splitlines()[0])
                os.environ["BU_CDP_URL"] = f"http://127.0.0.1:{port}"
                yield
            finally:
                with cleanup_signals():
                    try:
                        # The worker owns the daemon. Keep its shutdown outside the inference process.
                        supervise([sys.executable, "-c", "from browser_harness.admin import restart_daemon; "
                                   "restart_daemon(name='zero_browser')"],
                                  timeout=2, memory_limit=256 * 2**20)
                    except (RuntimeError, OSError):
                        pass
                    finally:
                        stop_process_group(process)


class FixtureHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@contextmanager
def fixture_url():
    handler = functools.partial(FixtureHandler, directory=str(ROOT / "jev_ultrafast/static"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/fixture.html?scenario=travel"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def doctor():
    from jev_ultrafast.browser import Browser
    from jev_ultrafast.local_model import get_model, get_model_info

    print("Loading the cached Qwen model with Metal.", flush=True)
    get_model()
    browser = Browser("about:blank")
    try:
        browser.observe(screenshot=False)
    finally:
        browser.close()
    print(json.dumps({"ready": True, "local_model": True, "browser_connection": True,
                      "model_revision": get_model_info()["model_revision"]}, indent=2))


def run_goal(args, url):
    from jev_ultrafast.agent import Agent
    from jev_ultrafast.local_model import get_model

    started = time.monotonic()
    with Agent(url, args.goal) as agent:
        stop_reason = challenge_reason(agent.state["page"])
        if stop_reason:
            agent.state["status"] = "blocked"
        else:
            print("Loading local Qwen.", flush=True)
            get_model()
        executed_count, rejected_count = 0, 0
        for state in agent.run():
            history = state["history"]
            decision = state["decisions"][-1]
            timing = f"model {decision['latency_ms']} ms"
            if len(history) > executed_count:
                executed_count = len(history)
                rejected_count = 0
                print(f"Action {executed_count}: executed {decision['operation']} ({timing})", flush=True)
            elif state["status"] not in {"done", "blocked"}:
                rejected_count += 1
                print(f"Decision {len(state['decisions'])}: skipped before execution ({timing})", flush=True)
            else:
                print(f"Decision {len(state['decisions'])}: {state['status']} ({timing})", flush=True)
            stop_reason = challenge_reason(state["page"])
            if not stop_reason and rejected_count >= 3:
                stop_reason = "Three consecutive decisions did not execute. The CLI stopped."
            running = state["status"] not in {"done", "blocked"}
            if not stop_reason and running and len(state["decisions"]) >= args.max_decisions:
                stop_reason = "Decision budget reached. The CLI stopped."
            if not stop_reason and running and time.monotonic() - started >= args.timeout:
                stop_reason = "Run deadline reached. The CLI stopped."
            if stop_reason:
                agent.state["status"] = "blocked"
                break
            if state["status"] in {"done", "blocked"}:
                break
        # Read the browser again. A DONE decision alone is not outcome evidence.
        final = agent.browser.evaluate("({url:location.href,title:document.title,text:document.body.innerText})")
        assertions = {f"text:{text}": text in final["text"] for text in args.expect_text}
        if args.expect_url:
            assertions[f"url:{args.expect_url}"] = args.expect_url in final["url"]
        summary = {
            "status": agent.state["status"], "outcome_verified": bool(assertions) and all(assertions.values()),
            "stop_reason": stop_reason,
            "assertions": assertions, "actions": len(agent.state["history"]),
            "decisions": len(agent.state["decisions"]), "text_calls": len(agent.state["text_calls"]),
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "decision_latency_ms": [d["latency_ms"] for d in agent.state["decisions"]],
            "text_latency_ms": [d["latency_ms"] for d in agent.state["text_calls"]],
            "final_page": final,
        }
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary, indent=2))
        return 0 if summary["status"] == "done" and (not assertions or summary["outcome_verified"]) else 1


def supervised_worker(args):
    request = {**vars(args), "output": str(args.output) if args.output else None}
    limit = worker_memory_limit()
    print(f"Worker memory budget: {limit / 2**30:.1f} GiB. Run deadline: {args.timeout:g} s.", flush=True)
    with tempfile.TemporaryDirectory(prefix="zero-browser-worker-") as directory:
        path = Path(directory) / "request.json"
        path.write_text(json.dumps(request))
        return supervise([sys.executable, str(Path(__file__).resolve()), "--_worker", str(path)],
                         timeout=args.timeout, memory_limit=limit)


def execute_worker(path):
    os.environ["JEV_LOCAL"] = "1"
    args = argparse.Namespace(**json.loads(path.read_text()))
    args.output = Path(args.output) if args.output else None
    if args.doctor:
        doctor()
        return 0
    if args.fixture:
        with fixture_url() as url:
            return run_goal(args, url)
    return run_goal(args, args.url)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goal", nargs="?", help="One natural-language browser goal.")
    parser.add_argument("--url", default="https://www.google.com", help="Initial page (default: Google).")
    parser.add_argument("--fixture", action="store_true", help="Start the local travel fixture.")
    parser.add_argument("--doctor", action="store_true", help="Test the cached model, Metal, and Chrome connection.")
    parser.add_argument("--install-browser", action="store_true", help="Download Chrome if it is absent.")
    parser.add_argument("--offline", action="store_true", help="Do not download Chrome.")
    parser.add_argument("--headless", action="store_true", help="Run Chrome without a window.")
    parser.add_argument("--max-decisions", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=180,
                        help="Worker deadline in seconds, including model loading and browser calls.")
    parser.add_argument("--expect-text", action="append", default=[],
                        help="Test final page text. Repeat for each requirement.")
    parser.add_argument("--expect-url", help="Test that the final URL contains this text.")
    parser.add_argument("--output", type=Path, help="Save the final page and summary. Keep private pages outside Git.")
    parser.add_argument("--_worker", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        parser.error("This version needs an Apple Silicon Mac with Metal.")
    if args.max_decisions < 1 or args.timeout <= 0:
        parser.error("The decision and time budgets must be positive.")
    if not args.doctor and not args.install_browser and not args._worker:
        if args.goal is None:
            args.goal = input("Browser goal: ")
        if not args.goal.strip():
            parser.error("Supply a browser goal.")
        if urlparse(args.url).scheme not in {"http", "https"}:
            parser.error("The initial URL must use http or https.")
    try:
        if args._worker:
            return execute_worker(args._worker)
        if args.install_browser:
            install_browser(args.offline)
            return 0
        with single_run(), isolated_browser(headless=args.headless or args.doctor):
            return supervised_worker(args)
    except KeyboardInterrupt:
        print("Stopped.", file=sys.stderr)
        return 130
    except Exception as error:
        print(f"Stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
