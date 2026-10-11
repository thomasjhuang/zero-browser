# zero-browser

Run browser goals with local Qwen on an Apple Silicon Mac with Metal.
This is a prototype. Live browser reliability and resource use remain unverified.

With Git installed, run:

```bash
git clone https://github.com/thomasjhuang/zero-browser.git
cd zero-browser
bash install.sh
```

If `uv` is absent, the installer installs it. It installs locked Python dependencies and downloads the pinned
[Qwen3-4B 4-bit model](https://huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-4bit).
The model download is about 2.3 GB. The installer reuses cached weights and preserves repository locks.
If Chrome is absent, it downloads Chrome for Testing. Setup tests the model, Metal, and the browser connection.

Give the CLI one goal and a starting page with `--url`.

Each run uses local model calls and an isolated Chrome profile. It needs no API keys.
If you omit the goal, the CLI asks for it.
Use `./zero-browser --doctor` to test setup. Use `bash install.sh --offline` after the required downloads finish.

The local fixture is a fake hotel page. Casa Flora is one of its sample hotels:

```bash
./zero-browser --fixture --expect-url '#casa-flora' --expect-text 'Casa Flora' "Open Casa Flora."
```

The CLI stops on recognizable human-verification text and three consecutive decisions without execution.
A separate worker enforces a deadline and monitors its memory footprint. The CLI permits one run at a time.
Prompt and cache limits reduce inference work. These safeguards do not establish live speed or prevent every system freeze.
[Safety evidence](results/cli-runtime-safety.json) records model-free tests and a local challenge stop.
Bounded local inference now has [measured results](results/milestone-local-runs.json). The multi-step tasks still fail.

The [flight milestone](contexts/16-flight-milestone.md) defines fixed goals and separate outcome tests.
Its [preparation evidence](results/milestone-preparation.json) covers model-free stops and scripted local browser checks.
The pilot showed a visible page, a responsive computer, and clean browser closure, according to the user.
The normal and reversed local tasks failed their outcome tests. The crowded task reached its external deadline.
The user also reported normal responsiveness and clean closure during cancellation. No live flight-search success is established.

The CLI reads the final page independently. Supplied expectations determine `outcome_verified`.
Without expectations, a DONE choice remains unverified. Failed expectations return a nonzero exit code.

[Installation evidence](results/install-cli-verification.json) includes the completed fixture goal and failed multi-step attempts.
Those failures prevent a claim of general browser reliability. Windows, Linux, and Intel Macs are unsupported.

Browser components come from [Jev Ultrafast](https://github.com/browser-use/jev-ultrafast).
See `LICENSE.jev-ultrafast` for attribution.
