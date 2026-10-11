# 11 Install and CLI

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

In progress. No installation or browser outcome claim yet.
