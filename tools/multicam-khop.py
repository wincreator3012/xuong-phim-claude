#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỒNG BỘ MULTICAM bằng đối chiếu âm thanh: đặt mọi file của mọi góc lên MỘT trục thời gian chung.

Cách dùng (từ gốc "xuong-phim-claude"):
  python3 tools/multicam-khop.py "du-an/<x>" [--chu toan] [--cau-hinh multicam.json]

Cấu trúc nguồn đề nghị: du-an/<x>/nguon/<tên góc>/<các file quay của góc đó>
  nguon/toan/A001.MP4            ← góc toàn (chạy liên tục là tốt nhất: làm trục chuẩn)
  nguon/an/IMG_1.MOV, IMG_2.MOV   ← góc cận người thứ nhất (máy tự tách file vẫn được)
  nguon/khach/C001.MP4           ← góc cận khách
  nguon/tieng/recorder.wav       ← (tuỳ chọn) file tiếng riêng, không có hình
Hoặc tự soạn du-an/<x>/multicam.json {"goc": [{"ten": "toan", "files": [...], "nguoi": null,
  "loai": "toan|can|tieng"}, ...]} rồi truyền --cau-hinh.

Thuật toán: rút tiếng mỗi file về 8 kHz mono (ffmpeg), tính đường bao năng lượng log
[log-energy envelope] 100 mẫu/giây có lọc trôi; tương quan chéo bằng FFT giữa đường bao của
file và đường bao của trục chuẩn → lệch thô 10 ms; tinh lại quanh đỉnh bằng đường bao 1 kHz →
~1 ms. Đo trôi đồng hồ [clock drift] bằng cách tương quan riêng ba đoạn đầu/giữa/cuối và khớp
đường thẳng (ppm). Đường bao (không phải sóng thô) chịu được tạp âm phòng, mic khác nhau,
khoảng cách khác nhau. Tin cậy = đỉnh/đỉnh phụ (cách > 1 s) và r = Pearson đường bao tại lag; đỉnh/phụ < 1.1 hay r < 0.2 là nghi ngờ (r thật với lời nói cùng phòng thường 0.4-0.8).

Kết quả: du-an/<x>/multicam.json (bổ sung/ghi mới) với từng file: offset (giây, mốc bắt đầu
file trên trục chung), dur, drift_ppm, tin_cay, snr_db; góc nào phủ đoạn nào; đề xuất track
tiếng chủ (SNR cao nhất). Mọi mốc trong timeline multicam sau đó dùng trục chung này.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys

# Thư viện Python cài riêng vào tools/pylib (tools/cai-dat.py lo việc này) - VM Cowork
# không giữ pip install qua các phiên, nên thư viện phải nằm trong thư mục xưởng.
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylib"))
import numpy as np

SR = 8000          # Hz tiếng rút ra
HOP = 80           # 80 mẫu = 10 ms → đường bao 100 Hz
FINE_HOP = 8       # 1 ms
EXTS = (".mp4", ".mov", ".m4v", ".mkv", ".mts", ".wav", ".m4a", ".mp3", ".aac", ".flac")


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"! Lệnh lỗi: {' '.join(cmd)}\n{p.stderr.decode(errors='ignore')[-600:]}")
    return p


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def probe(path):
    p = sh(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path])
    info = json.loads(p.stdout)
    has_v = any(s["codec_type"] == "video" for s in info["streams"])
    has_a = any(s["codec_type"] == "audio" for s in info["streams"])
    return float(info["format"].get("duration") or 0), has_v, has_a


def audio_8k(path):
    """Đọc toàn bộ tiếng về mảng float32 8 kHz mono (2 giờ ≈ 230 MB - đủ cho VM 3.8 GB)."""
    p = sh(["ffmpeg", "-hide_banner", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
            "-f", "s16le", "-acodec", "pcm_s16le", "-"])
    return np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def energy(x, hop):
    n = len(x) // hop
    if n < 10:
        return np.zeros(10, dtype=np.float32)
    return (x[: n * hop].reshape(n, hop) ** 2).mean(axis=1)


