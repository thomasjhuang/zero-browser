"""Test comparison isolation and scoring without making model requests."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("decision_baselines", ROOT / "scripts/decision_baselines.py")
baselines = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(baselines)


def test_suite_uses_exact_qwen_messages_without_answer_key():
    jobs, hashes = baselines.suite([
        ROOT / "fixtures/decision_cases.json", ROOT / "fixtures/decision_quality_cases.json"])
    assert len(jobs) == 48
    assert len(hashes) == 2
    for case, rotation, actions, prompt in jobs:
        assert "expected_action" not in prompt
        capture = baselines.Messages()
        baselines.make_prompt(capture, case["goal"], case["observation"], actions)
        assert prompt == capture.messages[1]["content"]
        assert actions[0] == case["candidates"][rotation]
        assert {a["id"] for a in actions} == {a["id"] for a in case["candidates"]}


def test_subscription_environment_excludes_api_routes(monkeypatch):
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY",
                "ANTHROPIC_BASE_URL", "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_API_KEY_HELPER",
                "CODEX_API_KEY", "CODEX_ACCESS_TOKEN", "CODEX_MODEL_PROVIDER", "CODEX_BASE_URL"):
        monkeypatch.setenv(key, "synthetic-value")
    monkeypatch.setenv("CODEX_HOME", "/synthetic/auth")
    env = baselines.subscription_env()
    assert env["CODEX_HOME"] == "/synthetic/auth"
    assert "ANTHROPIC_API_KEY" not in env
    assert "OPENAI_API_KEY" not in env
    assert "ANTHROPIC_BASE_URL" not in env
    assert "CLAUDE_CODE_USE_BEDROCK" not in env
    assert "CLAUDE_CODE_API_KEY_HELPER" not in env
    assert "CODEX_API_KEY" not in env
    assert "CODEX_ACCESS_TOKEN" not in env
    assert "CODEX_MODEL_PROVIDER" not in env
    assert "CODEX_BASE_URL" not in env


def test_claude_rejects_tools_and_failed_completion():
    events = [{"type": "system", "subtype": "init", "model": "synthetic-model", "tools": ["Read"]},
              {"type": "result", "result": "A", "is_error": False}]
    with pytest.raises(RuntimeError, match="exposed tools"):
        baselines.parse_events("claude", "\n".join(map(json.dumps, events)))
    events[0]["tools"] = []
    events[1]["is_error"] = True
    with pytest.raises(RuntimeError, match="successful result"):
        baselines.parse_events("claude", "\n".join(map(json.dumps, events)))


def test_codex_counts_tool_use_and_rejects_incomplete_turn():
    events = [{"type": "item.completed", "item": {"type": "command_execution", "command": "synthetic"}},
              {"type": "item.completed", "item": {"type": "agent_message", "text": "A"}},
              {"type": "turn.completed", "usage": {"input_tokens": 99, "output_tokens": 1}}]
    result = baselines.parse_events("codex", "\n".join(map(json.dumps, events)))
    assert result["tool_calls"] == 1
    assert result["usage"]["input_tokens"] == 99
    with pytest.raises(RuntimeError, match="completed message"):
        baselines.parse_events("codex", "\n".join(map(json.dumps, events[:-1])))


def test_claude_auth_rejects_api_login(monkeypatch, tmp_path):
    monkeypatch.setattr(baselines, "invoke", lambda *a, **kw: (
        json.dumps({"loggedIn": True, "authMethod": "api_key"}), 1))
    with pytest.raises(RuntimeError, match="subscription login"):
        baselines.preflight("claude", "synthetic-cli", {}, tmp_path)


def test_commands_disable_tools_and_customizations(tmp_path):
    claude = baselines.command("claude", "synthetic-cli", "synthetic-model", tmp_path, tmp_path / "system")
    assert claude[claude.index("--tools") + 1] == ""
    assert "--safe-mode" in claude
    assert "--strict-mcp-config" in claude
    codex = baselines.command("codex", "synthetic-cli", "synthetic-model", tmp_path, tmp_path / "system")
    assert codex[1:3] == ["exec", "--ignore-user-config"]
    assert 'project_doc_max_bytes=0' in codex
    assert 'web_search="disabled"' in codex
    assert "shell_tool" in codex


def test_codex_warning_is_metadata_not_a_tool_call():
    events = [{"type": "item.completed", "item": {"type": "error", "message": "Synthetic CLI warning"}},
              {"type": "item.completed", "item": {"type": "agent_message", "text": "B"}},
              {"type": "turn.completed", "usage": {"input_tokens": 99}}]
    result = baselines.parse_events("codex", "\n".join(map(json.dumps, events)))
    assert result["tool_calls"] == 0
    assert result["cli_warnings"] == ["Synthetic CLI warning"]


@pytest.mark.parametrize("failure", [TimeoutError("synthetic timeout"), json.JSONDecodeError("synthetic", "x", 0)])
def test_failed_attempt_is_preserved_and_excluded_from_latency(failure, monkeypatch, tmp_path):
    output = tmp_path / "result.json"
    monkeypatch.setattr(sys, "argv", ["decision_baselines.py", "--provider", "claude",
                        "--model", "synthetic", "--executable", "synthetic", "--run",
                        "--limit", "1", "--output", str(output)])
    monkeypatch.setattr(baselines, "preflight", lambda *a: {"auth_method": "claude.ai"})

    def fake_invoke(command, *args, **kwargs):
        if "--version" in command:
            return "synthetic-version", 1
        raise failure

    monkeypatch.setattr(baselines, "invoke", fake_invoke)
    assert baselines.main() == 1
    result = json.loads(output.read_text())
    assert result["attempted_requests"] == 1
    assert result["failed_requests"] == 1
    assert result["median_elapsed_ms"] is None
    assert result["measurements"][0]["case"] == "empty_field"
    assert result["measurements"][0]["rotation"] == 0
    assert result["measurements"][0]["failure_category"] == type(failure).__name__
    assert result["measurements"][0]["failed_attempt_ms"] >= 0


def test_comparison_audit_rejects_prompt_and_answer_changes(monkeypatch, tmp_path):
    import summarize_decision_baselines as summary

    case = {"name": "synthetic", "expected_action": "click", "candidates": [{"id": "click"}]}
    monkeypatch.setattr(summary, "suite", lambda paths: ([(case, 0, case["candidates"], "synthetic prompt")], {}))
    directory = tmp_path / "results"
    directory.mkdir()
    import hashlib

    base = {"case": "synthetic", "rotation": 0, "expected_action": "click", "candidate_order": ["click"],
            "correct": True, "selected_action": {"id": "click"}, "prompt_tokens": 1,
            "phase": "warm_forward", "inference_ms": 1}
    qwen = {"status": "completed", "measurements": [base], "cold_first_forward_ms": 1,
            "model_load_ms": 1, "peak_mlx_bytes": 1, "model_id": "synthetic", "model_revision": "synthetic"}
    (directory / "decision-smoke.json").write_text(json.dumps(qwen))
    (directory / "decision-quality.json").write_text(json.dumps({**qwen, "measurements": []}))
    cli_measurement = {**base, "selected_action": "click", "user_prompt_sha256": "changed", "elapsed_ms": 1,
                       "valid_response": True, "tool_calls": 0, "usage": {"input_tokens": 1}}
    cli = {"status": "completed", "measurements": [cli_measurement], "fixture_sha256": {},
           "system_sha256": hashlib.sha256(summary.SYSTEM.encode()).hexdigest(),
           "requested_model": "synthetic", "cli_version": "synthetic", "authentication": {}}
    (directory / "decision-codex.json").write_text(json.dumps(cli))
    with pytest.raises(ValueError, match="User prompts differ"):
        summary.summarize(tmp_path)
    cli_measurement["user_prompt_sha256"] = hashlib.sha256(b"synthetic prompt").hexdigest()
    cli_measurement["expected_action"] = "changed"
    (directory / "decision-codex.json").write_text(json.dumps(cli))
    with pytest.raises(ValueError, match="Answer keys"):
        summary.summarize(tmp_path)


def test_model_change_preserves_the_failed_attempt(monkeypatch, tmp_path):
    output = tmp_path / "result.json"
    monkeypatch.setattr(sys, "argv", ["decision_baselines.py", "--provider", "claude",
                        "--model", "synthetic", "--executable", "synthetic", "--run",
                        "--limit", "2", "--output", str(output)])
    monkeypatch.setattr(baselines, "preflight", lambda *a: {"auth_method": "claude.ai"})
    monkeypatch.setattr(baselines, "invoke", lambda *a, **kw: ("synthetic output", 10))
    results = iter([{"resolved_model": "synthetic-A", "response": "B", "tool_calls": 0},
                    {"resolved_model": "synthetic-B", "response": "A", "tool_calls": 0}])
    monkeypatch.setattr(baselines, "parse_events", lambda *a: next(results))
    assert baselines.main() == 1
    result = json.loads(output.read_text())
    assert result["attempted_requests"] == 2
    assert result["failed_requests"] == 1
    assert result["median_elapsed_ms"] == 10
    assert result["measurements"][1]["status"] == "failed"
    assert result["measurements"][1]["failure_category"] == "RuntimeError"
