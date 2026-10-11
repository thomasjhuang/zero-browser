# Shared project context

- [Shared progress](PROGRESS.md) records implemented work, measured outcomes, and remaining work.
- [Project context](PROJECT.md) contains setup and operation instructions.

Commit non-private project context under `contexts/`. Keep model weights and caches excluded.
The plan below describes proposed work. Current user instructions and `AGENTS.md` take precedence over its delivery and verification instructions.

## Hackathon plan (5 hours)

Goal of the day. One end-to-end run of the Jev agent loop where every model call is local Qwen on MLX.
No TypeSafe, no OpenRouter. Demo it on the local fixture page first, Google Flights only if time allows.

Not the goal. Calibration, broad reliability, new eval methodology, KV-cache research. Cut anything that
does not move the end-to-end demo forward.

## Rules for the day

- Every task has a timebox. When it expires, ship what works and move on.
- Test against the local fixture page (`fixture.html?scenario=travel`, served by `jev_ultrafast/demo.py`
  on 127.0.0.1:8766). It needs no network and no keys. Google Flights is a stretch target.
- Keep `agent.py` and `browser.py` untouched. All local work plugs in through `model.py` function signatures.
- Automated tests and code review remain deferred under `AGENTS.md`.
- Reuse `scripts/decision_smoke.py` logic by moving it, not rewriting it.
- Deliver authorized changes through a task branch and PR under `AGENTS.md`.

## Ranked tasks

| Rank | Task | Priority | Timebox | Lane | Blocks |
|---|---|---|---|---|---|
| 1 | 00-shared-local-model | P0 | 20 min | A | 01, 02 |
| 2 | 01-local-choose-adapter | P0 | 90 min | A | 06 |
| 3 | 02-local-type-text | P0 | 60 min | B | 06 |
| 4 | 05-real-fixtures | P1 | 45 min | C | 03 |
| 5 | 06-end-to-end-fixture-run | P0 | 60 min | A (all join) | demo |
| 6 | 03-label-scaling-eval | P1 | 45 min | C | informs 01 |
| 7 | 04-scorer-latency | P2 | 45 min | B | nothing |
| 8 | 07-google-flights-stretch | P2 | 45 min | whoever is free | nothing |
| 9 | 10-trim-jev-scaffolding | P0 phase 1 at 0:00, phase 2 at the end | 40 + 15 min | D | phase 2 waits on 01, 02 |
| 10 | 08-hygiene-and-readme | P3 | 20 min | anyone | nothing |
| 11 | 09-fix-filter-miss | P3 | 20 min | anyone | nothing |

## Lanes (four parallel workers)

```
Lane A  00 shared model (20m) -> 01 adapter (90m) -> 06 end-to-end (60m) -> 07 flights stretch
Lane B  02 local text (60m)   -> 04 latency (45m)  -> join 06
Lane C  05 real fixtures (45m) -> 03 label eval (45m) -> 09 filter miss -> 08 hygiene -> join 06
Lane D  10 trim phase 1 (40m) -> help 05 or 03 -> 10 trim phase 2 (15m, after 01 and 02 merge)
```

File ownership during the parallel window, to avoid merge pain.
Lane A owns `local_model.py` scoring and `model.choose()`. Lane B owns `local_field_text` and
`model.field_text()`. Lane C owns `fixtures/` and `scripts/capture_observation.py`. Lane D owns deletions,
`scripts/serve_fixture.py`, `AGENTS.md`, `upstream-lock.json`, `pyproject.toml`. Nobody edits `agent.py`,
`browser.py`, or `snapshot.js`.

Dependencies. 00 is a 20 minute prerequisite for 01 and 02 and should be done first by Lane A while
B and C read code. 05 feeds 01 with real candidate counts, so Lane C shares findings in the first hour.
Everything else is independent.

## Timeline

```
0:00  Lane A does 00. Lane D starts 10 phase 1. Lanes B and C read model.py, agent.py, decision_smoke.py.
0:40  10 phase 1 done. Fixture served by scripts/serve_fixture.py. Lane D helps C.
0:20  01, 02, 05 start in parallel.
1:05  05 done. Lane C reports real candidate counts to Lane A, starts 03.
1:20  02 done. Lane B starts 04 only if 01 reports latency is a problem, else helps 01.
1:50  01 done. Lane D runs 10 phase 2 (hosted paths removed). Everyone else joins 06.
2:50  End-to-end on fixture.html works or is being debugged. Hard stop on new features.
3:30  Decide on 07. Only attempt if fixture run is clean.
4:15  08 README update with real numbers. Record demo.
5:00  Done.
```

## Cut lines

If behind at 2:50, drop 04, 07, 09. If behind at 3:30, drop Google Flights entirely and demo the fixture.
If 02 is not working by 2:00, allow TYPE_TEXT to fall back to an env-provided literal for the demo and say so.

## Definition of done

- `TYPESAFE_API_KEY` and `TEXT_MODEL_API_KEY` unset. `scripts/smoke.py` (or a local variant) completes the
  travel fixture goal with status `done` and the final page shows Casa Flora.
- `results/local-e2e.json` records steps, per-decision latency, and text helper latency.
- README has one short section with the real numbers. No claims beyond what the JSON shows.
