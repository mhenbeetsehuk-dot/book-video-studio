import ast
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parents[1] / 'Book_Video_Studio_Colab.ipynb'


class ReproducibilityTests(unittest.TestCase):
    def setUp(self):
        self.source = ''.join(json.loads(NOTEBOOK.read_text())['cells'][4]['source'])
        self.tree = ast.parse(self.source)

    def test_reference_checksum_matches_file_bytes(self):
        node = next(n for n in self.tree.body if isinstance(n, ast.FunctionDef) and n.name == 'sha256_file')
        namespace = {'Path': Path, 'hashlib': hashlib}
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'checksum', 'exec'), namespace)
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder) / 'reference.png'
            fixture.write_bytes(b'private-reference-fixture')
            self.assertEqual(namespace['sha256_file'](fixture), hashlib.sha256(fixture.read_bytes()).hexdigest())

    def test_model_revision_is_used_by_every_model_loader(self):
        self.assertIn("model_revision=resolve_model_revision(model_repo)", self.source)
        self.assertIn("'model_revision':model_revision", self.source)
        self.assertEqual(self.source.count('from_pretrained('), 3)
        self.assertGreaterEqual(self.source.count('revision=revision'), 2)
        self.assertIn("revision=config['model_revision'],text_encoder=None", self.source)

    def test_reference_manifest_and_cache_revision_are_recorded(self):
        self.assertIn("request['reference_manifest']", self.source)
        self.assertIn("'sha256':sha256_file(snapshot)", self.source)
        self.assertIn("'dimensions':dimensions", self.source)
        self.assertIn("'model_revision':request['model_revision']", self.source)
        self.assertIn("'schema':2", self.source)


if __name__ == '__main__':
    unittest.main()
