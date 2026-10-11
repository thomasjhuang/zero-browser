"""Live demo site: trigger direct vs delegated Codex runs and stream token spend as it happens.

Usage:
    .venv/bin/python demo/server.py            # http://127.0.0.1:8765
    .venv/bin/python demo/server.py --port 9000

Live mode launches scripts/paired_browser_benchmark.py for one arm and tails its artifacts.
Replay mode re-streams a recorded passing run from artifacts/paired with its original timing.
"""

import argparse
import json
import os
import statistics
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
PAIRED = ROOT / 'artifacts/paired'
OUT = ROOT / 'artifacts/demo'
SESSIONS = Path.home() / '.codex/sessions'
MODES = ('direct', 'delegated')

RUNS = {}
LOCK = threading.Lock()


def jsonl(path, start=0):
    """Read complete lines from byte offset. Returns (events, new_offset)."""
    if not path.exists():
        return [], start
    with path.open('rb') as handle:
        handle.seek(start)
        data = handle.read()
    end = data.rfind(b'\n')
    if end < 0:
        return [], start
    events = []
    for line in data[:end].splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    return events, start + end + 1


def wall_ns(stamp):
    return int(datetime.fromisoformat(stamp.replace('Z', '+00:00')).timestamp() * 1e9)


def find_session(thread_id):
    for path in SESSIONS.rglob(f'*{thread_id}.jsonl'):
        return path
    return None


class Normalizer:
    """Turns raw codex/browser/session events into demo events with t (ms from dispatch)."""

    def __init__(self, base_ns):
        self.base = base_ns
        self.wall_offset = None  # monotonic_ns - wall_ns
        self.seen_tools = set()

    def t(self, ns):
        return round((ns - self.base) / 1e6)

    def codex(self, e):
        ns = e.get('received_monotonic_ns')
        kind = e.get('type')
        if ns is None:
            return []
        if kind == 'thread.started':
            return [{'kind': 'thread', 't': self.t(ns)}]
        item = e.get('item') or {}
        if item.get('type') == 'mcp_tool_call':
            key = (item.get('id'), kind)
            if key in self.seen_tools:
                return []
            self.seen_tools.add(key)
            if kind == 'item.started':
                return [{'kind': 'tool_start', 't': self.t(ns), 'tool': item.get('tool'),
                         'args': item.get('arguments')}]
            if kind == 'item.completed':
                size = sum(len(part.get('text', '')) for part in (item.get('result') or {}).get('content') or [])
                return [{'kind': 'tool_done', 't': self.t(ns), 'tool': item.get('tool'),
                         'result_chars': size, 'error': bool(item.get('error'))}]
        if kind == 'item.completed' and item.get('type') == 'agent_message':
            return [{'kind': 'verdict', 't': self.t(ns), 'text': item.get('text')}]
        if kind == 'turn.completed':
            return [{'kind': 'turn_done', 't': self.t(ns), 'usage': e.get('usage')}]
        return []

    def browser(self, e):
        ns = e.get('monotonic_ns')
        if ns is None:
            return []
        ev = e.get('event')
        if ev == 'browser_started':
            return [{'kind': 'browser', 't': self.t(ns), 'ms': e.get('duration_ms')}]
        if ev == 'model_call_started':
            return [{'kind': 'local_start', 't': self.t(ns)}]
        if ev == 'model_call_finished':
            timing = e.get('timing') or {}
            return [{'kind': 'local_call', 't': self.t(ns), 'usage': e.get('usage'),
                     'ms': round(e.get('wrapper_ms') or 0), 'gen_ms': timing.get('generation_ms'),
                     'load_ms': round(timing.get('model_acquisition_ms') or 0)}]
        if ev in ('executed', 'rejected'):
            action = e.get('action')
            label = action.get('label') if isinstance(action, dict) else None
            return [{'kind': ev, 't': self.t(ns), 'label': label, 'text': e.get('text'), 'source': e.get('source')}]
        if ev == 'independent_assessment':
            result = e.get('result') or {}
            return [{'kind': 'assessment', 't': self.t(ns), 'passed': result.get('passed'),
                     'checks': result.get('checks'), 'value': (result.get('observed') or {}).get('value')}]
        return []

    def session(self, e):
        if e.get('type') != 'token_usage_record' or self.wall_offset is None:
            return []
        ns = wall_ns(e['timestamp']) + self.wall_offset
        return [{'kind': 'llm_request', 't': self.t(ns), 'usage': e['payload'].get('usage')}]


