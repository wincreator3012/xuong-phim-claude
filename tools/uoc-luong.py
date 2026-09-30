#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm giấy: tự cộng thời lượng, kiểm mật độ hình và cột kiểm chứng của kịch bản
TRƯỚC khi dựng - để mô hình lo phần nghĩ, script lo phần tính.

Cách dùng (từ gốc xưởng):
    python3 tools/uoc-luong.py "du-an/<x>/KICH-BAN-THUC-TE.md"      [--muc-tieu 5-6p] [--out BAO-CAO.md]
    python3 tools/uoc-luong.py "du-an/<x>/KICH-BAN-INFOMOTION.md"   [--muc-tieu 8:00]

Tự nhận loại kịch bản theo dòng tiêu đề đầu file:
- "# Kịch bản thực tế ..." (skill phim-tai-lieu-phong-van): đọc bảng dưới "## Dòng dựng";
  cộng cột "Dài" (hỗ trợ "24s", "2.5s + 2.8s", "1m05s", "1:05"; ô trống thì lấy out - in
  từ cột "in - out") theo cột "Hồi"; so với mục tiêu (--muc-tieu, hoặc hàng "Tổng" của bảng
  "## Thời lượng ước tính"); vượt quá 30% thì nhắc đề xuất hai phương án. Dòng có đồ họa mang
  dữ kiện (con số, trích dẫn, bảng tên, InfoStat...) mà cột "Kiểm chứng" trống là điểm cần xem.
- "# Kịch bản hình tượng hoá ..." (skill phim-infomotion): đọc các khối
  "### Nhịp <n> · m:ss,d-m:ss,d (d s) · <loại>"; đếm hình, mật độ hình/phút, khoảng cách
  giữa hai hình liền nhau (trần 1 hình / 8 giây), khe nền giữa hai đồ họa toàn khung
  (tối thiểu 5 giây), ẩn dụ mới chờ duyệt, nhịp cần dòng "Kiểm chứng:".

