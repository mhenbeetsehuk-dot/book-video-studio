import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import runtime_manifest


class FakeCuda:
    @staticmethod
    def is_available():
        return True

    @staticmethod
    def device_count():
        return 1

    @staticmethod
    def get_device_properties(index):
        return SimpleNamespace(name="Test GPU", major=8, minor=0, total_memory=123456)

    @staticmethod
    def is_bf16_supported():
        return True


class RuntimeManifestTests(unittest.TestCase):
    def test_gpu_manifest_is_structured_and_private(self):
        fake = SimpleNamespace(__version__="test", version=SimpleNamespace(cuda="test"), cuda=FakeCuda())
        result = runtime_manifest.collect_runtime(fake)
        self.assertEqual(result["schema_version"], 1)
        self.assertTrue(result["accelerator"]["cuda_available"])
        self.assertEqual(result["accelerator"]["devices"][0]["compute_capability"], [8, 0])
        self.assertFalse(result["privacy"]["environment_variables_collected"])
        serialized = json.dumps(result).lower()
        for forbidden in ("token", "prompt", "manuscript", "recording"):
            self.assertNotIn(forbidden, serialized)

    def test_cli_writes_parseable_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "manifest.json"
            self.assertEqual(runtime_manifest.main(["--output", str(output)]), 0)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("packages", result)
            self.assertIn("accelerator", result)


if __name__ == "__main__":
    unittest.main()
