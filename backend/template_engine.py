from pathlib import Path
import cv2
import numpy as np

from media_utils import ffprobe_json
from beat_detector import detect_beats

def _duration(meta):
    try:
        return float(meta["format"]["duration"])
    except Exception:
        return 0.0

def _scene_cuts(path, sample_fps=4.0):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = total / fps if fps else 0
    step = max(1, int(round(fps / sample_fps)))
    prev = None
    cuts = []
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            small = cv2.resize(frame, (160, 90))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            if prev is not None:
                diff = float(cv2.absdiff(gray, prev).mean())
                if diff > 28:
                    cuts.append(round(idx / fps, 3))
            prev = gray
        idx += 1
        if duration and idx / fps > min(duration, 180):
            break
    cap.release()

    # Remove cuts that are too close together.
    result = []
    for t in cuts:
        if not result or t - result[-1] > 0.20:
            result.append(t)
    return result

def analyze_template(path: Path):
    meta = ffprobe_json(path)
    streams = meta.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video:
        raise RuntimeError("File template tidak memiliki video.")

    width = int(video.get("width", 0))
    height = int(video.get("height", 0))
    duration = _duration(meta)
    ratio = "9:16" if height > width else ("16:9" if width > height else "1:1")

    cuts = _scene_cuts(path)
    beats = detect_beats(path) if audio else []

    # Build usable edit points. Prefer beat points, then scene cuts.
    points = sorted(set([0.0] + beats + cuts + [round(duration, 3)]))
    points = [x for x in points if 0 <= x <= duration]
    segments = []
    for a, b in zip(points, points[1:]):
        if b - a >= 0.25:
            segments.append({
                "start": round(a, 3),
                "end": round(b, 3),
                "duration": round(b - a, 3),
                "transition": "cut",
            })

    return {
        "filename": path.name,
        "duration": round(duration, 3),
        "width": width,
        "height": height,
        "ratio": ratio,
        "fps": float(video.get("r_frame_rate", "30/1").split("/")[0]) if video.get("r_frame_rate") else 30,
        "beats": beats[:300],
        "scene_cuts": cuts[:300],
        "segments": segments[:400],
        "segment_count": len(segments),
        "reconstruction_note": "Timing direkonstruksi dari beat dan perubahan frame; efek project asli tidak dapat dipulihkan hanya dari MP4."
    }
