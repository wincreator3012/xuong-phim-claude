#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỌN KHUNG THUMBNAIL: tìm các khung hình khuôn mặt đẹp nhất của một video đã dựng để làm thumbnail
(skill phim-dang-tai). Máy chỉ LỌC ỨNG VIÊN; chọn khung cuối cùng là việc của mắt (Claude xem
bảng ứng viên, đề xuất, anh duyệt).

Cách dùng (từ gốc xưởng, sau khi video đã vào xuat-hoan-chinh/ cùng <video>.map.json):
  python3 tools/chon-khung-thumbnail.py --map "../Du an/<x>/xuat-hoan-chinh/<video>.map.json" \\
      [--ra "../Du an/<x>/dang-tai/<video>/khung"] [--nguon goc|thanh-pham] [--buoc 3] [--so 12] \\
      [--gioi-han 160]

  --nguon goc (mặc định): lấy khung từ FILE NGUỒN của từng đoạn cắt (không dính pill, bảng tên, phụ đề;
      độ phân giải gốc), có áp đơn màu mau-sac.json của nguồn đó nếu có. Bố cục crop của timeline
      (layout) không áp, vì thumbnail tự crop quanh khuôn mặt.
  --nguon thanh-pham: lấy từ chính video đã dựng (đã chỉnh màu, bố cục thật; có thể dính overlay).
      Dùng khi không còn nguồn, hoặc nguồn khác xa thành phẩm (tonemap phức tạp, ghép khung).
  Không có map (video không dựng bằng assemble): --video <file.mp4> lấy thẳng từ video đó.

Cách chấm (mỗi khung lấy mẫu mỗi --buoc giây trong các đoạn cắt, bỏ đoạn chèn đồ họa):
  - Dò mặt bằng YuNet (tools/models/face_detection_yunet_2023mar.onnx, OpenCV Zoo, giấy phép MIT).
  - diem = tin_cay x co_mat x chinh_dien x net x sang, cộng nhẹ cho nụ cười (miệng rộng so với hai mắt).
    co_mat: chiều cao mặt / chiều cao khung, đẹp nhất 0.16-0.45; chinh_dien: mũi nằm giữa hai mắt;
    net: độ nét (phương sai Laplace) trong vùng mặt, so với phân vị 90 của chính video;
    sang: độ sáng trung bình vùng mặt trong khoảng dễ nhìn.
  - Chọn --so khung điểm cao nhất, cách nhau tối thiểu 6 giây, rải đều các nguồn (nhiều góc máy).
  - Riêng khung có hai mặt trở lên được xếp một danh sách phụ "nhiều mặt" (podcast, phỏng vấn đôi).

Kết quả trong --ra:
  ung-vien.jpg   bảng ứng viên có đánh số k01..kNN, mốc, nguồn, điểm, khung mặt - để Claude NHÌN
  k01.jpg ...    khung độ phân giải đầy đủ (rộng tối đa 3840 px) của từng ứng viên
  khung.json     chi tiết: nguồn, mốc nguồn, mốc thành phẩm, điểm, các mặt (tâm cx, cy và chiều cao h,
                 chuẩn hoá 0-1 theo khung; w, h ảnh) - chép thẳng vào props "photos" của Thumbnail
  .diem.json     cache chấm điểm; lệnh bị ngắt (giới hạn 180 giây mỗi lượt) thì gọi lại y nguyên
Tinh chỉnh nét mặt (bước hai, sau khi đã nhìn ung-vien.jpg và chọn ứng viên):
  python3 tools/chon-khung-thumbnail.py --map "<...>.map.json" --quanh k05 [--rong 1.5]
  → khung mỗi 0.25 s quanh k05, mã k05a, k05b..., bảng quanh-k05.jpg cắt sát mặt; thêm vào khung.json.
  Cần vì khuôn mặt đang nói đổi rất nhanh: cùng một giây có khung cười thật và khung miệng méo.
Thoát mã 2 khi hết --gioi-han mà chưa chấm xong: gọi lại y nguyên để chấm tiếp.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, "tools", "models", "face_detection_yunet_2023mar.onnx")
SCORE_W = 960          # bề rộng khung để chấm
OUT_MAX_W = 3840       # bề rộng tối đa khung xuất (4K: đủ để phóng mặt ở cảnh toàn)


