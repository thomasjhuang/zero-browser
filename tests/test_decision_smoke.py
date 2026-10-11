"""Test label guards without loading MLX or contacting a model provider."""

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SPEC = importlib.util.spec_from_file_location(
    "decision_smoke", Path(__file__).resolve().parents[1] / "scripts/decision_smoke.py",
)
smoke = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(smoke)


class Tokenizer:
    def apply_chat_template(self, messages, **kwargs):
        return messages[0]["content"] + messages[1]["content"] + "\nassistant\n"

    def encode(self, text, **kwargs):
        return [ord(char) for char in text]

    def decode(self, tokens):
        return "".join(chr(token) for token in tokens)


def candidates():
    return [
        {"id": "fill", "operation": "TYPE_TEXT", "target": "1", "description": "Fill the empty field"},
        {"id": "done", "operation": "DONE", "target": None, "description": "Stop"},
    ]


def test_labels_are_distinct_and_preserve_prompt_boundary():
    ids, labels, tokens = smoke.make_prompt(Tokenizer(), "Search", "[1] textbox value=empty", candidates())
    assert labels == ["A", "B"]
    assert tokens == [65, 66]
    assert ids[-1] == ord("\n")


def test_rejects_multi_token_labels():
    class SplitTokenizer(Tokenizer):
        def encode(self, text, **kwargs):
            return [65, 1] if text == "A" else super().encode(text, **kwargs)

    with pytest.raises(ValueError, match="one reversible token"):
        smoke.make_prompt(SplitTokenizer(), "Search", "Observation", candidates())


def test_rejects_labels_that_merge_with_prompt():
    class MergeTokenizer(Tokenizer):
        def encode(self, text, **kwargs):
            tokens = super().encode(text, **kwargs)
            return tokens[:-2] + [999] if text.endswith("\nA") else tokens

    with pytest.raises(ValueError, match="assistant prompt boundary"):
        smoke.make_prompt(MergeTokenizer(), "Search", "Observation", candidates())


def test_rejects_duplicate_action_ids():
    actions = candidates()
    actions[1]["id"] = actions[0]["id"]
    with pytest.raises(ValueError, match="unique"):
        smoke.make_prompt(Tokenizer(), "Search", "Observation", actions)


def test_downloader_uses_existing_revision_without_override(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "download_local_model", smoke.ROOT / "scripts/download_local_model.py",
    )
    download = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(download)
    revision = "a" * 40
    (tmp_path / "model-lock.json").write_text(json.dumps({"revision": revision}))
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    config = snapshot / "config.json"
    config.write_text(json.dumps({"quantization": {"bits": 4}}))
    (snapshot / "model.safetensors").write_bytes(b"synthetic test weights")
    requested = []

    class API:
        def model_info(self, model_id, **kwargs):
            requested.append((model_id, kwargs["revision"]))
            return SimpleNamespace(sha=revision)

    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(
        HfApi=API, hf_hub_download=lambda *args, **kwargs: str(config),
        snapshot_download=lambda *args, **kwargs: str(snapshot),
    ))
    monkeypatch.setattr(download, "ROOT", tmp_path)
    monkeypatch.setattr(download.importlib.metadata, "version", lambda name: "test-version")
    monkeypatch.setattr(download.subprocess, "check_output", lambda *args, **kwargs: "")
    monkeypatch.setattr(sys, "argv", ["download_local_model.py"])
    download.main()
    assert requested == [(download.MODEL_ID, revision)]
    assert json.loads((tmp_path / "model-lock.json").read_text())["revision"] == revision
