# Generation prompts, settings, and source snapshots

`configurations.json` records the inference settings of the 13 model configurations and 14 reporting views. It preserves model identifiers, reasoning effort, sampling parameters, output allowances, call limits, software versions, prompt-placement differences, and local weight-manifest hashes. Settings variants retain the item IDs to which they applied. The settings come from the input-correction manifest, whose SHA-256 is recorded in the file; correction and recovery calls used the same inference settings.

The `EXP1`, `EXP2`, `EXP4`, and `EXP5` directories preserve the corresponding frozen driver source and its local helper modules. Each contains the exact `prompt_system.txt` and `prompt_user_template.txt`. `common.py` contains `build_prompt`, which inserts the numbered problem lines and proof text into the template. The parent directory's `reproduce.py` is the self-contained entrypoint for checking the published results.

These generation sources document the original execution environments:

- Claude configurations use the `run_critic.py` CLI driver, medium effort, a 16,000-output-token allowance, a 120,000-token call limit, and a 600-second wall limit.
- Local configurations use `run_local.py`, vLLM 0.29.0, the native model templates, and the per-model sampling and context settings in the source and JSON. Model weights are external dependencies identified by their saved manifest hashes.
- Gemini uses `EXP4/run_agy.py`, Antigravity CLI 1.2.8, low effort, and the benchmark system instruction at the head of the user turn.
- GPT-5.6 Luna uses `EXP4/run_codex.py`, Codex CLI 0.155.1, medium effort, and the isolated text-only transport supplied in `cli_transport/transport.py`. The driver overrides that shared helper's default model, effort, and CLI version. Its output allowance was checked from native usage after completion.

`SOURCE_MANIFEST.json` binds each source snapshot to its original and distributed hashes. Workstation paths are replaced by explicit `<repository>`, `<workspace>`, `<user-home>`, and `<scratch-workdirs>` placeholders; coordination references are anonymized. These locations must be configured when adapting a driver to a new machine. The original campaign's activation ledgers, installed CLI binaries, model weights, and private account files are external dependencies of new generation. The snapshots are provided for inspecting and adapting the generation method; the saved-answer scoring command uses none of those services or files.
