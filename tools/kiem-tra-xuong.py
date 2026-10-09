#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DỰNG THỬ dự án tổng hợp nhỏ để chắc xưởng chạy đúng trên máy này.

    python3 tools/kiem-tra-xuong.py [--co-slide] [--giu] [--chi-tai-lieu]

Tạo nguồn giả bằng ffmpeg (màn test + tiếng sine), soạn timeline có đủ các
kỹ thuật chính (cắt, fade, overlay alpha, B-roll, B-roll cảnh minh hoạ thu vào góc,
insert, tuỳ chọn bố cục slide và multicam audioSrc), rồi chạy đúng đường thật: assemble.py --kiem-tra →
assemble.py --preview → nghiem-thu.py video. Thoát mã 0 = ĐẠT.

Dự án thử nằm ở <Du an>/_tam/_kiem-tra-tu-dong/ (NGOÀI repo, xoá được). Không cần model, không cần mạng.

Trước khi dựng thử, chạy cổng kiểm tài liệu (tools/kiem-tai-lieu.py: YAML của skill,
đường dẫn trong tài liệu, kho ẩn dụ, dấu phiên bản). Tài liệu KHÔNG ĐẠT thì vẫn dựng
thử cho biết phần máy, nhưng kết quả chung là KHÔNG ĐẠT. --chi-tai-lieu: chỉ kiểm tài liệu.
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
    ap.add_argument("--chi-tai-lieu", action="store_true", help="chỉ chạy cổng kiểm tài liệu, không dựng thử")
    args = ap.parse_args()
    os.chdir(ROOT)

    tai_lieu_dat = True
    if os.path.isfile(os.path.join(TOOLS, "kiem-tai-lieu.py")):
        print("→ kiem-tai-lieu.py", flush=True)
        tai_lieu_dat = subprocess.run([sys.executable, os.path.join(TOOLS, "kiem-tai-lieu.py")]).returncode == 0
    if args.chi_tai_lieu:
        raise SystemExit(0 if tai_lieu_dat else 1)
    print("→ quy tắc điểm cắt Dựng bằng lời (ban_dung_loi.py, dữ liệu tổng hợp)", flush=True)
    if not kiem_cat_loi():
        raise SystemExit("! ban_dung_loi.py đặt điểm cắt khác mốc đã kiểm - xem dòng ✗ ở trên")

    sys.path.insert(0, TOOLS)
    import cau_hinh as CH
    proj = os.path.relpath(CH.tam("_kiem-tra-tu-dong"), ROOT)
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

    brolls = [{"src": "nguon/broll.mp4", "at": 8.0, "duration": 3.0, "from": 2.0}]
    # cảnh minh hoạ kiểu "người nói thu vào góc": canh-ghep.py đặt nguồn thật vào ô của cảnh, ra một B-roll
    if os.path.isfile(os.path.join(TOOLS, "canh-ghep.py")):
        print("→ thử ghép cảnh minh hoạ thu vào góc (canh-ghep.py pip)", flush=True)
        sh(ff + ["-f", "lavfi", "-i", "color=c=0x0e1230:size=640x360:rate=30", "-t", "2",
                 "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                 os.path.join(proj, "do-hoa", "canh-pip-nen.mp4")])
        with open(os.path.join(proj, "do-hoa", "do-hoa-manifest.json"), "w", encoding="utf-8") as f:
            json.dump({"canh-pip-nen.mp4": {"pip": {"x": 24, "y": 190, "w": 256, "h": 144, "r": 12}}}, f)
        sh([sys.executable, os.path.join(TOOLS, "canh-ghep.py"), "pip", os.path.join(proj, "do-hoa", "canh-pip-nen.mp4"),
            os.path.join(proj, "nguon", "chinh.mp4"), "--at", "11.5", "--out", os.path.join(proj, "do-hoa", "canh-pip.mp4")])
        brolls.append({"src": "do-hoa/canh-pip.mp4", "at": 11.5, "duration": 2.0, "from": 0})
    segs = [
        {"type": "video", "src": "nguon/chinh.mp4", "in": 2.0, "out": 14.0, "snap": False,
         "fadeIn": 0.5, "overlay": {"src": "do-hoa/lt.webm", "at": 1.0},
         "broll": brolls},
        {"type": "insert", "src": "do-hoa/intro.mp4"},
        # overlay "duration": thẻ đầu kéo dài 4 → 4,5 s (giữ khung giữa), thẻ sau rút 4 → 2,5 s; volumeDb -6
        {"type": "video", "src": "nguon/chinh.mp4", "in": 20.0, "out": 28.0, "snap": False,
         "fadeOut": 0.5, "volumeDb": -6,
         "overlay": [{"src": "do-hoa/lt.webm", "at": 0.5, "duration": 4.5},
                     {"src": "do-hoa/lt.webm", "at": 5.0, "duration": 2.5}]},
        # multicam có B-roll: tiếng chủ phải chạy liền qua B-roll (audioIn từng quãng = 10 + (đầu quãng - 3))
        {"type": "video", "src": "nguon/goc2.mp4", "in": 3.0, "out": 9.0, "snap": False,
         "audioSrc": "nguon/chinh.mp4", "audioIn": 10.0,
         "broll": [{"src": "nguon/broll.mp4", "at": 5.0, "duration": 1.5, "from": 0}]},
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
            # quay màn hình (r9): ô lớn lấy từ VIDEO màn hình cùng trục thời gian, có vùng phóng và lệch 0,5 s
            sh(ff + ["-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=25", "-t", "30",
                     "-c:v", "libx264", "-preset", "ultrafast", os.path.join(proj, "nguon", "man-hinh.mp4")])
            segs.insert(2, {"type": "video", "src": "nguon/chinh.mp4", "in": 5.0, "out": 9.0,
                            "snap": False, "layout": "ca-hai", "screen": "nguon/man-hinh.mp4",
                            "screenOffset": 0.5, "slideZoom": [0.24, 0.10, 0.52, 0.52]})
            print("→ có ba đoạn bố cục slide (ca-hai ảnh, ca-hai màn hình có phóng vùng, mat-chinh)")
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
    print("→ kiểm các trường r7 (overlay duration, volumeDb, audioIn multicam qua B-roll)", flush=True)
    if not kiem_r7(proj, out):
        raise SystemExit("! Trường overlay duration / volumeDb / audioIn multicam chưa đúng - xem dòng ✗ ở trên")
    print("→ kiểm vi mờ ở mối nối (r8)", flush=True)
    if not kiem_vi_mo(out):
        raise SystemExit("! Vi mờ ở mối nối chưa đúng - xem dòng ✗ ở trên")
    print("→ kiểm bố cục mat-tren của short dọc (r10/r11: ô mặt trên, nền giấy dưới, cropZoom)", flush=True)
    if not kiem_mat_tren(proj):
        raise SystemExit("! Bố cục mat-tren chưa đúng - xem dòng ✗ ở trên (short dọc mặt trên cảnh dưới sẽ hỏng)")
    print("→ kiem-dong-bo.py (đồng bộ hình-tiếng tuyệt đối: dựng thử chớp/click)", flush=True)
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "kiem-dong-bo.py")], text=True)
    if p.returncode != 0:
        raise SystemExit("! kiem-dong-bo.py KHÔNG ĐẠT - assemble.py hiện hành làm lệch hình-tiếng, KHÔNG dựng thật")
    print(f"\n✓ DỰNG THỬ ĐẠT trên máy này. Thư mục thử: {proj}/ (xoá được).")
    if not tai_lieu_dat:
        raise SystemExit("! Phần máy ĐẠT nhưng cổng kiểm tài liệu KHÔNG ĐẠT (xem LỖI ở đầu) - sửa tài liệu rồi chạy lại")


