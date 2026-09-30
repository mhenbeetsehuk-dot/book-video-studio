import ast
import json
import unittest
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parents[1] / 'Book_Video_Studio_Colab.ipynb'


class NotebookTests(unittest.TestCase):
    def setUp(self):
        self.notebook = json.loads(NOTEBOOK.read_text())
        self.source = ''.join(self.notebook['cells'][4]['source'])
        self.tree = ast.parse(self.source)

    def test_all_cells_and_subprocess_scripts_compile(self):
        for index, cell in enumerate(self.notebook['cells']):
            if cell['cell_type'] == 'code':
                compile(''.join(cell['source']), f'cell_{index}', 'exec')
                self.assertFalse(cell['outputs'])
        for node in self.tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in ('encode', 'generate')
                for t in node.targets
            ):
                compile(ast.literal_eval(node.value), 'subprocess_script', 'exec')

    def test_motion_duration_meets_requested_length_and_temporal_grid(self):
        function = next(n for n in self.tree.body if isinstance(n, ast.FunctionDef) and n.name == 'motion_frames')
        namespace = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), 'duration', 'exec'), namespace)
        for seconds in (5, 8, 10):
            frames = namespace['motion_frames'](seconds)
            self.assertGreaterEqual(frames / 8, seconds)
            self.assertEqual((frames - 1) % 8, 0)
        with self.assertRaises(ValueError):
            namespace['motion_frames'](30)

    def test_base_checkpoint_cannot_select_distilled_guidance(self):
        guidance = [n for n in ast.walk(self.tree) if isinstance(n, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == 'guidance' for t in n.targets)]
        self.assertEqual(len(guidance), 1)
        self.assertEqual(ast.literal_eval(guidance[0].value), 5.0)
        self.assertNotIn('Fast draft', self.source)


if __name__ == '__main__':
    unittest.main()