def envelope(x, hop):
    """Đường bao log-năng lượng có sàn (floor = phân vị 20 của năng lượng, tức mức nền của chính
    file) rồi chuẩn hoá z-score. Sàn theo file giúp mic khác nhau/khoảng cách khác nhau vẫn so
    được; KHÔNG lọc trôi (đã thử: lọc trôi phá cấu trúc lượt lời và tạo đỉnh giả)."""
    e = energy(x, hop)
    eps = float(np.percentile(e, 20)) + 1e-9
    le = np.log10(e + eps)
    return ((le - le.mean()) / (le.std() + 1e-9)).astype(np.float32)


def rms_env(x, hop):
    e = np.sqrt(energy(x, hop))
    return ((e - e.mean()) / (e.std() + 1e-9)).astype(np.float32)


def xcorr_offset(ref, sig, hop, lag_min=None, lag_max=None):
    """Tìm lag (giây) sao cho sig(t) ≈ ref(t + lag): lag > 0 → sig bắt đầu SAU ref lag giây.
    lag_min/lag_max (giây): giới hạn vùng tìm (dùng khi đã có ước lượng thô).
    Trả (lag_s, tin_cay) với tin_cay = đỉnh / đỉnh phụ cao nhất cách xa > 1 s (>= 1)."""
    n = len(ref) + len(sig)
    nfft = 1 << (n - 1).bit_length()
    R = np.fft.rfft(ref - ref.mean(), nfft)
    S = np.fft.rfft(sig - sig.mean(), nfft)
    cc = np.fft.irfft(R * np.conj(S), nfft)
    cc = np.concatenate([cc[-(len(sig) - 1):], cc[: len(ref)]])  # lag từ -(len(sig)-1) … len(ref)-1
    lags = np.arange(-(len(sig) - 1), len(ref)) * hop / SR
    if lag_min is not None or lag_max is not None:
        m = np.ones(len(lags), dtype=bool)
        if lag_min is not None:
            m &= lags >= lag_min
        if lag_max is not None:
            m &= lags <= lag_max
        cc = np.where(m, cc, -np.inf)
    k = int(np.argmax(cc))
    peak = cc[k]
    far = np.abs(lags - lags[k]) > 1.0
    second = np.max(cc[far]) if far.any() and np.isfinite(cc[far]).any() else 1e-9
    conf = float(peak / max(second, 1e-9)) if second > 0 else 99.0
    return float(lags[k]), conf


def pearson_at(er, es, lag_frames):
    """Hệ số tương quan Pearson của hai đường bao trên phần chồng lấn tại lag đã chọn (0-1, chất lượng khớp)."""
    if lag_frames >= 0:
        a, b = er[lag_frames:], es
    else:
        a, b = er, es[-lag_frames:]
    m = min(len(a), len(b))
    if m < 100:
        return 0.0
    a, b = a[:m], b[:m]
    return float(np.corrcoef(a, b)[0, 1])


def xcorr_multi(ref_x, sig_x):
    """Hai tầng độc lập rồi đối chiếu: (1) đường bao log 100 Hz toàn cục; (2) đường bao RMS
    trong ±3 s quanh (1). Trả (lag, tin_cay, r): tin_cay = đỉnh/đỉnh phụ của tầng 1, r = Pearson
    của đường bao log tại lag cuối (> 0.4 là khớp chắc với lời nói thật)."""
    er, es = envelope(ref_x, HOP), envelope(sig_x, HOP)
    lag1, conf1 = xcorr_offset(er, es, HOP)
    rr, rs = rms_env(ref_x, HOP), rms_env(sig_x, HOP)
    lag2, conf2 = xcorr_offset(rr, rs, HOP, lag_min=lag1 - 3.0, lag_max=lag1 + 3.0)
    lag = lag2 if abs(lag2 - lag1) <= 0.5 else lag1
    r = pearson_at(er, es, int(round(lag * SR / HOP)))
    return lag, conf1, r


