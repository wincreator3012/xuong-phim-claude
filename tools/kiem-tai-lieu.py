#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CỔNG KIỂM TÀI LIỆU của xưởng: skill, tài liệu và kho ẩn dụ có còn nói đúng với nhau không.

    python3 tools/kiem-tai-lieu.py                 # kiểm, thoát mã 0 = ĐẠT
    python3 tools/kiem-tai-lieu.py --dong-dau      # cập nhật dòng dấu phiên bản cuối mỗi SKILL.md
    python3 tools/kiem-tai-lieu.py --so-tai-khoan <thư mục skill đã cài>   # skill đã cài có cũ hơn bản nguồn không
    python3 tools/kiem-tai-lieu.py --goc <thư mục> # kiểm một cây xưởng khác (dùng khi đồng bộ)

Cổng máy cho video (nghiem-thu.py) không đọc chữ; cổng này làm việc đó cho tài liệu:
  1. SKILL.md: phần đầu YAML hợp lệ, name trùng tên thư mục, description dưới 1024 ký tự,
     không chứa ngoặc nhọn (skill tài khoản không lưu được).
  2. Không có gạch dài (em dash) trong tài liệu (quy ước chữ của xưởng: dùng gạch thường).
  3. Mọi đường dẫn viết trong dấu `...` trỏ tới tệp hay thư mục có thật (bỏ qua mẫu có <x>, *,
     và đường dẫn bên trong một dự án như nguon/, transcript/, do-hoa/...).
  4. Kho ẩn dụ do-hoa-chung/an-du-y-niem.json chỉ trỏ tới slug YNiem và variant YCanh có thật.
  5. Mỗi skill có dòng dấu phiên bản; ở xưởng nguồn, mã trong dấu phải khớp nội dung hiện tại
     (sửa skill xong thì chạy --dong-dau, rồi đề xuất lại skill tài khoản).
  6. Mỗi skill có mặt trong bảng "việc nào, skill nào" của CLAUDE.md; mọi tên skill được nhắc
     trong tài liệu đều có thật (bắt tên cũ, hay skill chỉ có ở một trong hai xưởng).
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TOOLS, "pylib"))
try:
    import yaml  # noqa: E402
except ImportError:  # máy thiếu PyYAML: vẫn kiểm được phần lớn, bỏ kiểm YAML chặt
    yaml = None

DAU = re.compile(r"^<!-- ban-nguon: (\S+) (\d{4}-\d{2}-\d{2}) ([0-9a-f]{8}) -->\s*$", re.M)
DAU_BAT_KY = re.compile(r"^<!-- ban-nguon:.*-->\s*\n?", re.M)
DUONG_DAN = re.compile(r"`([^`\s]+)`")
DUOI = (".md", ".py", ".json", ".tsx", ".ts", ".mjs", ".command", ".png", ".jpg", ".mp4", ".webm", ".txt", ".sh")
# đường dẫn bên trong một dự án, trong máy, hay sinh ra lúc chạy: không kiểm tồn tại
BO_QUA_DAU = ("du-an/", "nguon/", "transcript/", "do-hoa/", "xuat-nhap/", "xuat-hoan-chinh/", "slide/", "multicam/",
              "canvas/", "tu-lieu/", "clip-ngan/", "proxy/", ".tam/", "$", "~", "/", "http", "tools/go-bang/",
              "studio/public/brand/", "nhac-nen/rieng/",
              "references/<", "PROXY", "os.", "props.", "palettes.", "brand.", "job.")
BO_QUA_DAU += ("do-hoa-chung/the-gioi-hoat-hoa/", "studio/src/hoat-hoa/")
KY_TU_MAU = set("<>{}*|$=,:;()[]'\"")
# tệp, thư mục chỉ sinh ra khi dùng (cài đặt, dự án đầu tiên): vắng mặt không phải lỗi
SINH_KHI_DUNG = ("nhac-nen/THU-VIEN.md", "do-hoa-chung/an-du-y-niem.json", "tools/.cai-dat.json", "tools/pylib",
                 "tools/models/sherpa-onnx-whisper-", "sherpa-onnx-whisper-", "outputs/", "_to_delete/", "references/", "studio/node_modules/")
TEN_MIEN = re.compile(r"^[a-z0-9.-]+\.(com|org|net|io|vn|dev)/")


def bo_dau(text):
    return DAU_BAT_KY.sub("", text)


