#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NHẬP VÀ KIỂM KÊ ÂM THANH: xếp file mới vào đúng nhóm, đo LUFS, ghi danh mục thật của máy.

    python3 tools/nhap-am-thanh.py                       # kiểm kê nhac-nen/ và hieu-ung/, ghi nhac-nen/THU-VIEN.md
    python3 tools/nhap-am-thanh.py --tu ~/Downloads      # thêm: nhận file vừa tải, đổi tên, xếp nhóm, rồi kiểm kê
    python3 tools/nhap-am-thanh.py --tu ~/Downloads --nhom rieng   # file không khớp danh mục → nhac-nen/rieng/

Nhận diện file tải về bằng id Pixabay trong tên (ví dụ "meditation-music-550885.mp3") hoặc
tên track Kevin MacLeod ("That Zen Moment.mp3") so với thu-vien/am-thanh.json; file khớp được
đổi tên theo chuẩn <mô-tả>_<tác-giả>_<nguồn-id>.mp3 và chép vào đúng nhóm. File không khớp:
in ra để Claude hỏi người dùng (hoặc --nhom rieng để nhận là nhạc riêng).

gainDb gợi ý tính từ LUFS đo thật: full = -30 - LUFS (nhạc nằm dưới lời nói -14 LUFS),
bookends = full + 8 (chỉ ở intro/outro, được to hơn). Đây là điểm xuất phát; tai người quyết.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import unicodedata

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
CATALOG = os.path.join(ROOT, "thu-vien", "am-thanh.json")
AUDIO_EXT = (".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac")


def ffprobe_dur(path):
    p = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def do_lufs(path):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn",
                        "-af", "ebur128=framelog=verbose", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.findall(r"I:\s*(-?[0-9.]+)\s*LUFS", p.stderr)
    return float(m[-1]) if m else None


