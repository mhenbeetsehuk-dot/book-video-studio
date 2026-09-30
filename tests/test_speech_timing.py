import ast
import json
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace

NOTEBOOK = Path(__file__).resolve().parents[1] / 'Book_Video_Studio_Colab.ipynb'


def functions(*names, namespace=None):
    tree = ast.parse(''.join(json.loads(NOTEBOOK.read_text())['cells'][4]['source']))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = {} if namespace is None else namespace
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'notebook_functions', 'exec'), ns)
    return ns


class TimingTests(unittest.TestCase):
    def test_actual_recording_duration_selects_enough_motion(self):
        ns = functions('motion_frames', 'plan_motion', 'media_seconds', namespace={'subprocess': subprocess})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.wav'
            with wave.open(str(path), 'wb') as out:
                out.setnchannels(1); out.setsampwidth(2); out.setframerate(8000)
                out.writeframes(b'\0\0' * 57600)
            duration = ns['media_seconds'](path)
            self.assertAlmostEqual(duration, 7.2, places=3)
            plan = ns['plan_motion'](5, duration)
            self.assertEqual(plan['seconds'], 8)
            self.assertGreaterEqual(plan['motion_duration'], duration + .2)

    def test_no_speech_and_boundary_lengths(self):
        ns = functions('motion_frames', 'plan_motion')
        for selected in (5, 8, 10):
            self.assertEqual(ns['plan_motion'](selected)['seconds'], selected)
        self.assertEqual(ns['plan_motion'](5, 4.925)['seconds'], 5)
        self.assertEqual(ns['plan_motion'](5, 4.926)['seconds'], 8)
        self.assertEqual(ns['plan_motion'](5, 9.9)['seconds'], 10)

    def test_long_or_invalid_speech_rejected(self):
        ns = functions('motion_frames', 'plan_motion')
        for seconds in (10.0, 30.0, float('nan'), float('inf'), 0, -1):
            with self.assertRaises(ValueError):
                ns['plan_motion'](5, seconds)

    def test_prepared_voice_reused_without_second_service_call(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'voice').mkdir()
            audio = root / 'voice/speech.wav'; audio.write_bytes(b'fixture')
            metadata = {'type': 'human recording'}; calls = []
            def run(command, **kw):
                calls.append(command)
                return SimpleNamespace(returncode=0, stderr='')
            def make_speech(*args):
                raise AssertionError('Voice service must not run twice')
            ns = functions('voice_clip', namespace={
                'Path': Path, 'json': json, 'subprocess': SimpleNamespace(run=run),
                'media_seconds': lambda path: 7.2 if Path(path) == audio else 8.125,
                'sound_choices': SimpleNamespace(value=()), 'sound_level': SimpleNamespace(value=-20),
                'make_speech': make_speech, 'load': lambda: {'clips': []}, 'save': lambda data: None,
                'print': lambda *a: None})
            self.assertEqual(ns['voice_clip'](root, prepared=(audio, metadata)), root / 'voiced_video.mp4')
            self.assertIn(str(audio), calls[0]); self.assertEqual(len(calls), 1)
            self.assertNotIn('video', metadata)
            self.assertFalse(json.loads((root / 'voice/voice.json').read_text())['lip_sync'])


if __name__ == '__main__':
    unittest.main()
