"""Test the shared model contract without local inference dependencies."""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

from jev_ultrafast import local_model


def test_import_does_not_require_local_dependencies():
    result = subprocess.run(
        [sys.executable, "-c", """
import sys

class BlockLocalImports:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'mlx', 'mlx_lm', 'huggingface_hub'}:
            raise ImportError('Local dependencies are unavailable')

sys.meta_path.insert(0, BlockLocalImports())
from jev_ultrafast import local_model
assert local_model._MODEL is None
"""],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr


def test_concurrent_callers_share_one_lazy_model(monkeypatch):
    instances = (object(), object(), object())
    loads = []

    def load():
        loads.append(True)
        return instances, {"model_revision": "pinned"}

    monkeypatch.setattr(local_model, "_MODEL", None)
    monkeypatch.setattr(local_model, "_MODEL_INFO", None)
    monkeypatch.setattr(local_model, "_load_model", load)
    assert not loads
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: local_model.get_model(), range(16)))
    assert all(result is instances for result in results)
    assert len(loads) == 1
    info = local_model.get_model_info()
    info["model_revision"] = "changed"
    assert local_model.get_model_info()["model_revision"] == "pinned"
    assert len(loads) == 1


def test_failed_load_does_not_cache_a_model(monkeypatch):
    def fail():
        raise FileNotFoundError("The pinned model is absent")

    monkeypatch.setattr(local_model, "_MODEL", None)
    monkeypatch.setattr(local_model, "_MODEL_INFO", None)
    monkeypatch.setattr(local_model, "_load_model", fail)
    with pytest.raises(FileNotFoundError, match="pinned model"):
        local_model.get_model()
    assert local_model._MODEL is None
    assert local_model._MODEL_INFO is None
