# 11 Install and CLI

Current status: Implemented, including the installer. The old cut note below is historical. Reliability follows task 16.

Priority P1. Timebox 60 minutes. Owner Codex.

## Why

New users need one setup command and a CLI that accepts one browser goal.
The existing model downloader pins Qwen. The inherited browser runner needs hosted services.

## Do

1. Add a Bash installer for Apple Silicon Macs with Metal.
2. Install locked dependencies and download the pinned Qwen revision without changing the repository locks.
3. Provide a CLI for one goal and an initial URL.
4. Use the shared model for local operation selection, target selection, and field text.
5. Start an isolated Chrome profile and preserve the existing executor and agent loop.
6. Add a setup diagnostic and report model completion separately from outcome evidence.

## Verify

Run the required lint and tests. Exercise repeated setup with cached packages and weights.
Run a local fixture goal through the CLI. Read the final page independently.
Record evidence in `results/install-cli-verification.json`.

## Do not

Do not change shared model loading, browser execution, or the separate single-task pilot.
Do not publish model weights, private traces, or machine paths.
Do not claim support for Linux, Windows, or Intel Macs.

## Result

The installer and local CLI are implemented. Setup passed in a fresh Python environment and on repeated offline runs.
Automatic uv installation and Chrome download passed. The model and dependency locks stayed unchanged.
Local field-text generation returned Lisbon and reused the shared model instance.
The CLI completed the simple fixture goal. Multi-step destination and filter goals failed.
Evidence: `results/install-cli-verification.json`. Required lint and all 64 tests passed.

The CLI adapter overlaps tasks 01 and 02. Those tasks remain open for integration and reliability work.
Task 10 can remove the inherited hosted paths after it reconciles this adapter.
Task 06 must resolve and independently test the full fixture goal.
The 16 GB memory target and other machines remain untested.

## Status 12:50 PT

Cut or superseded. See README ranking. 03/05/06/07 are replaced by the live bench loop in 12. 04 is absorbed into 13. 11 keeps run_cli.py and drops the installer.

Shell retest 2026-10-11 12:44 PT: `bash install.sh` and the CLI fixture goal passed with exit code 0.
The final page met both supplied assertions. This run reused cached weights.
See the `shell_retest` record in the evidence file.
