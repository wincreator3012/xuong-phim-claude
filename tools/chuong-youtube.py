#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHƯƠNG YOUTUBE: quy mốc nội dung (theo trục nguồn/tiếng chủ) sang mốc của video đã dựng, xuất đúng
định dạng chương [chapters] YouTube để dán vào phần mô tả.

Cách dùng (từ gốc xưởng, sau khi assemble.py đã xuất <video>.map.json):
  python3 tools/chuong-youtube.py --map "du-an/<x>/xuat-hoan-chinh/<video>.map.json" \\
      --chuong "du-an/<x>/chuong.json" [--mo-dau "Mở đầu"] [--ket "Lời mời tham gia ..."]

chuong.json: [{"t": <giây trên trục nguồn>, "ten": "Tên chương"}, ...]
  - "t" là mốc trong TIẾNG CHỦ (audioIn) khi timeline multicam, hoặc mốc trong file nguồn (in/out)
    khi timeline một góc. Mốc pill trong kế hoạch overlay dùng thẳng được.
  - Mốc rơi vào quãng đã bị cắt bỏ khỏi video → dời về đầu đoạn kế tiếp và cảnh báo.

Luật YouTube được áp tự động: chương đầu tiên ở 0:00 (thêm "--mo-dau" nếu chương đầu muộn hơn),
tối thiểu 3 chương, mỗi chương dài >= 10 giây (chương quá sát chương trước bị gộp và báo lại).
"--ket" thêm một chương tại lúc bắt đầu outro (insert cuối cùng trong map).
In ra màn hình và ghi <video>.chuong.txt cạnh map.
"""
import argparse
import json
import os
import sys


def fmt(t):
    t = int(t)
    h, m, s = t // 3600, (t % 3600) // 60, t % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--chuong", required=True)
    ap.add_argument("--mo-dau", default="Mở đầu")
    ap.add_argument("--ket", default=None, help="tên chương cho outro (bỏ trống = không thêm)")
    args = ap.parse_args()

    parts = json.load(open(args.map, encoding="utf-8"))["parts"]
    chuong = json.load(open(args.chuong, encoding="utf-8"))
    cuts = [p for p in parts if p.get("kind") == "cut"]
    warns = []

    def to_out(t):
        for p in cuts:
            base = p.get("audio_in", p["in"])
            if base - 1e-3 <= t < base + (p["out"] - p["in"]):
                return p["start"] + (t - base)
        later = [p for p in cuts if p.get("audio_in", p["in"]) > t]
        if later:
            warns.append(f"mốc {t:.1f}s nằm trong quãng đã cắt bỏ → dời về đầu đoạn kế tiếp")
            return later[0]["start"]
        return None

    items = []
    for c in sorted(chuong, key=lambda c: c["t"]):
        o = to_out(float(c["t"]))
        if o is None:
            warns.append(f"bỏ chương '{c['ten']}': mốc {c['t']}s sau hết video")
            continue
        items.append([o, c["ten"]])
    if not items or items[0][0] >= 1.0:
        items.insert(0, [0.0, args.mo_dau])
    else:
        items[0][0] = 0.0
    if args.ket:
        inserts = [p for p in parts if p.get("kind") == "insert"]
        if inserts and inserts[-1]["start"] > items[-1][0]:
            items.append([inserts[-1]["start"], args.ket])
    kept = [items[0]]
    for t, name in items[1:]:
        if t - kept[-1][0] < 10:
            warns.append(f"gộp '{name}' vào chương trước (chỉ cách {t - kept[-1][0]:.0f}s, YouTube cần >= 10s)")
            continue
        kept.append([t, name])
    if len(kept) < 3:
        warns.append("YouTube cần ít nhất 3 chương mới hiện thanh chương - thêm mốc")
    lines = [f"{fmt(t)} {name}" for t, name in kept]
    out = os.path.splitext(args.map)[0].replace(".map", "") + ".chuong.txt"
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    for w in warns:
        print(f"  ⚠ {w}", file=sys.stderr)
    print(f"✓ {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
