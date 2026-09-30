#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GHÉP CẢNH MINH HOẠ VỚI CẢNH QUAY THẬT, chạy trên máy của anh (footage không rời máy).

Cảnh minh hoạ HTML được chụp ở sandbox bằng tools/canh.mjs rồi commit về máy. Hai kiểu chèn
cần tới hình quay thật thì làm ở đây bằng ffmpeg:

  1. Lấy một khung hình làm "nền mờ" cho cảnh (kiểu chèn: nền là khung hình mờ):
     python3 tools/canh-ghep.py khung <nguon.mp4> --at <giây nguồn> [--out <anh.jpg>] [--rong 1920]
     → ảnh JPEG nhỏ; stage ảnh này lên sandbox, chụp cảnh với: node tools/canh.mjs chup ... --nen-anh <anh.jpg>

  2. Đặt đoạn quay thật vào ô .o-pip của cảnh (kiểu chèn: anh thu vào góc nhỏ):
     python3 tools/canh-ghep.py pip <canh.mp4> <nguon.mp4> --at <giây nguồn> --out <broll.mp4>
        [--o x,y,w,h,r] [--tieu-diem 0.5] [--tieu-diem-y 0.4] [--vao 0.35]
     → một clip video (không tiếng) dùng làm broll: tiếng giảng vẫn đi liền từ nguồn chính.
     Toạ độ ô lấy từ do-hoa-manifest.json cạnh canh.mp4 (canh.mjs chup --pip ghi sẵn); --o để ghi đè.
     --at là mốc TRONG FILE NGUỒN nơi cảnh bắt đầu, trùng broll.at trong timeline.
     --tieu-diem / --tieu-diem-y: tâm cắt khung theo chiều ngang / dọc (0-1) để giữ mặt trong ô.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile


def probe(f):
    out = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-show_format", f],
                         capture_output=True, text=True).stdout
    info = json.loads(out or "{}")
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    if not v:
        sys.exit(f"! {f}: không đọc được luồng hình")
    n, d = (v.get("r_frame_rate") or "30/1").split("/")
    dur = float(v.get("duration") or info.get("format", {}).get("duration") or 0)
    return {"w": int(v["width"]), "h": int(v["height"]), "fps": float(n) / float(d or 1), "dur": dur}


def chan(x):
    return int(round(x / 2.0)) * 2


def cmd_khung(a):
    out = a.out or os.path.join(os.path.dirname(a.nguon) or ".", f"khung-{a.at:07.2f}.jpg")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-ss", f"{a.at:.3f}", "-i", a.nguon,
                    "-frames:v", "1", "-vf", f"scale={a.rong}:-2", "-q:v", "4", out], check=True)
    print(f"→ {out} (khung tại {a.at:.2f} s, rộng {a.rong} px)")


def cmd_pip(a):
    c = probe(a.canh)
    s = probe(a.nguon)
    if a.o:
        x, y, w, h, r = [int(float(v)) for v in (a.o.split(",") + ["0"])[:5]]
    else:
        mf = os.path.join(os.path.dirname(os.path.abspath(a.canh)), "do-hoa-manifest.json")
        try:
            muc = json.load(open(mf, encoding="utf-8"))[os.path.basename(a.canh)]
            o = muc["pip"]
        except (OSError, KeyError, ValueError):
            sys.exit(f"! Không thấy toạ độ ô trong {mf} (chụp cảnh với --pip, hoặc truyền --o x,y,w,h,r)")
        x, y, w, h, r = o["x"], o["y"], o["w"], o["h"], o.get("r", 0)
    w, h = chan(w), chan(h)
    dur = c["dur"]
    if a.at + dur > s["dur"] + 0.05:
        sys.exit(f"! Nguồn chỉ dài {s['dur']:.2f} s, không đủ {dur:.2f} s kể từ {a.at:.2f} s")
    # cắt nguồn theo tỉ lệ ô, giữ tâm quanh mặt người nói
    ti = w / h
    if s["w"] / s["h"] > ti:
        cw, ch = chan(s["h"] * ti), s["h"]
    else:
        cw, ch = s["w"], chan(s["w"] / ti)
    cx = min(max(0, a.tieu_diem * s["w"] - cw / 2), s["w"] - cw)
    cy = min(max(0, a.tieu_diem_y * s["h"] - ch / 2), s["h"] - ch)
    with tempfile.TemporaryDirectory() as tmp:
        mask = os.path.join(tmp, "mask.png")
        r = max(0, min(r, w // 2, h // 2))
        # mặt nạ bo góc: trắng trong ô, đen ở bốn góc ngoài bán kính r
        geq = ("255" if r == 0 else
               f"if(gt(abs(X-{w}/2),{w}/2-{r})*gt(abs(Y-{h}/2),{h}/2-{r}),"
               f"if(lte(hypot(abs(X-{w}/2)-({w}/2-{r}),abs(Y-{h}/2)-({h}/2-{r})),{r}),255,0),255)")
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-f", "lavfi", "-i",
                        f"color=c=black:s={w}x{h}:d=1,format=gray,geq=lum='{geq}'", "-frames:v", "1", mask], check=True)
        fc = (f"[1:v]setpts=PTS-STARTPTS,fps={c['fps']:.6f},crop={cw}:{ch}:{int(cx)}:{int(cy)},scale={w}:{h},"
              f"format=yuva420p[p];[2:v]format=gray,scale={w}:{h}[m];[p][m]alphamerge,"
              f"fade=t=in:st=0:d={a.vao:.3f}:alpha=1[pa];"
              f"[0:v][pa]overlay={x}:{y}:shortest=1:format=auto,format=yuv420p[v]")
        cmd = ["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", a.canh,
               "-ss", f"{a.at:.3f}", "-t", f"{dur:.3f}", "-i", a.nguon,
               "-loop", "1", "-i", mask, "-filter_complex", fc, "-map", "[v]", "-an",
               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
               "-r", f"{c['fps']:.6f}", "-t", f"{dur:.3f}", "-movflags", "+faststart", a.out]
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        subprocess.run(cmd, check=True)
    ra = probe(a.out)
    lech = abs(ra["dur"] - dur)
    print(f"→ {a.out}: {ra['dur']:.2f} s ({ra['w']}x{ra['h']}), ô {w}x{h} tại {x},{y}, bo {r} px"
          + (f"  CẢNH BÁO: lệch {lech:.2f} s so với cảnh" if lech > 0.1 else ""))
    print(f"   timeline: \"broll\": [{{\"src\": \"<đường dẫn tới {os.path.basename(a.out)}>\", \"at\": {a.at:.3f}, "
          f"\"duration\": {dur:.3f}, \"from\": 0}}]")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)
    k = sub.add_parser("khung", help="lấy một khung hình làm nền mờ")
    k.add_argument("nguon")
    k.add_argument("--at", type=float, required=True)
    k.add_argument("--out")
    k.add_argument("--rong", type=int, default=1920)
    p = sub.add_parser("pip", help="đặt đoạn quay thật vào ô .o-pip của cảnh")
    p.add_argument("canh")
    p.add_argument("nguon")
    p.add_argument("--at", type=float, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--o", help="x,y,w,h,r ghi đè toạ độ ô")
    p.add_argument("--tieu-diem", type=float, default=0.5)
    p.add_argument("--tieu-diem-y", type=float, default=0.4)
    p.add_argument("--vao", type=float, default=0.35, help="giây hiện dần của ô hình")
    a = ap.parse_args()
    cmd_khung(a) if a.lenh == "khung" else cmd_pip(a)


if __name__ == "__main__":
    main()
