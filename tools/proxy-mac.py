#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROXY MULTICAM chạy song song theo mảnh, dành cho máy Mac thật (và chạy được trong VM).

Vì sao: VM Cowork giải mã HEVC 4K rất chậm (khoảng 2,7 giây CPU cho mỗi giây hình) và hay bị tải
chung; Mac giải mã nhanh hơn nhiều lần. Việc này do hàng đợi `tools/hang-doi-go-bang.py` xếp (loại
"proxy") và chạy khi người dùng bấm đúp "Go bang tren Mac.command".

Cách dùng:  python3 tools/proxy-mac.py <job.json>

job.json:
  {"loai": "proxy", "tu": 440.0, "den": 3130.0, "chunk": 60, "workers": 3, "ra": "<thư mục tuyệt đối>",
   "du_an": "du-an/<x>",   (tương đối so với gốc xưởng, để ghi PROXY.json)
   "goc": [{"ten": "chinh", "loai": "can",
            "files": [{"file": "<tuyệt đối>", "offset": -210.059, "dur": 1797.796}, ...],
            "ra": [{"ten": "chinh", "vf": "scale=1920:1080"},                      (tuỳ chọn: nhiều đầu ra từ MỘT lần giải mã,
                   {"ten": "can-nguoi", "vf": "crop=2240:1260:0:250,scale=1920:1080"}]}, ...]}   vd cận ảo cắt từ 4K)

