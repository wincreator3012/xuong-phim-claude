#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KHÁM màu video - bước 1 của quy trình KHÁM - KÊ ĐƠN - SOI LẠI (skill phim-mau-sac).

Chẩn đoán từng file nguồn: metadata màu (phát hiện HDR chắc chắn), số liệu
sáng/tương phản/bão hòa/ám màu từ các frame rải đều, và xuất frame để Claude
xem bằng mắt. Script chỉ ĐO và GỢI Ý cờ hiệu - kết luận kê đơn do Claude
quyết sau khi nhìn frame, theo trần an toàn trong skill.

Cách dùng (từ gốc "xuong-phim-claude"):
  KHÁM cả dự án:   python3 tools/mau-sac.py kham "du-an/<x>"
  KHÁM một file:   python3 tools/mau-sac.py kham "du-an/<x>" --files "clip.MP4"
  SOI trước/sau:   python3 tools/mau-sac.py soi "du-an/<x>/nguon/clip.MP4" \
                       --vf "<chuỗi filter>" [--t 30,120,300]

Kết quả KHÁM: <dự án>/mau-sac-kham.json + frame ở <dự án>/.tam/mau/
Kết quả SOI:  ảnh ghép trước|sau ở <dự án>/.tam/mau/so-sanh-*.jpg
Đơn màu cuối (Claude soạn, user duyệt): <dự án>/mau-sac.json
  {"<tên file nguồn>": {"vf": "<chuỗi filter ffmpeg>", "note": "<lý do>"}}
  → assemble.py tự đọc và chèn vào lượt encode duy nhất của từng đoạn.
