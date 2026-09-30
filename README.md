# Book Video Studio

[Open in Colab](https://colab.research.google.com/github/mhenbeetsehuk-dot/book-video-studio/blob/main/Book_Video_Studio_Colab.ipynb)

Prompt and reference image to short video drafts, with saved project memory, character voices, narration and sound effects.

## Return when a GPU is available

1. Open `Book_Video_Studio_Colab.ipynb` in Google Colab (File → Open notebook → GitHub, then paste this repository URL).
2. Choose Runtime → Change runtime type → GPU.
3. Run the notebook code cells in order: lightweight setup, direct engine setup, studio interface.
4. Choose **Direct Colab GPU**, upload a reference image, enter character descriptions and the scene prompt.
5. Enter speech as `PILOT: Landing sequence started.` or `NARRATOR: The ship approaches the planet.` Preview the voice, select sounds, and enable automatic speech before generating.

Your existing Drive project reloads from `the Drive project folder configured in the notebook`. GitHub stores the program; Drive stores project memory, references and generated media. Back up the project with the notebook's Export project backup button.

## Features

- Direct Colab GPU generation, with an explicit experimental CPU option.
- Text prompts, image references, character/location/style memory and fixed seeds.
- Immutable model-revision records and SHA-256 reference-image manifests (dimensions, byte size and original filename) in every new clip request.
- Selectable 5, 8 or 10 seconds of generated motion at 8 fps; longer clips require more memory and time.
- Base-checkpoint guidance corrected to 5.0; default 24 steps, with 8/16-step previews and a 50-step option. GPU uses BF16 when supported, otherwise FP16.
- Separate saved neural voices for characters and narrator; real human recording uploads.
- Procedural engine hum, drill, radio static and alert beeps.
- Automatic speech duration measured before video inference; motion expands within the 5/8/10-second choices and reuses that prepared voice. Longer speech stops before video inference and needs multiple shots.
- Speech merging and assembly preserving audio.
- Logs and saved per-clip requests.

## Current limitations

Hosted Hugging Face Spaces inference and ZeroGPU requests have been removed. Public LTX model files and Hugging Face Python libraries are still downloaded; this is not a completely Hugging Face-free software stack.

Colab GPU access is required for practical generation and is not guaranteed by this program. CPU inference is experimental, can take hours and can exceed RAM. At least 20 GB free disk and 10 GB available RAM are checked before inference. Direct inference has not yet been verified end to end on a GPU in this project. Code syntax and procedural audio synthesis have been checked; the earlier hosted workflow produced a 5.1-second silent test, which does not validate the direct engine.

Output defaults are low-resolution drafts, not HD. Generated voices are synthetic, despite human-like sound; preview them or upload actual recordings. The speech service needs internet and may fail. Sound effects are synthesized approximations. Automatic speech now plans a bounded motion duration before inference; speech beyond the single-shot limit is rejected with a multi-shot instruction. Manually adding long speech to an existing clip still extends its last frame. Exact lip synchronization is not implemented. Character memory and reference images do not guarantee identical appearances.

New generations resolve the model repository's current `main` revision once, record its immutable commit hash, and pass that same revision to all model loaders. Reference snapshots are checksummed after copying. This improves auditability and cache correctness; it does not make diffusion output perfectly deterministic across different hardware or library builds.

## Sources and dependencies

- LTX-Video: https://github.com/Lightricks/LTX-Video
- Diffusers LTX documentation: https://huggingface.co/docs/diffusers/v0.36.0/en/api/pipelines/ltx_video
- edge-tts: https://github.com/rany2/edge-tts
- FFmpeg: https://ffmpeg.org/

Review model, service, dependency and recording rights before commercial distribution. No model weights, manuscript, recordings, tokens or generated media are included in this repository.


## Development evidence

See [PROGRESS.md](PROGRESS.md) for checks, unverified paths and next priorities, and [SOURCES.md](SOURCES.md) for the research ledger.