class Run:
    def __init__(self, mode, source, folder=None):
        self.id = uuid.uuid4().hex[:10]
        self.mode, self.source = mode, source
        self.events = []
        self.done = False
        self.cond = threading.Condition()
        self.folder = folder
        self.process = None
        self.thread = None

    def emit(self, items):
        if not items:
            return
        with self.cond:
            self.events.extend(items)
            self.cond.notify_all()

    def finish(self, error=None):
        with self.cond:
            self.events.append({'kind': 'done', 'error': error, 'mode': self.mode})
            self.done = True
            self.cond.notify_all()


def replay_candidates(mode):
    out = []
    for folder in sorted(PAIRED.glob(f'*/*-{mode}')):
        assessment = folder / 'assessment.json'
        if not assessment.exists() or not (folder / 'codex.jsonl').exists():
            continue
        try:
            if json.loads(assessment.read_text()).get('passed'):
                out.append(folder)
        except ValueError:
            pass
    return out


def replay(run, speed):
    folder = run.folder
    codex, _ = jsonl(folder / 'codex.jsonl')
    thread_event = next((e for e in codex if e.get('type') == 'thread.started'), None)
    if not thread_event:
        return run.finish('Recorded run has no thread start')
    normalizer = Normalizer(thread_event['received_monotonic_ns'] - 300_000_000)
    session = find_session(thread_event['thread_id'])
    records = jsonl(session)[0] if session else []
    events = []
    for e in codex:
        events += normalizer.codex(e)
    for e in jsonl(folder / 'browser.jsonl')[0]:
        events += normalizer.browser(e)
    # Session wall clocks and the monotonic event clock differ, so place each recorded model request in order:
    # request k produced tool call k, and the remaining requests produced the verdict.
    anchors = [e['t'] - 15 for e in events if e['kind'] == 'tool_start']
    anchors += [e['t'] - 15 for e in events if e['kind'] == 'verdict'][:1]
    usages = [e['payload'].get('usage') for e in records if e.get('type') == 'token_usage_record']
    for k, usage in enumerate(usages):
        anchor = anchors[min(k, len(anchors) - 1)] if anchors else 0
        events.append({'kind': 'llm_request', 't': anchor - (len(usages) - k if k >= len(anchors) else 0),
                       'usage': usage})
    events.sort(key=lambda e: e['t'])
    run.emit([{'kind': 'meta', 'source': 'replay', 'folder': str(folder.relative_to(ROOT)), 'speed': speed}])
    started = time.monotonic()
    for event in events:
        delay = event['t'] / 1000 / speed - (time.monotonic() - started)
        if delay > 0:
            time.sleep(delay)
        run.emit([event])
    run.finish()


def live(run):
    OUT.mkdir(parents=True, exist_ok=True)
    before = set(PAIRED.glob('*')) if PAIRED.exists() else set()
    output = OUT / f'{int(time.time())}-{run.mode}.json'
    log_path = OUT / f'{output.stem}.log'
    python = ROOT / '.venv/bin/python'
    command = [str(python if python.exists() else sys.executable), str(ROOT / 'scripts/paired_browser_benchmark.py'),
               '--order', run.mode, '--output', str(output)]
    normalizer = Normalizer(time.monotonic_ns())
    run.emit([{'kind': 'meta', 'source': 'live', 'output': str(output.relative_to(ROOT))}])
    with log_path.open('w') as log:
        run.process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        offsets, session, folder = {}, None, None
        while True:
            alive = run.process.poll() is None
            if folder is None and PAIRED.exists():
                new = [p for p in PAIRED.glob('*') if p not in before]
                if new:
                    folder = max(new) / f'1-{run.mode}'
            if folder is not None:
                events = []
                codex, offsets['codex'] = jsonl(folder / 'codex.jsonl', offsets.get('codex', 0))
                for e in codex:
                    if e.get('type') == 'thread.started' and normalizer.wall_offset is None:
                        normalizer.wall_offset = time.monotonic_ns() - time.time_ns()
                        run.thread = e.get('thread_id')
                    events += normalizer.codex(e)
                browser, offsets['browser'] = jsonl(folder / 'browser.jsonl', offsets.get('browser', 0))
                for e in browser:
                    events += normalizer.browser(e)
                if session is None and run.thread:
                    session = find_session(run.thread)
                if session is not None:
                    records, offsets['session'] = jsonl(session, offsets.get('session', 0))
                    for e in records:
                        events += normalizer.session(e)
                events.sort(key=lambda e: e.get('t', 0))
                run.emit(events)
            if not alive:
                break
            time.sleep(0.15)
    code = run.process.returncode
    error = None
    if code != 0:
        error = f'benchmark exited {code}: ' + log_path.read_text()[-300:].strip()
    run.finish(error)