def kiem_r7(proj, out):
    """Đo trên thành phẩm thử: (1) audioIn multicam từng quãng, (2) volumeDb -6 làm đoạn nhỏ hơn khoảng 6 dB,
    (3) thẻ kéo dài còn hiện sau mốc file gốc hết, thẻ rút ngắn đã tắt trước mốc file gốc hết."""
    import re
    ok = True
    mp = os.path.splitext(out)[0] + ".map.json"
    parts = json.load(open(mp, encoding="utf-8"))["parts"]
    mc = [p for p in parts if p.get("audio_src")]
    for p in mc:
        can = round(10.0 + (p["in"] - 3.0), 3)
        if abs(p["audio_in"] - can) > 0.002:
            print(f"  ✗ multicam part {p['part']}: audio_in {p['audio_in']} (cần {can})")
            ok = False
    if len(mc) < 3:
        print(f"  ✗ multicam có B-roll phải ra 3 part, thấy {len(mc)}")
        ok = False
    chinh = [p for p in parts if p["kind"] == "cut" and p["src"].endswith("chinh.mp4") and not p.get("audio_src")]
    def muc(a, b):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", out,
                            "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
        m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
        return float(m.group(1)) if m else None
    p1 = next(p for p in chinh if abs(p["in"] - 2.0) < 0.01)
    p3 = next(p for p in chinh if abs(p["in"] - 20.0) < 0.01)
    v1, v3 = muc(p1["start"] + 1.0, p1["start"] + 4.0), muc(p3["start"] + 1.0, p3["start"] + 4.0)
    if v1 is None or v3 is None or not (4.5 <= v1 - v3 <= 7.5):
        print(f"  ✗ volumeDb -6: mức đoạn thường {v1} dB, đoạn -6 dB {v3} dB (cần chênh 4,5-7,5)")
        ok = False
    else:
        print(f"  ✓ volumeDb -6: chênh {v1 - v3:.1f} dB")
    # thẻ: ô trắng của lt.webm ở 40..340 x 260..320 (khung 640x360); đo sáng giữa ô trên khung xuất
    def sang(t):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-ss", f"{t:.3f}", "-i", out, "-frames:v", "1",
                            "-vf", "scale=640:360,crop=200:30:90:275,format=gray", "-f", "rawvideo", "-"],
                           capture_output=True)
        b = r.stdout
        return sum(b) / len(b) if b else 0
    s0 = p3["start"]
    do = {"thẻ 1 kéo dài, sau 4,5 s (file gốc đã hết)": (sang(s0 + 4.7), True),
          "thẻ 2 rút ngắn, sau 7,5 s": (sang(s0 + 7.7), False),
          "thẻ 2 đang hiện": (sang(s0 + 6.0), True)}
    for ten, (v, phai_hien) in do.items():
        hien = v > 215
        print(f"  {'✓' if hien == phai_hien else '✗'} {ten}: độ sáng ô thẻ {v:.0f}")
        ok = ok and hien == phai_hien
    return ok