--khoang-hinh <giây> nới trần mật độ infomotion khi user chủ động yêu cầu (ghi lý do trong kịch bản).
--muc-tieu nhận "330" (giây), "5:30", "6p", "5-6p" (khoảng thì lấy cận trên).
Kết quả in ra dạng markdown, dòng cuối "KIỂM GIẤY: ĐẠT" hoặc "KIỂM GIẤY: CẦN XEM (n điểm)";
mã thoát 0 hoặc 1. Đây là bước soi trên giấy cho Cổng duyệt, KHÔNG thay cổng máy nghiem-thu.py.
"""
import argparse
import re
import sys

TRAN_VUOT = 0.30          # vượt mục tiêu quá 30% → đề xuất hai phương án
KHOANG_HINH_MIN = 8.0     # trần mật độ infomotion: tối đa 1 hình mới mỗi 8 giây
KHE_TOAN_KHUNG_MIN = 5.0  # tối thiểu 5 giây nền giữa hai đồ họa toàn khung

SO = r"\d+(?:[.,]\d+)?"


def so(x):
    return float(x.replace(",", "."))


def vn(x, n=1):
    return f"{x:.{n}f}".replace(".", ",")


def fmt(t):
    t = max(0.0, t)
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:04.1f}".replace(".", ",")


def doc_thoi_luong(text):
    """Cộng mọi mốc thời lượng trong một ô: '24s', '2.5s + 2.8s', '1m05s', '1:05'."""
    if not text:
        return None
    tong, thay = 0.0, False
    for m in re.finditer(rf"(\d+)\s*m\s*({SO})\s*s|(\d+):(\d{{2}}(?:[.,]\d+)?)(?!\d)|({SO})\s*s\b", text):
        thay = True
        if m.group(1) is not None:
            tong += int(m.group(1)) * 60 + so(m.group(2))
        elif m.group(3) is not None:
            tong += int(m.group(3)) * 60 + so(m.group(4))
        else:
            tong += so(m.group(5))
    return tong if thay else None


def doc_muc_tieu(text):
    if not text:
        return None
    t = text.strip().lower().replace("phút", "p").replace(" ", "")
    m = re.fullmatch(rf"({SO})-({SO})p?", t)
    if m:
        return so(m.group(2)) * 60
    m = re.fullmatch(rf"({SO})p", t)
    if m:
        return so(m.group(1)) * 60
    m = re.fullmatch(r"(\d+):(\d{2})", t)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    m = re.fullmatch(rf"({SO})s?", t)
    if m:
        return so(m.group(1))
    return doc_thoi_luong(text)


def bang_sau_tieu_de(lines, tieu_de):
    """Trả (header, rows) của bảng markdown đầu tiên sau dòng '## <tieu_de>'."""
    i = next((k for k, l in enumerate(lines) if l.strip().lower().startswith("## " + tieu_de.lower())), None)
    if i is None:
        return None, []
    k = i + 1
    while k < len(lines) and not lines[k].lstrip().startswith("|"):
        if lines[k].startswith("## "):
            return None, []
        k += 1
    rows = []
    while k < len(lines) and lines[k].lstrip().startswith("|"):
        cells = [c.strip() for c in lines[k].strip().strip("|").split("|")]
        rows.append(cells)
        k += 1
    if not rows:
        return None, []
    header = [h.lower() for h in rows[0]]
    body = [r for r in rows[1:] if not all(re.fullmatch(r":?-{2,}:?", c or "---") for c in r)]
    return header, body


def cot(header, *tu_khoa):
    for i, h in enumerate(header):
        if any(t in h for t in tu_khoa):
            return i
    return None


CAN_KIEM = re.compile(r"\d|[\"“”«»]|bảng tên|lowerthird|infostat|infoquote|trích|chức danh", re.I)


def kiem_tai_lieu(lines, muc_tieu_arg):
    diem, bao = [], []
    header, rows = bang_sau_tieu_de(lines, "Dòng dựng")
    if not header:
        return ["Không tìm thấy bảng dưới '## Dòng dựng'."], ["Không đọc được kịch bản."]
    c_hoi, c_dai = cot(header, "hồi"), cot(header, "dài")
    c_io, c_dh = cot(header, "in - out", "in-out", "in -"), cot(header, "đồ họa", "đồ hoạ")
    c_kc, c_nhan = cot(header, "kiểm chứng"), cot(header, "nhãn")
    if c_dai is None:
        return ["Bảng 'Dòng dựng' thiếu cột 'Dài'."], ["Không đọc được thời lượng."]
    if c_kc is None:
        diem.append("Bảng 'Dòng dựng' chưa có cột 'Kiểm chứng' (mẫu cũ): thêm cột theo references/mau-ho-so.md.")
    theo_hoi, tong, thieu = {}, 0.0, []
    for r in rows:
        r = r + [""] * (len(header) - len(r))
        if all(c in ("", "...", "…") for c in r):
            continue
        nhan = r[c_nhan] if c_nhan is not None else ""
        ten = nhan or (r[1] if len(r) > 1 else "?")
        d = doc_thoi_luong(r[c_dai])
        if d is None and c_io is not None:
            m = re.search(rf"({SO})\s*-\s*({SO})", r[c_io])
            if m and so(m.group(2)) > so(m.group(1)):
                d = so(m.group(2)) - so(m.group(1))
        if d is None:
            thieu.append(ten)
            continue
        hoi = (r[c_hoi] if c_hoi is not None else "") or "(không ghi hồi)"
        theo_hoi[hoi] = theo_hoi.get(hoi, 0.0) + d
        tong += d
        if c_dh is not None and c_kc is not None and r[c_dh] and CAN_KIEM.search(r[c_dh]) and not r[c_kc]:
            diem.append(f"Dòng {ten}: đồ họa \"{r[c_dh][:60]}\" mang dữ kiện nhưng cột 'Kiểm chứng' trống.")
    if thieu:
        diem.append("Dòng chưa có thời lượng: " + ", ".join(thieu) + ".")
    bao.append("| Hồi | Ước tính |\n|---|---|")
    for h, d in theo_hoi.items():
        bao.append(f"| {h} | {fmt(d)} |")
    bao.append(f"| **Tổng** | **{fmt(tong)}** |")
    muc_tieu = doc_muc_tieu(muc_tieu_arg) if muc_tieu_arg else None
    if muc_tieu is None:
        h2, r2 = bang_sau_tieu_de(lines, "Thời lượng ước tính")
        if h2:
            cm = cot(h2, "mục tiêu")
            for r in r2:
                if r and "tổng" in r[0].lower() and cm is not None and cm < len(r):
                    muc_tieu = doc_muc_tieu(r[cm])
    if muc_tieu:
        vuot = tong / muc_tieu - 1
        bao.append(f"\nMục tiêu: {fmt(muc_tieu)} · chênh {vuot:+.0%}.")
        if vuot > TRAN_VUOT:
            diem.append(f"Vượt mục tiêu {vuot:.0%} (> 30%): đề xuất hai phương án (đầy đủ và gọn, ghi rõ bỏ dòng nào) để chọn TRƯỚC khi dựng.")
    else:
        bao.append("\nChưa có mục tiêu thời lượng (--muc-tieu hoặc hàng 'Tổng' của bảng 'Thời lượng ước tính').")
    return diem, bao


NHIP = re.compile(rf"^###\s*Nhịp\s*(\w+)\s*·\s*(\d+):({SO})\s*-\s*(\d+):({SO})\s*(?:\(({SO})\s*s\))?\s*(?:·\s*(.*))?$")
TOAN_KHUNG = re.compile(r"toàn khung|InfoList|InfoSteps|InfoStat|InfoQuote", re.I)


def kiem_infomotion(lines, muc_tieu_arg):
    diem, bao, nhip = [], [], []
    cur = None
    for l in lines:
        m = NHIP.match(l.strip())
        if m:
            cur = {"ten": m.group(1), "bd": int(m.group(2)) * 60 + so(m.group(3)),
                   "kt": int(m.group(4)) * 60 + so(m.group(5)), "loai": (m.group(7) or "").strip(),
                   "hinh": "", "kiem": None, "moi": False}
            nhip.append(cur)
            continue
        if l.startswith("## "):
            cur = None
        if cur is None:
            continue
        s = l.strip()
        if s.lower().startswith("hình:"):
            cur["hinh"] = s[5:].strip()
        elif s.lower().startswith("kiểm chứng:"):
            cur["kiem"] = s[11:].strip()
        if "ẨN DỤ MỚI" in s:
            cur["moi"] = True
    if not nhip:
        return ["Không tìm thấy khối '### Nhịp <n> · m:ss,d-m:ss,d · <loại>'."], ["Không đọc được kịch bản."]
    tong = max(n["kt"] for n in nhip)
    co_hinh = [n for n in nhip if n["hinh"] and not n["hinh"].upper().startswith("KHÔNG")]
    for a, b in zip(co_hinh, co_hinh[1:]):
        if b["bd"] - a["bd"] < KHOANG_HINH_MIN:
            diem.append(f"Nhịp {a['ten']} → {b['ten']}: hai hình mới cách nhau {vn(b['bd'] - a['bd'])} giây (trần 1 hình / {vn(KHOANG_HINH_MIN, 0)} giây).")
    toan = [n for n in co_hinh if TOAN_KHUNG.search(n["hinh"]) and "nổi" not in n["hinh"].lower()]
    for a, b in zip(toan, toan[1:]):
        khe = b["bd"] - a["kt"]
        if 0 <= khe < KHE_TOAN_KHUNG_MIN:
            diem.append(f"Nhịp {a['ten']} → {b['ten']}: hai đồ họa toàn khung chỉ cách {vn(khe)} giây nền (tối thiểu 5 giây, hoặc gộp làm một).")
    for n in nhip:
        can = ("số liệu" in n["loai"].lower() or re.search(r"InfoStat|InfoQuote", n["hinh"], re.I)
               or re.search(r"[\"“][^\"”]*\d[^\"”]*[\"”]", n["hinh"]))
        if can and not n["kiem"]:
            diem.append(f"Nhịp {n['ten']} ({n['loai'] or 'không ghi loại'}): hiện dữ kiện nhưng thiếu dòng 'Kiểm chứng:'.")
    moi = [n["ten"] for n in nhip if n["moi"]]
    phut = tong / 60 if tong else 1
    bao.append(f"Tổng: {fmt(tong)} · {len(nhip)} nhịp · {len(co_hinh)} hình ({vn(len(co_hinh) / phut)} hình/phút, trần 6-7,5) · "
               f"{len(toan)} đồ họa toàn khung · {len(nhip) - len(co_hinh)} nhịp không hình.")
    if moi:
        bao.append("Ẩn dụ mới chờ duyệt ở nhịp: " + ", ".join(moi) + ".")
    muc_tieu = doc_muc_tieu(muc_tieu_arg) if muc_tieu_arg else None
    if muc_tieu:
        vuot = tong / muc_tieu - 1
        bao.append(f"Mục tiêu: {fmt(muc_tieu)} · chênh {vuot:+.0%}.")
    return diem, bao


def main():
    ap = argparse.ArgumentParser(description="Kiểm giấy kịch bản trước khi dựng")
    ap.add_argument("kich_ban")
    ap.add_argument("--muc-tieu", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--khoang-hinh", type=float, default=None,
                    help="infomotion: khoảng tối thiểu giữa hai hình mới, giây (mặc định 8; chỉ nới khi user chủ động yêu cầu)")
    a = ap.parse_args()
    global KHOANG_HINH_MIN
    if a.khoang_hinh:
        KHOANG_HINH_MIN = a.khoang_hinh
    with open(a.kich_ban, encoding="utf-8") as f:
        lines = f.read().splitlines()
    dau = next((l for l in lines if l.startswith("# ")), "").lower()
    if "hình tượng hoá" in dau or "hình tượng hóa" in dau or "infomotion" in dau:
        loai, (diem, bao) = "infomotion", kiem_infomotion(lines, a.muc_tieu)
    else:
        loai, (diem, bao) = "phim tài liệu", kiem_tai_lieu(lines, a.muc_tieu)
    out = [f"# Kiểm giấy ({loai}): {a.kich_ban}", ""] + bao + [""]
    if diem:
        out.append("## Cần xem")
        out += [f"- {d}" for d in diem]
        out.append("")
        out.append(f"KIỂM GIẤY: CẦN XEM ({len(diem)} điểm)")
    else:
        out.append("KIỂM GIẤY: ĐẠT")
    text = "\n".join(out)
    print(text)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    sys.exit(1 if diem else 0)


if __name__ == "__main__":
    main()
