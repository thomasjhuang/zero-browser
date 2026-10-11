# 10 Trim Jev scaffolding

Priority P0. Two phases. Phase 1 timebox 40 min at 0:00, Lane D (separate agent). Phase 2 timebox 15 min
after 01 and 02 merge. Phase 1 must not touch files owned by 00, 01, 02.

## Why

We imported all of jev-ultrafast. We want its browser loop, not its product. The inspector UI, demo video
tooling, launch drafts, performance writeups, and the hosted-model code paths are weight we carry for no
reason, and they make the repo read as a Jev fork instead of a local agent.

## Keep (the useful part)

| File | Why |
|---|---|
| `jev_ultrafast/snapshot.js` | DOM observer. Roles, names, values, visible text, node identity via WeakMap. Hard to rewrite. |
| `jev_ultrafast/browser.py` | CDP session, freshness guards, executor, settle waits. Keep as is. |
| `jev_ultrafast/agent.py` | Loop with consume-once decisions and log-before-observe. Keep as is. |
| `jev_ultrafast/model.py` | `action_space()`, `validate_choice()`, `field_context()`. Hosted calls go in phase 2. |
| `jev_ultrafast/questions.py` | `NEXT_ACTION`, `TARGET`, `TEXT_VALUE`, `MAX_STEPS`. Prompts are reused by the local scorer. |
| `jev_ultrafast/static/fixture.html` | Local offline test page. Our only no-network target. |
| `tests/test_agent.py` | Covers everything above. Prune only tests for deleted code. |
| `examples/flights.py` | `verify()` is the independent check for 07. Keep. |
| `scripts/check_guards.py` | Exercises freshness guards against the fixture. Cheap to keep. |
| `LICENSE.jev-ultrafast`, `upstream-lock.json` | Attribution. Update the lock's retained-hash list to match. |
| `docs/design.md` | Shortest accurate description of the loop. Keep, trim the "what changed after the first demo" section. |

## Delete (phase 1, now)

- `jev_ultrafast/demo.py`, `jev_ultrafast/static/index.html`, `static/app.js`, `static/style.css`.
  The inspector UI and its token-checked HTTP server. We will not use it today.
- `scripts/render_demo.py`, `scripts/render_fixture.py`, `scripts/record_flights.py`,
  `scripts/measure_flights.py`. Demo video and measurement tooling for Jev's launch.
- `scripts/smoke.py`. Imports `demo.load_environment`. 06 writes `scripts/local_smoke.py` fresh.
- `docs/launch-draft.md`, `docs/performance.md`, `docs/performance-prepared.md`, `docs/banner.svg`,
  `docs/*-measurement.json`, `docs/full-speed-measurement.json`. Jev's marketing and benchmarks.
- `docs/upstream/` (the README and gitignore copies). The lock file and license already record provenance.
- `examples/run.py`. Three lines, replaced by `local_smoke.py`.
- `.env.example`. Nothing local needs env keys. Phase 2 confirms.
- `[project.scripts] jev = ...` entry in `pyproject.toml`. It points at the deleted demo.
- `pillow` from the dev dependency group. Only the render scripts used it.
- `node --check jev_ultrafast/static/app.js` from README and AGENTS.md check lists.

## Replace (phase 1)

1. `scripts/serve_fixture.py`. Fifteen lines. `http.server` on 127.0.0.1:8766 serving
   `jev_ultrafast/static/`. No token, loopback only. Check whether `fixture.html` reads `__TOKEN__` or
   `scenario` from the query. If it needs the token substitution, serve a copy with `__TOKEN__` replaced
   by an empty string.
2. `AGENTS.md`. Update the applicable implementation rules. Preserve the context entry points,
   shared-context policy, weight and cache exclusions, and current verification and delivery rules.
3. `upstream-lock.json`. Remove hashes for deleted files, keep the revision and the omitted-media note.

## Phase 2 (after 01 and 02 merge, 15 min)

1. `model.py`. Delete `post_json`, the `CLIENT`, the TypeSafe body builder in `choose()`, and the hosted
   branch of `field_text()`. `choose()` and `field_text()` become thin wrappers over `local_model`.
   `JEV_LOCAL` env flag goes away since local is the only path.
2. `tests/test_agent.py`. Tests that monkeypatch `post_json` move to monkeypatching the local scorer.
   Most of them check dict shape and gating, so the change is mechanical.
3. Drop `httpx` from dependencies if nothing else imports it.
4. `README.md`. Remove the "Jev's inherited policy still requires hosted services" paragraph.

## Verify

The current `AGENTS.md` takes precedence. Automated test and lint steps below are deferred.

- Phase 1. `uv run pytest` and `ruff check .` pass. `python scripts/serve_fixture.py` then open
  `http://127.0.0.1:8766/fixture.html?scenario=travel` in Chrome and the travel page renders with search,
  category select, and the free cancellation checkbox.
- Phase 2. Same, plus `grep -rn "typesafe\|openrouter\|deepseek" jev_ultrafast/` returns nothing.
- Inspect the diff for changes outside the assigned files. Keep non-private context tracked.

## Don't

- Don't rename the `jev_ultrafast` package today. Every import and test references it. Rename is a
  follow-up after the hackathon.
- Don't edit `agent.py`, `browser.py`, `snapshot.js`. Those are the whole reason we imported Jev.
- Don't touch `model.py` or `questions.py` in phase 1. Lanes A and B are in them.
- Follow `AGENTS.md` for task branch and PR delivery.
