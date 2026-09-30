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
