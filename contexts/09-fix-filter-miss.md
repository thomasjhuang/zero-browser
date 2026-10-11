# 09 Fix the remove_restrictive_filter miss

Priority P3. Timebox 20 min. Anyone with spare time. Fully independent.

## Why

35 of 36 on the quality cases. One candidate order picks "apply sale filter" instead of "remove stock filter."
Small, isolated, and good to have fixed before anyone quotes the number.

## Do

1. Read the case in `fixtures/decision_quality_cases.json` and the rerun in
   `results/decision-quality-filter-rerun.json`. Look at the raw logits for the failing order.
2. Try exactly one of these, in order, and stop at the first that passes all four orders.
   - Add one sentence to `SYSTEM` in `local_model.py`. "Removing a filter that hides the requested items
     counts as progress."
   - Reword the candidate description in the fixture so the action reads as "Uncheck In stock only."
3. Rerun the full quality set. Make sure nothing else regressed. Write the new pass count here.

## Don't

- Don't spend time on why. Don't add more cases.
