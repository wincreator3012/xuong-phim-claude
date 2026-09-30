#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIỂM ĐỒNG BỘ HÌNH-TIẾNG TUYỆT ĐỐI bằng dựng thử có chớp sáng và tiếng click.

    python3 tools/kiem-dong-bo.py [--giu] [--thu-muc <thư mục>] [--ngat 40]

Vì sao có công cụ này: check_av() chỉ so THỜI LƯỢNG hình với tiếng, còn lệch căn chỉnh cục bộ hay
lệch cộng dồn qua nhiều part (ví dụ mỗi part dư một khung hình đầu đoạn) vẫn có thể ĐẠT. Ở đây
nguồn giả có chớp trắng ba khung và một tiếng click bắt đầu ĐÚNG cùng một thời điểm (nằm trên lưới
khung của nguồn 29.97 fps), nên phim dựng ra đo được trực tiếp "tiếng - hình" tại từng sự kiện.

Dựng thử đi đúng đường thật của assemble.py: 12 đoạn cắt tại mốc lẻ (không trùng lưới khung),
tiếng chủ tách riêng (audioSrc/audioIn như multicam), một thẻ chèn (insert) giữa phim, fade đầu
và cuối, nguồn 29.97 fps ra 30 fps. Chưa ĐẠT thì không được dựng thật bằng assemble.py này.

Tiêu chí ĐẠT (tính trên mọi cặp chớp-click còn thấy được sau fade):
  - mỗi cặp lệch không quá --ngat mili giây (mặc định 40: một khung hình 30 fps là 33 ms);
  - độ lệch trung bình không quá 20 ms;
  - độ trôi (đường thẳng khớp theo thời gian) không quá 15 ms mỗi phút, và không quá 25 ms
    giữa đầu và cuối phim;
  - còn ít nhất 60% cặp sự kiện đo được.
Thoát mã 0 = ĐẠT. Cần ffmpeg, ffprobe, numpy. Không cần mạng, không cần model.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
FPS_SRC = 30000 / 1001
SR = 48000
NGUON_GIAY = 100.0
W, H = 320, 180


def sh(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, **kw)
    if p.returncode != 0:
        sys.stderr.write((p.stderr or b"")[-2000:].decode("utf-8", "ignore"))
        raise SystemExit("! Lệnh lỗi: " + " ".join(cmd[:6]) + " ...")
    return p


def tao_nguon(pj):
    """a.mp4 (chớp + click, 29.97 fps, có tiếng), master.wav (cùng tiếng, mono 48 kHz), card.mp4 (thẻ chèn)."""
    ng = os.path.join(pj, "nguon")
    os.makedirs(ng, exist_ok=True)
    n_khung = int(NGUON_GIAY * FPS_SRC)
    # sự kiện mỗi ~0,9 s, đặt đúng trên lưới khung nguồn
    k_khung = [int(round(i * 0.9 * FPS_SRC)) for i in range(1, int(NGUON_GIAY / 0.9) - 1)]
    tieng = (np.random.RandomState(7).randn(int(NGUON_GIAY * SR)) * 0.002).astype(np.float32)
    burst = (0.8 * np.sin(2 * np.pi * 1000 * np.arange(int(0.004 * SR)) / SR)).astype(np.float32)
    flash = set()
    for f in k_khung:
        t0 = int(round(f / FPS_SRC * SR))
        tieng[t0:t0 + len(burst)] += burst
        flash.update((f, f + 1, f + 2))
    wav = os.path.join(ng, "master.wav")
    pcm = (np.clip(tieng, -1, 1) * 32767).astype("<i2").tobytes()
    import wave
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm)
    # hình
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}",
                          "-r", "30000/1001", "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30000/1001", "-c:a", "aac", "-b:a", "128k",
                          "-shortest", os.path.join(ng, "a.mp4")], stdin=subprocess.PIPE)
    den = np.full((H, W), 16, dtype=np.uint8).tobytes()
    trang = np.full((H, W), 235, dtype=np.uint8).tobytes()
    for i in range(n_khung):
        p.stdin.write(trang if i in flash else den)
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("! không tạo được nguồn giả")
    # thẻ chèn: 3 giây, tiếng sine nhẹ, nền màu, 30 fps
    sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x224466:s=320x180:r=30:d=3",
        "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=3", "-c:v", "libx264", "-pix_fmt",
        "yuv420p", "-c:a", "aac", "-shortest", os.path.join(ng, "card.mp4")])
    return len(k_khung)


MOC = [(3.2, 9.7), (9.7, 14.35), (14.35, 21.1), (21.1, 27.9), (27.9, 33.33), (33.33, 41.0),
       ("card",), (41.0, 48.6), (48.6, 55.2), (55.2, 62.9), (62.9, 70.4), (70.4, 77.7), (77.7, 84.5),
       (84.5, 91.3), (91.3, 97.11)]


def tao_timeline(pj):
    segs = []
    dau = True
    for m in MOC:
        if m[0] == "card":
            segs.append({"type": "insert", "src": "nguon/card.mp4"})
            continue
        s = {"type": "video", "src": "nguon/a.mp4", "in": m[0], "out": m[1], "snap": False,
             "audioSrc": "nguon/master.wav", "audioIn": m[0]}
        if dau:
            s["fadeIn"] = 0.5
            dau = False
        segs.append(s)
    segs[-1]["fadeOut"] = 0.5
    tl = {"aspect": "ngang", "fps": 30, "segments": segs}
    json.dump(tl, open(os.path.join(pj, "timeline.json"), "w"), indent=1)


