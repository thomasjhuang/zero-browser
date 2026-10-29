# Goal

Test whether a high-level coordinator plus a local offline model can complete fixed browser goals without hosted model calls, and whether that arm is faster than browser-use, vanilla Grok 4.7, and Grok 4.7 plus zero-browser.

Judge every run with `scripts/experiment_scoreboard.py`. A DONE choice is not success. The first goal is `local_search` in `fixtures/milestone_tasks.json`. Do not start a live flight goal before three consecutive independently passing local runs. Change one lever at a time. The hypothesis arm must record `hosted_model_calls: 0`.

Execution of the browser and the local model belongs on the desktop machine. This directory is the sealed measurement task for those records.
