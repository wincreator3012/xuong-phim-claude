#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo transcript có mốc thời gian cho video/audio bằng Whisper (sherpa-onnx, chạy offline).

Hai nơi chạy (từ thư mục gốc "xuong-phim-claude"):
  1. ƯU TIÊN - trên macOS, ngoài VM: đủ RAM để chạy large-v3. Không gọi trực tiếp;
     Claude xếp việc bằng tools/hang-doi-go-bang.py, người dùng bấm đúp
     "Go bang tren Mac.command" ở thư mục gốc (xem tools/models/TAI-MODEL.md).
  2. DỰ PHÒNG - trong VM Cowork (device_bash):
       python3 tools/transcribe.py "../Du an/x/nguon/clip.mp4" --out-dir "../Du an/x/transcript"
     VM chỉ khoảng 3-4 GB RAM nên --model auto sẽ chọn turbo (large-v3 chết lặng trong VM).

Kết quả (đặt theo tên file nguồn, ví dụ clip.*):
    clip.transcript.json  - [{"start", "end", "text"}, …] (giây)
    clip.srt              - phụ đề SRT
    clip.txt              - dạng đọc nhanh: [hh:mm:ss - hh:mm:ss] nội dung
    clip.silences.json    - các khoảng lặng (từ ffmpeg silencedetect) để cắt chính xác

Model đặt tại tools/models/sherpa-onnx-whisper-<model>/ (large-v3 | turbo | small).
--model auto (mặc định): large-v3 khi đủ RAM (Linux: >= 7 GB còn trống; macOS: tổng RAM
>= 12 GB), không thì turbo. Dòng "model tự chọn: whisper-..." ghi rõ model đã dùng.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import wave

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if sys.platform.startswith("linux"):
    # tools/pylib chứa thư viện biên dịch cho Linux (VM Cowork); trên macOS dùng
    # môi trường riêng do "Go bang tren Mac.command" dựng, không nạp pylib.
    sys.path.insert(0, os.path.join(TOOLS_DIR, "pylib"))

import numpy as np  # noqa: E402
import sherpa_onnx  # noqa: E402

SAMPLE_RATE = 16000
MAX_CHUNK_SECONDS = 28.0  # whisper xử lý tối đa 30s mỗi lượt


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def extract_wav(src: str, dst: str):
    run([
        "ffmpeg", "-hide_banner", "-y", "-i", src,
        "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), "-c:a", "pcm_s16le", dst,
    ])


def detect_silences(src: str, noise_db: float = -35.0, min_dur: float = 0.5):
    """Phát hiện khoảng lặng bằng ffmpeg silencedetect."""
    p = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", src, "-vn",
         "-af", f"silencedetect=noise={noise_db}dB:d={min_dur}", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    text = p.stderr
    silences = []
    start = None
    for line in text.splitlines():
        m1 = re.search(r"silence_start:\s*([0-9.]+)", line)
        m2 = re.search(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", line)
        if m1:
            start = float(m1.group(1))
        elif m2 and start is not None:
            silences.append({
                "start": round(start, 3),
                "end": round(float(m2.group(1)), 3),
                "duration": round(float(m2.group(2)), 3),
            })
            start = None
    return silences


def read_wav(path: str) -> np.ndarray:
    with wave.open(path, "rb") as f:
        assert f.getframerate() == SAMPLE_RATE
        data = f.readframes(f.getnframes())
    samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    return samples


def vad_segments(samples: np.ndarray, models_dir: str):
    """Cắt audio thành các đoạn có tiếng nói bằng silero VAD."""
    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = os.path.join(models_dir, "silero_vad.onnx")
    cfg.silero_vad.threshold = 0.5
    cfg.silero_vad.min_silence_duration = 0.35
    cfg.silero_vad.min_speech_duration = 0.25
    cfg.silero_vad.max_speech_duration = MAX_CHUNK_SECONDS
    cfg.sample_rate = SAMPLE_RATE
    window = cfg.silero_vad.window_size
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=120)

    segments = []

    def drain():
        while not vad.empty():
            seg = vad.front
            segments.append((seg.start / SAMPLE_RATE, np.array(seg.samples)))
            vad.pop()

    i = 0
    n = len(samples)
    while i < n:
        vad.accept_waveform(samples[i:i + window])
        i += window
        drain()
    vad.flush()
    drain()

    # Chia nhỏ đoạn dài quá 28s
    out = []
    max_len = int(MAX_CHUNK_SECONDS * SAMPLE_RATE)
    for start, arr in segments:
        off = 0
        while off < len(arr):
            piece = arr[off:off + max_len]
            out.append((start + off / SAMPLE_RATE, piece))
            off += max_len
    return out


def build_recognizer(models_dir: str, model: str, lang: str, threads: int):
    d = os.path.join(models_dir, f"sherpa-onnx-whisper-{model}")
    if not os.path.isdir(d):
        sys.exit(f"Không tìm thấy model tại {d} - hãy kiểm tra tools/models/")

    def pick(pattern):
        cands = sorted(
            f for f in os.listdir(d)
            if re.fullmatch(pattern, f)
        )
        # ưu tiên int8 (nhanh hơn trên CPU)
        int8 = [c for c in cands if ".int8." in c]
        return os.path.join(d, (int8 or cands)[0])

    encoder = pick(rf"{re.escape(model)}-encoder.*\.onnx")
    decoder = pick(rf"{re.escape(model)}-decoder.*\.onnx")
    tokens = os.path.join(d, f"{model}-tokens.txt")
    return sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=encoder, decoder=decoder, tokens=tokens,
        language=lang, task="transcribe", num_threads=threads,
    )