def ma_skill(thu_muc):
    h = hashlib.sha256()
    with open(os.path.join(thu_muc, "SKILL.md"), encoding="utf-8") as f:
        h.update(bo_dau(f.read()).rstrip().encode("utf-8"))
    for p in sorted(glob.glob(os.path.join(thu_muc, "references", "*.md"))):
        h.update(b"\0" + os.path.basename(p).encode("utf-8") + b"\0")
        with open(p, "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:8]


class KetQua:
    def __init__(self):
        self.loi, self.canh = [], []

    def l(self, s):
        self.loi.append(s)

    def c(self, s):
        self.canh.append(s)


def bo_cuc(goc):
    """Xưởng nguồn (có thư mục skills-nguon, tài liệu ở gốc) hay repo (skills/, tài liệu ở docs/)."""
    if os.path.isdir(os.path.join(goc, "skills-nguon")):
        return {"nguon": True, "skills": os.path.join(goc, "skills-nguon"),
                "tai_lieu": ["CLAUDE.md", "QUY-TRINH" + "-KY-THUAT.md", "BAI-HOC" + ".md", "HUONG-DAN.md", "phong-cach/PHONG-CACH.md"]}
    return {"nguon": False, "skills": os.path.join(goc, "skills"),
            "tai_lieu": ["CLAUDE.md", "docs/QUY-TRINH-KY-THUAT.md", "docs/BAI-HOC.md", "HUONG-DAN.md", "BAT-DAU.md",
                         "README.md", "phong-cach/PHONG-CACH.md"]}


def cac_skill(bc):
    return sorted(d for d in glob.glob(os.path.join(bc["skills"], "*")) if os.path.isfile(os.path.join(d, "SKILL.md")))


def doc_dau_yaml(text):
    if not text.startswith("---\n"):
        return None, "không mở bằng ---"
    j = text.find("\n---", 4)
    if j < 0:
        return None, "phần đầu YAML không đóng"
    khoi = text[4:j]
    if yaml is not None:
        try:
            d = yaml.safe_load(khoi)
        except yaml.YAMLError as e:
            return None, f"YAML lỗi: {str(e).splitlines()[0]}"
        if not isinstance(d, dict):
            return None, "phần đầu không phải bảng khoá"
        return d, None
    d = {}
    for dong in khoi.splitlines():
        if ":" in dong:
            k, v = dong.split(":", 1)
            d[k.strip()] = v.strip().strip('"')
    return d, None


def kiem_skill(goc, bc, kq):
    for d in cac_skill(bc):
        ten = os.path.basename(d)
        rel = os.path.relpath(os.path.join(d, "SKILL.md"), goc)
        text = open(os.path.join(d, "SKILL.md"), encoding="utf-8").read()
        dau, loi = doc_dau_yaml(text)
        if loi:
            kq.l(f"{rel}: {loi}")
            continue
        if dau.get("name") != ten:
            kq.l(f"{rel}: name '{dau.get('name')}' khác tên thư mục '{ten}'")
        mo_ta = dau.get("description")
        if not isinstance(mo_ta, str) or not mo_ta.strip():
            kq.l(f"{rel}: thiếu description")
        else:
            if len(mo_ta) > 1024:
                kq.l(f"{rel}: description {len(mo_ta)} ký tự (trần 1024)")
            if "<" in mo_ta or ">" in mo_ta:
                kq.l(f"{rel}: description chứa ngoặc nhọn")
        m = DAU.findall(text)
        if not m:
            (kq.l if bc["nguon"] else kq.c)(f"{rel}: thiếu dòng dấu phiên bản (chạy tools/kiem-tai-lieu.py --dong-dau ở xưởng nguồn)")
        elif bc["nguon"]:
            ten_dau, _, ma = m[-1]
            if ten_dau != ten:
                kq.l(f"{rel}: dấu phiên bản ghi tên '{ten_dau}'")
            elif ma != ma_skill(d):
                kq.l(f"{rel}: dấu phiên bản cũ (nội dung đã đổi) - chạy --dong-dau rồi đề xuất lại skill tài khoản")


REPO_CHU_THICH = re.compile(r"<!--\s*REPO:.*?-->", re.S)


def cac_dong(p):
    """Các dòng của một tài liệu, bỏ chú thích <!-- REPO: ... --> (chữ chỉ dành cho repo công khai, kiểm ở bản repo)
    nhưng giữ số dòng."""
    text = open(p, encoding="utf-8").read()
    text = REPO_CHU_THICH.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return text.splitlines(keepends=True)


def cac_tep_tai_lieu(goc, bc):
    ra = [os.path.join(goc, t) for t in bc["tai_lieu"] if os.path.isfile(os.path.join(goc, t))]
    ra += sorted(glob.glob(os.path.join(bc["skills"], "**", "*.md"), recursive=True))
    ra += sorted(glob.glob(os.path.join(goc, "do-hoa-chung", "*.md")))
    return ra


def kiem_chu(goc, bc, kq):
    for p in cac_tep_tai_lieu(goc, bc):
        rel = os.path.relpath(p, goc)
        for i, dong in enumerate(cac_dong(p), 1):
            if "\u2014" in dong and "gạch dài" not in dong:
                kq.l(f"{rel}:{i}: có gạch dài (em dash)")


def thu_muc_skill_chua(bc, tep):
    """Thư mục skill chứa tệp (skills/<x>/), hoặc None nếu tệp không thuộc skill nào."""
    d = os.path.dirname(os.path.abspath(tep))
    goc_skill = os.path.abspath(bc["skills"])
    while d != os.path.dirname(d):
        if os.path.dirname(d) == goc_skill:
            return d
        d = os.path.dirname(d)
    return None


def tim(goc, bc, tep, dd):
    dd = dd.rstrip(".").rstrip("/")
    ung_vien = [os.path.join(goc, dd), os.path.join(os.path.dirname(tep), dd), os.path.join(bc["skills"], dd),
                os.path.join(goc, "studio", dd)]
    sk = thu_muc_skill_chua(bc, tep)
    if sk:
        ung_vien.append(os.path.join(sk, dd))
    elif dd.startswith("references/"):
        # tài liệu chung nhắc references/ của một skill đã nêu tên ngay cạnh: chấp nhận nếu skill nào đó có
        ung_vien += [os.path.join(s, dd) for s in cac_skill(bc)]
    return any(os.path.exists(u) for u in ung_vien)


def kiem_duong_dan(goc, bc, kq):
    for p in cac_tep_tai_lieu(goc, bc):
        rel = os.path.relpath(p, goc)
        trong_ma = False
        for i, dong in enumerate(cac_dong(p), 1):
            if dong.lstrip().startswith("```"):
                trong_ma = not trong_ma
                continue
            if trong_ma:
                continue
            for m in DUONG_DAN.finditer(dong):
                dd = m.group(1)
                if "/" not in dd or not (dd.endswith(DUOI) or dd.endswith("/")):
                    continue
                if any(k in KY_TU_MAU for k in dd) or dd.startswith(BO_QUA_DAU) or dd.startswith("-"):
                    continue
                if TEN_MIEN.match(dd) or dd == "references/" or (dd.startswith(SINH_KHI_DUNG) and not dd.startswith("references/")):
                    continue
                if not tim(goc, bc, p, dd):
                    kq.l(f"{rel}:{i}: đường dẫn không tồn tại `{dd}`")


TEN_SKILL = re.compile(r"(?<![-\w/])((?:ldn-)?phim-[a-z]+(?:-[a-z]+)*)(?![-\w./])")


def kiem_ten_skill(goc, bc, kq):
    """Tài liệu nhắc tới skill nào thì skill đó phải có thật (bắt tên cũ, skill chỉ có ở một xưởng)."""
    co = {os.path.basename(d) for d in cac_skill(bc)}
    for p in cac_tep_tai_lieu(goc, bc):
        rel = os.path.relpath(p, goc)
        for i, dong in enumerate(cac_dong(p), 1):
            for m in TEN_SKILL.finditer(dong):
                ten = m.group(1)
                if bc["nguon"] and not ten.startswith("ldn-"):
                    continue   # xưởng nguồn: tên không tiền tố thường là tên repo được nhắc có chủ đích
                if ten not in co:
                    kq.l(f"{rel}:{i}: nhắc skill '{ten}' không có trong {os.path.relpath(bc['skills'], goc)}/")


def kiem_an_du(goc, kq):
    tu_dien = os.path.join(goc, "do-hoa-chung", "an-du-y-niem.json")
    kho = os.path.join(goc, "studio", "src", "y-niem", "index.ts")
    ycanh = os.path.join(goc, "studio", "src", "components", "YCanh.tsx")
    if not os.path.isfile(tu_dien):
        return
    if not (os.path.isfile(kho) and os.path.isfile(ycanh)):
        kq.c("không thấy studio/src để đối chiếu kho ẩn dụ")
        return
    slug = set(re.findall(r"^  '([a-z0-9-]+)': \{", open(kho, encoding="utf-8").read(), re.M))
    t = open(ycanh, encoding="utf-8").read()
    kieu = re.search(r"export type YCanhVariant =(.*?);", t, re.S)
    variant = set(re.findall(r"'([a-z0-9-]+)'", kieu.group(1))) if kieu else set()
    try:
        d = json.load(open(tu_dien, encoding="utf-8"))
    except ValueError as e:
        kq.l(f"do-hoa-chung/an-du-y-niem.json: JSON lỗi ({e})")
        return
    muc = d.get("muc", d) if isinstance(d, dict) else {}
    dung = set()
    for k, v in muc.items():
        if not isinstance(v, dict):
            continue
        hinh = v.get("hinh-thuc")
        props = v.get("props") or {}
        if hinh == "YNiem":
            s = props.get("slug") or v.get("slug-hinh")
            dung.add(s)
            if s not in slug:
                kq.l(f"an-du-y-niem.json mục '{k}': slug YNiem '{s}' không có trong studio/src/y-niem/index.ts")
        elif hinh == "YCanh":
            s = props.get("variant") or v.get("slug-hinh")
            if s not in variant:
                kq.l(f"an-du-y-niem.json mục '{k}': variant YCanh '{s}' không có trong YCanh.tsx")
    for s in sorted(slug - dung):
        kq.c(f"slug YNiem '{s}' có hình nhưng chưa có mục trong an-du-y-niem.json (slug mồ côi)")


def kiem_bang_skill(goc, bc, kq):
    p = os.path.join(goc, "CLAUDE.md")
    if not os.path.isfile(p):
        kq.c("không có CLAUDE.md để đối chiếu bảng skill")
        return
    t = open(p, encoding="utf-8").read()
    for d in cac_skill(bc):
        ten = os.path.basename(d)
        if ten not in t:
            kq.l(f"CLAUDE.md: bảng việc chưa có skill '{ten}'")


def dong_dau(goc, bc):
    if not bc["nguon"]:
        sys.exit("! --dong-dau chỉ chạy ở xưởng nguồn (có thư mục skills-nguon)")
    hom_nay = dt.date.today().isoformat()
    for d in cac_skill(bc):
        ten = os.path.basename(d)
        p = os.path.join(d, "SKILL.md")
        text = open(p, encoding="utf-8").read()
        ma = ma_skill(d)
        m = DAU.findall(text)
        if m and m[-1][0] == ten and m[-1][2] == ma:
            print(f"  = {ten} {m[-1][1]} {ma}")
            continue
        than = bo_dau(text).rstrip() + "\n"
        with open(p, "w", encoding="utf-8") as f:
            f.write(than + f"\n<!-- ban-nguon: {ten} {hom_nay} {ma} -->\n")
        print(f"  ✎ {ten} {hom_nay} {ma}")


def so_tai_khoan(goc, bc, thu_muc):
    lech = 0
    for d in cac_skill(bc):
        ten = os.path.basename(d)
        nguon = DAU.findall(open(os.path.join(d, "SKILL.md"), encoding="utf-8").read())
        p = os.path.join(thu_muc, ten, "SKILL.md")
        if not os.path.isfile(p):
            print(f"  ? {ten}: chưa cài")
            lech += 1
            continue
        cai = DAU.findall(open(p, encoding="utf-8").read())
        n = nguon[-1] if nguon else None
        c = cai[-1] if cai else None
        if n and c and n[2] == c[2]:
            print(f"  = {ten} {c[1]} {c[2]}")
        else:
            print(f"  ≠ {ten}: đã cài {c[1] + ' ' + c[2] if c else '(không có dấu)'}, nguồn {n[1] + ' ' + n[2] if n else '(không có dấu)'}")
            lech += 1
    print(f"\n{lech} skill cần đề xuất lại." if lech else "\nMọi skill đã cài khớp bản nguồn.")
    return 1 if lech else 0


def main():
    ap = argparse.ArgumentParser(description="Cổng kiểm tài liệu của xưởng")
    ap.add_argument("--goc", default=os.path.dirname(TOOLS))
    ap.add_argument("--dong-dau", action="store_true")
    ap.add_argument("--so-tai-khoan", metavar="THU_MUC")
    a = ap.parse_args()
    goc = os.path.abspath(a.goc)
    bc = bo_cuc(goc)
    if a.dong_dau:
        dong_dau(goc, bc)
        return 0
    if a.so_tai_khoan:
        return so_tai_khoan(goc, bc, a.so_tai_khoan)
    kq = KetQua()
    kiem_skill(goc, bc, kq)
    kiem_chu(goc, bc, kq)
    kiem_duong_dan(goc, bc, kq)
    kiem_ten_skill(goc, bc, kq)
    kiem_an_du(goc, kq)
    kiem_bang_skill(goc, bc, kq)
    n = len(cac_skill(bc))
    for s in kq.canh:
        print("  cảnh báo:", s)
    for s in kq.loi:
        print("  LỖI:", s)
    if yaml is None:
        print("  cảnh báo: thiếu PyYAML, bỏ qua kiểm YAML chặt")
    print(f"KIỂM TÀI LIỆU: {'ĐẠT' if not kq.loi else 'KHÔNG ĐẠT'} ({n} skill, {len(kq.loi)} lỗi, {len(kq.canh)} cảnh báo)")
    return 1 if kq.loi else 0


if __name__ == "__main__":
    sys.exit(main())
