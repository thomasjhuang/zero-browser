"""Record up to two human demonstrations in an isolated Chromium session.

Run with: uv run --with playwright python scripts/record_demo.py
Install Chromium first with: uv run --with playwright playwright install chromium
"""

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import uuid
from datetime import datetime, timezone

from playwright.async_api import async_playwright


class Recorder:
    def __init__(self, browser, observer, output, starting_url):
        self.browser = browser
        self.observer = observer
        self.output = output
        self.starting_url = starting_url
        self.context = None
        self.page = None
        self.controller = None
        self.active = False
        self.saved = 0
        self.rows = []
        self.files = []
        self.error = None
        self.session = None
        self.stream = None
        self.done = asyncio.Event()
        self.lock = asyncio.Lock()
        self.pages = {}
        self.checkpoints = set()

    def config(self):
        return {"active": self.active, "session_id": self.session}

    def status(self):
        return {"active": self.active, "saved": self.saved, "events": len(self.rows),
                "files": self.files, "error": self.error}

    async def save_event(self, source, row):
        if not self.active or row.get("session_id") != self.session:
            return
        if source["frame"] != source["page"].main_frame:
            row.update(mapping="unsupported", reason="The production observer does not support child frames.")
        row["page_id"] = self.pages.setdefault(source["page"], str(uuid.uuid4()))
        row["event_index"] = len(self.rows) + 1
        row["label_source"] = "human_demonstration"
        observation = row.get("observation")
        selected = row.get("selected_action")
        if row.get("mapping") == "matched":
            matches = [a for a in (observation or {}).get("actions", []) if a == selected]
            if len(matches) != 1:
                row.update(mapping="unsupported", reason="The selected action does not match the observation.")
        if observation and observation.get("omitted_actions"):
            row["candidate_truncation"] = observation["omitted_actions"]
        try:
            self.stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            self.stream.flush()
            os.fsync(self.stream.fileno())
            self.rows.append(row)
        except Exception as exc:
            self.error = f"The recorder could not save an action: {exc}"
            raise
        # This captures a DOM checkpoint in the trace after the manual event.
        task = asyncio.create_task(self.checkpoint(source["page"]))
        self.checkpoints.add(task)
        task.add_done_callback(self.checkpoints.discard)

    async def checkpoint(self, page):
        try:
            await page.evaluate(self.observer)
        except Exception:
            # Navigation can remove this document. The pre-action observation is already saved.
            pass

    async def open_page(self, url):
        if not url.startswith(("https://", "http://")):
            raise ValueError("Enter an HTTP or HTTPS starting URL.")
        if self.context:
            await self.context.close()
        self.context = await self.browser.new_context(viewport=None)
        await self.context.expose_binding("__saveDemoEvent", self.save_event)
        await self.context.expose_binding("__getDemoConfig", lambda source: self.config())
        script = (Path(__file__).parent / "recorder/events.js").read_text()
        await self.context.add_init_script(script=script.replace("__OBSERVER__", self.observer.strip().rstrip(";")))
        self.page = await self.context.new_page()
        self.starting_url = url
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as exc:
            self.error = f"The page did not finish loading: {exc}"
        await self.page.bring_to_front()

    async def start(self, goal, url):
        if self.saved >= 2:
            raise ValueError("Two demonstrations are already saved.")
        if not goal.strip():
            raise ValueError("Enter the task goal before recording.")
        if not self.page or self.page.is_closed():
            await self.open_page(url)
        if self.error:
            raise ValueError(self.error)
        self.session = str(uuid.uuid4())
        self.directory = self.output / self.session
        self.directory.mkdir(parents=True, mode=0o700)
        self.stream = (self.directory / "events.jsonl").open("x", encoding="utf-8")
        self.rows = []
        self.metadata = {
            "schema_version": 1, "session_id": self.session, "goal": goal.strip(),
            "started_at": datetime.now(timezone.utc).isoformat(), "starting_url": self.page.url,
            "observer_sha256": hashlib.sha256(self.observer.encode()).hexdigest(),
            "label_source": "human_demonstration", "model_inference": False,
            "outcome_verified": False, "status": "recording",
            "limitations": [
                "Manual events are stored in events.jsonl. The Playwright trace adds page checkpoints.",
                "Scroll distances, Enter submissions, and child-frame actions are not training labels.",
                "A matched action is not proof that the action achieved the task goal.",
                "Candidate capacity and tokenizer compatibility require a separate export step.",
            ],
        }
        self.write_metadata()
        await self.context.tracing.start(screenshots=True, snapshots=True, sources=False)
        self.active = True
        for page in self.context.pages:
            for frame in page.frames:
                try:
                    await frame.evaluate("s => window.__humanRecorderSet(s)", self.config())
                except Exception as exc:
                    self.error = f"The recorder could not attach to a document: {exc}"
        self.metadata["initial_observation"] = await self.page.evaluate(self.observer)
        self.write_metadata()
        await self.page.bring_to_front()

    def write_metadata(self):
        target = self.directory / "session.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.metadata, indent=2, ensure_ascii=False) + "\n")
        temporary.replace(target)

    async def save(self, outcome="unverified", interrupted=False):
        if not self.active:
            raise ValueError("No demonstration is recording.")
        final_pages = []
        # Keep the binding active until every document flushes its pending input.
        for page in list(self.context.pages):
            for frame in page.frames:
                try:
                    await frame.evaluate("s => window.__humanRecorderSet(s)",
                                         {"active": False, "session_id": self.session})
                    if frame == page.main_frame:
                        final_pages.append(await page.evaluate(self.observer))
                except Exception as exc:
                    self.error = f"A document could not finish recording: {exc}"
        self.active = False
        if self.checkpoints:
            await asyncio.gather(*list(self.checkpoints), return_exceptions=True)
        try:
            await self.context.tracing.stop(path=self.directory / "trace.zip")
        except Exception as exc:
            self.error = f"The trace could not finish: {exc}"
        self.stream.close()
        self.metadata.update(
            status="incomplete" if interrupted or self.error else "saved",
            ended_at=datetime.now(timezone.utc).isoformat(), user_reported_outcome=outcome,
            final_observations=final_pages, event_count=len(self.rows),
            matched_events=sum(r.get("mapping") == "matched" for r in self.rows),
            unsupported_events=sum(r.get("mapping") != "matched" for r in self.rows),
            error=self.error,
        )
        self.write_metadata()
        self.files.append(str(self.directory))
        self.saved += 1
        print(json.dumps({"saved": str(self.directory), "events": len(self.rows), "error": self.error}), flush=True)

    async def command(self, source, request):
        action = request.get("action")
        if action == "status":
            return self.status()
        async with self.lock:
            if action in ("open", "start") and self.active:
                raise ValueError("Save the current demonstration first.")
            if action == "open":
                self.error = None
                await self.open_page(request["url"])
            elif action == "start":
                await self.start(request["goal"], request["url"])
            elif action == "save":
                await self.save(request.get("outcome", "unverified"))
            elif action == "finish":
                if self.active:
                    raise ValueError("Save the current demonstration first.")
                self.done.set()
            else:
                raise ValueError("Unknown recorder action.")
            return self.status()

    async def run(self):
        self.controller = await self.browser.new_page(viewport={"width": 920, "height": 900})
        await self.controller.expose_binding("__recorderControl", self.command)
        await self.controller.set_content((Path(__file__).parent / "recorder/control.html").read_text())
        await self.controller.locator("#url").fill(self.starting_url)
        self.controller.on("close", lambda _: self.done.set())
        self.browser.on("disconnected", lambda _: self.done.set())
        print(json.dumps({"status": "ready", "output": str(self.output)}), flush=True)
        await self.done.wait()
        if self.active:
            await self.save(interrupted=True)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observer-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path.home() / ".local/share/zero-browser/demonstrations")
    parser.add_argument("--url", default="https://www.google.com/travel/flights")
    args = parser.parse_args()
    observer = (args.observer_root / "jev_ultrafast/snapshot.js").read_text()
    os.umask(0o077)
    args.output.mkdir(parents=True, exist_ok=True, mode=0o700)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        try:
            await Recorder(browser, observer, args.output.resolve(), args.url).run()
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
