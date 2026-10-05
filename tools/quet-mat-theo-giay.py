#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUÉT MẶT THEO GIÂY: tìm khung thumbnail trong một quãng của file nguồn gốc (bổ trợ chon-khung-thumbnail.py).

Dùng khi cần khung CHỌN TAY theo nội dung (ví dụ khung rộng, zoom out, có slide của khái niệm đang nói
sau lưng người giảng) thay vì khung do máy chấm tự động:

  python3 tools/quet-mat-theo-giay.py "<nguon.mp4>" --tu 352 --den 380 --buoc 1.5 \\
      [--cat x:y:w:h] --ra "<thư mục tạm trong $HOME, không để trong thư mục của anh nếu không cần giữ>"

- Mỗi mốc trích một khung từ nguồn gốc (4K càng tốt), cắt theo --cat (pixel gốc; mặc định cả khung), dò mặt bằng YuNet.
- In 10 mặt chính diện nhất (độ lệch mũi so với hai mắt thấp, mặt to) và ghi `quet-mat.json`.
- Ghi `quet-mat.jpg`: lưới 8 ô cận mặt (520x520 quanh mặt) có nhãn giây để NHÌN rồi chọn nét mặt:
  mắt mở, miệng khép hay cười thật, không nháy mắt, không mờ chuyển động.
- Khung đã trích được giữ lại (s<giây>.jpg) nên chạy lại cùng tham số sẽ không trích lại.
- Một lượt gọi 120 giây kham khảng 25-30 mốc ở 4K: chia quãng thành nhiều lượt, kết quả json cộng dồn.
Sau khi chọn: cắt khung cuối bằng ffmpeg từ nguồn gốc (-ss <giây> -vf crop=...), ghi vào khung/khung.json
(id, file, loai "rong" hoặc "mot", w, h, mat[{cx,cy,h,fw}] theo tỉ lệ ảnh) rồi `tools/dang-tai.py job`.
"""
import argparse, json, os, subprocess, sys
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, "tools", "models", "face_detection_yunet_2023mar.onnx")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nguon")
    ap.add_argument("--tu", type=float, required=True)
    ap.add_argument("--den", type=float, required=True)
    ap.add_argument("--buoc", type=float, default=1.5)
    ap.add_argument("--cat", default=None, help="x:y:w:h theo pixel của nguồn")
    ap.add_argument("--ra", required=True)
    ap.add_argument("--top", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(a.ra, exist_ok=True)
    vf = "null"
    if a.cat:
        w, h, x, y = (a.cat.split(":")[2], a.cat.split(":")[3], a.cat.split(":")[0], a.cat.split(":")[1])
        vf = f"crop={w}:{h}:{x}:{y}"
    jp = os.path.join(a.ra, "quet-mat.json")
    res = json.load(open(jp)) if os.path.exists(jp) else []
    done = {r["t"] for r in res}
    t = a.tu
    while t <= a.den + 1e-6:
        key = round(t, 2)
        f = os.path.join(a.ra, f"s{key:.2f}.jpg")
        if key in done:
            t += a.buoc
            continue
        if not os.path.exists(f):
            subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", str(key), "-i", a.nguon,
                            "-frames:v", "1", "-vf", vf, "-q:v", "2", f])
        im = cv2.imread(f)
        if im is not None:
            det = cv2.FaceDetectorYN.create(MODEL, "", (im.shape[1], im.shape[0]), 0.6, 0.3, 50)
            _, fa = det.detect(im)
            for r in (fa if fa is not None else []):
                x_, y_, w_, h_ = [float(v) for v in r[:4]]
                re_, le, nose = r[4:6], r[6:8], r[8:10]
                asym = abs(nose[0] - (re_[0] + le[0]) / 2) / max(1.0, abs(le[0] - re_[0]))
                res.append(dict(t=key, x=x_, y=y_, w=w_, h=h_, sc=float(r[14]), asym=float(asym)))
        done.add(key)
        json.dump(res, open(jp, "w"))
        t += a.buoc
    best = sorted(res, key=lambda r: r["asym"] - r["w"] / 2000)[: max(a.top, 10)]
    for r in best:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    tiles = []
    for r in best[: a.top]:
        im = cv2.imread(os.path.join(a.ra, f"s{r['t']:.2f}.jpg"))
        cx, cy = int(r["x"] + r["w"] / 2), int(r["y"] + r["h"] / 2)
        x0, y0 = max(0, cx - 260), max(0, cy - 260)
        c = cv2.resize(im[y0:y0 + 520, x0:x0 + 520], (480, 480))
        c = cv2.copyMakeBorder(c, 0, 480 - c.shape[0], 0, 480 - c.shape[1], cv2.BORDER_CONSTANT) if c.shape[:2] != (480, 480) else c
        cv2.putText(c, f"{r['t']:.1f}", (8, 30), 0, 1, (0, 255, 255), 2)
        tiles.append(c)
    while len(tiles) % 4:
        tiles.append(np.zeros((480, 480, 3), np.uint8))
    rows = [np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]
    cv2.imwrite(os.path.join(a.ra, "quet-mat.jpg"), np.vstack(rows))
    print("✓", os.path.join(a.ra, "quet-mat.jpg"), file=sys.stderr)


if __name__ == "__main__":
    main()
