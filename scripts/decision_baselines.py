"""Compare synthetic decisions through subscription CLIs. No browser or model scores."""

import argparse
import hashlib
import json
import os
import shutil
import signal
import statistics
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from decision_smoke import LABELS, ROOT, SYSTEM, make_prompt

CODEX_APP = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"


class Messages:
    """Capture the exact messages from the unchanged Qwen prompt builder."""

    def apply_chat_template(self, messages, **kwargs):
        self.messages = messages
        return messages[1]["content"] + "\n"

    def encode(self, text, **kwargs):
        return list(text.encode())

    def decode(self, tokens):
        return bytes(tokens).decode()


def user_prompt(case, actions):
    capture = Messages()
    make_prompt(capture, case["goal"], case["observation"], actions)
    return capture.messages[1]["content"]


def subscription_env():
    """Remove API credentials and alternate provider routes from the child environment."""
    return {key: value for key, value in os.environ.items() if not (
        key.startswith(("ANTHROPIC_", "OPENAI_", "CLAUDE_CODE_USE_"))
        or key in {"CLAUDE_CODE_API_KEY_HELPER", "CLAUDECODE", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN",
                   "CODEX_MODEL_PROVIDER", "CODEX_BASE_URL"}
    )}


def invoke(command, cwd, env, timeout=90, prompt=None):
    started = time.perf_counter()
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, start_new_session=True)
    try:
        stdout, stderr = process.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
        raise TimeoutError("CLI request timed out") from None
    if process.returncode:
        raise RuntimeError(f"CLI exited with status {process.returncode}: {stderr[-500:]}")
    return stdout, (time.perf_counter() - started) * 1000


def preflight(provider, executable, env, cwd):
    if provider == "codex":
        output, _ = invoke([executable, "login", "status"], cwd, env)
        # Codex writes this status to stderr on some releases.
        if "ChatGPT" not in output:
            result = subprocess.run([executable, "login", "status"], cwd=cwd, env=env,
                                    capture_output=True, text=True, timeout=15, check=True)
            output = result.stdout + result.stderr
        if "Logged in using ChatGPT" not in output:
            raise RuntimeError("Codex needs a ChatGPT subscription login")
        return {"auth_method": "ChatGPT subscription"}
    output, _ = invoke([executable, "auth", "status"], cwd, env)
    auth = json.loads(output)
    if not auth.get("loggedIn") or auth.get("authMethod") != "claude.ai":
        raise RuntimeError("Claude needs a claude.ai subscription login")
    return {"auth_method": auth["authMethod"], "subscription_type": auth.get("subscriptionType")}


def command(provider, executable, model, cwd, system_file):
    if provider == "claude":
        return [executable, "--print", "--verbose", "--output-format", "stream-json",
                "--model", model, "--effort", "high", "--tools", "", "--safe-mode",
                "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                "--system-prompt", SYSTEM, "--no-session-persistence",
                "--permission-mode", "dontAsk"]
    args = [executable, "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
            "--sandbox", "read-only", "--json", "--model", model, "--cd", str(cwd),
            "-c", 'model_reasoning_effort="high"', "-c", "project_doc_max_bytes=0",
            "-c", 'web_search="disabled"', "-c", f"model_instructions_file={json.dumps(str(system_file))}"]
    for feature in ("shell_tool", "shell_snapshot", "apps", "plugins", "multi_agent", "hooks",
                    "browser_use", "browser_use_external", "browser_use_full_cdp_access", "computer_use",
                    "view_image", "image_generation", "skill_search", "skill_mcp_dependency_install",
                    "workspace_dependencies", "sleep_tool", "goals"):
        args += ["--disable", feature]
    return args + ["--enable", "skip_host_skill_discovery", "-"]


def parse_events(provider, output):
    events = [json.loads(line) for line in output.splitlines() if line.strip()]
    if provider == "claude":
        init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
        result = next((e for e in events if e.get("type") == "result"), None)
        if result is None or result.get("is_error"):
            raise RuntimeError("Claude returned no successful result")
        if init.get("tools") or init.get("mcp_servers"):
            raise RuntimeError("Claude exposed tools in the isolated decision test")
        tool_calls = sum(block.get("type") == "tool_use" for event in events
                         for block in event.get("message", {}).get("content", []) if isinstance(block, dict))
        models = list(result.get("modelUsage", {}))
        return {"response": result.get("result", ""), "resolved_model": init.get("model"),
                "models_used": models, "usage": result.get("usage"), "tool_calls": tool_calls,
                "provider_duration_ms": result.get("duration_api_ms"),
                "estimated_api_equivalent_usd": result.get("total_cost_usd")}
    items = [e["item"] for e in events if e.get("type") == "item.completed"]
    messages = [item["text"] for item in items if item.get("type") == "agent_message"]
    completed = next((e for e in events if e.get("type") == "turn.completed"), None)
    if completed is None or len(messages) != 1:
        raise RuntimeError("Codex returned no single completed message")
    return {"response": messages[0], "resolved_model": None, "models_used": [],
            "usage": completed.get("usage"),
            "tool_calls": sum(item.get("type") not in {"agent_message", "reasoning", "error"} for item in items),
            "completed_item_types": [item.get("type") for item in items],
            "cli_warnings": [item.get("message") for item in items if item.get("type") == "error"],
            "provider_duration_ms": None, "estimated_api_equivalent_usd": None}


