# 15 CLI runtime safety

Priority P0. Owner Codex. Timebox 60 minutes.

## Why

The user reported a computer freeze, slow decisions, CAPTCHA, and delayed interruption from the CLI.
The console log does not establish the cause of the computer freeze.

## Do

- Bound inference prompts, allocator cache, and prefill work.
- Run CLI inference in an owned worker with an external deadline and bounded shutdown.
- Stop on observed human verification and repeated rejected decisions.
- Show executed actions separately from rejected decisions.
- Preserve the existing Agent and Browser pipeline. Keep hosted calls disabled.

## Verify

Use model-free tests for prompt limits, prefill order, timeout, interruption, and CAPTCHA stops.
Run the required lint and tests. Do not repeat the Google task or load Qwen during this safety repair.
Record evidence in results/cli-runtime-safety.json. Do not claim a crash cause or faster live inference.

## Do not

Do not stop unrelated processes or change the benchmark task.
Do not bypass CAPTCHA or publish private page contents.

## Result

Prompt, cache, prefill, worker deadline, memory footprint, and shutdown guards landed.
The CLI stops on recognizable human verification and three consecutive rejected decisions.
It reports executed actions separately from rejected decisions.

The model-free suite passes. A real CLI run against a local challenge page stops before loading Qwen.
Evidence: [runtime safety](../results/cli-runtime-safety.json).
Qwen correctness, live speed, and prevention of the reported freeze remain unverified.
Tasks 12 and 13 retain benchmark and latency ownership. Preserve these guards during their work.
