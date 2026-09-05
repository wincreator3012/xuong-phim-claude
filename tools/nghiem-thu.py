#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NGHIỆM THU tự động - cổng kiểm định BẮT BUỘC trước khi nói "xong" với user.

Ra đời sau một lỗi thật (xem docs/BAI-HOC.md): thành phẩm lệch hình-tiếng cộng dồn
hàng giây mà không ai đo, vì "xem vài frame" không phát hiện được lệch tiếng.
Nguyên tắc: máy đo những gì mắt không thấy; mắt (Claude, rồi user) chỉ soi
những gì máy không đo được. KHÔNG ĐẠT = không giao, không biện hộ.

Cách dùng (từ gốc "xuong-phim-claude"):
  Video:      python3 tools/nghiem-thu.py video "du-an/<x>/xuat-nhap/<file>.mp4"
                  [--khung ngang|doc] [--nhap] [--fps 30] [--anh]
              --anh: xuất thêm ảnh lưới 12 khung (contact sheet) để soi mắt
  Transcript: python3 tools/nghiem-thu.py transcript "du-an/<x>" [--nguon <file nguồn>]
              (phát hiện đoạn nói bị Whisper bỏ trống, mốc thời gian đảo, câu dài bất thường)
  Đồ họa:     python3 tools/nghiem-thu.py do-hoa "du-an/<x>/do-hoa" [--fps 30]
              (mọi file render: thời lượng khớp tên/props, fps, alpha còn không)