def history():
    """Recorded evidence for the static panels."""
    out = {}
    path = ROOT / 'results/paired-browser-five-pairs-v3.json'
    if path.exists():
        data = json.loads(path.read_text())
        arms = {}
        for mode in MODES:
            rows = [r for r in data['runs'] if r['method'] == mode]
            totals = [r['coordinator_usage_totals'] for r in rows if r.get('coordinator_usage_totals')]
            arms[mode] = {
                'n': len(rows), 'passed': sum(bool(r['passed']) for r in rows),
                'median_ms': statistics.median(r['goal_dispatch_to_verdict_ms'] for r in rows),
                'median_total_tokens': statistics.median(t['total_tokens'] for t in totals),
                'median_uncached': statistics.median(t['input_tokens'] - t['cached_input_tokens'] for t in totals),
                'median_requests': statistics.median(len(r['coordinator_requests']) for r in rows),
                'local_prompt_tokens': statistics.median(
                    sum((c.get('usage') or {}).get('prompt_tokens', 0) for c in r['local_calls']) for r in rows),
            }
        out['paired'] = {'goal': data['goal'], 'model': data['model'], 'arms': arms, 'scope': data['scope']}
    native = ROOT / 'results/native-desktop-sequential.json'
    if native.exists():
        data = json.loads(native.read_text())
        run = data['runs'][0]
        ref = data.get('successful_system_reference') or {}
        out['workflow'] = {
            'native': {'ms': run['goal_dispatch_to_verdict_ms'], 'tokens': run['coordinator_usage']['total_tokens'],
                       'uncached': run['uncached_input_tokens'], 'requests': run['coordinator_response_count']},
            'system': {'ms': ref.get('goal_dispatch_to_verdict_ms'), 'tokens': ref.get('coordinator_tokens'),
                       'local_calls': ref.get('local_calls'), 'local_prompt_tokens': ref.get('local_prompt_tokens')},
        }
    return out


BLOCKERS = ('paired_browser_benchmark', 'single_action_worker', 'scripts/milestone', 'run_jfk_once',
            'workflow_session', 'coordinator_handoff')


def busy():
    """Another benchmark or local worker already running blocks live mode."""
    try:
        listing = subprocess.check_output(['ps', '-axo', 'pid=,command='], text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    for line in listing.splitlines():
        if any(token in line for token in BLOCKERS):
            return line.strip()[:160]
    return None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, code, body, kind='application/json'):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            return self.send(200, (HERE / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        if path == '/api/history':
            return self.send(200, history())
        if path == '/api/status':
            return self.send(200, {'busy': busy(), 'replays': {m: len(replay_candidates(m)) for m in MODES}})
        if path.startswith('/api/stream/'):
            return self.stream(path.rsplit('/', 1)[-1])
        self.send(404, {'error': 'not found'})

    def do_POST(self):
        if self.path.split('?')[0] != '/api/start':
            return self.send(404, {'error': 'not found'})
        length = int(self.headers.get('Content-Length') or 0)
        body = json.loads(self.rfile.read(length) or b'{}')
        mode, source = body.get('mode'), body.get('source', 'replay')
        if mode not in MODES or source not in ('live', 'replay'):
            return self.send(400, {'error': 'mode must be direct or delegated; source live or replay'})
        with LOCK:
            if source == 'live':
                if any(r.source == 'live' and not r.done for r in RUNS.values()):
                    return self.send(409, {'error': 'A live run is already active'})
                blocker = busy()
                if blocker:
                    return self.send(409, {'error': f'Browser slot busy: {blocker}'})
                run = Run(mode, source)
                target, args = live, (run,)
            else:
                candidates = replay_candidates(mode)
                if not candidates:
                    return self.send(404, {'error': f'No recorded passing {mode} run'})
                index = int(body.get('index', -1)) % len(candidates)
                run = Run(mode, source, candidates[index])
                target, args = replay, (run, float(body.get('speed', 1)))
            RUNS[run.id] = run
        threading.Thread(target=target, args=args, daemon=True).start()
        self.send(200, {'id': run.id, 'mode': mode, 'source': source})

    def stream(self, run_id):
        run = RUNS.get(run_id)
        if not run:
            return self.send(404, {'error': 'unknown run'})
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        index = 0
        try:
            while True:
                with run.cond:
                    if index >= len(run.events) and not run.done:
                        run.cond.wait(timeout=10)
                    batch = run.events[index:]
                    index += len(batch)
                    finished = run.done and index >= len(run.events)
                if not batch:
                    self.wfile.write(b': keepalive\n\n')
                for event in batch:
                    self.wfile.write(f'data: {json.dumps(event)}\n\n'.encode())
                self.wfile.flush()
                if finished:
                    return
        except (BrokenPipeError, ConnectionResetError):
            return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--host', default='127.0.0.1')
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f'zero-browser demo on http://{args.host}:{args.port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
