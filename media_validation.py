"""Validate a local rendered video without loading the generation model.

Requires ffprobe. This checks file properties, not visual quality or lip sync.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess


def validate_video(path, *, minimum_seconds=5.0, speech_seconds=None,
                   expected_frames=None, expected_fps=None, width=None, height=None):
    """Return a content-free manifest, or raise ValueError on invalid output."""
    path = Path(path).resolve()
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError('Video output is missing or empty')
    for value in (minimum_seconds, speech_seconds, expected_fps):
        if value is not None and (not math.isfinite(value) or value < 0):
            raise ValueError('Duration and frame rate expectations must be finite and nonnegative')
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
            '-show_entries', 'stream=codec_name,width,height,avg_frame_rate,duration,nb_read_frames',
            '-of', 'json', str(path)], capture_output=True, text=True, timeout=120)
    except FileNotFoundError as exc:
        raise ValueError('ffprobe is not installed') from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError('Video validation timed out') from exc
    if result.returncode or result.stderr.strip():
        raise ValueError('Video could not be decoded cleanly')
    try:
        stream = json.loads(result.stdout)['streams'][0]
        fps = float(Fraction(stream['avg_frame_rate']))
        duration = float(stream['duration'])
        frames = int(stream['nb_read_frames'])
        actual_width, actual_height = int(stream['width']), int(stream['height'])
        if not math.isfinite(fps) or not math.isfinite(duration) or min(fps, duration, frames, actual_width, actual_height) <= 0:
            raise ValueError('Invalid stream properties')
    except (KeyError, IndexError, TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError('Video has no usable duration, frame count or dimensions') from exc
    required = max(minimum_seconds, speech_seconds or 0)
    if duration + 0.001 < required:
        raise ValueError('Video ends before the required duration')
    for label, actual, expected in [('frames', frames, expected_frames),
                                     ('width', actual_width, width), ('height', actual_height, height)]:
        if expected is not None and actual != expected:
            raise ValueError('Unexpected video ' + label)
    if expected_fps is not None and not math.isclose(fps, expected_fps, rel_tol=0, abs_tol=0.001):
        raise ValueError('Unexpected video frame rate')
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return dict(duration_seconds=duration, frames=frames, fps=fps,
                width=actual_width, height=actual_height, codec=stream.get('codec_name'),
                bytes=path.stat().st_size, sha256=digest.hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--minimum-seconds', type=float, default=5)
    parser.add_argument('--speech-seconds', type=float)
    parser.add_argument('--expected-frames', type=int)
    parser.add_argument('--expected-fps', type=float)
    parser.add_argument('--width', type=int)
    parser.add_argument('--height', type=int)
    args = vars(parser.parse_args())
    path = args.pop('video')
    try:
        print(json.dumps({'valid': True, **validate_video(path, **args)}, indent=2))
    except ValueError as exc:
        print(json.dumps({'valid': False, 'error': str(exc)}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
