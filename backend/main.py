from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
import shutil
import json
import asyncio

from media_utils import run_cmd, ffprobe_json, download_template
from template_engine import analyze_template
from video_processor import render_template

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
OUTPUTS = BASE / "outputs"
TEMPLATES = BASE / "templates"
for p in (UPLOADS, OUTPUTS, TEMPLATES):
    p.mkdir(exist_ok=True)

app = FastAPI(title="Template Video Editor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/template/analyze")
async def template_analyze(
    url: str = Form(""),
    template: UploadFile | None = File(None)
):
    work = TEMPLATES / uuid.uuid4().hex
    work.mkdir()

    try:
        if template:
            ext = Path(template.filename or ".mp4").suffix.lower()
            if ext not in VIDEO_EXTS:
                raise HTTPException(400, "Template harus berupa video.")
            path = work / f"source{ext}"
            with path.open("wb") as f:
                shutil.copyfileobj(template.file, f)
        elif url.strip():
            path = work / "source.mp4"
            await asyncio.to_thread(download_template, url.strip(), path)
        else:
            raise HTTPException(400, "Masukkan URL atau upload template.")

        meta = await asyncio.to_thread(analyze_template, path)
        meta["template_id"] = work.name
        meta["source_path"] = str(path)
        (work / "analysis.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return meta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Gagal menganalisis template: {e}")

@app.post("/api/render")
async def render(
    template_id: str = Form(...),
    effect_strength: float = Form(1.0),
    output_ratio: str = Form("9:16"),
    files: list[UploadFile] = File(...)
):
    work = TEMPLATES / template_id
    analysis_file = work / "analysis.json"
    if not analysis_file.exists():
        raise HTTPException(404, "Template tidak ditemukan.")

    try:
        analysis = json.loads(analysis_file.read_text(encoding="utf-8"))
    except Exception:
        raise HTTPException(500, "Analisis template rusak.")

    job_id = uuid.uuid4().hex
    job_dir = UPLOADS / job_id
    job_dir.mkdir()

    media_paths = []
    for i, upload in enumerate(files):
        ext = Path(upload.filename or ".jpg").suffix.lower()
        if ext not in VIDEO_EXTS | IMAGE_EXTS:
            continue
        p = job_dir / f"{i:03d}{ext}"
        with p.open("wb") as f:
            shutil.copyfileobj(upload.file, f)
        media_paths.append(p)

    if not media_paths:
        raise HTTPException(400, "Tidak ada foto/video yang valid.")

    out = OUTPUTS / f"{job_id}.mp4"
    jobs[job_id] = {"status": "rendering", "progress": 0}

    try:
        await asyncio.to_thread(
            render_template,
            analysis,
            media_paths,
            out,
            output_ratio,
            float(effect_strength),
        )
        jobs[job_id] = {"status": "done", "progress": 100, "file": out.name}
        return {"job_id": job_id, "status": "done", "download": f"/api/download/{job_id}"}
    except Exception as e:
        jobs[job_id] = {"status": "error", "error": str(e)}
        raise HTTPException(500, f"Rendering gagal: {e}")

@app.get("/api/jobs/{job_id}")
def job(job_id: str):
    return jobs.get(job_id, {"status": "unknown"})

@app.get("/api/download/{job_id}")
def download(job_id: str):
    item = jobs.get(job_id)
    if not item or item.get("status") != "done":
        raise HTTPException(404, "Hasil belum tersedia.")
    path = OUTPUTS / item["file"]
    if not path.exists():
        raise HTTPException(404, "File hasil tidak ditemukan.")
    return FileResponse(path, media_type="video/mp4", filename="template-result.mp4")
