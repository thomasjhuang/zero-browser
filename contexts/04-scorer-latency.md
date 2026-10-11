# 04 Scorer latency

Current status: Absorbed into task 13. Do not start this historical plan.

Priority P2. Timebox 45 min. Lane B after 02. Only start if 01 reports per-step latency above ~1.5s.

## Why

The adapter does two full prefills per step (operation, then target). The system prompt, rules, goal, and
observation are identical between the two. A prefix cache removes most of the second prefill.

## Do

1. In `score_decision`, accept an optional prompt cache from `mlx_lm.models.cache.make_prompt_cache`.
2. Prefill the shared prefix once per step (system + user header + observation), then score each
   candidate menu suffix from a copy of the cache. mlx-lm exposes cache state through the model call
   `model(inputs, cache=cache)`. Copying a cache is a list of per-layer state copies.
3. Measure before and after on the travel fixture observation. Record both numbers in this file.
4. If cache copying is awkward in the installed mlx-lm version, stop at 30 minutes and instead shrink
   the observation text (cap page text at 1500 chars). Cheaper and probably enough.

## Verify

- Decision picks are identical with and without the cache on the synthetic fixtures.
- Latency numbers written here and in `results/local-latency.json`.

## Don't

- Don't batch across steps or across candidates. Don't touch generation in 02.

## Status 12:50 PT

Cut or superseded. See README ranking. 03/05/06/07 are replaced by the live bench loop in 12. 04 is absorbed into 13. 11 keeps run_cli.py and drops the installer.
