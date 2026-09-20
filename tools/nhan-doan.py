#!/usr/bin/env python3
"""
nhan-doan.py - sinh/cap nhat bang doi chieu NHAN <-> moc thoi gian that cho
mot du an phim tai lieu phong van, tu timeline.json (nguon nhan on dinh)
va ban .map.json moi nhat cua mot nhap (nguon moc thoi gian that).

Quy uoc nhan (xem references/ke-chuyen-phong-van.md muc 8):
  A<n>  doan loi lien tuc (phong van hoac phat bieu su kien)
  B<n>.<m>  canh tram phu len loi cua A<n>, danh so m theo thu tu trong A<n>
  T<n>  canh tram doc lap dung lam cau noi giua hai nguoi noi (khong phu len loi ai)
  M<n>  tung canh trong chuoi mo dau nhieu canh truoc A1

Nhan duoc gan thu cong vao truong "label" cua tung segment trong timeline.json
khi viet Buoc 2.3/dung Buoc 2.4 (nhieu sub-segment cung mot dong dung mang
CUNG mot label). Script nay CHI doc, khong tu suy doan nhan thay cho nguoi
dung - segment nao chua co "label" se in canh bao va dung placeholder "?<idx>".

Dung: python3 nhan-doan.py <timeline.json> <ban-moi-nhat.map.json> [--out NHAN-DOAN.md]
"""
import json
import sys
import argparse


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def consume_parts_for_segment(seg, parts, idx):
    """Tra ve danh sach cac 'part' thuoc ve segment nay (theo thu tu), va idx moi."""
    target = round(seg.get("out", 0) - seg.get("in", 0), 3)
    if seg.get("type") == "insert":
        # mot segment insert (do-hoa) luon dung dung 1 part kind=insert
        if idx < len(parts) and parts[idx].get("kind") == "insert":
            return [parts[idx]], idx + 1
        return [], idx  # lech cau truc, bo qua an toan
    got = []
    total = 0.0
    while idx < len(parts) and total < target - 0.01:
        p = parts[idx]
        if p.get("kind") != "cut":
            break
        got.append(p)
        total += round(p.get("dur", p.get("end", 0) - p.get("start", 0)), 3)
        idx += 1
    return got, idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline")
    ap.add_argument("mapfile")
    ap.add_argument("--out", default="NHAN-DOAN.md")
    args = ap.parse_args()

    tl = load(args.timeline)
    mp = load(args.mapfile)
    segments = tl["segments"]
    parts = [p for p in mp["parts"]]

    idx = 0
    # groups: label -> {"onset_parts": [...], "broll_parts": [...]}
    order = []  # thu tu xuat hien lan dau cua moi nhan
    groups = {}
    unlabeled_count = 0

    for seg in segments:
        seg_parts, idx = consume_parts_for_segment(seg, parts, idx)
        if seg.get("type") == "insert":
            continue  # the do hoa (intro/outro/slide chuyen) khong gan nhan
        label = seg.get("label")
        if not label:
            unlabeled_count += 1
            label = f"?{unlabeled_count}"
        if label not in groups:
            groups[label] = {"onset": [], "broll": []}
            order.append(label)
        for p in seg_parts:
            if p.get("video_from"):
                groups[label]["broll"].append(p)
            else:
                groups[label]["onset"].append(p)

    def fmt(t):
        m, s = divmod(round(t, 1), 60)
        return f"{int(m):02d}:{s:05.2f}"

    lines = []
    lines.append("# NHAN-DOAN.md - bang doi chieu nhan doan <-> moc thoi gian that\n")
    lines.append(f"Sinh tu `{args.mapfile}`. Nhan on dinh qua moi nhap; chi moc thoi gian doi.\n")
    if unlabeled_count:
        lines.append(f"\n**Canh bao**: {unlabeled_count} doan trong timeline.json chua co truong "
                      "\"label\" - da danh so tam \"?1\", \"?2\"... Gan nhan that vao timeline.json "
                      "(hoac ngay tu KICH-BAN-THUC-TE.md khi viet Buoc 2.3) roi chay lai script.\n")
    lines.append("\n| Nhan | Bat dau | Ket thuc | Thoi luong | Nguon |\n|---|---|---|---|---|\n")

    for label in order:
        g = groups[label]
        all_pts = g["onset"] + g["broll"]
        if not all_pts:
            continue
        start = min(p["start"] for p in all_pts)
        end = max(p["end"] for p in all_pts)
        src = all_pts[0].get("src", "")
        lines.append(f"| {label} | {fmt(start)} | {fmt(end)} | {end-start:.1f}s | {src} |\n")
        for m, b in enumerate(g["broll"], start=1):
            blabel = f"{label}.{m}" if not label.startswith("?") else f"{label}b{m}"
            lines.append(f"| {blabel} | {fmt(b['start'])} | {fmt(b['end'])} | "
                          f"{b['end']-b['start']:.1f}s | {b.get('video_from','')} |\n")

    with open(args.out, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Da ghi {args.out}: {len(order)} nhan chinh, {unlabeled_count} chua gan nhan.")


if __name__ == "__main__":
    main()
