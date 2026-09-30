# Source ledger

Reviewed 2026-09-30. Two targeted primary documents reviewed in this cycle; existing README dependencies retained. Revisit documents only for changed behaviour or unanswered questions.

| Source | Finding | Decision | Verification limit |
| --- | --- | --- | --- |
| [Diffusers 0.36.0 LTX documentation](https://huggingface.co/docs/diffusers/v0.36.0/en/api/pipelines/ltx_video) | Guidance 1.0 is for guidance-distilled variants; other models need higher guidance, with 5.0 suggested. BF16 is recommended; generation parameters depend on checkpoint. | Base checkpoint uses guidance 5.0 and 24 default steps; expose 50 steps. Select BF16 on supporting CUDA hardware, FP16 otherwise. Avoid claiming low-step previews are distilled. | No GPU output benchmark performed. 24 steps is a draft tradeoff, not the documented 50-step example or a proven quality optimum. |
| [Google Colab FAQ](https://research.google.com/colaboratory/faq.html) | Free resources and accelerator types are not guaranteed; limits and availability vary. | Retain explicit GPU checks and experimental CPU choice. No quota bypass, paid fallback or guaranteed free GPU claim. | Cannot allocate a Colab GPU from this development environment. |

Next research: LTX reference conditioning and continuation, bounded speech-length motion, Kaggle official compute policy, voice-service usage and model rights. Novel panel image generation is a separate planned workflow; it is not implemented by these video changes.

## Reproducibility and continuity review — 2026-09-30

- https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download — official Hub documentation says a revision can be resolved to a commit hash and then reused to pin downloads. Implemented one revision resolution per clip and passed it to tokenizer, text encoder and video pipeline loaders.
- https://huggingface.co/docs/diffusers/api/models/overview — official Diffusers API documents `revision` as a branch, tag or commit identifier for `from_pretrained`. Recorded the resolved revision in `request.json` and included it in the embedding-cache fingerprint.

Reference snapshots now carry a SHA-256 checksum, dimensions, byte size and original filename. This is local provenance metadata, not a claim of identity consistency or cross-hardware determinism. No weights were downloaded and no GPU generation was run in this review.


## Speech timing review — 2026-09-30

- https://ffmpeg.org/ffprobe.html — Query actual media duration through show_entries, rather than estimating speech from word count. Implemented preflight measurement for recorded/synthesized audio. Duration planning tested with actual WAV files.
- https://ffmpeg.org/ffmpeg-filters.html#tpad — stop_mode=clone repeats the last frame; it does not create new motion. Keep legacy manual voice merging honest; automatic speech now plans enough motion within the bounded single-shot limit, or refuses before video inference. No multi-shot continuation or lip sync claim.

## Runtime evidence review — 2026-09-30

- https://docs.pytorch.org/docs/stable/generated/torch.cuda.get_device_properties.html — PyTorch exposes CUDA device properties for the active runtime. The diagnostic records device name, compute capability and total memory only when CUDA is available.
- https://docs.python.org/3/library/importlib.metadata.html — Python's standard library exposes installed distribution versions. The diagnostic queries a fixed allow-list of video dependencies rather than dumping the full environment.

The manifest deliberately excludes environment variables, prompts, references, audio, manuscript content and tokens. It was validated with a simulated CUDA device and the current CPU runtime; it does not prove GPU inference works.

## 2026-09-30 — output integrity follow-up

Revisited [official FFprobe documentation](https://ffmpeg.org/ffprobe.html) specifically for `-count_frames`, `-select_streams`, `-show_entries` and JSON output, rather than repeating the earlier audio-duration research. Applied these to a standalone local video diagnostic. Decoded frame count, stream duration and file hash provide output evidence; they do not establish visual realism or lip synchronization.
