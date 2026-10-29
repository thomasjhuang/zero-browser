"""Test resource stops without loading Qwen or opening a network page."""

import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from jev_ultrafast import agent as agent_module
from jev_ultrafast import local_model, local_policy
from scripts import runtime_guard

ROOT = Path(__file__).resolve().parents[1]


def load_cli():
    spec = importlib.util.spec_from_file_location("cli_runtime_test", ROOT / "scripts/run_cli.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return cli


@pytest.mark.parametrize("size", [1, 255, 256, 257, 600])
def test_prefill_preserves_every_token_and_bounds_each_chunk(size):
    tokens, chunks, evaluations = list(range(size)), [], []
    cache = [SimpleNamespace(state=[])]

    class Output:
        def __getitem__(self, key):
            assert key == (0, -1, slice(None))
            return list(cache[0].state)

    def model(inputs, *, cache):
        chunks.append(inputs[0])
        cache[0].state.extend(inputs[0])
        return Output()

    mx = SimpleNamespace(array=lambda value: value, eval=lambda state: evaluations.append(state))
    result = local_model.bounded_prefill(model, mx, tokens, cache)
    assert result == tokens
    assert all(len(chunk) <= local_model.PREFILL_CHUNK_TOKENS for chunk in chunks)
    assert chunks[-1] == [tokens[-1]]
    assert len(evaluations) == len(chunks) - 1


def test_oversized_prompt_stops_before_any_inference():
    with pytest.raises(ValueError, match="safety limit"):
        local_model.bounded_prefill(lambda *_a, **_k: pytest.fail("Inference ran"), None,
                                    [1] * (local_model.MAX_PROMPT_TOKENS + 1), [])


def test_prompt_guard_runs_before_candidate_boundary_tokenization():
    class Tokenizer:
        def apply_chat_template(self, *_args, **_kwargs):
            return "long prompt"

        def encode(self, text, **_kwargs):
            assert text == "long prompt"
            return [1] * (local_model.MAX_PROMPT_TOKENS + 1)

    with pytest.raises(ValueError, match="safety limit"):
        local_model.make_prompt(Tokenizer(), "Goal", "Page", [
            {"id": "DONE", "operation": "DONE", "target": None, "description": "Stop"},
        ])


def test_oversized_field_context_does_not_generate_text(monkeypatch):
    tokenizer = SimpleNamespace(apply_chat_template=lambda *_a, **_k: "large context",
                                encode=lambda *_a, **_k: [1] * (local_model.MAX_PROMPT_TOKENS + 1))
    monkeypatch.setattr(local_policy, "get_model", lambda: (None, tokenizer, None))
    monkeypatch.setitem(sys.modules, "mlx_lm", SimpleNamespace(
        generate=lambda *_a, **_k: pytest.fail("Text generation ran"),
    ))
    monkeypatch.setitem(sys.modules, "mlx_lm.sample_utils", SimpleNamespace(make_sampler=lambda **_k: None))
    with pytest.raises(ValueError, match="safety limit"):
        local_policy.local_field_text({"goal": "Fill the field"})


def test_process_memory_reads_a_live_process():
    assert runtime_guard.process_memory(os.getpid()) > 0


class _Worker:
    def __init__(self, pid=1491437, code=None):
        self.pid = pid
        self.code = code

    def poll(self):
        return self.code


def test_transient_memory_read_is_retried_for_a_live_worker():
    calls = {"n": 0}

    def read(_pid):
        calls["n"] += 1
        if calls["n"] == 1:
            raise OSError("Cannot read the worker memory footprint for 1491437")
        return 8192

    assert runtime_guard.read_live_footprint(_Worker(), read, pause=0) == 8192
    assert calls["n"] == 2


def test_memory_read_after_exit_is_not_a_parent_stop():
    def read(_pid):
        raise OSError("Cannot read the worker memory footprint for 1491437")

    assert runtime_guard.read_live_footprint(_Worker(code=0), read, pause=0) is None


def test_repeated_unreadable_memory_still_stops_a_live_worker():
    def read(_pid):
        raise OSError("Cannot read the worker memory footprint for 1491437")

    with pytest.raises(OSError, match="1491437"):
        runtime_guard.read_live_footprint(_Worker(), read, attempts=2, pause=0)


def test_low_memory_headroom_refuses_model_start(monkeypatch):
    monkeypatch.setattr(runtime_guard.sys, "platform", "darwin")

    def output(command, **kwargs):
        return str(24 * 2**30) if "sysctl" in command[0] else "System-wide memory free percentage: 10%"

    monkeypatch.setattr(runtime_guard.subprocess, "check_output", output)
    with pytest.raises(RuntimeError, match="Insufficient memory"):
        runtime_guard.worker_memory_limit()


def test_memory_budget_leaves_room_for_other_applications(monkeypatch):
    monkeypatch.setattr(runtime_guard.sys, "platform", "darwin")

    def output(command, **kwargs):
        return str(16 * 2**30) if "sysctl" in command[0] else "System-wide memory free percentage: 40%"

    monkeypatch.setattr(runtime_guard.subprocess, "check_output", output)
    assert runtime_guard.worker_memory_limit() == (16 * 2**30 * 40 // 100) - 2 * 2**30


def test_watchdog_kills_a_worker_that_ignores_termination(tmp_path):
    pid_file = tmp_path / "pid"
    code = ("import os,signal,time; from pathlib import Path; "
            "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            f"Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(30)")
    started = time.monotonic()
    with pytest.raises(RuntimeError, match="deadline"):
        runtime_guard.supervise([sys.executable, "-c", code], timeout=0.5, memory_limit=2**30)
    assert time.monotonic() - started < 4
    with pytest.raises(ProcessLookupError):
        os.kill(int(pid_file.read_text()), 0)


def test_watchdog_stops_on_reported_memory_budget(tmp_path):
    pid_file = tmp_path / "pid"
    code = ("import os,time; from pathlib import Path; "
            f"Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(30)")

    def memory_reader(pid):
        return 2**30 if pid_file.exists() else 0

    with pytest.raises(RuntimeError, match="memory budget"):
        runtime_guard.supervise([sys.executable, "-c", code], timeout=5,
                                memory_limit=1024, memory_reader=memory_reader)
    with pytest.raises(ProcessLookupError):
        os.kill(int(pid_file.read_text()), 0)


def test_single_run_rejects_a_second_cli(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime_guard.tempfile, "gettempdir", lambda: str(tmp_path))
    with runtime_guard.single_run():
        with pytest.raises(RuntimeError, match="Another zero-browser"):
            with runtime_guard.single_run():
                pytest.fail("A second run acquired the lock")
    with runtime_guard.single_run():
        pass


def test_interrupt_stops_the_worker_without_a_traceback(tmp_path):
    pid_file = tmp_path / "pid"
    worker = ("import os,signal,time; from pathlib import Path; "
              "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
              f"Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(30)")
    parent_code = ("import sys; from scripts.runtime_guard import supervise\n"
                   "try:\n"
                   f" supervise([sys.executable, '-c', {worker!r}], timeout=30, memory_limit=2**30)\n"
                   "except KeyboardInterrupt:\n sys.exit(130)\n")
    parent = subprocess.Popen([sys.executable, "-c", parent_code], cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        deadline = time.monotonic() + 5
        while not pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert pid_file.exists()
        parent.send_signal(signal.SIGINT)
        time.sleep(0.15)
        parent.send_signal(signal.SIGINT)
        _, stderr = parent.communicate(timeout=4)
        assert parent.returncode == 130
        assert b"Traceback" not in stderr
        with pytest.raises(ProcessLookupError):
            os.kill(int(pid_file.read_text()), 0)
    finally:
        runtime_guard.stop_process_group(parent)
        if pid_file.exists():
            try:
                os.kill(int(pid_file.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass


def args(tmp_path):
    return SimpleNamespace(goal="Open the documentation", max_decisions=20, timeout=10,
                           expect_text=[], expect_url=None, output=tmp_path / "summary.json")


def fake_agent(monkeypatch, *, challenge_at=None, stale=False):
    class FakeAgent:
        def __init__(self, *_args):
            self.state = {"page": {"text": "Verify you are human" if challenge_at == 0 else "Documentation"},
                          "status": "ready", "history": [], "decisions": [], "text_calls": []}
            self.browser = SimpleNamespace(evaluate=lambda _code: {
                "url": "https://example.invalid", "title": "Test", "text": self.state["page"]["text"],
            })

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def run(self):
            for step in range(5):
                if self.state["status"] == "blocked":
                    return
                self.state["decisions"].append({"operation": "CLICK", "latency_ms": 1})
                if not stale:
                    self.state["history"].append({"operation": "CLICK"})
                if challenge_at == step + 1:
                    self.state["page"]["text"] = "Our systems have detected unusual traffic"
                yield self.state
            pytest.fail("The CLI did not stop")

    monkeypatch.setattr(agent_module, "Agent", FakeAgent)


def test_initial_captcha_does_not_load_qwen(tmp_path, monkeypatch):
    fake_agent(monkeypatch, challenge_at=0)
    monkeypatch.setattr(local_model, "get_model", lambda: pytest.fail("Qwen loaded on a CAPTCHA page"))
    assert load_cli().run_goal(args(tmp_path), "https://example.invalid") == 1
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["decisions"] == summary["actions"] == 0
    assert "Human verification" in summary["stop_reason"]


def test_new_captcha_stops_before_another_decision(tmp_path, monkeypatch):
    fake_agent(monkeypatch, challenge_at=1)
    monkeypatch.setattr(local_model, "get_model", lambda: None)
    assert load_cli().run_goal(args(tmp_path), "https://example.invalid") == 1
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["decisions"] == summary["actions"] == 1
    assert "Human verification" in summary["stop_reason"]


def test_stale_decisions_stop_and_do_not_print_executed_actions(tmp_path, monkeypatch, capsys):
    fake_agent(monkeypatch, stale=True)
    monkeypatch.setattr(local_model, "get_model", lambda: None)
    assert load_cli().run_goal(args(tmp_path), "https://example.invalid") == 1
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["decisions"] == 3
    assert summary["actions"] == 0
    assert "did not execute" in summary["stop_reason"]
    output = capsys.readouterr().out
    assert output.count("skipped before execution") == 3
    assert "Action 0:" not in output


def test_an_article_that_mentions_captcha_is_not_a_challenge():
    assert runtime_guard.challenge_reason({"text": "This article explains CAPTCHA implementations."}) is None
