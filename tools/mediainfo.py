#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tóm tắt thông số media của các file trong một thư mục (hoặc một file).

Cách dùng: python3 tools/mediainfo.py "du-an/x/nguon"
"""
import json
import os
import subprocess
import sys

EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".mts", ".mp3", ".m4a", ".wav", ".aac", ".webm"}


def probe(path):
    p = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True,
    )
    if p.returncode != 0:
        return None
    return json.loads(p.stdout)


def fmt_dur(t):
    t = float(t)
    return f"{int(t//3600):02d}:{int(t%3600//60):02d}:{t%60:04.1f}"


def describe(path):
    info = probe(path)
    if not info:
        return f"{os.path.basename(path)}: KHÔNG ĐỌC ĐƯỢC"
    fmt = info.get("format", {})
    dur = fmt_dur(fmt.get("duration", 0))
    size_mb = float(fmt.get("size", 0)) / 1e6
    parts = [f"{os.path.basename(path)}  |  {dur}  |  {size_mb:.0f} MB"]
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            fps = s.get("avg_frame_rate", "0/1")
            try:
                a, b = fps.split("/")
                fps = f"{float(a)/float(b):.2f}" if float(b) else "?"
            except Exception:
                pass
            parts.append(
                f"    video: {s.get('codec_name')} {s.get('width')}x{s.get('height')} @ {fps}fps"
            )
        elif s.get("codec_type") == "audio":
            parts.append(
                f"    audio: {s.get('codec_name')} {s.get('sample_rate')}Hz {s.get('channels')}ch"
            )
    return "\n".join(parts)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    if os.path.isfile(target):
        print(describe(target))
        return
    files = sorted(
        f for f in os.listdir(target)
        if os.path.splitext(f)[1].lower() in EXTS
    )
    if not files:
        print(f"Không có file media trong {target}")
        return
    for f in files:
        print(describe(os.path.join(target, f)))
        print()


if __name__ == "__main__":
    main()
