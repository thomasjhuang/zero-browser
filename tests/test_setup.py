import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_installer_download_keeps_locks_and_uses_exact_revision(tmp_path, monkeypatch):
    download = load_script("download_local_model")
    revision = "b" * 40
    lock = json.dumps({"model_id": download.MODEL_ID, "revision": revision})
    (tmp_path / "model-lock.json").write_text(lock)
    (tmp_path / "requirements-local.lock.txt").write_text("Keep these exact dependencies.\n")
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    config = snapshot / "config.json"
    config.write_text(json.dumps({"quantization": {"bits": 4}}))
    (snapshot / "model.safetensors").write_bytes(b"synthetic test weights")
    calls = []

    def snapshot_download(model_id, **kwargs):
        calls.append((model_id, kwargs))
        return str(snapshot)

    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(
        HfApi=lambda: pytest.fail("Installation must use the pinned revision"),
        hf_hub_download=lambda *a, **k: str(config), snapshot_download=snapshot_download,
    ))
    monkeypatch.setattr(download, "ROOT", tmp_path)
    monkeypatch.setattr(download.importlib.metadata, "version", lambda name: "test-version")
    monkeypatch.setattr(download.subprocess, "check_output", lambda *a, **k: pytest.fail("Locks must stay unchanged"))
    monkeypatch.setattr(sys, "argv", ["download_local_model.py", "--no-write-lock", "--offline"])
    download.main()
    assert calls[0][0] == download.MODEL_ID
    assert calls[0][1]["revision"] == revision
    assert calls[0][1]["local_files_only"] is True
    assert (tmp_path / "model-lock.json").read_text() == lock
    assert (tmp_path / "requirements-local.lock.txt").read_text() == "Keep these exact dependencies.\n"


def test_chrome_candidates_include_linux_executables():
    cli = load_script("run_cli")
    assert Path("/usr/bin/google-chrome") in cli.CHROME_CANDIDATES
    assert Path("/usr/bin/google-chrome-stable") in cli.CHROME_CANDIDATES


def test_installer_rejects_platform_before_download(tmp_path):
    command = tmp_path / "uname"
    command.write_text('#!/bin/sh\necho Linux\n')
    command.chmod(0o755)
    result = subprocess.run(["/bin/bash", str(ROOT / "install.sh")],
                            env={"PATH": f"{tmp_path}:/usr/bin:/bin"}, capture_output=True, text=True)
    assert result.returncode == 1
    assert "Apple Silicon" in result.stderr
    assert "Downloading" not in result.stdout


def test_browser_offline_failure_does_not_start_a_download(monkeypatch):
    cli = load_script("run_cli")
    monkeypatch.setattr(cli, "chrome_path", lambda: None)
    monkeypatch.setattr(cli.urllib.request, "urlopen", lambda *a, **k: pytest.fail("Network call in offline mode"))
    with pytest.raises(RuntimeError, match="network access first"):
        cli.install_browser(offline=True)


def test_cli_rejects_empty_goal_and_invalid_url_before_browser_launch(monkeypatch):
    cli = load_script("run_cli")
    monkeypatch.setattr(cli.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(cli.platform, "machine", lambda: "arm64")
    for args in ([""], ["Open a page", "--url", "file:///private/example"],
                 ["Open a page", "--max-decisions", "0"]):
        with pytest.raises(SystemExit) as error:
            cli.main(args)
        assert error.value.code == 2
