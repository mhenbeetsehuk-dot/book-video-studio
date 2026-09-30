#!/usr/bin/env python3
"""Write a privacy-safe runtime manifest for Book Video Studio diagnostics."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_NAMES = (
    "torch",
    "diffusers",
    "transformers",
    "accelerate",
    "huggingface-hub",
    "safetensors",
    "Pillow",
    "imageio",
    "imageio-ffmpeg",
)


def _package_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in PACKAGE_NAMES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def collect_runtime(torch_module=None) -> dict:
    """Collect only allow-listed runtime facts; never copy environment variables."""
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "packages": _package_versions(),
        "accelerator": {"cuda_available": False, "devices": []},
        "privacy": {
            "environment_variables_collected": False,
            "project_content_collected": False,
        },
    }

    try:
        torch = torch_module if torch_module is not None else importlib.import_module("torch")
        manifest["accelerator"]["torch_version"] = str(torch.__version__)
        manifest["accelerator"]["cuda_runtime"] = getattr(torch.version, "cuda", None)
        available = bool(torch.cuda.is_available())
        manifest["accelerator"]["cuda_available"] = available
        if available:
            for index in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(index)
                manifest["accelerator"]["devices"].append(
                    {
                        "index": index,
                        "name": props.name,
                        "compute_capability": [props.major, props.minor],
                        "total_memory_bytes": props.total_memory,
                        "bf16_supported": bool(torch.cuda.is_bf16_supported()),
                    }
                )
    except (ImportError, RuntimeError, AttributeError) as exc:
        manifest["accelerator"]["inspection_error"] = type(exc).__name__

    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("runtime_manifest.json"))
    args = parser.parse_args(argv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(collect_runtime(), indent=2) + "\n", encoding="utf-8")
    print(f"Runtime manifest saved: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
