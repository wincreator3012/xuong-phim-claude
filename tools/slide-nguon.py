#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NHẬP SLIDE vào dự án: từ PPTX / PDF / bộ ảnh / video quay màn hình → bộ ảnh slide chuẩn
+ slide.json (chữ trên slide, ghi chú diễn giả, mốc thời gian nếu có) để bước khớp
(slide-khop.py) và bước dựng (assemble.py) dùng.

Cách dùng (từ gốc "xuong-phim-claude"):
  python3 tools/slide-nguon.py "du-an/<x>/nguon/bai-giang.pptx"  --project "du-an/<x>"
  python3 tools/slide-nguon.py "du-an/<x>/nguon/bai-giang.pdf"   --project "du-an/<x>"
  python3 tools/slide-nguon.py "du-an/<x>/nguon/slide-anh/"       --project "du-an/<x>"
  python3 tools/slide-nguon.py "du-an/<x>/nguon/man-hinh.mp4"    --project "du-an/<x>" [--nguong 1.5]

Kết quả: du-an/<x>/slide/slide-01.png … + du-an/<x>/slide/slide.json
  {"nguon": "...", "loai": "pptx|pdf|anh|man-hinh",
   "slides": [{"n": 1, "file": "slide-01.png", "text": "...", "notes": "...",
               "so_tu": 23, "ts": 12.4 (chỉ khi từ quay màn hình)}]}

Môi trường: PPTX cần LibreOffice (soffice), PDF cần poppler (pdftoppm/pdftotext) - đã kiểm
Máy ảo Cowork thường có cả hai (kiểm bằng which soffice pdftoppm), sandbox đám mây cũng có.
Máy khác (Mac Studio) kiểm bằng `which` trước; thiếu thì chạy bước này ở đám mây rồi commit
thư mục slide/ về máy. Bộ ảnh và quay màn hình chạy được ở bất cứ đâu có ffmpeg + Pillow.
Keynote: user xuất PDF hoặc PPTX từ Keynote trước (File > Export To).
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
# Thư viện Python cài riêng vào tools/pylib (tools/cai-dat.py lo việc này) - VM Cowork
# không giữ pip install qua các phiên, nên thư viện phải nằm trong thư mục xưởng.
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylib"))

MAX_W = 1920


def sh(cmd, check=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit(f"! Lệnh lỗi: {' '.join(cmd)}\n{p.stderr[-800:]}")
    return p


def need(binary, goi_y):
    if shutil.which(binary) is None:
        raise SystemExit(f"! Thiếu `{binary}` trên máy này. {goi_y}")


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def fit_png(src, dst):
    """Thu về tối đa 1920 ngang, giữ tỉ lệ, PNG."""
    from PIL import Image
    im = Image.open(src).convert("RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(dst, "PNG", optimize=True)
    return im.size


def words(s):
    return len(re.findall(r"\w+", s or "", flags=re.UNICODE))


# ---------------------------------------------------------------- PPTX
def from_pptx(src, out_dir):
    need("soffice", "Máy này không có LibreOffice: chạy bước này ở sandbox đám mây rồi commit slide/ về máy.")
    texts, notes = [], []
    try:
        from pptx import Presentation
        prs = Presentation(src)
        for s in prs.slides:
            t = []
            for shp in s.shapes:
                if shp.has_text_frame:
                    t.append(shp.text_frame.text)
                if getattr(shp, "has_table", False) and shp.has_table:
                    for row in shp.table.rows:
                        t.append(" | ".join(c.text for c in row.cells))
            texts.append("\n".join(x for x in t if x.strip()))
            notes.append(s.notes_slide.notes_text_frame.text if s.has_notes_slide else "")
    except ImportError:
        print("  ⚠ thiếu python-pptx (pip install python-pptx) - không đọc được chữ, chỉ xuất ảnh")
    with tempfile.TemporaryDirectory() as td:
        sh(["soffice", "--headless", "--convert-to", "pdf", "--outdir", td, src])
        pdf = glob.glob(os.path.join(td, "*.pdf"))[0]
        slides = from_pdf(pdf, out_dir, texts_override=texts or None)
    for i, s in enumerate(slides):
        if i < len(notes):
            s["notes"] = notes[i].strip()
    return slides


# ---------------------------------------------------------------- PDF
def from_pdf(src, out_dir, texts_override=None):
    need("pdftoppm", "Cài poppler-utils (apt) hoặc chạy bước này ở sandbox đám mây.")
    with tempfile.TemporaryDirectory() as td:
        sh(["pdftoppm", "-r", "144", "-png", src, os.path.join(td, "p")])
        pages = sorted(glob.glob(os.path.join(td, "p-*.png")), key=natural_key)
        slides = []
        for i, p in enumerate(pages, start=1):
            dst = os.path.join(out_dir, f"slide-{i:02d}.png")
            w, h = fit_png(p, dst)
            if texts_override and i - 1 < len(texts_override):
                text = texts_override[i - 1]
            elif shutil.which("pdftotext"):
                text = sh(["pdftotext", "-f", str(i), "-l", str(i), "-layout", src, "-"], check=False).stdout
            else:
                text = ""
            text = re.sub(r"[ \t]+", " ", text or "").strip()
            slides.append({"n": i, "file": os.path.basename(dst), "w": w, "h": h,
                           "text": text, "notes": "", "so_tu": words(text)})
    return slides


# ---------------------------------------------------------------- Bộ ảnh
def from_images(src_dir, out_dir):
    files = sorted([f for f in os.listdir(src_dir)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))], key=natural_key)
    if not files:
        raise SystemExit(f"! Không có ảnh trong {src_dir}")
    slides = []
    for i, f in enumerate(files, start=1):
        dst = os.path.join(out_dir, f"slide-{i:02d}.png")
        w, h = fit_png(os.path.join(src_dir, f), dst)
        slides.append({"n": i, "file": os.path.basename(dst), "w": w, "h": h, "text": "",
                       "notes": "", "so_tu": 0, "ten_goc": f})
    print("  ⚠ bộ ảnh không có chữ - Claude stage vài ảnh lên để đọc nội dung khi khớp")
    return slides


