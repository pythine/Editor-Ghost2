from pathlib import Path
import librosa
import numpy as np

def detect_beats(video_path: Path):
    y, sr = librosa.load(str(video_path), sr=22050, mono=True, duration=180)
    if len(y) < sr:
        return []
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units="frames")
    times = librosa.frames_to_time(beat_frames, sr=sr)
    return [round(float(x), 3) for x in times]
