#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DỰNG THỬ dự án tổng hợp nhỏ để chắc xưởng chạy đúng trên máy này.

    python3 tools/kiem-tra-xuong.py [--co-slide] [--giu]

Tạo nguồn giả bằng ffmpeg (màn test + tiếng sine), soạn timeline có đủ các
kỹ thuật chính (cắt, fade, overlay alpha, B-roll, insert, tuỳ chọn bố cục slide
và multicam audioSrc), rồi chạy đúng đường thật: assemble.py --kiem-tra →
assemble.py --preview → nghiem-thu.py video. Thoát mã 0 = ĐẠT.

Dự án thử nằm ở du-an/_kiem-tra-tu-dong/ (xoá được). Không cần model, không cần mạng.
"""
import argparse
import json
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "pylib"))


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout[-2000:], p.stderr[-2000:])
        raise SystemExit(f"! Lệnh lỗi: {' '.join(cmd)}")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--co-slide", action="store_true", help="thêm hai đoạn bố cục slide (cần do-hoa-chung/bo-cuc và Pillow)")
    ap.add_argument("--giu", action="store_true", help="không dọn cache cũ trước khi dựng")
    args = ap.parse_args()
    os.chdir(ROOT)

    proj = os.path.join("du-an", "_kiem-tra-tu-dong")
    for d in ("nguon", "do-hoa"):
        os.makedirs(os.path.join(proj, d), exist_ok=True)
    ff = ["ffmpeg", "-hide_banner", "-v", "error", "-y"]
    print("→ tạo nguồn giả", flush=True)
    sh(ff + ["-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30", "-f", "lavfi",
             "-i", "sine=frequency=440:sample_rate=48000", "-t", "30",
             "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest",
             os.path.join(proj, "nguon", "chinh.mp4")])
    sh(ff + ["-f", "lavfi", "-i", "smptebars=size=640x360:rate=30", "-t", "10",
             "-c:v", "libx264", "-preset", "ultrafast", os.path.join(proj, "nguon", "broll.mp4")])
    sh(ff + ["-f", "lavfi", "-i", "color=c=white@0.9:s=300x60:r=30,format=yuva420p,"
             "pad=640:360:40:260:color=black@0.0", "-t", "4", "-c:v", "libvpx",
             "-pix_fmt", "yuva420p", "-auto-alt-ref", "0", os.path.join(proj, "do-hoa", "lt.webm")])
    sh(ff + ["-f", "lavfi", "-i", "color=c=0x2F5D50:size=640x360:rate=30", "-t", "3",
             "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
             os.path.join(proj, "do-hoa", "intro.mp4")])
    # góc thứ hai (multicam): hình khác, tiếng riêng - segment lấy hình từ đây nhưng tiếng từ track chủ
    sh(ff + ["-f", "lavfi", "-i", "mandelbrot=size=640x360:rate=30", "-f", "lavfi",
             "-i", "sine=frequency=880:sample_rate=48000", "-t", "12",
             "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest",
             os.path.join(proj, "nguon", "goc2.mp4")])

    segs = [
        {"type": "video", "src": "nguon/chinh.mp4", "in": 2.0, "out": 14.0, "snap": False,
         "fadeIn": 0.5, "overlay": {"src": "do-hoa/lt.webm", "at": 1.0},
         "broll": [{"src": "nguon/broll.mp4", "at": 8.0, "duration": 3.0, "from": 2.0}]},
        {"type": "insert", "src": "do-hoa/intro.mp4"},
        {"type": "video", "src": "nguon/chinh.mp4", "in": 20.0, "out": 28.0, "snap": False,
         "fadeOut": 0.5, "overlay": [{"src": "do-hoa/lt.webm", "at": 0.5},
                                     {"src": "do-hoa/lt.webm", "at": 5.0}]},
        {"type": "video", "src": "nguon/goc2.mp4", "in": 3.0, "out": 9.0, "snap": False,
         "audioSrc": "nguon/chinh.mp4", "audioIn": 10.0},
    ]
    co_bo_cuc = os.path.isfile(os.path.join("do-hoa-chung", "bo-cuc", "bo-cuc.json"))
    if args.co_slide and co_bo_cuc:
        try:
            from PIL import Image, ImageDraw
            os.makedirs(os.path.join(proj, "slide"), exist_ok=True)
            im = Image.new("RGB", (1920, 1080), "white")
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 1920, 180], fill="#2F5D50")
            for k in range(4):
                d.rectangle([160, 300 + k * 150, 1400, 360 + k * 150], fill="#DDDDDD")
            im.save(os.path.join(proj, "slide", "slide-01.png"))
            segs.insert(1, {"type": "video", "src": "nguon/chinh.mp4", "in": 14.0, "out": 20.0,
                            "snap": False, "layout": "ca-hai", "slide": "slide/slide-01.png"})
            segs.append({"type": "video", "src": "nguon/chinh.mp4", "in": 28.0, "out": 30.0,
                         "snap": False, "layout": "mat-chinh", "slide": "slide/slide-01.png"})
            print("→ có hai đoạn bố cục slide (ca-hai, mat-chinh)")
        except ImportError:
            print("⚠ thiếu Pillow - bỏ qua đoạn thử bố cục slide")
    elif args.co_slide:
        print("⚠ chưa có do-hoa-chung/bo-cuc - bỏ qua đoạn thử bố cục slide")

    tl = {"aspect": "ngang", "fps": 30, "theme": "light",
          "intro": "do-hoa/intro.mp4", "outro": "do-hoa/intro.mp4", "segments": segs}
    with open(os.path.join(proj, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)

    if not args.giu:
        tam = os.path.join(proj, ".tam")
        if os.path.isdir(tam):
            for fn in os.listdir(tam):
                try:
                    open(os.path.join(tam, fn), "w").close()   # ghi rỗng thay cho xoá
                except OSError:
                    pass

    print("→ assemble.py --kiem-tra", flush=True)
    p = subprocess.run([sys.executable, "tools/assemble.py", "--project", proj, "--kiem-tra"], text=True)
    if p.returncode != 0:
        raise SystemExit("! Kiểm timeline thất bại")
    print("→ assemble.py --preview", flush=True)
    p = subprocess.run([sys.executable, "tools/assemble.py", "--project", proj, "--preview"], text=True)
    if p.returncode != 0:
        raise SystemExit("! Dựng thử THẤT BẠI - cổng nghiệm thu bắt được lỗi hoặc môi trường khác; đọc chẩn đoán ở trên")
    out = os.path.join(proj, "xuat-nhap", "_kiem-tra-tu-dong-ngang-nhap.mp4")
    print("→ nghiem-thu.py video", flush=True)
    p = subprocess.run([sys.executable, "tools/nghiem-thu.py", "video", out, "--khung", "ngang", "--nhap", "--anh"], text=True)
    if p.returncode != 0:
        raise SystemExit("! nghiem-thu.py báo KHÔNG ĐẠT trên dự án thử - xưởng CHƯA an toàn")
    print(f"\n✓ DỰNG THỬ ĐẠT trên máy này. Thư mục thử: {proj}/ (xoá được).")


if __name__ == "__main__":
    main()
