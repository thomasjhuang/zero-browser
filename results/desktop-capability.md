# Desktop capability

Machine: Linux x86_64, NVIDIA GeForce RTX 3080 (10 GB), 32 cores, about 29 GB RAM. Chrome 155 is installed and can start headless with remote debugging. Firefox is also installed.

Codex CLI 0.162.0 is logged in with ChatGPT. Claude CLI 2.1.287 is present and reports `loggedIn: false`. No Grok login and no browser-use API credential were found, so those arms are blocked rather than run.

The pinned Qwen checkpoint is cached. MLX 0.32.4 with the CUDA 13 build can run a GPU matmul and can load that checkpoint. The repository installer and milestone runner still require Apple Silicon Metal, and the frozen lock has no Linux MLX wheel. A process-local launch adapter outside the repo was used for the local-coordinator run. That adapter is not a committed lever.

`/cursor/stores/self` is not mounted here, so this note is in the repo.
