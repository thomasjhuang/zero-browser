"""Replay recorded decision menus offline against any cached Qwen3 checkpoint. One model per process.

Sources: --records results/replay/*.jsonl (written by ZB_RECORD_PATH during a live or smoke run) and/or
--cases fixtures/*.json (synthetic cases with expected_action). Variants: plain (the repo's bounded prefill)
and prefix (menus in one decision group share one prefilled KV prefix; each menu scores only its suffix).
Reports latency, agreement with the recorded 4B pick, and accuracy against expected actions where known.
"""

import argparse
import copy
import json
import os
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_MODEL = "mlx-community/Qwen3-4B-Instruct-2507-4bit"
ALLOWED = {
    DEFAULT_MODEL,
    "mlx-community/Qwen3-1.7B-4bit",
    "mlx-community/Qwen3-0.6B-4bit",
}


def load_rows(args):
    rows = []
    for path in args.records:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                row.setdefault("expected_action", None)
                row["source"] = Path(path).name
                rows.append(row)
    for path in args.cases:
        for case in json.loads(Path(path).read_text()):
            rows.append({
                "group": f"case:{case['name']}", "goal": case["goal"], "observation": case["observation"],
                "candidates": case["candidates"], "selected_label": None, "scores": None,
                "expected_action": case["expected_action"], "source": Path(path).name,
            })
    if args.limit:
        rows = rows[:args.limit]
    return rows