Kết quả: in bảng ĐẠT/KHÔNG ĐẠT/CẢNH BÁO, ghi <file>.nghiem-thu.json, mã thoát 1 nếu
có mục KHÔNG ĐẠT (để chuỗi lệnh dừng lại). Chạy được trên ffmpeg 4.4 (VM máy user).
"""
import argparse
import json
import os
import re
import subprocess
import sys

AV_TOL = 0.06           # hình - tiếng lệch quá 2 khung hình là lỗi
LUFS_TARGET = -14.0
LUFS_TOL = 1.0          # -15 … -13 đạt
TP_MAX = -1.0           # true peak dBTP
SIZES = {"ngang": (1920, 1080), "doc": (1080, 1920)}
PREVIEW_SIZES = {"ngang": (854, 480), "doc": (480, 854)}


class KQ:
    """Gom kết quả: dat / khong_dat / canh_bao."""

    def __init__(self):
        self.items = []

    def dat(self, m, s=""):
        self.items.append(("ĐẠT", m, s))

    def loi(self, m, s=""):
        self.items.append(("KHÔNG ĐẠT", m, s))

    def canh(self, m, s=""):
        self.items.append(("CẢNH BÁO", m, s))

    @property
    def fail(self):
        return any(k == "KHÔNG ĐẠT" for k, _, _ in self.items)

    def dump(self, path, extra=None):
        d = {"ket_luan": "KHÔNG ĐẠT" if self.fail else "ĐẠT",
             "muc": [{"trang_thai": k, "muc": m, "chi_tiet": s} for k, m, s in self.items]}
        if extra:
            d.update(extra)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)

    def show(self, title):
        print(f"\n{'=' * 72}\nNGHIỆM THU: {title}\n{'-' * 72}")
        icon = {"ĐẠT": "✓", "KHÔNG ĐẠT": "✗", "CẢNH BÁO": "⚠"}
        for k, m, s in self.items:
            print(f" {icon[k]} {k:<9} {m}" + (f"  ({s})" if s else ""))
        print("-" * 72)
        print(" KẾT LUẬN:", "KHÔNG ĐẠT - không giao, sửa rồi chạy lại" if self.fail else "ĐẠT")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    p = run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path])
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe không đọc được {path}")
    return json.loads(p.stdout)


def stream_info(info):
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    fmt_d = float(info["format"].get("duration") or 0)

    def dur(s):
        if not s:
            return None
        if s.get("duration"):
            return float(s["duration"])
        t = s.get("tags", {}).get("DURATION")
        if t:
            h, m, sec = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(sec)
        return fmt_d
    return v, a, dur(v), dur(a)


def fps_of(v):
    num, den = v.get("r_frame_rate", "0/1").split("/")
    return float(num) / float(den) if float(den) else 0.0


# ---------------------------------------------------------------- video
def cmd_video(args):
    path = args.file
    kq = KQ()
    info = probe(path)
    v, a, vd, ad = stream_info(info)

    # 1. Hình = tiếng (bất biến số một)
    if not v:
        kq.loi("Thiếu stream hình")
    if not a:
        kq.loi("Thiếu stream tiếng")
    if v and a:
        diff = vd - ad
        (kq.dat if abs(diff) <= AV_TOL else kq.loi)(
            f"Hình {vd:.3f}s / tiếng {ad:.3f}s (lệch {diff:+.3f}s, ngưỡng {AV_TOL}s)",
            "" if abs(diff) <= AV_TOL else "đúng lớp lỗi lệch hình-tiếng - kiểm từng part bằng assemble.py mới")

    # 2. Khớp với tổng part đã ghi (nếu assemble.py ghi nghiem-thu.json)
    side = os.path.splitext(path)[0] + ".nghiem-thu.json"
    if os.path.isfile(side):
        try:
            sd = json.load(open(side, encoding="utf-8"))
            tong = float(sd.get("tong_part", 0))
            if tong and v:
                (kq.dat if abs(vd - tong) <= 0.1 + 0.01 * int(sd.get("parts", 1)) else kq.loi)(
                    f"Khớp tổng part lúc dựng: {tong:.2f}s (thành phẩm {vd:.2f}s)")
        except Exception:
            pass

    # 3. Khung hình, fps, codec
    if v:
        w, h = int(v["width"]), int(v["height"])
        khung = args.khung or ("doc" if h > w else "ngang")
        exp = (PREVIEW_SIZES if args.nhap else SIZES)[khung]
        (kq.dat if (w, h) == exp else kq.canh)(f"Kích cỡ {w}x{h} (chuẩn {khung}: {exp[0]}x{exp[1]})")
        fps = fps_of(v)
        (kq.dat if abs(fps - args.fps) < 0.01 else kq.canh)(f"fps {fps:.3f} (chuẩn {args.fps})")
        ok_codec = v.get("codec_name") == "h264" and v.get("pix_fmt") == "yuv420p"
        (kq.dat if ok_codec else kq.canh)(f"Codec {v.get('codec_name')} {v.get('pix_fmt')} (chuẩn h264 yuv420p)")
        if v.get("color_transfer") in ("smpte2084", "arib-std-b67"):
            kq.loi(f"Thành phẩm còn HDR ({v['color_transfer']}) - thiếu tonemap (skill phim-mau-sac)")
    if a:
        ok_a = int(a.get("sample_rate", 0)) == 48000 and int(a.get("channels", 0)) == 2
        (kq.dat if ok_a else kq.canh)(f"Tiếng {a.get('codec_name')} {a.get('sample_rate')}Hz {a.get('channels')}ch (chuẩn aac 48000 2ch)")

    # 4. Âm lượng chuẩn (-14 LUFS, TP ≤ -1), im lặng dài, hình đứng
    if a:
        p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn",
                 "-af", "ebur128=peak=true,silencedetect=noise=-45dB:d=4", "-f", "null", "-"])
        err = p.stderr
        m_i = re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):])
        m_tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", err[err.rfind("Summary:"):])
        if m_i:
            lufs = float(m_i.group(1))
            (kq.dat if abs(lufs - LUFS_TARGET) <= LUFS_TOL else kq.loi)(
                f"Âm lượng tích hợp {lufs:.1f} LUFS (chuẩn {LUFS_TARGET}±{LUFS_TOL})")
        if m_tp:
            tp = float(m_tp.group(1))
            (kq.dat if tp <= TP_MAX else kq.canh)(f"True peak {tp:.1f} dBTP (≤ {TP_MAX})")
        sil = re.findall(r"silence_start: ([\d.]+)", err)
        sil_d = re.findall(r"silence_duration: ([\d.]+)", err)
        long_mid = [(float(s), float(d)) for s, d in zip(sil, sil_d) if float(s) > 1.0 and vd and float(s) + float(d) < vd - 1.0]
        if long_mid:
            kq.canh(f"{len(long_mid)} khoảng im lặng ≥4s giữa bài",
                    "; ".join(f"{s:.0f}s ({d:.0f}s)" for s, d in long_mid[:5]) + " - mất tiếng hay cố ý?")
        else:
            kq.dat("Không có khoảng im lặng dài bất thường giữa bài")
    if v:
        p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an",
                 "-vf", "scale=160:-2,freezedetect=n=0.003:d=4,blackdetect=d=3:pic_th=0.98", "-f", "null", "-"])
        fz = re.findall(r"freeze_start: ([\d.]+)", p.stderr)
        fz_mid = [float(t) for t in fz if 1.0 < float(t) < (vd or 1e9) - 5.0]
        # Quãng layout "slide" (bài giảng có slide) đứng hình là cố ý - bỏ khỏi cảnh báo
        mp = os.path.splitext(path)[0] + ".map.json"
        if os.path.isfile(mp):
            try:
                parts = json.load(open(mp, encoding="utf-8")).get("parts", [])
                static = [(q["start"], q["end"]) for q in parts if q.get("layout") == "slide"]
                fz_mid = [t for t in fz_mid if not any(a - 0.5 <= t <= b for a, b in static)]
            except Exception:
                pass
        if fz_mid:
            kq.canh(f"{len(fz_mid)} quãng hình đứng ≥4s", ", ".join(f"{t:.0f}s" for t in fz_mid[:6]) + " - đồ họa tĩnh hay lỗi?")
        else:
            kq.dat("Không có quãng hình đứng bất thường")
        bl = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", p.stderr)
        bl_mid = [(float(s), float(e)) for s, e in bl if float(s) > 0.5 and float(e) < (vd or 1e9) - 0.5]
        if bl_mid:
            kq.canh(f"{len(bl_mid)} quãng đen ≥3s giữa bài", ", ".join(f"{s:.0f}-{e:.0f}s" for s, e in bl_mid[:6]))

    # 5. Ảnh lưới để soi mắt
    if args.anh and v and vd:
        out = os.path.splitext(path)[0] + ".luoi.jpg"
        n = 12
        step = max(vd / n, 0.5)
        vf = (f"fps=1/{step:.4f},scale=480:-2,"
              f"drawtext=text='%{{pts\\:hms}}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6,"
              f"tile=4x3")
        p = run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", path, "-vf", vf, "-frames:v", "1", "-q:v", "3", out])
        if p.returncode != 0:  # drawtext thiếu font → bỏ chữ
            vf = f"fps=1/{step:.4f},scale=480:-2,tile=4x3"
            p = run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", path, "-vf", vf, "-frames:v", "1", "-q:v", "3", out])
        if p.returncode == 0:
            kq.dat(f"Ảnh lưới 12 khung: {out}", "stage lên và NHÌN: intro/outro đúng chỗ, bảng tên hiện, không khung đen/lệch crop")
        else:
            kq.canh("Không tạo được ảnh lưới", p.stderr[-200:])

    kq.show(os.path.basename(path))
    kq.dump(os.path.splitext(path)[0] + ".nghiem-thu.json",
            {"file": os.path.basename(path), "hinh": vd, "tieng": ad})
    sys.exit(1 if kq.fail else 0)


# ---------------------------------------------------------------- transcript
def cmd_transcript(args):
    """Whisper hay bỏ trống cả đoạn (đặc biệt sau khoảng lặng dài hay khi nói nhanh).
    Đối chiếu transcript với silences: quãng > 8s KHÔNG nằm trong khoảng lặng mà
    không có câu nào = nghi mất chữ → phải nghe lại / nhận dạng lại đoạn đó."""
    project = args.project.rstrip("/")
    tdir = os.path.join(project, "transcript")
    files = [args.nguon] if args.nguon else sorted(
        f[:-len(".transcript.json")] for f in os.listdir(tdir) if f.endswith(".transcript.json"))
    any_fail = False
    for base in files:
        base = os.path.splitext(base)[0] if base.endswith((".mp4", ".MP4", ".mov", ".MOV")) else base
        kq = KQ()
        tj = os.path.join(tdir, f"{base}.transcript.json")
        sj = os.path.join(tdir, f"{base}.silences.json")
        if not os.path.isfile(tj):
            print(f"! không thấy {tj}")
            continue
        data = json.load(open(tj, encoding="utf-8"))
        segs = data if isinstance(data, list) else data.get("segments", [])
        segs = [s for s in segs if "start" in s and "end" in s]
        sil = json.load(open(sj, encoding="utf-8")) if os.path.isfile(sj) else []
        src = None
        for ext in (".mp4", ".MP4", ".mov", ".MOV", ".m4v", ".mkv"):
            c = os.path.join(project, "nguon", base + ext)
            if os.path.isfile(c):
                src = c
                break
        total = probe(src)["format"]["duration"] if src else None
        total = float(total) if total else (segs[-1]["end"] if segs else 0)

        # thứ tự & chồng lấn
        bad_order = [i for i in range(1, len(segs)) if segs[i]["start"] < segs[i - 1]["end"] - 0.5]
        (kq.dat if not bad_order else kq.loi)(f"Mốc thời gian tăng dần ({len(segs)} câu)",
                                              "" if not bad_order else f"{len(bad_order)} câu đảo/chồng, ví dụ câu #{bad_order[0]}")
        long_seg = [s for s in segs if s["end"] - s["start"] > 25]
        if long_seg:
            kq.canh(f"{len(long_seg)} câu dài >25s", "Whisper gộp câu - phụ đề sẽ quá dài, cần tách")

        def in_silence(t0, t1):
            cov = 0.0
            for s in sil:
                cov += max(0.0, min(t1, s["end"]) - max(t0, s["start"]))
            return cov / max(t1 - t0, 1e-6) > 0.7

        gaps = []
        cur = 0.0
        for s in segs + [{"start": total, "end": total}]:
            if s["start"] - cur > 8.0 and not in_silence(cur, s["start"]):
                gaps.append((cur, s["start"]))
            cur = max(cur, s["end"])
        (kq.dat if not gaps else kq.loi)(
            f"Phủ kín lời nói ({total:.0f}s nguồn)",
            "" if not gaps else f"{len(gaps)} quãng >8s có tiếng mà không có chữ: "
            + ", ".join(f"{a:.0f}-{b:.0f}s" for a, b in gaps[:8]) + " → nhận dạng lại đoạn đó (Whisper bỏ đoạn)")
        if not sil:
            kq.canh("Không có silences.json để đối chiếu - chỉ kiểm được thứ tự")
        kq.show(f"transcript {base}")
        kq.dump(os.path.join(tdir, f"{base}.nghiem-thu.json"))
        any_fail |= kq.fail
    sys.exit(1 if any_fail else 0)


# ---------------------------------------------------------------- đồ họa
def cmd_do_hoa(args):
    """Đồ họa render từ Remotion: thời lượng đúng props, fps đúng, webm còn alpha."""
    kq = KQ()
    files = []
    for root, _, fs in os.walk(args.folder):
        files += [os.path.join(root, f) for f in fs if f.lower().endswith((".mp4", ".webm", ".mov"))]
    manifest = {}
    mf = os.path.join(args.folder, "do-hoa-manifest.json")
    if os.path.isfile(mf):
        manifest = json.load(open(mf, encoding="utf-8"))
    for f in sorted(files):
        info = probe(f)
        v, a, vd, ad = stream_info(info)
        name = os.path.relpath(f, args.folder)
        if not v:
            kq.loi(f"{name}: không có hình")
            continue
        fps = fps_of(v)
        fps_ok = abs(fps - args.fps) < 0.01
        note = f"{vd:.2f}s, {fps:.0f}fps, {v['width']}x{v['height']}, {v.get('pix_fmt')}"
        if f.lower().endswith(".webm"):
            # webm VP8/VP9 ghi alpha ở tag alpha_mode=1 (ffprobe vẫn báo yuv420p)
            has_alpha = (v.get("pix_fmt") in ("yuva420p", "yuva444p", "gbrap")
                         or str(v.get("tags", {}).get("alpha_mode", "0")) == "1")
            if not has_alpha:
                kq.loi(f"{name}: webm không có kênh alpha ({v.get('pix_fmt')}) - phủ lên sẽ che hết hình", note)
                continue
        if a and abs(vd - ad) > AV_TOL:
            kq.loi(f"{name}: hình {vd:.2f}s ≠ tiếng {ad:.2f}s", note)
            continue
        exp = manifest.get(os.path.basename(f), {}).get("durationInSeconds")
        if exp and abs(vd - float(exp)) > 0.1:
            kq.loi(f"{name}: dài {vd:.2f}s nhưng props yêu cầu {exp}s", note)
            continue
        (kq.dat if fps_ok else kq.canh)(f"{name}", note + ("" if fps_ok else f" - fps khác {args.fps}"))
    if not files:
        kq.canh("Không có file đồ họa nào trong " + args.folder)
    kq.show(f"đồ họa {args.folder}")
    kq.dump(os.path.join(args.folder, "nghiem-thu.json"))
    sys.exit(1 if kq.fail else 0)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("video")
    v.add_argument("file")
    v.add_argument("--khung", choices=["ngang", "doc"], default=None)
    v.add_argument("--nhap", action="store_true", help="bản nháp 480p")
    v.add_argument("--fps", type=float, default=30)
    v.add_argument("--anh", action="store_true", help="xuất ảnh lưới 12 khung để soi mắt")
    t = sub.add_parser("transcript")
    t.add_argument("project")
    t.add_argument("--nguon", default=None)
    d = sub.add_parser("do-hoa")
    d.add_argument("folder")
    d.add_argument("--fps", type=float, default=30)
    args = ap.parse_args()
    {"video": cmd_video, "transcript": cmd_transcript, "do-hoa": cmd_do_hoa}[args.cmd](args)


if __name__ == "__main__":
    main()