# ---------------------------------------------------------------- Quay màn hình
def from_screen(src, out_dir, nguong):
    """Phát hiện đổi slide: lấy mẫu 2 khung/giây thu nhỏ 160px, so độ lệch trung bình với khung
    trước; đổi slide = lệch vượt ngưỡng (mặc định 1.5/255 - slide nền trắng đổi chữ chỉ lệch nhẹ,
    scene-change của ffmpeg bỏ sót). Sau mỗi mốc lấy frame full-res, loại frame trùng."""
    need("ffmpeg", "")
    from PIL import Image, ImageChops, ImageStat
    with tempfile.TemporaryDirectory() as td:
        sh(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", src, "-vf", "fps=2,scale=160:-2",
            os.path.join(td, "s-%06d.png")])
        frames = sorted(glob.glob(os.path.join(td, "s-*.png")))
        diffs, prev = [], None
        for fp in frames:
            im = Image.open(fp).convert("L")
            if prev is not None:
                diffs.append(ImageStat.Stat(ImageChops.difference(im, prev)).mean[0])
            prev = im
        marks = [0.0]
        for k, d in enumerate(diffs):
            t = (k + 1) / 2.0
            if d >= nguong and t - marks[-1] > 1.5:
                marks.append(t)
        # gộp cụm đổi liên tiếp (transition/animation): giữ mốc cuối của cụm cách nhau < 1.5s đã lo ở trên
    slides, prev_small, n = [], None, 0
    for t in marks:
        with tempfile.TemporaryDirectory() as td:
            tmp = os.path.join(td, "f.png")
            sh(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-ss", f"{t + 0.8:.2f}", "-i", src,
                "-frames:v", "1", tmp], check=False)
            if not os.path.isfile(tmp):
                continue
            im = Image.open(tmp).convert("RGB")
            small = im.resize((160, 90)).convert("L")
            if prev_small is not None and ImageStat.Stat(ImageChops.difference(small, prev_small)).mean[0] < 1.0:
                continue  # trùng slide trước (mốc giả)
            prev_small = small
            n += 1
            dst = os.path.join(out_dir, f"slide-{n:02d}.png")
            if im.width > MAX_W:
                im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
            im.save(dst, "PNG", optimize=True)
            slides.append({"n": n, "file": os.path.basename(dst), "w": im.width, "h": im.height,
                           "text": "", "notes": "", "so_tu": 0, "ts": round(t, 2)})
    print(f"  {len(marks)} mốc đổi hình → {len(slides)} slide khác nhau (ngưỡng lệch {nguong}/255). "
          "Mốc `ts` theo file quay màn hình; quay màn hình và quay mặt không cùng bắt đầu thì truyền "
          "--lech cho slide-khop.py. Slide từ quay màn hình không có chữ - Claude stage ảnh lên đọc.")
    return slides


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--project", required=True)
    ap.add_argument("--nguong", type=float, default=1.5, help="ngưỡng lệch ảnh (0-255) để coi là đổi slide khi quay màn hình")
    args = ap.parse_args()
    out_dir = os.path.join(args.project, "slide")
    os.makedirs(out_dir, exist_ok=True)
    # dọn slide cũ (truncate, VM không cho rm)
    for f in os.listdir(out_dir):
        if f.startswith("slide-") and f.endswith(".png"):
            try:
                os.remove(os.path.join(out_dir, f))
            except OSError:
                open(os.path.join(out_dir, f), "w").close()

    src = args.src
    ext = os.path.splitext(src)[1].lower()
    if os.path.isdir(src):
        loai, slides = "anh", from_images(src, out_dir)
    elif ext in (".pptx", ".ppt", ".key"):
        if ext == ".key":
            raise SystemExit("! Keynote: xuất PDF hoặc PPTX từ Keynote (File > Export To) rồi chạy lại")
        loai, slides = "pptx", from_pptx(src, out_dir)
    elif ext == ".pdf":
        loai, slides = "pdf", from_pdf(src, out_dir)
    elif ext in (".mp4", ".mov", ".mkv", ".m4v"):
        loai, slides = "man-hinh", from_screen(src, out_dir, args.nguong)
    else:
        raise SystemExit(f"! Không nhận dạng được loại nguồn: {src}")

    meta = {"nguon": os.path.relpath(src, args.project) if not os.path.isabs(src) else src,
            "loai": loai, "so_slide": len(slides), "slides": slides}
    with open(os.path.join(out_dir, "slide.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"✓ {len(slides)} slide → {out_dir}/ (slide.json kèm chữ/ghi chú)")
    for s in slides[:60]:
        head = (s.get("text") or "").replace("\n", " / ")[:70]
        print(f"   {s['n']:>2}. {s['file']}  {s.get('so_tu', 0):>3} từ  {head}")


if __name__ == "__main__":
    main()