def fmt(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def chuan(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def khop_danh_muc(fname, cat):
    """Tìm mục danh mục khớp với tên file tải về."""
    base = os.path.splitext(os.path.basename(fname))[0]
    ids = re.findall(r"(\d{4,7})", base)
    for loai in ("nhac", "hieu_ung"):
        for m in cat[loai]:
            mid = re.search(r"pixabay-(\d+)$", m["id"])
            if mid and mid.group(1) in ids:
                return loai, m
    cb = chuan(base)
    for loai in ("nhac", "hieu_ung"):
        for m in cat[loai]:
            tg = m.get("ten_goc")
            if tg and chuan(tg) and chuan(tg) in cb:
                return loai, m
    return None, None


def nhap_tu(thu_muc, cat, nhom_mac_dinh):
    thu_muc = os.path.expanduser(thu_muc)
    if not os.path.isdir(thu_muc):
        print(f"⚠ không thấy thư mục {thu_muc}")
        return
    files = sorted(f for f in os.listdir(thu_muc) if f.lower().endswith(AUDIO_EXT))
    if not files:
        print(f"  (không có file âm thanh trong {thu_muc})")
        return
    print(f"→ nhận file từ {thu_muc}")
    for f in files:
        src = os.path.join(thu_muc, f)
        loai, m = khop_danh_muc(f, cat)
        if m:
            dst_dir = os.path.join(ROOT, "nhac-nen" if loai == "nhac" else "hieu-ung", m["nhom"])
            dst = os.path.join(dst_dir, m["id"] + os.path.splitext(f)[1].lower())
        elif nhom_mac_dinh:
            dst_dir = os.path.join(ROOT, "nhac-nen", nhom_mac_dinh)
            dst = os.path.join(dst_dir, re.sub(r"[^\w.-]+", "-", chuan(os.path.splitext(f)[0])) + os.path.splitext(f)[1].lower())
        else:
            print(f"  ? {f}: không khớp danh mục - hỏi người dùng đây là nhạc gì, có quyền dùng không; "
                  "nếu là nhạc riêng: chạy lại với --nhom rieng")
            continue
        os.makedirs(dst_dir, exist_ok=True)
        if os.path.isfile(dst) and os.path.getsize(dst) > 10000:
            print(f"  = {os.path.relpath(dst, ROOT)} đã có, bỏ qua {f}")
            continue
        shutil.copy2(src, dst)
        print(f"  ✓ {f} → {os.path.relpath(dst, ROOT)}")
        try:
            os.remove(src)   # môi trường không cho xoá thì thôi, file gốc còn trong Downloads
        except OSError:
            pass


def kiem_ke(cat):
    theo_id = {m["id"]: (loai, m) for loai in ("nhac", "hieu_ung") for m in cat[loai]}
    ket = {"nhac": [], "hieu_ung": []}
    for loai, thu_muc in (("nhac", "nhac-nen"), ("hieu_ung", "hieu-ung")):
        goc = os.path.join(ROOT, thu_muc)
        if not os.path.isdir(goc):
            continue
        for nhom in sorted(os.listdir(goc)):
            d = os.path.join(goc, nhom)
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                if not f.lower().endswith(AUDIO_EXT):
                    continue
                path = os.path.join(d, f)
                if os.path.getsize(path) < 10000:
                    continue
                base = os.path.splitext(f)[0]
                _, m = theo_id.get(base, (None, None))
                dur = ffprobe_dur(path)
                lufs = do_lufs(path) if loai == "nhac" else None
                muc = {"file": f"{thu_muc}/{nhom}/{f}", "nhom": nhom, "dai": fmt(dur), "dai_giay": round(dur, 1)}
                if m:
                    muc.update({"ten_goc": m.get("ten_goc", ""), "tac_gia": m.get("tac_gia", ""),
                                "giay_phep": m.get("giay_phep", ""), "trang": m.get("trang", ""),
                                "ghi_chu": m.get("ghi_chu", "")})
                else:
                    muc.update({"ten_goc": base, "tac_gia": "", "giay_phep": "rieng" if nhom == "rieng" else "chua-ro",
                                "trang": "", "ghi_chu": "nhạc riêng của người dùng" if nhom == "rieng" else "CHƯA RÕ NGUỒN - xác minh trước khi dùng"})
                if lufs is not None:
                    muc["lufs"] = round(lufs, 1)
                    muc["gain_full"] = int(round(-30 - lufs))
                    muc["gain_bookends"] = muc["gain_full"] + 8
                ket[loai].append(muc)
    return ket


def ghi_danh_muc(ket, cat):
    gp = cat["giay_phep"]
    out_json = os.path.join(ROOT, "nhac-nen", "thu-vien.json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(ket, f, ensure_ascii=False, indent=1)
    lines = ["# THƯ VIỆN ÂM THANH CỦA MÁY NÀY (tự sinh bởi tools/nhap-am-thanh.py - đừng sửa tay, chạy lại script)",
             "",
             "Đây là danh mục THẬT: chỉ liệt kê file đang có trong nhac-nen/ và hieu-ung/. LUFS đo bằng ebur128 trên chính file; "
             "gainDb là giá trị đặt vào timeline.json (`full` = nhạc chạy suốt dưới lời nói, `bookends` = chỉ intro/outro). "
             "Giấy phép và trang nguồn lấy từ thu-vien/am-thanh.json. Track CC-BY (Kevin MacLeod) phải kèm dòng ghi công trong mô tả video:",
             "", "    " + gp["cc-by"]["mau_ghi_cong"].replace("\n", "\n    "), ""]
    lines += ["## Nhạc nền", ""]
    nhom_mo_ta = cat.get("nhom_nhac", {})
    for nhom in sorted({m["nhom"] for m in ket["nhac"]}):
        lines += [f"### {nhom}: {nhom_mo_ta.get(nhom, '')}", "",
                  "| File | Track gốc, tác giả | Dài | LUFS | gainDb full / bookends | Giấy phép |", "|---|---|---|---|---|---|"]
        for m in ket["nhac"]:
            if m["nhom"] != nhom:
                continue
            lines.append(f"| {os.path.basename(m['file'])} | {m['ten_goc']}{', ' + m['tac_gia'] if m['tac_gia'] else ''} | {m['dai']} | "
                         f"{m.get('lufs', '?')} | {m.get('gain_full', '?')} / {m.get('gain_bookends', '?')} | {m['giay_phep']} |")
        lines.append("")
    if not ket["nhac"]:
        lines += ["(chưa có nhạc - chạy tools/tai-chat-lieu.py --mau <mẫu> hoặc thả nhạc riêng vào nhac-nen/rieng/)", ""]
    lines += ["## Hiệu ứng", ""]
    if ket["hieu_ung"]:
        lines += ["| File | Nhóm | Dài | Dùng khi | Giấy phép |", "|---|---|---|---|---|"]
        for m in ket["hieu_ung"]:
            lines.append(f"| {os.path.basename(m['file'])} | {m['nhom']} | {m['dai']} | {m.get('ghi_chu', '')} | {m['giay_phep']} |")
    else:
        lines.append("(chưa có hiệu ứng)")
    lines += ["", "Nguyên tắc dùng: nhạc bài giảng mặc định `bookends`; clip quảng bá ngắn `full` + `duck: true`. "
              "Hiệu ứng dùng tiết chế, thấp hơn đỉnh lời nói 20-26 dB."]
    out_md = os.path.join(ROOT, "nhac-nen", "THU-VIEN.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✓ {os.path.relpath(out_md, ROOT)}: {len(ket['nhac'])} track nhạc, {len(ket['hieu_ung'])} hiệu ứng")
    for m in ket["nhac"] + ket["hieu_ung"]:
        if m["giay_phep"] == "chua-ro":
            print(f"  ⚠ {m['file']}: chưa rõ nguồn/giấy phép - xác minh với người dùng trước khi dùng")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tu", help="thư mục chứa file vừa tải (ví dụ ~/Downloads)")
    ap.add_argument("--nhom", help="nhóm nhận file không khớp danh mục (thường là 'rieng')")
    args = ap.parse_args()
    with open(CATALOG, encoding="utf-8") as f:
        cat = json.load(f)
    if args.tu:
        nhap_tu(args.tu, cat, args.nhom)
    ket = kiem_ke(cat)
    ghi_danh_muc(ket, cat)


if __name__ == "__main__":
    main()