def load(model_id, allow_download):
    os.environ.setdefault("HF_HUB_OFFLINE", "0" if allow_download else "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "0" if allow_download else "1")
    import mlx.core as mx
    from huggingface_hub import snapshot_download
    from mlx_lm import load as mlx_load

    mx.set_default_device(mx.gpu)
    mx.set_memory_limit(min(6 * 2**30, mx.device_info()["memory_size"] // 3))
    mx.set_cache_limit(256 * 2**20)
    revision = None
    if model_id == DEFAULT_MODEL:  # the repo downloader pins this revision and may not store a main ref
        revision = json.loads((ROOT / "model-lock.json").read_text())["revision"]
    snapshot = snapshot_download(
        model_id, revision=revision, local_files_only=not allow_download,
        allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt", "tokenizer.model"],
    )
    started = time.perf_counter()
    model, tokenizer = mlx_load(snapshot, lazy=False)
    mx.synchronize()
    return model, tokenizer, mx, (time.perf_counter() - started) * 1000


def common_prefix_len(sequences):
    n = min(len(s) for s in sequences)
    for i in range(n):
        first = sequences[0][i]
        if any(s[i] != first for s in sequences[1:]):
            return i
    return n


def finish(mx, model, logits, label_ids, candidates):
    indices = mx.array(label_ids)
    scores = mx.softmax(logits.astype(mx.float32)[indices])
    mx.eval(scores)
    mx.synchronize()
    numbers = scores.tolist()
    selected = max(range(len(numbers)), key=numbers.__getitem__)
    return selected, numbers


def score_plain(ctx, prepared):
    from mlx_lm.models.cache import make_prompt_cache

    from jev_ultrafast.local_model import bounded_prefill

    model, mx = ctx["model"], ctx["mx"]
    out = []
    for row, (prompt_ids, labels, label_ids) in prepared:
        mx.synchronize()
        started = time.perf_counter()
        logits = bounded_prefill(model, mx, prompt_ids, make_prompt_cache(model))
        selected, numbers = finish(mx, model, logits, label_ids, row["candidates"])
        out.append((row, labels[selected], numbers, (time.perf_counter() - started) * 1000, len(prompt_ids), 0))
    return out


def score_prefix(ctx, prepared):
    """Share one KV prefix per decision group; score each menu's suffix from a copy."""
    from mlx_lm.models.cache import make_prompt_cache

    from jev_ultrafast.local_model import bounded_prefill

    model, mx = ctx["model"], ctx["mx"]
    groups = {}
    for item in prepared:
        groups.setdefault(item[0]["group"], []).append(item)
    out = []
    for members in groups.values():
        ids = [p[0] for _, p in members]
        shared = common_prefix_len(ids) if len(members) > 1 else 0
        shared = max(0, min(shared, min(len(s) for s in ids) - 1))
        mx.synchronize()
        started = time.perf_counter()
        base = make_prompt_cache(model)
        for offset in range(0, shared, 256):  # prefill exactly the shared prefix, in bounded chunks
            model(mx.array([ids[0][offset:min(offset + 256, shared)]]), cache=base)
            mx.eval([c.state for c in base])
        prefix_ms = (time.perf_counter() - started) * 1000
        for index, (row, (prompt_ids, labels, label_ids)) in enumerate(members):
            mx.synchronize()
            t0 = time.perf_counter()
            cache = copy.deepcopy(base) if shared else make_prompt_cache(model)
            suffix = prompt_ids[shared:]
            logits = bounded_prefill(model, mx, suffix, cache)
            selected, numbers = finish(mx, model, logits, label_ids, row["candidates"])
            ms = (time.perf_counter() - t0) * 1000 + (prefix_ms if index == 0 else 0)
            out.append((row, labels[selected], numbers, ms, len(prompt_ids), len(suffix)))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=sorted(ALLOWED))
    parser.add_argument("--records", action="append", default=[])
    parser.add_argument("--cases", action="append", default=[])
    parser.add_argument("--variant", choices=["plain", "prefix"], default="plain")
    parser.add_argument("--repeats", type=int, default=1, help="Timed repeats per menu (median reported)")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = load_rows(args)
    if not rows:
        parser.error("No records or cases supplied")
    from jev_ultrafast.local_model import make_prompt

    model, tokenizer, mx, load_ms = load(args.model, args.allow_download)
    ctx = {"model": model, "mx": mx}
    prepared = [(row, make_prompt(tokenizer, row["goal"], row["observation"], row["candidates"])) for row in rows]
    scorer = score_prefix if args.variant == "prefix" else score_plain
    scorer(ctx, prepared[:2])  # warm kernels once, untimed
    runs = [scorer(ctx, prepared) for _ in range(args.repeats)]
    results = []
    for i, row in enumerate(rows):
        picks = [run[i][1] for run in runs]
        ms = statistics.median(run[i][3] for run in runs)
        label = picks[0]
        chosen = row["candidates"]["ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(label)]["id"]
        results.append({
            "source": row["source"], "group": row["group"], "prompt_tokens": runs[0][i][4],
            "suffix_tokens": runs[0][i][5], "latency_ms": ms, "selected_label": label, "selected_action": chosen,
            "agrees_with_recorded": (label == row["selected_label"]) if row["selected_label"] else None,
            "correct": (chosen == row["expected_action"]) if row["expected_action"] else None,
            "scores": dict(zip([c["id"] for c in row["candidates"]], runs[0][i][2])),
            "stable_across_repeats": len(set(picks)) == 1,
        })
    agree = [r["agrees_with_recorded"] for r in results if r["agrees_with_recorded"] is not None]
    correct = [r["correct"] for r in results if r["correct"] is not None]
    latencies = [r["latency_ms"] for r in results]
    groups = {}
    for r in results:
        groups.setdefault(r["group"], 0)
        groups[r["group"]] += r["latency_ms"]
    summary = {
        "model": args.model, "variant": args.variant, "menus": len(results), "decision_groups": len(groups),
        "model_load_ms": load_ms, "repeats": args.repeats,
        "latency_ms_median": statistics.median(latencies),
        "latency_ms_p90": sorted(latencies)[int(0.9 * (len(latencies) - 1))],
        "latency_ms_total": sum(latencies),
        "decision_ms_median": statistics.median(groups.values()) if groups else None,
        "prompt_tokens_median": statistics.median(r["prompt_tokens"] for r in results),
        "agreement_with_recorded": (sum(agree), len(agree)) if agree else None,
        "accuracy_vs_expected": (sum(correct), len(correct)) if correct else None,
        "peak_mlx_bytes": mx.get_peak_memory(), "hardware": mx.device_info()["device_name"],
        "notes": [
            "Latency excludes tokenization. The prefix variant counts the shared prefill once per decision group.",
            "Agreement compares against the label recorded during the original run, which may itself have been wrong.",
            "Synthetic cases do not establish browser-task reliability.",
        ],
    }
    print(json.dumps(summary, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"summary": summary, "results": results}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
