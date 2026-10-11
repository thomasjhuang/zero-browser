# 08 Hygiene and README

Priority P3. Timebox 20 min. Anyone, mostly at the end. First five minutes can happen at 0:00.

## At 0:00 (5 min)

1. `git add -A && git commit -m "Import Jev scaffolding and local scorer milestone"` so there is a baseline
   to diff against. Do not push.
2. Confirm `contexts/` is ignored. `git status` should not list it.

## At 4:15 (15 min)

1. README. Add a "Local end-to-end" section. Commands to run `scripts/local_smoke.py`, the pass count from
   06, per-step latency, text helper latency. Numbers come from `results/local-e2e.json` only.
2. Update the "Browser scaffolding" paragraph. The adapter now exists. Say TYPE_TEXT is local too.
3. `AGENTS.md`. Replace the TypeSafe sentence with the local dispatch rule, `JEV_LOCAL=1` or missing keys.
4. `pyproject.toml`. Rename project to `zero-browser` only if nothing imports the dist name. Otherwise skip.
5. Final commit. Not pushed.

## Don't

- Don't claim anything the JSON does not show. Don't rewrite the measurement section.