def kiem_mat_tren(proj):
    """Dựng một đoạn 4 giây khung dọc với layout mat-tren (cropFocus, cropFocusY, cropZoom) từ nguồn thử rồi đo trên khung:
    tỉ lệ 9:16, ô mặt phủ kín tới hàng paneH (nguồn thử có màu, không phải màu giấy), phần dưới đúng màu nền giấy."""
    tl = {"aspect": "doc", "fps": 30, "nen": "#FAF7F1", "paneH": 960,
          "segments": [{"type": "video", "src": "nguon/chinh.mp4", "in": 2.0, "out": 6.0, "snap": False,
                        "layout": "mat-tren", "cropFocus": 0.5, "cropFocusY": 0.0, "cropZoom": 1.12, "label": "mat-tren-thu"}]}
    with open(os.path.join(proj, "timeline-mat-tren.json"), "w", encoding="utf-8") as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)
    p = subprocess.run([sys.executable, "tools/assemble.py", "--project", proj, "--timeline", "timeline-mat-tren.json",
                        "--preview", "--out", "mat-tren-thu"], capture_output=True, text=True)
    out = os.path.join(proj, "xuat-nhap", "mat-tren-thu-nhap.mp4")
    if p.returncode != 0 or not os.path.isfile(out):
        print("  ✗ assemble.py không dựng được đoạn mat-tren:", (p.stdout + p.stderr)[-600:])
        return False
    kt = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                         "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(kt[0]), int(kt[1])
    ok = abs(w / h - 9 / 16) < 0.01
    print(f"  {'✓' if ok else '✗'} khung {w}x{h} (cần tỉ lệ 9:16)")

    def mau(y):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-ss", "1", "-i", out, "-frames:v", "1", "-vf",
                            f"scale=1080:1920,crop=40:10:520:{y},scale=1:1,format=rgb24", "-f", "rawvideo", "-"],
                           capture_output=True)
        return tuple(r.stdout[:3]) if len(r.stdout) >= 3 else (0, 0, 0)
    giay = (250, 247, 241)
    for y, phai_giay in ((100, False), (900, False), (930, False), (990, True), (1700, True)):
        c = mau(y)
        d = max(abs(c[i] - giay[i]) for i in range(3))
        dung = (d <= 8) if phai_giay else (d >= 30)
        ok = ok and dung
        print(f"  {'✓' if dung else '✗'} hàng {y} của khung 1920: {c} ({'nền giấy' if phai_giay else 'ô mặt'})")
    return ok


