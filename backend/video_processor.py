from pathlib import Path
import subprocess
import tempfile
import math
import json

from media_utils import run_cmd, ffprobe_json

def ratio_size(ratio):
    if ratio == "16:9":
        return 1280, 720
    if ratio == "1:1":
        return 1080, 1080
    return 1080, 1920

def media_duration(path):
    data = ffprobe_json(path)
    return float(data["format"]["duration"])

def make_clip(src, dst, duration, width, height, index, strength=1.0):
    # Alternating subtle motion recreates a common "jedag-jedug" style:
    # zoom + slight horizontal/vertical motion. It intentionally does not
    # claim to recover the exact proprietary effect chain of a source project.
    z = 1.0 + min(0.12, 0.045 * strength)
    zoom = f"scale={width*2}:{height*2}:force_original_aspect_ratio=increase,crop={width*2}:{height*2},scale=iw*{z}:ih*{z},crop={width}:{height}"
    if index % 3 == 0:
        zoom += ",eq=contrast=1.05:saturation=1.08"
    elif index % 3 == 1:
        zoom += ",eq=contrast=1.08"
    else:
        zoom += ",eq=saturation=1.10"

    is_image = src.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        *(["-loop", "1"] if is_image else []),
        "-i", str(src),
        "-t", str(max(0.25, duration)),
        "-vf", zoom,
        "-r", "30",
        "-an",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        str(dst)
    ]
    run_cmd(cmd)

def render_template(analysis, media_paths, output, output_ratio="9:16", effect_strength=1.0):
    width, height = ratio_size(output_ratio)
    segments = analysis.get("segments") or []
    if not segments:
        duration = float(analysis.get("duration", 5))
        segments = [{"duration": duration}]

    with tempfile.TemporaryDirectory(prefix="template-render-") as td:
        td = Path(td)
        clips = []
        media_index = 0
        for i, seg in enumerate(segments):
            duration = float(seg.get("duration", 0.5))
            if duration <= 0:
                continue
            src = media_paths[media_index % len(media_paths)]
            media_index += 1
            clip = td / f"clip_{i:04d}.mp4"
            make_clip(src, clip, duration, width, height, i, effect_strength)
            clips.append(clip)

        concat = td / "concat.txt"
        concat.write_text(
            "".join(f"file '{str(p).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'\n" for p in clips),
            encoding="utf-8"
        )

        silent = td / "silent.mp4"
        run_cmd([
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat),
            "-c", "copy", str(silent)
        ])

        # Try to reuse the extracted template audio if available. This is
        # useful for local templates the user has rights to use.
        template_path = Path(analysis["source_path"])
        final = output
        try:
            run_cmd([
                "ffmpeg", "-y", "-v", "error",
                "-i", str(silent),
                "-i", str(template_path),
                "-map", "0:v:0", "-map", "1:a:0?",
                "-c:v", "copy", "-c:a", "aac",
                "-shortest", str(final)
            ])
        except Exception:
            run_cmd([
                "ffmpeg", "-y", "-v", "error",
                "-i", str(silent),
                "-c", "copy", str(final)
            ])