def probe(src):
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", src],
                       capture_output=True, text=True)
    info = json.loads(p.stdout or "{}")
    st = (info.get("streams") or [{}])[0]
    return st.get("width"), st.get("height"), float(info.get("format", {}).get("duration", 0) or 0)


def grab(src, t, width, vf_pre=""):
    """Một khung ở mốc t (giây), trả về ảnh BGR rộng `width` (giữ tỉ lệ)."""
    vf = f"{vf_pre}scale={width}:-2:flags=lanczos" if width else (vf_pre.rstrip(",") or "null")
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", src, "-frames:v", "1",
           "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0 or not p.stdout:
        return None
    return cv2.imdecode(np.frombuffer(p.stdout, np.uint8), cv2.IMREAD_COLOR)


def faces_of(det, img):
    h, w = img.shape[:2]
    det.setInputSize((w, h))
    _, res = det.detect(img)
    out = []
    if res is None:
        return out
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    for r in res:
        x, y, fw, fh = [float(v) for v in r[:4]]
        conf = float(r[14])
        reye, leye, nose, rmouth, lmouth = [(float(r[4 + 2 * i]), float(r[5 + 2 * i])) for i in range(5)]
        eye_d = max(1.0, abs(leye[0] - reye[0]))
        yaw = (nose[0] - (leye[0] + reye[0]) / 2) / eye_d
        smile = abs(lmouth[0] - rmouth[0]) / eye_d
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(w, int(x + fw)), min(h, int(y + fh))
        crop = gray[y0:y1, x0:x1]
        if crop.size < 100:
            continue
        crop = cv2.resize(crop, (128, 128))
        sharp = float(cv2.Laplacian(crop, cv2.CV_64F).var())
        bright = float(crop.mean())
        out.append({"cx": float((x + fw / 2) / w), "cy": float((y + fh / 2) / h), "h": float(fh / h),
                    "fw": float(fw / w),
                    "conf": conf, "yaw": float(yaw), "smile": float(smile),
                    "sharp": sharp, "bright": bright})
    return out


def save_cache(path, cache):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(cache, fh)
    os.replace(tmp, path)


def band(v, lo_bad, lo_ok, hi_ok, hi_bad):
    if v <= lo_bad or v >= hi_bad:
        return 0.0
    if v < lo_ok:
        return (v - lo_bad) / (lo_ok - lo_bad)
    if v > hi_ok:
        return (hi_bad - v) / (hi_bad - hi_ok)
    return 1.0


def face_score(f, sharp_ref):
    size = band(f["h"], 0.05, 0.16, 0.45, 0.8)
    frontal = max(0.0, 1.0 - abs(f["yaw"]) * 2.2)
    sharp = min(1.0, f["sharp"] / max(1.0, sharp_ref))
    light = band(f["bright"], 40, 85, 195, 245)
    smile_bonus = 1.0 + 0.25 * min(1.0, max(0.0, (f["smile"] - 0.85) / 0.35))
    return f["conf"] * size * frontal * (0.35 + 0.65 * sharp) * light * smile_bonus