Đầu ra trong "ra": nguon/<tên đầu ra>/<tên>.mp4 (chỉ hình, 1080p, 30 fps cfr), multicam.json và
PROXY.json của proxy (mọi góc offset 0; mốc proxy = mốc trục gốc - tu). Tiếng chủ
(nguon/tieng-chu.wav) do VM dựng sẵn. Chạy lại được: mảnh đã xong được giữ.
"""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import time


def pieces(files, t0, t1):
    out, t = [], t0
    fs = sorted(files, key=lambda f: f["offset"])
    while t < t1 - 1e-3:
        fe = next((f for f in fs if f["offset"] <= t < f["offset"] + f["dur"] - 0.05), None)
        if not fe:
            # khe hở nhỏ (dưới 0,3 s) giữa hai file liền nhau: lấy đầu file kế tiếp, lệch tối đa vài khung
            nx = [f for f in fs if f["offset"] > t and f["offset"] - t < 0.3]
            if not nx:
                sys.exit(f"! Khoảng trống nguồn tại trục {t:.2f}s")
            fe = nx[0]
        d = min(t1, fe["offset"] + fe["dur"]) - t
        # bù trôi đồng hồ camera: mốc trong file = (T - offset) * (1 + drift_ppm*1e-6), như multicam-dan.py
        x = t - fe["offset"]
        out.append((fe["file"], max(0.0, x * (1 + fe.get("drift_ppm", 0) * 1e-6)), d, t))
        t += d
    return out


def chunk_ok(path, expect):
    """Mảnh đã có và đúng độ dài (sai quá 0,2 s là làm lại). Đo bằng ffmpeg (Mac không chắc có ffprobe)."""
    if not os.path.isfile(path):
        return False
    try:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path], capture_output=True, text=True)
        m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
        if not m:
            return False
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        return abs(dur - expect) < 0.02
    except Exception:
        return False


def run_ffmpeg(cmd_in, cmd_rest):
    # thử giải mã phần cứng (VideoToolbox) trước, lỗi thì quay về phần mềm
    if sys.platform == "darwin":
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-hwaccel", "videotoolbox"] + cmd_in + cmd_rest, capture_output=True)
        if r.returncode == 0:
            return r
    return subprocess.run(["ffmpeg", "-v", "error", "-y"] + cmd_in + cmd_rest, capture_output=True)


def main():
    job = json.load(open(sys.argv[1], encoding="utf-8"))
    tu, den, ch = job["tu"], job["den"], float(job.get("chunk", 60))
    ra = job["ra"].rstrip("/")
    n = int((den - tu) // ch) + (1 if (den - tu) % ch > 1e-3 else 0)
    t_start = time.time()
    outs_of = {g["ten"]: (g.get("ra") or [{"ten": g["ten"], "vf": "scale=-2:1080"}]) for g in job["goc"]}
    tasks = []
    for g in job["goc"]:
        for o in outs_of[g["ten"]]:
            os.makedirs(os.path.join(ra, "nguon", o["ten"], ".manh"), exist_ok=True)
        for k in range(n):
            t0, t1 = tu + k * ch, min(den, tu + (k + 1) * ch)
            if all(chunk_ok(os.path.join(ra, "nguon", o["ten"], ".manh", f"{k:03d}.mp4"), t1 - t0) for o in outs_of[g["ten"]]):
                continue
            tasks.append((g["ten"], k, pieces(g["files"], t0, t1)))
    print(f"Proxy {tu}-{den}s: còn {len(tasks)} mảnh giải mã ({n} mảnh mỗi góc) → {ra}", flush=True)
    failed = []

    def run(t):
        ten, k, ps = t
        outs = outs_of[ten]
        subs = {o["ten"]: [] for o in outs}
        t0k = tu + k * ch
        for j, (f, ss, d, tstart) in enumerate(ps):
            # ĐÚNG số khung: lọc fps=30 cộng -t từng thừa 1-2 khung mỗi mảnh, cộng dồn làm hình trễ hơn tiếng cả giây ở cuối phim
            nfr = int(round((tstart + d - t0k) * 30)) - int(round((tstart - t0k) * 30))
            parts = {o["ten"]: os.path.join(ra, "nguon", o["ten"], ".manh", f"{k:03d}.{j}.part.mp4") for o in outs}
            chains = [f"[0:v]fps=30,split={len(outs)}" + "".join(f"[s{i}]" for i in range(len(outs)))]
            for i, o in enumerate(outs):
                chains.append(f"[s{i}]{o['vf']},setsar=1,format=yuv420p[o{i}]")
            rest = ["-filter_complex", ";".join(chains)]
            for i, o in enumerate(outs):
                rest += ["-map", f"[o{i}]", "-an", "-frames:v", str(nfr), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-g", "60",
                         "-pix_fmt", "yuv420p", "-f", "mp4", parts[o["ten"]]]
            r = run_ffmpeg(["-ss", f"{ss:.3f}", "-t", f"{d + 0.1:.3f}", "-i", f], rest)
            if r.returncode:
                print("LỖI", ten, k, r.stderr.decode(errors="ignore")[-300:], flush=True)
                failed.append((ten, k))
                return
            for o in outs:
                subs[o["ten"]].append(parts[o["ten"]])
        for o in outs:
            out = os.path.join(ra, "nguon", o["ten"], ".manh", f"{k:03d}.mp4")
            sl = subs[o["ten"]]
            if len(sl) == 1:
                os.replace(sl[0], out)
            else:
                lst = out + ".txt"
                open(lst, "w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in sl))
                r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                                    "-f", "mp4", out + ".part.mp4"], capture_output=True)
                if r.returncode:
                    print("LỖI nối", o["ten"], k, flush=True)
                    failed.append((ten, k))
                    return
                os.replace(out + ".part.mp4", out)
        print(f"  ✓ {ten} mảnh {k + 1}/{n}  ({time.time() - t_start:.0f}s)", flush=True)

    with cf.ThreadPoolExecutor(int(job.get("workers", 3))) as ex:
        list(ex.map(run, tasks))
    if failed:
        sys.exit(f"! {len(failed)} mảnh lỗi, chạy lại để làm tiếp")
    allout = [(g, o) for g in job["goc"] for o in outs_of[g["ten"]]]
    for g, o in allout:
        gdir = os.path.join(ra, "nguon", o["ten"])
        cdir = os.path.join(gdir, ".manh")
        final = os.path.join(gdir, f"{o['ten']}.mp4")
        lst = os.path.join(cdir, "all.txt")
        open(lst, "w").write("".join(f"file '{os.path.abspath(os.path.join(cdir, f'{k:03d}.mp4'))}'\n" for k in range(n)))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart",
                        "-f", "mp4", final + ".part.mp4"], check=True)
        os.replace(final + ".part.mp4", final)
        print("  ✓", final, flush=True)
    span = round(den - tu, 3)
    pm = {"_ghi_chu": f"PROXY từ {job.get('du_an', '?')} quãng {tu}-{den} s trục gốc; mốc proxy = mốc gốc - {tu}",
          "truc_chuan": job.get("truc_chuan", "toan"), "tong_dai": span,
          "tieng_chu": {"file": "nguon/tieng-chu.wav", "offset": 0.0},
          "goc": [{"ten": o["ten"], "loai": o.get("loai") or g["loai"], "nguoi": o.get("nguoi") or g.get("nguoi"), "vf": o["vf"],
                   "files": [{"file": f"nguon/{o['ten']}/{o['ten']}.mp4", "dur": span, "offset": 0.0, "ket_thuc": span,
                              "co_hinh": True, "co_tieng": False, "drift_ppm": 0}],
                   "phu": [[0.0, span]], "khoang_trong": []} for g, o in allout]}
    json.dump(pm, open(os.path.join(ra, "multicam.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"nguon": job.get("du_an"), "tu": tu, "den": den, "_ghi_chu": "mốc proxy = mốc trục gốc - tu"},
              open(os.path.join(ra, "PROXY.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✓ Xong proxy + multicam.json trong {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
