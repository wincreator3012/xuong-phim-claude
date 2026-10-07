#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROXY MULTICAM: từ các góc gốc (thường 4K, mỗi file hàng chục GB) đã có multicam.json, tạo bản
làm việc 1080p ĐÃ CĂN SẴN trên cùng một trục (mọi góc bắt đầu cùng mốc 0), kèm tiếng chủ .wav.
Mọi bước sau (đo chuyển động, dàn góc, dựng) chạy trên proxy nhanh hơn nhiều lần và không đụng tới
file gốc; mỗi lượt gọi lệnh trên máy bị giới hạn ~180 s nên tool làm từng mảnh và chạy tiếp được.

Cách dùng (từ gốc xưởng, sau multicam-khop.py trên thư mục gốc):
  python3 tools/multicam-proxy.py "../Du an/<x>" [--ra "../Du an/<x>/proxy"] [--tu 340 --den 1570]
      [--chieu-cao 1080] [--fps 30] [--crf 18] [--gioi-han 150]

Đầu ra trong --ra: nguon/<góc>/<góc>.mp4 (chỉ hình, 1080p, cfr), nguon/tieng-chu.wav (tiếng góc
chuẩn hoặc tieng_chu_de_xuat, 48 kHz stereo), PROXY.json (mốc --tu để quy ngược về file gốc).
Chạy lại đúng lệnh tới khi báo "✓ Xong"; tool ghi luôn multicam.json của proxy (offset 0, tiếng chủ
.wav) để multicam-dan.py dùng ngay. Không chạy multicam-khop.py trên proxy (proxy không có tiếng).

