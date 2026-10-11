"""Test the shared model contract without local inference dependencies."""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

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


def test_prefix_cache_reuses_only_exact_tokens_and_does_not_mutate_saved_cache(monkeypatch):
    from mlx_lm.models import cache as cache_module

    monkeypatch.setattr(cache_module, "make_prompt_cache", lambda model: [SimpleNamespace(ids=[])])
    monkeypatch.setattr(cache_module, "can_trim_prompt_cache", lambda cache: True)

    def trim(cache, count):
        del cache[0].ids[-count:]
        return count

    def prefill(model, mx, ids, cache):
        cache[0].ids.extend(ids)
        return tuple(cache[0].ids)

    monkeypatch.setattr(cache_module, "trim_prompt_cache", trim)
    monkeypatch.setattr(local_model, "bounded_prefill", prefill)
    model = object()
    first, second = list(range(300)), list(range(290)) + [999]
    with local_model.decision_prefix_cache():
        assert local_model.cached_prefill(model, None, first) == (tuple(first), 0)
        saved = local_model._PREFIX_STATE.get()["cache"]
        assert local_model.cached_prefill(model, None, second) == (tuple(second), 256)
        assert saved[0].ids == first
        assert local_model.cached_prefill(object(), None, second) == (tuple(second), 0)
        with pytest.raises(ValueError):
            local_model.cached_prefill(model, None, list(range(4097)))
    assert local_model._PREFIX_STATE.get() is None
    with pytest.raises(RuntimeError), local_model.decision_prefix_cache():
        raise RuntimeError("cancel")
    assert local_model._PREFIX_STATE.get() is None
