"use client";

import { useMemo, useState } from "react";
import {
  Upload, Link as LinkIcon, Sparkles, Play, Download,
  Film, Music2, Zap, CheckCircle2, Loader2
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type Analysis = {
  template_id: string;
  filename: string;
  duration: number;
  width: number;
  height: number;
  ratio: string;
  beats: number[];
  scene_cuts: number[];
  segment_count: number;
  segments: { start: number; end: number; duration: number }[];
  reconstruction_note: string;
};

export default function Home() {
  const [url, setUrl] = useState("");
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [media, setMedia] = useState<File[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [ratio, setRatio] = useState("9:16");
  const [strength, setStrength] = useState("1");
  const [loading, setLoading] = useState(false);
  const [rendering, setRendering] = useState(false);
  const [resultUrl, setResultUrl] = useState("");
  const [error, setError] = useState("");

  const totalSize = useMemo(
    () => (media.reduce((n, f) => n + f.size, 0) / 1024 / 1024).toFixed(1),
    [media]
  );

  async function analyze() {
    setError("");
    setLoading(true);
    setAnalysis(null);
    try {
      const fd = new FormData();
      if (url.trim()) fd.append("url", url.trim());
      if (templateFile) fd.append("template", templateFile);
      const res = await fetch(`${API}/api/template/analyze`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Gagal menganalisis template.");
      setAnalysis(data);
    } catch (e: any) {
      setError(e.message || "Terjadi kesalahan.");
    } finally {
      setLoading(false);
    }
  }

  async function render() {
    if (!analysis || !media.length) {
      setError("Analisis template dan masukkan minimal satu foto/video.");
      return;
    }
    setError("");
    setRendering(true);
    setResultUrl("");
    try {
      const fd = new FormData();
      fd.append("template_id", analysis.template_id);
      fd.append("output_ratio", ratio);
      fd.append("effect_strength", strength);
      media.forEach(f => fd.append("files", f));
      const res = await fetch(`${API}/api/render`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Render gagal.");
      setResultUrl(`${API}${data.download}`);
    } catch (e: any) {
      setError(e.message || "Render gagal.");
    } finally {
      setRendering(false);
    }
  }

  return (
    <main className="min-h-screen grid-bg">
      <div className="mx-auto max-w-6xl px-5 py-8 md:py-12">
        <header className="mb-8 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-violet-400/20 bg-violet-500/10 px-3 py-1 text-xs text-violet-200">
              <Sparkles size={14}/> TEMPLATE VIDEO ENGINE
            </div>
            <h1 className="text-4xl font-black tracking-tight md:text-6xl">
              Ubah foto jadi <span className="text-violet-400">video jedag-jedug.</span>
            </h1>
            <p className="mt-4 max-w-2xl text-zinc-400">
              Analisis timing template, beat dan perpindahan frame lalu rekonstruksi
              dengan foto/video milikmu.
            </p>
          </div>
          <div className="glass rounded-2xl px-4 py-3 text-sm text-zinc-300">
            <div className="flex items-center gap-2"><Zap size={16} className="text-yellow-300"/> FFmpeg + OpenCV + Beat Analysis</div>
          </div>
        </header>

        {error && (
          <div className="mb-5 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">
            {error}
          </div>
        )}

        <section className="glass rounded-3xl p-5 shadow-2xl md:p-7">
          <div className="mb-6 flex items-center gap-3">
            <div className="rounded-xl bg-violet-500/15 p-3"><LinkIcon size={20}/></div>
            <div>
              <h2 className="font-bold">1. Ambil Template</h2>
              <p className="text-sm text-zinc-500">URL YouTube/TikTok atau upload video template.</p>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-[1fr_auto]">
            <input
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder="https://www.youtube.com/... atau https://www.tiktok.com/..."
              className="w-full rounded-2xl border border-white/10 bg-black/30 px-4 py-4 outline-none transition focus:border-violet-500"
            />
            <button
              onClick={analyze}
              disabled={loading || (!url.trim() && !templateFile)}
              className="flex items-center justify-center gap-2 rounded-2xl bg-violet-600 px-6 py-4 font-bold transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {loading ? <Loader2 className="animate-spin"/> : <Sparkles size={18}/>}
              {loading ? "Menganalisis..." : "Analisis Template"}
            </button>
          </div>

          <label className="mt-3 flex cursor-pointer items-center gap-3 rounded-2xl border border-dashed border-white/15 bg-white/[.02] p-4 hover:bg-white/[.04]">
            <Upload size={18}/>
            <span className="text-sm text-zinc-300">
              {templateFile ? templateFile.name : "Atau pilih video template dari komputer"}
            </span>
            <input
              type="file"
              accept="video/*"
              className="hidden"
              onChange={e => setTemplateFile(e.target.files?.[0] || null)}
            />
          </label>
        </section>

        {analysis && (
          <section className="glass mt-5 rounded-3xl p-5 md:p-7">
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-emerald-500/15 p-3"><CheckCircle2 className="text-emerald-400"/></div>
                <div>
                  <h2 className="font-bold">Template terdeteksi</h2>
                  <p className="text-sm text-zinc-500">{analysis.filename}</p>
                </div>
              </div>
              <span className="rounded-full bg-white/5 px-3 py-1 text-xs">{analysis.ratio}</span>
            </div>

            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              {[
                ["Durasi", `${analysis.duration.toFixed(1)} dtk`],
                ["Beat", `${analysis.beats.length}`],
                ["Perpindahan", `${analysis.scene_cuts.length}`],
                ["Segmen", `${analysis.segment_count}`],
              ].map(([a,b]) => (
                <div key={a} className="rounded-2xl bg-black/25 p-4">
                  <div className="text-xs text-zinc-500">{a}</div>
                  <div className="mt-1 text-xl font-bold">{b}</div>
                </div>
              ))}
            </div>

            <p className="mt-4 text-xs leading-5 text-zinc-500">{analysis.reconstruction_note}</p>
          </section>
        )}

        <section className="glass mt-5 rounded-3xl p-5 md:p-7">
          <div className="mb-6 flex items-center gap-3">
            <div className="rounded-xl bg-pink-500/15 p-3"><Film size={20}/></div>
            <div>
              <h2 className="font-bold">2. Masukkan Foto / Video</h2>
              <p className="text-sm text-zinc-500">Urutan file akan digunakan mengikuti segmen template.</p>
            </div>
          </div>

          <label className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-white/15 bg-black/20 p-6 text-center hover:bg-white/[.03]">
            <Upload size={30} className="mb-3 text-zinc-400"/>
            <span className="font-semibold">Klik untuk memilih banyak file</span>
            <span className="mt-1 text-xs text-zinc-500">JPG, PNG, WEBP, MP4, MOV, WEBM</span>
            <input
              multiple
              type="file"
              accept="image/*,video/*"
              className="hidden"
              onChange={e => setMedia(Array.from(e.target.files || []))}
            />
          </label>

          {media.length > 0 && (
            <div className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-5">
              {media.map((f,i) => (
                <div key={`${f.name}-${i}`} className="rounded-xl bg-white/5 p-3 text-xs">
                  <div className="truncate font-medium">{i+1}. {f.name}</div>
                  <div className="mt-1 text-zinc-500">{(f.size/1024/1024).toFixed(1)} MB</div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-6 grid gap-3 md:grid-cols-2">
            <label className="rounded-2xl bg-black/25 p-4">
              <div className="mb-2 text-xs text-zinc-500">Rasio output</div>
              <select value={ratio} onChange={e => setRatio(e.target.value)} className="w-full bg-transparent outline-none">
                <option value="9:16">9:16 — TikTok / Reels / Shorts</option>
                <option value="16:9">16:9 — YouTube</option>
                <option value="1:1">1:1 — Square</option>
              </select>
            </label>
            <label className="rounded-2xl bg-black/25 p-4">
              <div className="mb-2 text-xs text-zinc-500">Kekuatan efek</div>
              <select value={strength} onChange={e => setStrength(e.target.value)} className="w-full bg-transparent outline-none">
                <option value="0.7">0.7 — Halus</option>
                <option value="1">1.0 — Normal</option>
                <option value="1.5">1.5 — Kuat</option>
                <option value="2">2.0 — Ekstra</option>
              </select>
            </label>
          </div>

          <button
            onClick={render}
            disabled={rendering || !analysis || !media.length}
            className="mt-5 flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-violet-600 to-pink-600 px-6 py-4 font-black transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {rendering ? <Loader2 className="animate-spin"/> : <Sparkles/>}
            {rendering ? "Sedang membuat video..." : "Buat Video Template"}
          </button>
          {media.length > 0 && <div className="mt-2 text-center text-xs text-zinc-600">{media.length} file • {totalSize} MB</div>}
        </section>

        <section className="glass mt-5 rounded-3xl p-5 md:p-7">
          <div className="mb-6 flex items-center gap-3">
            <div className="rounded-xl bg-cyan-500/15 p-3"><Play size={20}/></div>
            <div>
              <h2 className="font-bold">3. Hasil Template</h2>
              <p className="text-sm text-zinc-500">Preview dan download hasil render.</p>
            </div>
          </div>

          <div className="flex min-h-96 items-center justify-center rounded-3xl bg-black/40 p-4">
            {resultUrl ? (
              <video src={resultUrl} controls playsInline className="max-h-[650px] max-w-full rounded-2xl shadow-2xl"/>
            ) : (
              <div className="text-center text-zinc-600">
                <Music2 size={44} className="mx-auto mb-3 opacity-40"/>
                <p>Hasil video akan muncul di sini.</p>
              </div>
            )}
          </div>

          {resultUrl && (
            <div className="mt-4 flex flex-col gap-3 sm:flex-row">
              <a href={resultUrl} target="_blank" rel="noreferrer"
                 className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-white/10 px-5 py-4 font-bold hover:bg-white/15">
                <Play size={18}/> Preview
              </a>
              <a href={resultUrl} download="template-result.mp4"
                 className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-violet-600 px-5 py-4 font-bold hover:bg-violet-500">
                <Download size={18}/> Download MP4
              </a>
            </div>
          )}
        </section>

        <footer className="py-8 text-center text-xs text-zinc-600">
          Gunakan template dan musik yang Anda punya hak/izin untuk gunakan.
        </footer>
      </div>
    </main>
  );
}
