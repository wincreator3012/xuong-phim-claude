#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐO ĐỒNG BỘ HÌNH-TIẾNG TRÊN PHIM THẬT: so thành phẩm với chính nguồn của nó tại nhiều mốc trải khắp phim.

    python3 tools/do-dong-bo.py "../Du an/<x>/xuat-hoan-chinh/<phim>.mp4" [--mau 12] [--cua-so 6] [--project "../Du an/<x>"]

Cần <phim>.map.json cạnh file (assemble.py ghi). Với mỗi part cắt (loại "cut") đủ dài, lấy một cửa sổ
vài giây và đo:
  - TIẾNG: trễ của tiếng thành phẩm so với tiếng nguồn cùng mốc (tiếng chủ theo audio_src/audio_in của
    map nếu là multicam, không thì chính file nguồn), bằng tương quan pha GCC-PHAT. Đơn vị mili giây,
    dương = thành phẩm trễ hơn nguồn.
  - HÌNH: trễ của hình thành phẩm so với hình nguồn cùng mốc, bằng tương quan năng lượng chuyển động
    trên mốc pts thật (nội suy dưới một khung).
Rồi báo trễ HÌNH - TIẾNG từng mốc, độ trôi theo thời gian (ms mỗi phút) và kết luận. Mốc dương nghĩa là
hình đến muộn hơn tiếng (tiếng đi trước hình): người xem nhận ra khi vượt khoảng 45 ms, nên ngưỡng ở đây
là 50 ms; hình đi trước tiếng dung sai lớn hơn nhưng vẫn giữ ±50 ms.

Đây là lớp kiểm thứ hai, bổ sung cho tools/kiem-dong-bo.py (dựng thử chớp/click, đo tuyệt đối) và cho
check_av() (chỉ so thời lượng). Bắt buộc chạy cho phim multicam trước khi giao bản chính.
Đoạn hình tĩnh (ít chuyển động) tự bị bỏ qua vì tương quan yếu; cần ít nhất 5 mốc đo được.
Thoát mã 0 = ĐẠT. Cần ffmpeg, ffprobe, numpy.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

SR = 16000
W, H = 96, 54


def run(cmd):
    return subprocess.run(cmd, capture_output=True)


def pcm(path, ss, dur):
    r = run(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{dur}", "-i", path, "-vn", "-ac", "1",
             "-ar", str(SR), "-f", "s16le", "-"])
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32)


def lag_gcc(a, b, maxlag=0.4):
    n = min(len(a), len(b))
    if n < SR * 2:
        return None, 0.0
    a = a[:n] - a[:n].mean()
    b = b[:n] - b[:n].mean()
    N = 1 << int(np.ceil(np.log2(2 * n)))
    R = np.fft.rfft(a, N) * np.conj(np.fft.rfft(b, N))
    R /= np.abs(R) + 1e-9
    c = np.fft.irfft(R, N)
    m = int(maxlag * SR)
    c = np.concatenate([c[-m:], c[:m + 1]])
    k = int(np.argmax(c)) - m
    return k / SR * 1000.0, float(c.max())


def chuyen_dong(path, ss, dur):
    """(năng lượng chuyển động giữa hai khung liền nhau, mốc thời gian thật của chúng theo pts).
    Khung đầu sau -ss thường có pts lẻ (0 đến 1 khung), bỏ qua nó là sai một khung: dùng pts thật."""
    r = run(["ffmpeg", "-v", "info", "-ss", f"{ss:.4f}", "-t", f"{dur}", "-i", path, "-an", "-vf",
             f"scale={W}:{H},format=gray,showinfo", "-vsync", "0", "-f", "rawvideo", "-"])
    v = np.frombuffer(r.stdout, dtype=np.uint8)
    n = len(v) // (W * H)
    if n < 20:
        return None, None
    import re
    pts = [float(x) for x in re.findall(r"pts_time:\s*(-?[\d.]+)", r.stderr.decode("utf-8", "ignore"))][:n]
    if len(pts) < n:
        return None, None
    v = v[:n * W * H].reshape(n, W * H).astype(np.float32)
    e = np.abs(np.diff(v, axis=0)).mean(axis=1)
    t = (np.array(pts[:-1]) + np.array(pts[1:])) / 2.0
    return e, t


def fps_of(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=avg_frame_rate", "-of",
             "csv=p=0", path]).stdout.decode().split()[0].strip(",")
    a, _, b = r.partition("/")
    return float(a) / float(b or 1)