def quanh(args, ra, vf_pre):
    """Tinh chỉnh nét mặt: quanh một ứng viên đã chọn, lấy khung mỗi 0.25 s trong ±--rong giây, xuất đủ
    độ phân giải với mã <kid>a, <kid>b..., thêm vào khung.json và ghi bảng quanh-<kid>.jpg để Claude NHÌN
    (mắt mở, miệng khép hoặc cười thật, không nháy)."""
    kj_path = os.path.join(ra, "khung.json")
    kj = json.load(open(kj_path, encoding="utf-8"))
    goc = next((k for k in kj["ung_vien"] if k["id"] == args.quanh), None)
    if not goc:
        sys.exit(f"Không có ứng viên {args.quanh} trong {kj_path}")
    kj["ung_vien"] = [k for k in kj["ung_vien"] if not (k["id"].startswith(args.quanh) and k["id"] != args.quanh)]
    src = os.path.join(ROOT, goc["nguon"])
    W, H, _ = probe(src)
    det = cv2.FaceDetectorYN.create(MODEL, "", (320, 320), 0.7, 0.3, 50)
    steps = int(round(args.rong / 0.25))
    tiles = []
    for j, dt in enumerate([i * 0.25 for i in range(-steps, steps + 1)]):
        kid = f"{args.quanh}{chr(97 + j)}"
        t = goc["t_nguon"] + dt
        full = grab(src, t, min(W or OUT_MAX_W, OUT_MAX_W), vf_pre(src))
        if full is None:
            continue
        cv2.imwrite(os.path.join(ra, f"{kid}.jpg"), full, [cv2.IMWRITE_JPEG_QUALITY, 94])
        small = cv2.resize(full, (960, int(960 * full.shape[0] / full.shape[1])))
        faces = faces_of(det, small)
        faces.sort(key=lambda f: -f["conf"] * f["h"])
        mat = [{k: round(f[k], 4) for k in ("cx", "cy", "h", "fw", "yaw", "smile")} for f in faces]
        kj["ung_vien"].append({"id": kid, "file": f"{kid}.jpg", "loai": goc["loai"], "w": full.shape[1],
                               "h": full.shape[0], "nguon": goc["nguon"], "t_nguon": round(t, 2),
                               "t_thanh_pham": round(goc["t_thanh_pham"] + dt, 2), "diem": None, "mat": mat})
        # ô xem: cắt quanh mặt lớn nhất cho dễ soi nét mặt
        th, tw = small.shape[:2]
        if faces:
            f = faces[0]
            ch = int(min(th, f["h"] * th * 2.6))
            cy, cx = int(f["cy"] * th), int(f["cx"] * tw)
            y0 = max(0, min(th - ch, cy - ch // 2))
            x0 = max(0, min(tw - ch, cx - ch // 2))
            crop = small[y0:y0 + ch, x0:x0 + ch]
        else:
            crop = small[:, (tw - th) // 2:(tw + th) // 2]
        tile = cv2.resize(crop, (300, 300))
        tile = cv2.copyMakeBorder(tile, 0, 30, 0, 0, cv2.BORDER_CONSTANT, value=(30, 30, 30))
        cv2.putText(tile, f"{kid} {dt:+.2f}s", (8, 322), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (235, 235, 235), 1,
                    cv2.LINE_AA)
        tiles.append(tile)
    n_khung = len(tiles)
    cols = 5
    while len(tiles) % cols:
        tiles.append(np.full_like(tiles[0], 30))
    grid = np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)])
    cv2.imwrite(os.path.join(ra, f"quanh-{args.quanh}.jpg"), grid, [cv2.IMWRITE_JPEG_QUALITY, 88])
    json.dump(kj, open(kj_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✓ {n_khung} khung quanh {args.quanh} → {os.path.relpath(ra, ROOT)}/quanh-{args.quanh}.jpg"
          f" (mã {args.quanh}a...; đã thêm vào khung.json)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map")
    ap.add_argument("--video")
    ap.add_argument("--ra")
    ap.add_argument("--nguon", choices=["goc", "thanh-pham"], default="goc")
    ap.add_argument("--buoc", type=float, default=3.0)
    ap.add_argument("--so", type=int, default=12)
    ap.add_argument("--toi-da", type=int, default=160, help="số mẫu chấm tối đa")
    ap.add_argument("--gioi-han", type=float, default=160)
    ap.add_argument("--quanh", help="mã ứng viên (vd k05): xuất thêm các khung sát bên để chọn nét mặt đẹp nhất")
    ap.add_argument("--rong", type=float, default=1.5, help="--quanh: lấy ± bao nhiêu giây (bước 0.25 s)")
    args = ap.parse_args()
    t0 = time.time()
    if not (args.map or args.video):
        sys.exit("Cần --map hoặc --video")
    if not os.path.exists(MODEL):
        sys.exit(f"Thiếu model dò mặt: {MODEL} (xem tools/models/TAI-MODEL.md)")

    # ---- mẫu cần chấm: (nguồn, mốc nguồn, mốc thành phẩm) ----
    samples = []
    if args.map:
        mp = json.load(open(args.map, encoding="utf-8"))
        video = args.map[:-len(".map.json")] + ".mp4"
        project = os.path.dirname(os.path.dirname(os.path.abspath(args.map)))
        ms_path = os.path.join(project, "mau-sac.json")
        mau_sac = json.load(open(ms_path, encoding="utf-8")) if os.path.exists(ms_path) else {}
        for p in mp["parts"]:
            if p.get("kind") != "cut" or p["dur"] < 1.2:
                continue
            n = max(1, int(p["dur"] // args.buoc))
            for i in range(n):
                off = 0.6 + (p["dur"] - 1.2) * (i + 0.5) / n
                if args.nguon == "goc":
                    src = os.path.join(project, p["src"])
                    samples.append((src, p["in"] + off, p["start"] + off))
                else:
                    samples.append((video, p["start"] + off, p["start"] + off))
        stem = os.path.basename(video)[:-4]
        ra = args.ra or os.path.join(project, "dang-tai", stem, "khung")
    else:
        video = args.video
        _, _, dur = probe(video)
        mau_sac = {}
        t = 1.0
        while t < dur - 1.0:
            samples.append((video, t, t))
            t += args.buoc
        stem = os.path.splitext(os.path.basename(video))[0]
        ra = args.ra or os.path.join(os.path.dirname(os.path.abspath(video)), "..", "dang-tai", stem, "khung")
    if len(samples) > args.toi_da:
        idx = np.linspace(0, len(samples) - 1, args.toi_da).round().astype(int)
        samples = [samples[i] for i in sorted(set(idx))]
    os.makedirs(ra, exist_ok=True)

    def vf_pre(src):
        don = mau_sac.get(os.path.basename(src)) or {}
        return f"{don['vf']}," if don.get("vf") else ""

    if args.quanh:
        return quanh(args, ra, vf_pre)

    cache_path = os.path.join(ra, ".diem.json")
    try:
        cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    except (ValueError, OSError):
        cache = {}  # cache hỏng (lượt trước bị ngắt giữa lúc ghi): chấm lại từ đầu
    det = cv2.FaceDetectorYN.create(MODEL, "", (320, 320), 0.7, 0.3, 50)
    todo = [s for s in samples if f"{s[0]}|{s[1]:.2f}" not in cache]
    print(f"Mẫu: {len(samples)} (còn chấm {len(todo)}), nguồn khung: {args.nguon}", flush=True)
    for k, (src, t, tout) in enumerate(todo):
        if time.time() - t0 > args.gioi_han:
            save_cache(cache_path, cache)
            print(f"⏸ Hết giới hạn thời gian, đã chấm {len(samples) - len(todo) + k}/{len(samples)}."
                  " Gọi lại y nguyên lệnh để chấm tiếp.")
            sys.exit(2)
        img = grab(src, t, SCORE_W, vf_pre(src))
        cache[f"{src}|{t:.2f}"] = {"src": src, "t": t, "tout": tout,
                                   "faces": faces_of(det, img) if img is not None else [],
                                   "ok": img is not None}
        if k % 20 == 19:
            save_cache(cache_path, cache)
    save_cache(cache_path, cache)

    rows = [cache[f"{s[0]}|{s[1]:.2f}"] for s in samples]
    sharp_all = [f["sharp"] for r in rows for f in r["faces"]]
    if not sharp_all:
        print("Không dò được khuôn mặt nào: video không có người trên hình (infomotion, hoạt hình)"
              " hoặc mặt quá nhỏ. Thumbnail dùng bố cục chữ, hình ẩn dụ (skill phim-dang-tai).")
        sys.exit(3)
    sharp_ref = float(np.percentile(sharp_all, 90))
    for r in rows:
        for f in r["faces"]:
            f["diem"] = face_score(f, sharp_ref)
        r["faces"].sort(key=lambda f: -f["diem"])
        good = [f for f in r["faces"] if f["diem"] > 0.15]
        r["diem"] = r["faces"][0]["diem"] if r["faces"] else 0.0
        r["nhieu_mat"] = len(good) >= 2
        r["diem_doi"] = (good[0]["diem"] + good[1]["diem"]) / 2 if len(good) >= 2 else 0.0

    def pick(pool, key, n, per_src_cap):
        chosen, per_src = [], {}
        for r in sorted(pool, key=lambda r: -r[key]):
            if r[key] <= 0.05 or len(chosen) >= n:
                break
            if per_src.get(r["src"], 0) >= per_src_cap:
                continue
            if any(c["src"] == r["src"] and abs(c["t"] - r["t"]) < 6 for c in chosen):
                continue
            chosen.append(r)
            per_src[r["src"]] = per_src.get(r["src"], 0) + 1
        return chosen

    n_src = len({r["src"] for r in rows if r["diem"] > 0.05}) or 1
    main_pick = pick(rows, "diem", args.so, max(2, -(-args.so // n_src) + 1))
    duo_pick = pick([r for r in rows if r["nhieu_mat"] and r not in main_pick], "diem_doi", 4, 4)
    picks = [(r, "mot") for r in main_pick] + [(r, "doi") for r in duo_pick]

    # ---- xuất khung đầy đủ + bảng ứng viên ----
    ket_qua, tiles = [], []
    for i, (r, kind) in enumerate(picks, 1):
        kid = f"k{i:02d}"
        W, H, _ = probe(r["src"])
        full = grab(r["src"], r["t"], min(W or OUT_MAX_W, OUT_MAX_W), vf_pre(r["src"]))
        if full is None:
            continue
        cv2.imwrite(os.path.join(ra, f"{kid}.jpg"), full, [cv2.IMWRITE_JPEG_QUALITY, 94])
        fh, fw = full.shape[:2]
        faces = [{k: round(f[k], 4) for k in ("cx", "cy", "h", "fw", "yaw", "smile", "diem")}
                 for f in r["faces"] if f["diem"] > 0.05]
        ket_qua.append({"id": kid, "file": f"{kid}.jpg", "loai": kind, "w": fw, "h": fh,
                        "nguon": os.path.relpath(r["src"], ROOT), "t_nguon": round(r["t"], 2),
                        "t_thanh_pham": round(r["tout"], 2),
                        "diem": round(r["diem_doi"] if kind == "doi" else r["diem"], 3), "mat": faces})
        tile = cv2.resize(full, (480, int(480 * fh / fw)))
        th, tw = tile.shape[:2]
        for f in faces:
            x0 = int((f["cx"] - f["fw"] / 2) * tw)
            y0 = int((f["cy"] - f["h"] / 2) * th)
            cv2.rectangle(tile, (x0, y0), (x0 + int(f["fw"] * tw), y0 + int(f["h"] * th)), (80, 200, 120), 1)
        tile = cv2.copyMakeBorder(tile, 0, 34, 0, 0, cv2.BORDER_CONSTANT, value=(30, 30, 30))
        m, s = divmod(int(r["tout"]), 60)
        label = f"{kid} {'2 mat ' if kind == 'doi' else ''}{m}:{s:02d} {os.path.basename(r['src'])[:14]} {ket_qua[-1]['diem']:.2f}"
        cv2.putText(tile, label, (8, th + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (235, 235, 235), 1, cv2.LINE_AA)
        tiles.append(tile)
    if tiles:
        th = max(t.shape[0] for t in tiles)
        tiles = [cv2.copyMakeBorder(t, 0, th - t.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(30, 30, 30))
                 for t in tiles]
        cols = 4
        while len(tiles) % cols:
            tiles.append(np.full_like(tiles[0], 30))
        grid = np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)])
        cv2.imwrite(os.path.join(ra, "ung-vien.jpg"), grid, [cv2.IMWRITE_JPEG_QUALITY, 88])
    json.dump({"video": os.path.relpath(video, ROOT), "nguon_khung": args.nguon,
               "ung_vien": ket_qua}, open(os.path.join(ra, "khung.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"✓ {len(ket_qua)} ứng viên ({len(duo_pick)} khung nhiều mặt) → {os.path.relpath(ra, ROOT)}/ung-vien.jpg")
    for k in ket_qua:
        print(f"  {k['id']} {k['loai']:4s} {k['t_thanh_pham']:8.1f}s  {k['nguon']:40s} điểm {k['diem']:.2f}  mặt {len(k['mat'])}")


if __name__ == "__main__":
    main()