def refine(ref_x, sig_x, coarse_lag, win_s=90.0):
    """Tinh lại quanh coarse_lag bằng đường bao 1 ms trên một cửa sổ chung ~90 s."""
    # chọn cửa sổ nằm trong phần chồng lấn của hai file
    ov_start = max(0.0, coarse_lag)                       # trên trục ref
    ov_end = min(len(ref_x) / SR, coarse_lag + len(sig_x) / SR)
    if ov_end - ov_start < 20:
        return coarse_lag
    mid = (ov_start + ov_end) / 2
    a = max(ov_start, mid - win_s / 2)
    b = min(ov_end, a + win_s)
    r = ref_x[int(a * SR): int(b * SR)]
    s = sig_x[int((a - coarse_lag) * SR): int((b - coarse_lag) * SR)]
    if len(r) < SR * 5 or len(s) < SR * 5:
        return coarse_lag
    m = min(len(r), len(s))
    er, es = envelope(r[:m], FINE_HOP), envelope(s[:m], FINE_HOP)
    d, conf = xcorr_offset(er, es, FINE_HOP)
    if abs(d) > 0.05 or conf < 1.2:    # tinh chỉnh chỉ được phép dịch trong ±50 ms
        return coarse_lag
    return coarse_lag + d


def drift_ppm(ref_x, sig_x, lag, n_probe=3, probe_s=120.0):
    """Đo trôi: tương quan 3 đoạn dọc phần chồng lấn, khớp đường thẳng lệch(t) = a + b·t."""
    ov_start = max(0.0, lag)
    ov_end = min(len(ref_x) / SR, lag + len(sig_x) / SR)
    span = ov_end - ov_start
    if span < probe_s * 2.5:
        return 0.0, []
    pts = []
    for i in range(n_probe):
        a = ov_start + (span - probe_s) * i / (n_probe - 1)
        r = ref_x[int(a * SR): int((a + probe_s) * SR)]
        s = sig_x[int((a - lag) * SR): int((a - lag + probe_s) * SR)]
        m = min(len(r), len(s))
        if m < SR * 30:
            continue
        d, conf = xcorr_offset(envelope(r[:m], HOP), envelope(s[:m], HOP), HOP)
        if conf >= 1.2 and abs(d) < 1.0:
            pts.append((a + probe_s / 2, d))
    if len(pts) < 2:
        return 0.0, pts
    t = np.array([p[0] for p in pts])
    d = np.array([p[1] for p in pts])
    b = np.polyfit(t, d, 1)[0]
    return float(b * 1e6), [(round(x, 1), round(y, 4)) for x, y in pts]


def snr_db(x):
    raw_db = 10 * np.log10(energy(x, HOP) + 1e-10)
    return float(np.percentile(raw_db, 90) - np.percentile(raw_db, 10))