def lag_hinh(e_out, t_out, e_src, t_src, L):
    g = np.arange(max(t_out[0], t_src[0]) + 0.2, min(t_out[-1], t_src[-1]) - 0.2, 0.001)
    if len(g) < 2000:
        return None, 0.0
    a = np.interp(g, t_out, e_out)
    b = np.interp(g, t_src, e_src)
    if a.std() < 1e-6 or b.std() < 1e-6:
        return None, 0.0
    a = (a - a.mean()) / a.std()
    b = (b - b.mean()) / b.std()
    best = (-2.0, 0)
    for lag in range(-150, 151):
        c = np.mean(a[lag:] * b[:len(b) - lag]) if lag >= 0 else np.mean(a[:lag] * b[-lag:])
        if c > best[0]:
            best = (c, lag)
    return float(best[1]), float(best[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--mau", type=int, default=12, help="số mốc đo, trải đều phim")
    ap.add_argument("--cua-so", type=float, default=6.0, help="độ dài mỗi cửa sổ đo (giây)")
    ap.add_argument("--project", default=None, help="thư mục dự án (mặc định: cha của xuat-nhap hoặc xuat-hoan-chinh)")
    ap.add_argument("--ngat", type=float, default=50.0, help="ngưỡng |hình - tiếng| mỗi mốc (ms)")
    args = ap.parse_args()

    path = os.path.abspath(args.file)
    mp = os.path.splitext(path)[0] + ".map.json"
    if not os.path.isfile(mp):
        print(f"ĐO ĐỒNG BỘ: KHÔNG ĐỦ DỮ LIỆU (không thấy {mp}; assemble.py ghi cạnh thành phẩm)")
        sys.exit(2)
    parts = json.load(open(mp, encoding="utf-8"))["parts"]
    project = os.path.abspath(args.project) if args.project else os.path.dirname(os.path.dirname(path))
    cand = [p for p in parts if p.get("kind") == "cut" and p["dur"] >= args.cua_so + 2 and not p.get("video_from")]
    if len(cand) < 5:
        print("ĐO ĐỒNG BỘ: KHÔNG ĐỦ DỮ LIỆU (quá ít part cắt đủ dài để đo, cần ít nhất 5)")
        sys.exit(2)
    step = max(1, len(cand) / args.mau)
    chon = [cand[int(i * step)] for i in range(min(args.mau, len(cand)))]
    L = args.cua_so
    kq = []
    print(f"Đo {len(chon)} mốc trên {os.path.basename(path)} (cửa sổ {L:.0f} s)")
    for p in chon:
        s_out = p["start"] + 1.0
        src = os.path.join(project, p["src"])
        if p.get("audio_src"):
            ref_a = os.path.join(project, p["audio_src"])
            t_ref = p["audio_in"] + 1.0
        else:
            ref_a, t_ref = src, p["in"] + 1.0
        a = pcm(path, s_out, L)
        b = pcm(ref_a, t_ref, L)
        la, qa = lag_gcc(a, b)
        eo, to = chuyen_dong(path, s_out, L)
        es, ts = chuyen_dong(src, p["in"] + 1.0, L)
        lv, qv = (None, 0.0)
        if eo is not None and es is not None:
            lv, qv = lag_hinh(eo, to, es, ts, L)
        ok = la is not None and qa >= 0.15 and lv is not None and qv >= 0.5
        d = (lv - la) if ok else None
        kq.append({"t": p["start"], "part": p["part"], "src": os.path.basename(p["src"]), "la": la, "qa": qa,
                   "lv": lv, "qv": qv, "d": d})
        ghi = (f"tiếng {la:+6.1f} ms (q{qa:.2f}) | hình {lv:+6.1f} ms (q{qv:.2f}) | hình - tiếng {d:+6.1f} ms"
               if ok else f"bỏ qua (tương quan yếu: tiếng q{qa:.2f}, hình q{qv:.2f})")
        print(f"  {p['start'] / 60:6.1f} phút  part {p['part']:3d}  {os.path.basename(p['src']):18s} {ghi}", flush=True)
    do = [k for k in kq if k["d"] is not None]
    if len(do) < 5:
        print("ĐO ĐỒNG BỘ: KHÔNG ĐỦ DỮ LIỆU (dưới 5 mốc đo được) - tăng --mau hoặc --cua-so")
        sys.exit(2)
    t = np.array([k["t"] for k in do])
    d = np.array([k["d"] for k in do])
    la = np.array([k["la"] for k in do])
    lv = np.array([k["lv"] for k in do])
    sl_a = np.polyfit(t, la, 1)[0] * 60.0
    sl_v = np.polyfit(t, lv, 1)[0] * 60.0
    loi = []
    if np.abs(d).max() > args.ngat:
        loi.append(f"mốc lệch {d[np.abs(d).argmax()]:+.0f} ms tại {t[np.abs(d).argmax()] / 60:.1f} phút (ngưỡng ±{args.ngat:.0f})")
    if np.abs(la).max() > 25:
        loi.append(f"tiếng lệch {la[np.abs(la).argmax()]:+.0f} ms so với nguồn tại {t[np.abs(la).argmax()] / 60:.1f} phút (ngưỡng ±25): "
                   "mốc map.json hoặc nối tiếng có sai số")
    if abs(sl_a) > 15 or abs(sl_v) > 15:
        loi.append(f"trôi theo thời gian: tiếng {sl_a:+.1f}, hình {sl_v:+.1f} ms/phút (ngưỡng ±15)")
    print(f"  Tổng: {len(do)} mốc | hình - tiếng trung bình {d.mean():+.1f} ms, khoảng [{d.min():+.0f}, {d.max():+.0f}] | "
          f"trôi tiếng {sl_a:+.1f}, hình {sl_v:+.1f} ms/phút")
    if loi:
        print("ĐO ĐỒNG BỘ: KHÔNG ĐẠT - " + "; ".join(loi))
        raise SystemExit(1)
    print("ĐO ĐỒNG BỘ: ĐẠT")


if __name__ == "__main__":
    main()
