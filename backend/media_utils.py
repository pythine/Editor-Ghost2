from pathlib import Path
import subprocess
import json
import yt_dlp

def run_cmd(args, timeout=1800):
    p = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-4000:])
    return p.stdout

def ffprobe_json(path: Path):
    out = run_cmd([
        "ffprobe", "-v", "error",
        "-show_streams", "-show_format",
        "-of", "json", str(path)
    ])
    return json.loads(out)

def download_template(url: str, destination: Path):
    # Uses yt-dlp's supported extractors. The user is responsible for rights
    # and platform terms for the source content.
    opts = {
        "outtmpl": str(destination.with_suffix(".%(ext)s")),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    candidates = sorted(destination.parent.glob(destination.stem + ".*"))
    mp4s = [p for p in candidates if p.suffix.lower() == ".mp4"]
    if not mp4s:
        raise RuntimeError("yt-dlp tidak menghasilkan MP4. Coba upload file template secara langsung.")
    if mp4s[0] != destination:
        mp4s[0].replace(destination)
    return destination
