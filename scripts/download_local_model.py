"""Download only the requested 4-bit checkpoint into the normal HF shared cache."""

import argparse
import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MODEL_ID = "mlx-community/Qwen3-4B-Instruct-2507-4bit"
ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", help="Override the locked revision. Use main for an explicit update.")
    parser.add_argument("--no-write-lock", action="store_true", help="Download without changing repository locks.")
    parser.add_argument("--offline", action="store_true", help="Use only cached model files.")
    args = parser.parse_args()
    if args.no_write_lock and args.revision:
        parser.error("--revision cannot be combined with --no-write-lock")
    from huggingface_hub import HfApi, hf_hub_download, snapshot_download

    lock_path = ROOT / "model-lock.json"
    requested_revision = args.revision
    if requested_revision is None:
        existing = json.loads(lock_path.read_text()) if lock_path.exists() else {}
        requested_revision = existing.get("revision", "main")
        if args.no_write_lock and existing.get("model_id") != MODEL_ID:
            raise ValueError("Installation needs the expected Qwen model lock")
    if args.offline or args.no_write_lock:
        if not re.fullmatch(r"[0-9a-f]{40}", requested_revision):
            raise ValueError("Installation needs a pinned model revision")
        revision = requested_revision
    else:
        revision = HfApi().model_info(MODEL_ID, revision=requested_revision).sha
    config_path = hf_hub_download(MODEL_ID, "config.json", revision=revision, local_files_only=args.offline)
    config = json.loads(Path(config_path).read_text())
    quantization = config.get("quantization", config.get("quantization_config", {}))
    if quantization.get("bits") != 4:
        raise ValueError("Refusing to download weights: expected a 4-bit checkpoint")
    snapshot = Path(snapshot_download(
        MODEL_ID,
        revision=revision,
        local_files_only=args.offline,
        allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt", "tokenizer.model", "README.md"],
    ))
    weights = list(snapshot.glob("*.safetensors"))
    if not weights:
        raise ValueError("Download contains no safetensors weights")
    lock = {
        "model_id": MODEL_ID,
        "revision": revision,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "quantization": quantization,
        "weight_bytes": sum(p.stat().st_size for p in weights),
        "snapshot_bytes": sum(p.stat().st_size for p in snapshot.iterdir() if p.is_file()),
        "python": platform.python_version(),
        "dependencies": {
            name: importlib.metadata.version(name)
            for name in ("mlx", "mlx-lm", "huggingface-hub", "transformers", "tokenizers", "numpy")
        },
    }
    if not args.no_write_lock:
        (ROOT / "model-lock.json").write_text(json.dumps(lock, indent=2) + "\n")
        frozen = subprocess.check_output(
            ["uv", "pip", "freeze", "--python", sys.executable, "--exclude-editable"], text=True,
        )
        (ROOT / "requirements-local.lock.txt").write_text(frozen)
    print(json.dumps(lock, indent=2))


if __name__ == "__main__":
    main()