def fmt_ts(t: float, srt: bool = False) -> str:
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    if srt:
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
    return f"{h:02d}:{m:02d}:{s:04.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--model", default="auto", choices=["auto", "small", "turbo", "large-v3", "tiny", "base", "medium"],
                    help="auto: large-v3 khi đủ RAM (Linux >= 7 GB trống, macOS tổng >= 12 GB), không thì turbo")
    ap.add_argument("--lang", default="vi")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--threads", type=int, default=None,
                    help="mặc định: 4 trong VM Linux, tối đa 8 luồng trên macOS")
    ap.add_argument("--batch", type=int, default=2)
    args = ap.parse_args()
    if args.threads is None:
        args.threads = min(os.cpu_count() or 4, 8) if sys.platform == "darwin" else 4
    if args.model == "auto":
        # VM Cowork ~3-4 GB RAM làm large-v3 chết lặng lẽ (hết bộ nhớ, không báo lỗi)
        if sys.platform == "darwin":
            try:
                total_gb = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True,
                                              text=True).stdout.strip()) / 1024 ** 3
            except (ValueError, OSError):
                total_gb = 0.0
            args.model = "large-v3" if total_gb >= 12 else "turbo"
            print(f"      model tự chọn: whisper-{args.model} (macOS, tổng RAM {total_gb:.0f} GB)", flush=True)
        else:
            avail_gb = 0.0
            try:
                for line in open("/proc/meminfo"):
                    if line.startswith("MemAvailable:"):
                        avail_gb = int(line.split()[1]) / 1024 / 1024
            except OSError:
                pass
            args.model = "large-v3" if avail_gb >= 7 else "turbo"
            print(f"      model tự chọn: whisper-{args.model} (RAM trống {avail_gb:.1f} GB)", flush=True)

        # máy chưa tải large-v3 (repo công khai chỉ cài turbo): lùi về model đang có, không dừng
        if not os.path.isdir(os.path.join(TOOLS_DIR, "models", f"sherpa-onnx-whisper-{args.model}")):
            for thay in ("turbo", "small"):
                if os.path.isdir(os.path.join(TOOLS_DIR, "models", f"sherpa-onnx-whisper-{thay}")):
                    print(f"      chưa có whisper-{args.model} trong tools/models/ (xem TAI-MODEL.md), dùng whisper-{thay}", flush=True)
                    args.model = thay
                    break
    src = args.input
    base = os.path.splitext(os.path.basename(src))[0]
    out_dir = args.out_dir or os.path.join(os.path.dirname(src), "..", "transcript")
    os.makedirs(out_dir, exist_ok=True)
    models_dir = os.path.join(TOOLS_DIR, "models")

    print(f"[1/4] Tách audio 16kHz từ {os.path.basename(src)} …", flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "audio.wav")
        extract_wav(src, wav)
        samples = read_wav(wav)
    dur = len(samples) / SAMPLE_RATE
    print(f"      Thời lượng: {fmt_ts(dur)}", flush=True)

    print("[2/4] Phát hiện khoảng lặng …", flush=True)
    silences = detect_silences(src)
    with open(os.path.join(out_dir, f"{base}.silences.json"), "w", encoding="utf-8") as f:
        json.dump(silences, f, ensure_ascii=False, indent=1)

    print("[3/4] Tách đoạn có tiếng nói (VAD) …", flush=True)
    segs = vad_segments(samples, models_dir)
    print(f"      {len(segs)} đoạn nói", flush=True)

    print(f"[4/4] Nhận dạng bằng whisper-{args.model} (có thể lâu với bài dài) …", flush=True)
    rec = build_recognizer(models_dir, args.model, args.lang, args.threads)
    results = []
    for i in range(0, len(segs), args.batch):
        batch = segs[i:i + args.batch]
        streams = []
        for _, arr in batch:
            st = rec.create_stream()
            st.accept_waveform(SAMPLE_RATE, arr)
            streams.append(st)
        rec.decode_streams(streams)
        for (start, arr), st in zip(batch, streams):
            text = st.result.text.strip()
            if text:
                results.append({
                    "start": round(start, 2),
                    "end": round(start + len(arr) / SAMPLE_RATE, 2),
                    "text": text,
                })
        done = min(i + args.batch, len(segs))
        print(f"      {done}/{len(segs)} đoạn", flush=True)

    with open(os.path.join(out_dir, f"{base}.transcript.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    with open(os.path.join(out_dir, f"{base}.srt"), "w", encoding="utf-8") as f:
        for i, r in enumerate(results, 1):
            f.write(f"{i}\n{fmt_ts(r['start'], True)} --> {fmt_ts(r['end'], True)}\n{r['text']}\n\n")

    with open(os.path.join(out_dir, f"{base}.txt"), "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"[{fmt_ts(r['start'])} - {fmt_ts(r['end'])}] {r['text']}\n")

    print(f"✓ Xong. Kết quả trong {out_dir}/{base}.*")


if __name__ == "__main__":
    main()