"""
import argparse
import json
import os
import subprocess
import sys

EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".mts", ".avi", ".webm"}
HDR_TRANSFERS = {"smpte2084": "PQ/Dolby Vision", "arib-std-b67": "HLG"}

# Công thức tonemap chuẩn cho HDR → SDR (hable giữ chi tiết, desat=0 giữ bão hòa)
TONEMAP_VF = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
              "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Lệnh lỗi: {' '.join(cmd)}\n{p.stderr[-800:]}")
    return p


def probe(path):
    p = sh(["ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", path])
    return json.loads(p.stdout)


def frame_stats(path, ts):
    """Đo một frame tại giây ts từ raw RGB 96x54: mean R/G/B, phân vị luma, bão hòa."""
    p = subprocess.run(
        ["ffmpeg", "-hide_banner", "-v", "error", "-ss", f"{ts:.2f}", "-i", path,
         "-frames:v", "1", "-vf", "scale=96:54", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True)
    buf = p.stdout
    n = len(buf) // 3
    if n < 100:
        return None
    rs = gs = bs = 0
    lumas = []
    sats = []
    for i in range(n):
        r, g, b = buf[3 * i], buf[3 * i + 1], buf[3 * i + 2]
        rs += r; gs += g; bs += b
        lumas.append(0.2126 * r + 0.7152 * g + 0.0722 * b)
        mx, mn = max(r, g, b), min(r, g, b)
        sats.append((mx - mn) / mx if mx else 0)
    lumas.sort()
    def pct(q):
        return lumas[min(n - 1, int(q * n))]
    return {
        "r": rs / n, "g": gs / n, "b": bs / n,
        "p5": pct(0.05), "p50": pct(0.50), "p95": pct(0.95),
        "sat": sum(sats) / n,
    }


def kham_file(path, out_dir, n_frames):
    info = probe(path)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    dur = float(info["format"].get("duration", 0))
    transfer = vs.get("color_transfer", "")
    hdr = HDR_TRANSFERS.get(transfer)
    base = os.path.splitext(os.path.basename(path))[0]

    # Trích frame rải đều (bỏ 5% đầu/cuối) - full size để xem mắt, stats từ bản nhỏ
    pts = [dur * (0.05 + 0.9 * i / max(1, n_frames - 1)) for i in range(n_frames)]
    stats = []
    for i, ts in enumerate(pts):
        jpg = os.path.join(out_dir, f"{base}-f{i}.jpg")
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y",
                        "-ss", f"{ts:.2f}", "-i", path, "-frames:v", "1",
                        "-vf", "scale=960:-2", "-q:v", "3", jpg], capture_output=True)
        st = frame_stats(path, ts)
        if st:
            st["ts"] = round(ts, 1)
            stats.append(st)

    med = lambda k: sorted(s[k] for s in stats)[len(stats) // 2] if stats else 0
    agg = {k: round(med(k), 1) for k in ("r", "g", "b", "p5", "p50", "p95", "sat")}
    agg["sat"] = round(med("sat"), 3)

    flags = []
    if hdr:
        flags.append(f"HDR {hdr} - BẮT BUỘC tonemap")
    spread = agg["p95"] - agg["p5"]
    if not hdr and spread < 140:
        flags.append(f"tương phản thấp? (dải {spread:.0f}/255)")
    cast = max(agg["r"], agg["g"], agg["b"]) - min(agg["r"], agg["g"], agg["b"])
    if cast > 14:
        kenh = max(("r", "g", "b"), key=lambda k: agg[k])
        flags.append(f"ám màu? (lệch kênh {cast:.0f}, trội {kenh.upper()})")
    if agg["p50"] < 85:
        flags.append("hơi tối?")
    elif agg["p50"] > 170:
        flags.append("hơi cháy sáng?")
    if agg["sat"] < 0.10:
        flags.append("bão hòa rất thấp?")

    return {
        "file": os.path.basename(path),
        "thong_so": f"{vs.get('width')}x{vs.get('height')} {vs.get('pix_fmt')} "
                    f"transfer={transfer or '?'} primaries={vs.get('color_primaries', '?')}",
        "dai": round(dur, 1),
        "hdr": bool(hdr),
        "do_luong": agg,
        "co_hieu": flags or ["đạt (theo số liệu)"],
        "goi_y_tonemap": TONEMAP_VF if hdr else None,
    }


def cmd_kham(args):
    project = args.project.rstrip("/")
    src_dir = os.path.join(project, "nguon")
    out_dir = os.path.join(project, ".tam", "mau")
    os.makedirs(out_dir, exist_ok=True)
    if args.files:
        files = [os.path.join(src_dir, f) for f in args.files]
    else:
        files = sorted(os.path.join(src_dir, f) for f in os.listdir(src_dir)
                       if os.path.splitext(f)[1].lower() in EXTS)
    if not files:
        sys.exit(f"Không có file video trong {src_dir}")

    results = []
    for f in files:
        print(f"KHÁM {os.path.basename(f)} …", flush=True)
        results.append(kham_file(f, out_dir, args.frames))

    # So chéo các nguồn: lệch sáng / lệch màu giữa các file dùng chung dự án
    so_cheo = []
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            a, b = results[i], results[j]
            if a["hdr"] != b["hdr"]:
                so_cheo.append(f"{a['file']} vs {b['file']}: một HDR một SDR - tonemap xong mới so tiếp")
                continue
            da, db = a["do_luong"], b["do_luong"]
            dluma = abs(da["p50"] - db["p50"])
            dcast = max(abs(da[k] - db[k]) for k in ("r", "g", "b"))
            if dluma > 18 or dcast > 14:
                so_cheo.append(f"{a['file']} vs {b['file']}: lệch nhau "
                               f"(sáng {dluma:.0f}, màu {dcast:.0f}) - cần khớp nếu cắt qua lại")

    out = {"ket_qua": results, "so_cheo_nguon": so_cheo or ["các nguồn tương đồng"],
           "frame_xem_mat": out_dir}
    dst = os.path.join(project, "mau-sac-kham.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"\n{'='*70}")
    for r in results:
        print(f"{r['file']}  |  {r['thong_so']}")
        d = r["do_luong"]
        print(f"   sáng p5/p50/p95: {d['p5']:.0f}/{d['p50']:.0f}/{d['p95']:.0f}"
              f"  RGB: {d['r']:.0f}/{d['g']:.0f}/{d['b']:.0f}  bão hòa: {d['sat']}")
        print(f"   → {'; '.join(r['co_hieu'])}")
    print("SO CHÉO:", "; ".join(out["so_cheo_nguon"]))
    print(f"✓ Kết quả: {dst} | Frame xem mắt: {out_dir}/")


def cmd_soi(args):
    """Ghép trước|sau cạnh nhau tại vài mốc để duyệt mắt."""
    src = args.src
    project = os.path.dirname(os.path.dirname(src))
    out_dir = os.path.join(project, ".tam", "mau")
    os.makedirs(out_dir, exist_ok=True)
    dur = float(probe(src)["format"].get("duration", 60))
    ts_list = ([float(t) for t in args.t.split(",")] if args.t
               else [dur * 0.15, dur * 0.5, dur * 0.85])
    base = os.path.splitext(os.path.basename(src))[0]
    for i, ts in enumerate(ts_list):
        out = os.path.join(out_dir, f"so-sanh-{base}-{i}.jpg")
        fc = (f"[0:v]scale=960:-2,drawbox=x=0:y=0:w=6:h=ih:c=black[a];"
              f"[0:v]{args.vf},scale=960:-2[b];[a][b]hstack")
        sh(["ffmpeg", "-hide_banner", "-v", "error", "-y",
            "-ss", f"{ts:.2f}", "-i", src, "-frames:v", "1",
            "-filter_complex", fc, "-q:v", "3", out])
        print(out)
    print("✓ Trái = gốc, phải = sau đơn màu")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("kham")
    k.add_argument("project")
    k.add_argument("--files", nargs="*")
    k.add_argument("--frames", type=int, default=5)
    s = sub.add_parser("soi")
    s.add_argument("src")
    s.add_argument("--vf", required=True)
    s.add_argument("--t", default=None)
    args = ap.parse_args()
    (cmd_kham if args.cmd == "kham" else cmd_soi)(args)


if __name__ == "__main__":
    main()
