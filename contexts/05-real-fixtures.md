# 05 Real fixtures

Priority P1. Timebox 45 min. Lane C first. Feeds 01 and 03.

## Why

The synthetic observations are three lines long. The adapter needs to be tested on what `Browser.observe()`
actually returns, with real candidate counts and labels, before 06 tries the live loop. Needs Chrome and
browser-harness. No API keys.

## Do

1. Start the demo server, `uv run jev` or `python -m jev_ultrafast.demo`. It serves `fixture.html`.
2. Write `scripts/capture_observation.py`. Opens `Browser(url)`, calls `observe(screenshot=False)`,
   drops `node` references into plain ints if needed, writes JSON to `fixtures/observations/<name>.json`.
3. Capture the travel fixture at three states. Landing page, after typing Lisbon, results list with filters
   visible. Drive the intermediate states by hand in the owned tab or by calling `browser.act` with a
   hardcoded action in the script (this script is allowed to hardcode, the policy is not).
4. Report to Lane A. Number of elements, number of CLICK targets, number of TYPE_TEXT targets, length of
   `page["text"]`. Paste the numbers at the top of this file.
5. If time remains, capture the Google Flights landing page once. That tells us the real candidate count
   for 07.

## Verify

- `python -c "import json; json.load(open('fixtures/observations/travel-landing.json'))"` works.
- `action_space(obs["actions"])` runs on the captured JSON without error.

## Don't

- Don't record video or screenshots. Don't run the agent loop. Observation only.