def su_kien(path):
    """(mốc chớp [giây], mốc click [giây]) trong file thành phẩm, theo pts thật của hình."""
    r = sh(["ffmpeg", "-v", "error", "-i", path, "-an", "-vf", "scale=32:18,format=gray", "-vsync", "0",
            "-f", "rawvideo", "-"])
    v = np.frombuffer(r.stdout, dtype=np.uint8).reshape(-1, 18 * 32).mean(axis=1)
    q = sh(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "frame=best_effort_timestamp_time",
            "-of", "csv=p=0", path]).stdout.decode().split()
    pt = np.array([float(x.strip(",")) for x in q if x.strip(",").replace(".", "", 1).isdigit()])
    n = min(len(v), len(pt))
    idx = np.where(v[:n] > 120)[0]
    fl = []
    for i in idx:
        if not fl or pt[i] - fl[-1] > 0.5:
            fl.append(float(pt[i]))
    r = sh(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    a = np.abs(np.frombuffer(r.stdout, dtype=np.float32))
    ia = np.where(a > 0.3 * a.max())[0] / SR
    ck = []
    for t in ia:
        if not ck or t - ck[-1] > 0.5:
            ck.append(float(t))
    return fl, ck


def do(path, ngat):
    fl, ck = su_kien(path)
    fl_a = np.array(fl)
    cap = []
    for t in ck:
        if len(fl_a) == 0:
            break
        j = int(np.argmin(np.abs(fl_a - t)))
        if abs(fl_a[j] - t) < 0.25:
            cap.append((t, (t - fl_a[j]) * 1000.0))
    return fl, ck, cap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--giu", action="store_true", help="giữ thư mục dựng thử để soi")
    ap.add_argument("--thu-muc", default=None)
    ap.add_argument("--ngat", type=float, default=40.0, help="ngưỡng mỗi cặp (ms)")
    ap.add_argument("--assemble", default=os.path.join(TOOLS, "assemble.py"), help="đường dẫn assemble.py cần thử (mặc định bản hiện hành)")
    args = ap.parse_args()

    pj = args.thu_muc or tempfile.mkdtemp(prefix="kiem-dong-bo-")
    os.makedirs(pj, exist_ok=True)
    print(f"[1/3] Tạo nguồn giả ở {pj} …", flush=True)
    tao_nguon(pj)
    tao_timeline(pj)
    print("[2/3] Dựng thử bằng assemble.py (bản nháp 480p) …", flush=True)
    r = subprocess.run([sys.executable, args.assemble, "--project", pj, "--preview",
                        "--out", "kdb-nhap1"], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-1500:], r.stderr[-2500:])
        print("KIỂM ĐỒNG BỘ: KHÔNG ĐẠT (assemble.py dừng - xem lỗi ở trên)")
        raise SystemExit(1)
    out = os.path.join(pj, "xuat-nhap", "kdb-nhap1.mp4")
    if not os.path.isfile(out):
        print("KIỂM ĐỒNG BỘ: KHÔNG ĐẠT (assemble.py chạy xong nhưng không ra file thành phẩm)")
        raise SystemExit(1)
    print("[3/3] Đo chớp - click trên thành phẩm …", flush=True)
    fl, ck, cap = do(out, args.ngat)
    if len(cap) < 10:
        print(f"KIỂM ĐỒNG BỘ: KHÔNG ĐẠT (chỉ ghép được {len(cap)} cặp chớp-click; chớp {len(fl)}, click {len(ck)})")
        raise SystemExit(1)
    t = np.array([c[0] for c in cap])
    d = np.array([c[1] for c in cap])
    slope = np.polyfit(t, d, 1)[0] * 60.0          # ms mỗi phút
    dau_cuoi = abs(d[-5:].mean() - d[:5].mean())
    ty_le = len(cap) / max(1, len(ck))
    loi = []
    if np.abs(d).max() > args.ngat:
        loi.append(f"có cặp lệch {d[np.abs(d).argmax()]:+.0f} ms (ngưỡng ±{args.ngat:.0f}) tại {t[np.abs(d).argmax()]:.1f} s")
    if abs(d.mean()) > 20:
        loi.append(f"lệch trung bình {d.mean():+.0f} ms (ngưỡng ±20)")
    if abs(slope) > 15:
        loi.append(f"trôi {slope:+.1f} ms/phút (ngưỡng ±15)")
    if dau_cuoi > 25:
        loi.append(f"đầu và cuối phim chênh {dau_cuoi:.0f} ms (ngưỡng 25)")
    if ty_le < 0.6:
        loi.append(f"chỉ đo được {ty_le * 100:.0f}% sự kiện (ngưỡng 60%)")
    print(f"  {len(cap)} cặp | tiếng - hình: trung bình {d.mean():+.1f} ms, khoảng [{d.min():+.0f}, {d.max():+.0f}] ms, "
          f"trôi {slope:+.1f} ms/phút, đầu-cuối {dau_cuoi:.0f} ms")
    if not args.giu and not args.thu_muc:
        shutil.rmtree(pj, ignore_errors=True)
    if loi:
        print("KIỂM ĐỒNG BỘ: KHÔNG ĐẠT - " + "; ".join(loi))
        print("  → Đây là lớp lỗi 'lệch hình-tiếng': không dựng thật bằng assemble.py này. Xem docs/BAI-HOC.md chủ đề "
              "\"Đồng bộ hình tiếng\" và docs/QUY-TRINH-KY-THUAT.md mục \"Phòng ngừa lớp lỗi ngầm\".")
        raise SystemExit(1)
    print("KIỂM ĐỒNG BỘ: ĐẠT")


if __name__ == "__main__":
    main()
