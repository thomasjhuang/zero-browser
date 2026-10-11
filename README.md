# zero-browser

Run browser goals with local Qwen on an Apple Silicon Mac with Metal.
This is a prototype. Simple browser execution works. Longer tasks still need reliability work.

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

Give the CLI one goal:

```bash
./zero-browser --url https://www.google.com "Find the official Python downloads page for macOS."
```

Each run uses local model calls and an isolated Chrome profile. It needs no API keys.
If you omit the goal, the CLI asks for it.
Use `./zero-browser --doctor` to test setup. Use `bash install.sh --offline` after the required downloads finish.

Try the tested local fixture:

```bash
./zero-browser --fixture --expect-url '#casa-flora' --expect-text 'Casa Flora' "Open Casa Flora."
```

The CLI reads the final page independently. Supplied expectations determine `outcome_verified`.
Without expectations, a DONE choice remains unverified. Failed expectations return a nonzero exit code.

[Installation evidence](results/install-cli-verification.json) includes the completed fixture goal and failed multi-step attempts.
Those failures prevent a claim of general browser reliability. Windows, Linux, and Intel Macs are unsupported.

Browser components come from [Jev Ultrafast](https://github.com/browser-use/jev-ultrafast).
See `LICENSE.jev-ultrafast` for attribution.