Ghi chú: proxy KHÔNG có tiếng (nối các mảnh bằng -c copy an toàn vì không có AAC; xem BAI-HOC về
lệch hình-tiếng khi concat AAC). Tiếng chủ là một file .wav liền, timeline dùng audioSrc trỏ vào đó.
Mốc trên trục proxy = mốc trục gốc - --tu.
"""
import argparse
import json
import os
import subprocess
import sys
import time

CHUNK = 120.0


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"! Lệnh lỗi: {' '.join(cmd)}\n{p.stderr.decode(errors='ignore')[-600:]}")
    return p


def pieces(goc, t0, t1):
    """Các mảnh (file, ss, dài) hoặc (None, 0, dài) cho khoảng trống, phủ [t0, t1) trên trục chung."""
    out, t = [], t0
    files = sorted((f for f in goc["files"] if f.get("offset") is not None and f.get("co_hinh", True)),
                   key=lambda f: f["offset"])
    while t < t1 - 1e-3:
        fe = next((f for f in files if f["offset"] <= t < f["ket_thuc"] - 0.05), None)
        if fe:
            d = min(t1, fe["ket_thuc"]) - t
            out.append((fe["file"], t - fe["offset"], d))
        else:
            nxt = [f["offset"] for f in files if f["offset"] > t]
            d = min(t1, nxt[0] if nxt else t1) - t
            out.append((None, 0.0, d))
        t += d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--ra", default=None)
    ap.add_argument("--tu", type=float, default=None)
    ap.add_argument("--den", type=float, default=None)
    ap.add_argument("--chieu-cao", type=int, default=1080)
    ap.add_argument("--fps", default="30")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--gioi-han", type=float, default=150.0)
    args = ap.parse_args()
    proj = args.project.rstrip("/")
    ra = (args.ra or os.path.join(proj, "proxy")).rstrip("/")
    mc = json.load(open(os.path.join(proj, "multicam.json"), encoding="utf-8"))
    video_goc = [g for g in mc["goc"] if any(f.get("co_hinh", True) for f in g["files"])]
    # mặc định: quãng mọi góc cùng có hình
    starts = [min(f["offset"] for f in g["files"] if f.get("offset") is not None) for g in video_goc]
    ends = [max(f["ket_thuc"] for f in g["files"] if f.get("offset") is not None) for g in video_goc]
    tu = args.tu if args.tu is not None else max(0.0, max(starts))
    den = args.den if args.den is not None else min(ends)
    deadline = time.time() + args.gioi_han
    W = f"scale=-2:{args.chieu_cao}"
    print(f"Quãng trục chung {tu:.2f} - {den:.2f} s ({(den - tu) / 60:.1f} phút) → {ra}")
    os.makedirs(os.path.join(ra, "nguon"), exist_ok=True)
    json.dump({"nguon": proj, "tu": tu, "den": den, "_ghi_chu": "mốc proxy = mốc trục gốc - tu"},
              open(os.path.join(ra, "PROXY.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # tiếng chủ
    wav = os.path.join(ra, "nguon", "tieng-chu.wav")
    if not os.path.isfile(wav):
        src_goc = mc.get("tieng_chu_de_xuat") or mc["truc_chuan"]
        g = next((x for x in mc["goc"] if x["ten"] == src_goc), None) or \
            next(x for x in mc["goc"] if x["ten"] == mc["truc_chuan"])
        ps = [p for p in pieces(g, tu, den) if p[0]]
        if len(ps) != 1:
            print(f"  ! góc tiếng {g['ten']} có {len(ps)} mảnh trong quãng - dùng mảnh đầu, kiểm lại tiếng chủ")
        f, ss, d = ps[0]
        sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-i", os.path.join(proj, f), "-t", f"{d:.3f}",
            "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", wav + ".part.wav"])
        os.replace(wav + ".part.wav", wav)
        print(f"  ✓ tiếng chủ từ {g['ten']}: {wav}")

    todo = 0
    for g in video_goc:
        gdir = os.path.join(ra, "nguon", g["ten"])
        final = os.path.join(gdir, f"{g['ten']}.mp4")
        if os.path.isfile(final):
            continue
        cdir = os.path.join(gdir, ".manh")
        os.makedirs(cdir, exist_ok=True)
        n = int((den - tu) // CHUNK) + (1 if (den - tu) % CHUNK > 1e-3 else 0)
        done = True
        for k in range(n):
            out = os.path.join(cdir, f"{k:03d}.mp4")
            if os.path.isfile(out):
                continue
            if time.time() > deadline:
                done = False
                break
            t0, t1 = tu + k * CHUNK, min(den, tu + (k + 1) * CHUNK)
            subs = []
            for j, (f, ss, d) in enumerate(pieces(g, t0, t1)):
                so = os.path.join(cdir, f"{k:03d}-{j}.mp4")
                if f:
                    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-i", os.path.join(proj, f), "-t", f"{d:.3f}"]
                else:
                    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                           f"color=black:s=1920x{args.chieu_cao}:r={args.fps}", "-t", f"{d:.3f}"]
                sh(cmd + ["-an", "-vf", W, "-r", args.fps, "-vsync", "cfr", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", str(args.crf), "-g", "60", "-pix_fmt", "yuv420p", "-f", "mp4", so + ".part"])
                os.replace(so + ".part", so)
                subs.append(so)
            if len(subs) == 1:
                os.replace(subs[0], out)
            else:
                lst = out + ".txt"
                open(lst, "w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in subs))
                sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-f", "mp4", out + ".part"])
                os.replace(out + ".part", out)
            print(f"  ✓ {g['ten']} mảnh {k + 1}/{n}", flush=True)
        if not done:
            todo += 1
            continue
        lst = os.path.join(cdir, "all.txt")
        open(lst, "w").write("".join(f"file '{os.path.abspath(os.path.join(cdir, f'{k:03d}.mp4'))}'\n" for k in range(n)))
        sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart",
            "-f", "mp4", final + ".part"])
        os.replace(final + ".part", final)
        print(f"  ✓ {final}")
    if todo:
        print(f"⏸ Còn {todo} góc chưa xong - chạy lại đúng lệnh này để làm tiếp (mảnh đã xong được giữ)")
        sys.exit(2)
    # multicam.json của proxy: mọi góc một file, offset 0 (đã căn khi cắt), tiếng chủ là .wav.
    # Không chạy lại multicam-khop.py trên proxy: proxy không có tiếng; đồng bộ đã bảo đảm từ multicam.json gốc.
    span = round(den - tu, 3)
    pm = {"_ghi_chu": f"PROXY từ {proj} quãng {tu}-{den} s trục gốc; mốc proxy = mốc gốc - {tu}",
          "truc_chuan": mc["truc_chuan"], "tong_dai": span,
          "tieng_chu": {"file": "nguon/tieng-chu.wav", "offset": 0.0},
          "goc": [{"ten": g["ten"], "loai": g["loai"], "nguoi": g.get("nguoi"),
                   "files": [{"file": f"nguon/{g['ten']}/{g['ten']}.mp4", "dur": span, "offset": 0.0,
                              "ket_thuc": span, "co_hinh": True, "co_tieng": False, "drift_ppm": 0}],
                   "phu": [[0.0, span]], "khoang_trong": []} for g in video_goc]}
    json.dump(pm, open(os.path.join(ra, "multicam.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✓ Xong proxy + multicam.json. Kiểm đồng bộ bằng mắt: trích cùng một mốc ở các góc (khoảnh khắc vỗ tay,"
          f" gật đầu) rồi ghép cạnh nhau. Mảnh tạm nguon/<góc>/.manh/ dọn được sau khi kiểm.")


if __name__ == "__main__":
    main()
