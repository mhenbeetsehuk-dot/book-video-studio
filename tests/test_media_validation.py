import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from media_validation import validate_video


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg tools required')
class MediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.video = cls.root / 'video.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                        'color=c=blue:s=192x128:r=8', '-frames:v', '41',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(cls.video)],
                       check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_valid_decoded_manifest(self):
        report = validate_video(self.video, expected_frames=41, expected_fps=8, width=192, height=128)
        self.assertEqual(report['frames'], 41)
        self.assertAlmostEqual(report['duration_seconds'], 5.125)
        self.assertEqual(report['sha256'], hashlib.sha256(self.video.read_bytes()).hexdigest())
        self.assertNotIn(str(self.root), json.dumps(report))

    def test_missing_empty_corrupt(self):
        for name, content in [('empty.mp4', b''), ('corrupt.mp4', b'not a movie')]:
            path = self.root / name
            path.write_bytes(content)
            with self.assertRaises(ValueError):
                validate_video(path)
        with self.assertRaises(ValueError):
            validate_video(self.root / 'missing.mp4')

    def test_duration_speech_and_request_mismatch(self):
        for options in [dict(minimum_seconds=6), dict(speech_seconds=6),
                        dict(expected_frames=42), dict(expected_fps=24),
                        dict(width=256), dict(height=160), dict(speech_seconds=float('nan'))]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                validate_video(self.video, **options)

    def test_cli_exit_codes(self):
        script = Path(__file__).resolve().parents[1] / 'media_validation.py'
        result = subprocess.run([sys.executable, str(script), str(self.video)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(json.loads(result.stdout)['valid'])
        result = subprocess.run([sys.executable, str(script), str(self.video), '--speech-seconds', '9'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['valid'])
