# Progress — 2026-09-30

## Baseline

Read current main at `0fa6930be64db5702bbdbe012f3711b8cceadaab`, README and notebook before editing. No prior progress file existed. Preserved current setup, project storage, audio path and reference handling.

## Changes

- Correct base LTX guidance from selectable 1.0/3.0 to 5.0. Remove misleading Fast draft model mode; 8/16-step settings remain explicitly low-quality previews.
- Default to 24 steps and add a 50-step quality experiment. This may increase processing time; neither setting has been visually benchmarked here.
- Select BF16 on CUDA hardware supporting it, otherwise FP16. CPU remains experimental BF16.
- Offer 5, 8 or 10 seconds of motion, save the choice in project memory and request records, and round frame count to LTX's 8n+1 temporal grid. Export uses the recorded frame rate.
- Add source ledger and dependency-free notebook regression checks. Clear notebook outputs before public upload.

## Validation

`python3 -m unittest discover -s tests -v`: three checks passed, covering all code cells and embedded inference-script compilation, duration/grid constraints and base-guidance regression. No model downloads, GPU inference, voice-service calls or visual-quality tests performed.

## Limits and next priorities

Free Colab GPU availability is controlled by Google. Increasing duration costs memory and time; this change does not provide extra compute. Direct GPU rendering still needs end-to-end verification. Existing output sizes remain draft quality. Long speech still holds the last frame once generated motion ends, and lip synchronization is not implemented. Next: measure actual audio before generation, plan bounded continuation shots for its full duration, validate reference preservation and CUDA generation on an available GPU, and improve checkpoint/version reproducibility. Keep public reports free of manuscript and personal media.


## Second cycle — speech-first motion planning

Read current main at 6dc283c3e3a2c2b11588d877b14fed50e26d6aeb and prior progress/source records. Added automatic voice preparation before video inference, actual FFprobe duration measurement, a saved timing plan, and prepared-audio reuse after rendering. Motion expands to a supported 5/8/10-second choice, with a 0.2-second audio tail. Lines exceeding the bounded single-shot motion capacity fail before model loading, avoiding wasted video compute. Legacy manual add-voice mode still uses frame holds. Full multi-shot speech motion and lip sync remain future work.

Validation: notebook/subprocess compilation and prior three regressions pass; additional real-WAV/FFprobe duration planning, invalid durations, supported boundaries, long-speech rejection and prepared-audio reuse checks pass. No external voice-service calls or model generation performed. No measured GPU speed or visual-quality improvement claimed.

## Third cycle — reproducible model and reference provenance

Read current main at `2023e84931d8a4305d41b41489f8c51cd442c812` and preserved the speech-first workflow. Each new clip now resolves the model repository once to an immutable commit, records it, and gives the same revision to all three model-loading calls. Reference snapshots record SHA-256, dimensions, byte size and original filename. The embedding-cache key includes the model revision, preventing reuse across changed upstream model snapshots.

Validation: ten dependency-free checks pass, including all notebook and subprocess-script compilation, reference checksum correctness, manifest/revision presence, cache-key revision coverage, timing boundaries and prepared-audio reuse. No model download, external voice request or GPU/video inference was performed. These provenance records improve repeatability and diagnosis but do not guarantee identical pixels across hardware or software stacks. Next: verify CUDA generation, capture runtime package/GPU manifests, and add bounded multi-shot continuation before lip-sync work.