def kiem_cat_loi():
    """Dựng một lời nói tổng hợp (âm tiết 0,22 s; khe lặng, thung năng lượng, chữ dính liền, từ đệm kéo dài)
    rồi so điểm cắt của ban_dung_loi.py với mốc đã kiểm (Pha 2 Bàn dựng, 2026-10-01)."""
    sys.path.insert(0, TOOLS)
    import ban_dung_loi as L
    nl = [38] * 3001
    def dat(a, b, v):
        for i in range(int(round(a * 100)), int(round(b * 100))):
            if 0 <= i < len(nl):
                nl[i] = v
    cau = ["xin chào các bạn ờ hôm nay chúng ta sẽ nói về cách dựng phim".split(),
           "thì ờ đây là một thử nghiệm nhỏ à để kiểm tra bàn dựng".split()]
    vong = ["hep", "hep", "lang", "hep", "gat", "hep", "lang"]
    tu, t, ci = [], 1.0, 0
    for c in cau:
        for n, w in enumerate(c):
            d = 0.36 if w in ("ờ", "à", "á") else 0.22
            dat(t, t + d, 80)
            tu.append({"w": w, "s": round(t + 0.02, 3), "e": round(t + d - 0.06, 3), "c": 0.95, "k": 0})
            e0 = t + d
            if w == "thì":
                kieu = "gat"
            elif n == len(c) - 1:
                kieu = "cau"
            else:
                kieu = vong[ci % len(vong)]
                ci += 1
            if kieu == "gat":
                t = e0
            elif kieu == "hep":
                dat(e0, e0 + 0.03, 62)
                t = e0 + 0.03
            elif kieu == "lang":
                t = e0 + 0.15
            else:
                t = e0 + 0.45
    loi = L.Loi(tu, bytes(nl), -62.0)
    can = [("vào trước 'nay' (bỏ 'ờ hôm')", loi.diem_vao(6), 2.72, "hep"),
           ("ra sau 'phim'", loi.diem_ra(14), 5.48, "lang"),
           ("vào trước 'đây' (bỏ 'thì ờ')", loi.diem_vao(17), 6.33, "hep"),
           ("vào trước 'ờ'", loi.diem_vao(4), 2.11, "hep")]
    ok = True
    for ten, kq, t_can, loai in can:
        dung = abs(kq["t"] - t_can) < 0.001 and kq["loai"] == loai
        ok = ok and dung
        print(f"  {'✓' if dung else '✗'} {ten}: {kq['t']} ({kq['loai']}), cần {t_can} ({loai})")
    gat = loi.khe(4)["loai"] == "gat"
    print(f"  {'✓' if gat else '✗'} 'ờ' và 'hôm' dính liền: {loi.khe(4)['loai']}")
    return ok and gat


def kiem_vi_mo(out):
    """Mối nối tiếng KHÔNG liền (cắt bỏ một quãng, đổi file, giáp đồ họa chèn) phải có vi mờ: năng lượng
    1 ms sát mối nối nhỏ hơn hẳn năng lượng 12-30 ms bên cạnh. Mối nối tiếng liền (tách đoạn, B-roll,
    đổi góc multicam cùng tiếng chủ) phải giữ nguyên. Đo trên thành phẩm (tiếng sine của nguồn giả)."""
    import array
    import math
    parts = json.load(open(os.path.splitext(out)[0] + ".map.json", encoding="utf-8"))["parts"]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", out, "-map", "0:a", "-ac", "1", "-ar", "48000",
                          "-f", "f32le", "-"], capture_output=True).stdout
    a = array.array("f")
    a.frombytes(raw)

    def rms(t0, t1):
        x = a[int(round(t0 * 48000)):int(round(t1 * 48000))]
        return math.sqrt(sum(v * v for v in x) / max(1, len(x)))

    def tieng(p):
        if p["kind"] != "cut":
            return None
        if p.get("audio_src"):
            return (p["audio_src"], p["audio_in"], p["audio_in"] + (p["out"] - p["in"]))
        return (p["src"], p["in"], p["out"])
    ok, dem = True, 0
    for p, q in zip(parts, parts[1:]):
        x, y = tieng(p), tieng(q)
        lien = x is not None and y is not None and x[0] == y[0] and abs(x[2] - y[1]) < 0.002
        t = q["start"]
        for ten, ref, sat in (("trước", rms(t - 0.03, t - 0.012), rms(t - 0.0012, t - 0.0002)),
                              ("sau", rms(t + 0.012, t + 0.03), rms(t + 0.0002, t + 0.0012))):
            if ref < 1e-3:
                continue
            r = sat / ref
            dung = r > 0.8 if lien else r < 0.5
            dem += 1
            if not dung:
                ok = False
                print(f"  ✗ mối nối part {p['part']}→{q['part']} ({'liền' if lien else 'không liền'}), phía {ten}: tỉ lệ {r:.2f}")
    if ok:
        print(f"  ✓ vi mờ đúng ở {dem} mép mối nối")
    return ok


if __name__ == "__main__":
    main()