def suite(paths):
    cases = []
    hashes = {}
    for path in paths:
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        cases.extend(json.loads(path.read_text()))
    if not cases or len({c["name"] for c in cases}) != len(cases):
        raise ValueError("Case names must be unique and nonempty")
    jobs = []
    for case in cases:
        actions = case["candidates"]
        if case["expected_action"] not in {a["id"] for a in actions}:
            raise ValueError("Expected action must belong to the candidates")
        for rotation in range(len(actions)):
            rotated = actions[rotation:] + actions[:rotation]
            jobs.append((case, rotation, rotated, user_prompt(case, rotated)))
    return jobs, hashes


def save(report, path):
    measurements = report["measurements"]
    times = [m["elapsed_ms"] for m in measurements if m.get("status") == "completed"]
    report.update(decisions=len(measurements), attempted_requests=len(measurements),
                  failed_requests=sum(m.get("status") == "failed" for m in measurements),
                  correct=sum(m["correct"] for m in measurements),
                  invalid=sum(not m.get("valid_response", False) for m in measurements),
                  median_elapsed_ms=statistics.median(times) if times else None,
                  first_request_ms=times[0] if times else None,
                  subsequent_median_ms=statistics.median(times[1:]) if len(times) > 1 else None)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["codex", "claude"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--executable")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cases", type=Path, nargs="+", default=[
        ROOT / "fixtures/decision_cases.json", ROOT / "fixtures/decision_quality_cases.json"])
    parser.add_argument("--run", action="store_true", help="Use the logged-in subscription for inference")
    parser.add_argument("--limit", type=int, help="Limit requests for an installation probe")
    args = parser.parse_args()
    if not args.run:
        parser.error("Pass --run to authorize subscription requests")
    if args.output.exists():
        parser.error("Output exists. Use a new path to preserve the baseline")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    jobs, hashes = suite(args.cases)
    executable = args.executable or shutil.which(args.provider)
    if not executable and args.provider == "codex" and Path(CODEX_APP).is_file():
        executable = CODEX_APP
    if not executable:
        parser.error("CLI executable is unavailable")
    report = {"status": "started", "provider": args.provider, "requested_model": args.model,
              "timestamp_utc": datetime.now(timezone.utc).isoformat(), "fixture_sha256": hashes,
              "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "system_sha256": hashlib.sha256(SYSTEM.encode()).hexdigest(), "measurements": [],
              "planned_decisions": min(len(jobs), args.limit or len(jobs)),
              "notes": ["These synthetic observations do not establish browser-task reliability.",
                        "Latency includes CLI startup, network access, and provider computation.",
                        "Each request starts a new session. Provider prompt caches can still apply.",
                        "CLI transport metadata is JSON. The requested model response is one label.",
                        "CLI logit scores and remote peak memory are unavailable.",
                        "The system and user text match Qwen. Provider wrappers and tokenizers differ.",
                        "Codex adds global instruction and skill context despite project_doc_max_bytes=0.",
                        "High reasoning effort is requested. Qwen uses one forward pass without reasoning.",
                        "API-equivalent cost metadata is not an invoice or a subscription charge."]}
    env = subscription_env()
    try:
        with tempfile.TemporaryDirectory(prefix="zero-decision-") as directory:
            cwd = Path(directory)
            report["authentication"] = preflight(args.provider, executable, env, cwd)
            report["cli_version"] = invoke([executable, "--version"], cwd, env)[0].strip()
            system_file = cwd / "system.txt"
            system_file.write_text(SYSTEM)
            model = args.model
            for case, rotation, actions, prompt in jobs[:args.limit]:
                measurement = {"case": case["name"], "rotation": rotation,
                               "expected_action": case["expected_action"],
                               "candidate_order": [a["id"] for a in actions],
                               "user_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                               "user_prompt_bytes": len(prompt.encode()), "scores": None}
                measurement.update(status="started", correct=False, valid_response=False)
                report["measurements"].append(measurement)
                started = time.perf_counter()
                try:
                    output, elapsed = invoke(command(args.provider, executable, model, cwd, system_file),
                                             cwd, env, prompt=prompt)
                    result = parse_events(args.provider, output)
                    if args.provider == "claude" and result["resolved_model"]:
                        if report.get("resolved_model", result["resolved_model"]) != result["resolved_model"]:
                            raise RuntimeError("The resolved model changed during the run")
                        model = result["resolved_model"]
                        report["resolved_model"] = model
                    label = result["response"]
                    valid = label in LABELS[:len(actions)] and len(label) == 1 and not result["tool_calls"]
                    selected = actions[LABELS.index(label)]["id"] if valid else None
                    measurement.update(result, status="completed", elapsed_ms=elapsed, valid_response=valid,
                                       selected_action=selected, correct=selected == case["expected_action"])
                except Exception as error:
                    measurement.update(status="failed", failure_category=type(error).__name__,
                                       failed_attempt_ms=(time.perf_counter() - started) * 1000)
                    raise
                save(report, args.output)
                print(json.dumps({"case": case["name"], "rotation": rotation,
                                  "correct": measurement["correct"], "elapsed_ms": round(elapsed)}), flush=True)
            report["status"] = "completed"
    except Exception as error:
        # Do not persist CLI stderr. It can contain private account or authentication details.
        report.update(status="failed", error_type=type(error).__name__, error="Subscription CLI request failed")
        print(f"{type(error).__name__}: {error}", flush=True)
    save(report, args.output)
    print(json.dumps({k: v for k, v in report.items() if k not in {"measurements", "notes"}}, indent=2))
    return int(report["status"] != "completed")


if __name__ == "__main__":
    raise SystemExit(main())