def discover(project):
    src = os.path.join(project, "nguon")
    goc = []
    for d in sorted(os.listdir(src)):
        p = os.path.join(src, d)
        if not os.path.isdir(p):
            continue
        files = sorted([f for f in os.listdir(p) if f.lower().endswith(EXTS)], key=natural_key)
        if not files:
            continue
        loai = "tieng" if d.lower().startswith("tieng") else ("toan" if "toan" in d.lower() else "can")
        goc.append({"ten": d, "loai": loai, "nguoi": None if loai != "can" else d,
                    "files": [os.path.join("nguon", d, f) for f in files]})
    return goc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--chu", default=None, help="tên góc làm trục chuẩn (mặc định: góc 'toan' hoặc góc ít file nhất)")
    ap.add_argument("--cau-hinh", default=None, help="multicam.json soạn tay (thay cho quét nguon/<góc>/)")
    ap.add_argument("--tron-tieng", action="store_true",
                    help="trộn tiếng các góc cận (mic gần từng người) đã căn offset thành nguon/tieng-chu.wav làm track chủ")
    args = ap.parse_args()
    project = args.project.rstrip("/")

    if args.cau_hinh:
        cfg = json.load(open(args.cau_hinh, encoding="utf-8"))
        goc = cfg["goc"]
    else:
        goc = discover(project)
    if len(goc) < 2:
        sys.exit("! Cần ít nhất 2 góc (nguon/<góc>/ hoặc --cau-hinh)")

    # góc chuẩn: --chu, hoặc góc 'toan' có 1 file, hoặc góc ít file nhất
    def pick_master():
        if args.chu:
            return next(g for g in goc if g["ten"] == args.chu)
        one = [g for g in goc if len(g["files"]) == 1 and g["loai"] != "tieng"]
        for g in one:
            if g["loai"] == "toan":
                return g
        return min(goc, key=lambda g: (len(g["files"]), g["loai"] == "tieng"))
    master = pick_master()
    if len(master["files"]) > 1:
        print(f"  ⚠ góc chuẩn '{master['ten']}' có {len(master['files'])} file - các file này được xếp "
              "NỐI TIẾP giả định không có khoảng nghỉ; nếu có nghỉ giữa các file, mốc sẽ sai. "
              "Nên chọn --chu là góc quay liên tục.", flush=True)

    print(f"[1/3] Rút tiếng góc chuẩn '{master['ten']}' …", flush=True)
    ref_parts, ref_offsets, t = [], [], 0.0
    for f in master["files"]:
        x = audio_8k(os.path.join(project, f))
        ref_parts.append(x)
        ref_offsets.append(t)
        t += len(x) / SR
    ref_x = np.concatenate(ref_parts)
    total = len(ref_x) / SR

    result = {"truc_chuan": master["ten"], "tong_dai": round(total, 2), "goc": []}
    print(f"[2/3] Khớp từng file của các góc còn lại (trục chuẩn dài {total/60:.1f} phút) …", flush=True)
    for g in goc:
        entry = {"ten": g["ten"], "loai": g["loai"], "nguoi": g.get("nguoi"), "files": []}
        for i, f in enumerate(g["files"]):
            full = os.path.join(project, f)
            dur, has_v, has_a = probe(full)
            if g is master:
                x = ref_parts[i]
                off, conf, r, ppm, probes = ref_offsets[i], 99.0, 1.0, 0.0, []
            else:
                if not has_a:
                    print(f"  ! {f}: không có tiếng - không khớp được, đặt tay", flush=True)
                    entry["files"].append({"file": f, "dur": round(dur, 2), "offset": None, "co_hinh": has_v})
                    continue
                x = audio_8k(full)
                lag, conf, r = xcorr_multi(ref_x, x)
                lag = refine(ref_x, x, lag)
                ppm, probes = drift_ppm(ref_x, x, lag)
                off = lag
            snr = snr_db(x)
            fe = {"file": f, "dur": round(dur, 2), "offset": round(off, 3), "ket_thuc": round(off + dur, 3),
                  "tin_cay": round(conf, 2), "khop_r": round(r, 3), "drift_ppm": round(ppm, 1), "snr_db": round(snr, 1),
                  "co_hinh": has_v}
            if g is not master and (conf < 1.1 or r < 0.2):
                fe["canh_bao"] = ("khớp yếu (đỉnh/đỉnh phụ %.2f, r %.2f) - kiểm tay bằng câu nói chung ở hai góc "
                                  "hoặc file không cùng buổi" % (conf, r))
            if abs(ppm) > 30:
                fe["canh_bao_drift"] = (f"trôi {ppm:.0f} ppm ≈ {abs(ppm) * dur / 1e6 * 1000:.0f} ms cuối file - "
                                        "assemble tự bù theo offset tại giữa mỗi đoạn; đoạn dài > 2 phút nên tách")
            entry["files"].append(fe)
            flag = "" if g is master or (conf >= 1.1 and r >= 0.2) else "  ⚠"
            print(f"   {g['ten']:<10} {os.path.basename(f):<28} offset {off:+9.3f}s  dài {dur:7.1f}s  "
                  f"đỉnh/phụ {conf:4.2f}  r {r:4.2f}  trôi {ppm:+6.1f}ppm  SNR {snr:4.1f}dB{flag}", flush=True)
        # khoảng phủ của góc (gộp các file)
        segs = sorted([(fe["offset"], fe["ket_thuc"]) for fe in entry["files"] if fe.get("offset") is not None])
        entry["phu"] = [[round(a, 2), round(b, 2)] for a, b in segs]
        gaps = [[round(segs[k][1], 2), round(segs[k + 1][0], 2)] for k in range(len(segs) - 1)
                if segs[k + 1][0] - segs[k][1] > 0.5]
        entry["khoang_trong"] = gaps
        result["goc"].append(entry)

    # Trộn tiếng các góc cận đã căn offset → nguon/tieng-chu.wav (podcast: mỗi người một mic gần)
    if args.tron_tieng:
        can_files = [fe for g in result["goc"] if g["loai"] == "can" for fe in g["files"] if fe.get("offset") is not None]
        if len(can_files) >= 2:
            cmd, fc, k = ["ffmpeg", "-hide_banner", "-v", "error", "-y"], "", 0
            for fe in can_files:
                cmd += ["-i", os.path.join(project, fe["file"])]
                off = fe["offset"]
                chain = "aformat=sample_rates=48000:channel_layouts=mono,"
                chain += (f"adelay={int(off * 1000)}" if off >= 0 else f"atrim=start={-off:.3f},asetpts=PTS-STARTPTS")
                fc += f"[{k}:a]{chain},dynaudnorm=f=500:g=15:p=0.9[a{k}];"
                k += 1
            fc += "".join(f"[a{i}]" for i in range(k)) + f"amix=inputs={k}:duration=longest:normalize=0,atrim=0:{total:.3f}[out]"
            out_wav = os.path.join(project, "nguon", "tieng-chu.wav")
            sh(cmd + ["-filter_complex", fc, "-map", "[out]", "-ar", "48000", "-ac", "1", out_wav])
            result["tieng_chu"] = {"file": "nguon/tieng-chu.wav", "offset": 0.0,
                                   "ghi_chu": "trộn từ các góc cận đã căn offset (dynaudnorm từng track rồi amix); "
                                              "transcript và assemble dùng file này làm tiếng"}
            print(f"   ✓ tiếng chủ trộn: {out_wav}", flush=True)
        else:
            print("   ⚠ --tron-tieng cần >= 2 góc cận có tiếng", flush=True)

    # Đề xuất track tiếng chủ: SNR cao nhất trong các file phủ toàn bộ (ưu tiên góc 'tieng')
    cands = []
    for g in result["goc"]:
        for fe in g["files"]:
            if fe.get("offset") is None:
                continue
            cover = fe["ket_thuc"] - fe["offset"]
            bonus = 6 if g["loai"] == "tieng" else 0
            cands.append((fe["snr_db"] + bonus, cover, g["ten"], fe["file"]))
    cands.sort(reverse=True)
    if cands:
        result["tieng_chu_de_xuat"] = {"goc": cands[0][2], "file": cands[0][3],
                                       "ly_do": f"SNR {cands[0][0]:.1f} dB (đã ưu tiên file tiếng riêng), phủ {cands[0][1]:.0f}s"}
    result["_ghi_chu"] = ("offset = mốc (giây) trên trục chuẩn mà file bắt đầu; mốc trục chuẩn T nằm trong file "
                          "tại T - offset (+ drift_ppm*1e-6*(T - offset) nếu trôi). Kiểm tay: nghe 3 giây quanh "
                          "một câu nói chung ở 2 góc sau khi dựng nháp.")
    out = os.path.join(project, "multicam.json")
    if os.path.isfile(out):
        old = json.load(open(out, encoding="utf-8"))
        for k in ("session", "dan_goc", "tieng_chu"):
            if k in old:
                result[k] = old[k]
    json.dump(result, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[3/3] ✓ {out}")
    if "tieng_chu_de_xuat" in result:
        print(f"   Tiếng chủ đề xuất: {result['tieng_chu_de_xuat']['goc']} - {result['tieng_chu_de_xuat']['ly_do']}")
    for g in result["goc"]:
        if g["khoang_trong"]:
            print(f"   ⚠ góc {g['ten']} có khoảng trống {g['khoang_trong']} - dàn góc sẽ tránh dùng góc này ở đó")


if __name__ == "__main__":
    main()
