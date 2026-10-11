"""Download only the requested 4-bit checkpoint into the normal HF shared cache."""

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MODEL_ID = "mlx-community/Qwen3-4B-Instruct-2507-4bit"
ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", help="Override the locked revision. Use main for an explicit update.")
    args = parser.parse_args()
    from huggingface_hub import HfApi, hf_hub_download, snapshot_download

    lock_path = ROOT / "model-lock.json"
    requested_revision = args.revision
    if requested_revision is None:
        requested_revision = json.loads(lock_path.read_text())["revision"] if lock_path.exists() else "main"
    revision = HfApi().model_info(MODEL_ID, revision=requested_revision).sha
    config_path = hf_hub_download(MODEL_ID, "config.json", revision=revision)
    config = json.loads(Path(config_path).read_text())
    quantization = config.get("quantization", config.get("quantization_config", {}))
    if quantization.get("bits") != 4:
        raise ValueError("Refusing to download weights: expected a 4-bit checkpoint")
    snapshot = Path(snapshot_download(
        MODEL_ID,
        revision=revision,
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
    (ROOT / "model-lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    frozen = subprocess.check_output(
        ["uv", "pip", "freeze", "--python", sys.executable, "--exclude-editable"], text=True,
    )
    (ROOT / "requirements-local.lock.txt").write_text(frozen)
    print(json.dumps(lock, indent=2))


if __name__ == "__main__":
    main()
