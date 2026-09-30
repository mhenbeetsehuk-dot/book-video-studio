# Source ledger

Reviewed 2026-09-30. Two targeted primary documents reviewed in this cycle; existing README dependencies retained. Revisit documents only for changed behaviour or unanswered questions.

| Source | Finding | Decision | Verification limit |
| --- | --- | --- | --- |
| [Diffusers 0.36.0 LTX documentation](https://huggingface.co/docs/diffusers/v0.36.0/en/api/pipelines/ltx_video) | Guidance 1.0 is for guidance-distilled variants; other models need higher guidance, with 5.0 suggested. BF16 is recommended; generation parameters depend on checkpoint. | Base checkpoint uses guidance 5.0 and 24 default steps; expose 50 steps. Select BF16 on supporting CUDA hardware, FP16 otherwise. Avoid claiming low-step previews are distilled. | No GPU output benchmark performed. 24 steps is a draft tradeoff, not the documented 50-step example or a proven quality optimum. |
| [Google Colab FAQ](https://research.google.com/colaboratory/faq.html) | Free resources and accelerator types are not guaranteed; limits and availability vary. | Retain explicit GPU checks and experimental CPU choice. No quota bypass, paid fallback or guaranteed free GPU claim. | Cannot allocate a Colab GPU from this development environment. |

Next research: LTX reference conditioning and continuation, bounded speech-length motion, Kaggle official compute policy, voice-service usage and model rights. Novel panel image generation is a separate planned workflow; it is not implemented by these video changes.
