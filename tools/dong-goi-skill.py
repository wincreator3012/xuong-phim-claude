#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐÓNG GÓI SKILL của xưởng thành tệp .skill để lưu vào tài khoản AI của người dùng, và theo dõi bản nào đã lưu.

Skill nguồn nằm trong thư mục xưởng (thư mục skill của repo; mỗi skill một thư mục có SKILL.md).
Bản lưu trong tài khoản (Claude: Customize > Skills) là BẢN CHÉP: giúp AI tự nhận ra việc và gọi đúng
quy trình ở mọi phiên, nhưng không tự cập nhật khi nguồn đổi. Công cụ này giữ hai bên khớp nhau.

    python3 tools/dong-goi-skill.py                    # trạng thái: skill nào cần lưu (lại) vào tài khoản
    python3 tools/dong-goi-skill.py --lam              # đóng gói các skill đã đổi so với lần lưu cuối
    python3 tools/dong-goi-skill.py --lam --tat-ca     # đóng gói tất cả
    python3 tools/dong-goi-skill.py --lam <tên> ...    # đóng gói vài skill (tên thư mục hoặc tên tài khoản)
    python3 tools/dong-goi-skill.py --da-luu [<tên> ...|--tat-ca]   # ghi nhận người dùng đã lưu xong
    python3 tools/dong-goi-skill.py --so-voi <thư mục skill đã cài> # đối chiếu thẳng với bản đã cài

Tên trong tài khoản = tiền tố riêng + tên thư mục (vd tiền tố "tma": phim-dung-bai thành tma-phim-dung-bai),
để người dùng nhận ra skill của mình và không trùng skill người khác. Tiền tố đặt một lần trong
cau-hinh.json, khoá "tienToSkill" (2-6 chữ thường hoặc số, thường là chữ cái đầu họ tên). Thư mục skill
đã mang sẵn tiền tố thì giữ nguyên tên. Trong bản đóng gói, mọi chỗ nhắc tên skill khác của xưởng cũng
đổi sang tên tài khoản (đường dẫn như skills/phim-x/ thì giữ, vì đó là đường trong thư mục xưởng).

Tệp ra ở thư mục tạm của xưởng (Du an/_tam/goi-skill/<ngày giờ>/, ngoài repo): <tên>.skill là tệp ZIP chứa thư mục
<tên>/ (SKILL.md, references/). Cuối SKILL.md có dấu "ban-nguon: <tên> <ngày> <mã 8 ký tự>"; mã tính trên
nội dung nguồn (SKILL.md và references/*.md, cùng cách với kiem-tai-lieu.py), nên chỉ cần so mã là biết
bản trong tài khoản có còn đúng nguồn không. Sổ ghi ở tools/.dong-goi-skill.json (sổ riêng của từng xưởng; repo công khai không mang theo).
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys
import zipfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import cau_hinh as CH  # noqa: E402

SO = os.path.join(TOOLS, ".dong-goi-skill.json")
DAU = re.compile(r"^<!-- ban-nguon: (\S+) (\d{4}-\d{2}-\d{2}) ([0-9a-f]{8}) -->\s*$", re.M)
DAU_BAT_KY = re.compile(r"^<!-- ban-nguon:.*-->\s*\n?", re.M)
TEN_HOP_LE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
TIEN_TO_HOP_LE = re.compile(r"^[a-z0-9]{2,6}$")


def thu_muc_skill():
    for ten in ("skills-nguon", "skills"):
        d = os.path.join(GOC, ten)
        if os.path.isdir(d):
            return d
    sys.exit("! Không thấy thư mục skill của xưởng (skills/).")


def cac_skill():
    goc = thu_muc_skill()
    return sorted(d for d in glob.glob(os.path.join(goc, "*"))
                  if os.path.isfile(os.path.join(d, "SKILL.md")) and not os.path.basename(d).startswith("_"))


def bo_dau(text):
    return DAU_BAT_KY.sub("", text)


def ma_skill(d):
    """Cùng cách tính với tools/kiem-tai-lieu.py (ma_skill)."""
    h = hashlib.sha256()
    with open(os.path.join(d, "SKILL.md"), encoding="utf-8") as f:
        h.update(bo_dau(f.read()).rstrip().encode("utf-8"))
    for p in sorted(glob.glob(os.path.join(d, "references", "*.md"))):
        h.update(b"\0" + os.path.basename(p).encode("utf-8") + b"\0")
        with open(p, "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:8]


def tien_to():
    v = (CH.doc().get("tienToSkill") or "").strip().lower()
    if v and not TIEN_TO_HOP_LE.match(v):
        sys.exit(f"! tienToSkill '{v}' không hợp lệ: 2-6 chữ thường hoặc số, không dấu (vd chữ cái đầu họ tên).")
    return v


def ten_tai_khoan(d, tt):
    ten = os.path.basename(d)
    if tt and ten.startswith(tt + "-"):
        return ten
    if not tt:
        if re.match(r"^[a-z0-9]{2,6}-", ten) and not ten.startswith(("phim-", "thiet-")):
            return ten  # thư mục đã mang tiền tố riêng
        sys.exit("! Chưa có tiền tố skill. Thêm vào cau-hinh.json ở gốc xưởng, ví dụ: \"tienToSkill\": \"tma\" "
                 "(chữ cái đầu họ tên người dùng), rồi chạy lại. Chưa có cau-hinh.json thì chép từ cau-hinh.mau.json.")
    return f"{tt}-{ten}"


def bang_ten(tt):
    return {os.path.basename(d): ten_tai_khoan(d, tt) for d in cac_skill()}


def doi_ten(text, bang):
    for goc_ten in sorted(bang, key=len, reverse=True):
        moi = bang[goc_ten]
        if moi == goc_ten:
            continue
        text = re.sub(r"(?<![\w/.-])" + re.escape(goc_ten) + r"(?![\w/-])", moi, text)
    return text


def tach_dau_yaml(text):
    if not text.startswith("---\n"):
        return None, None
    j = text.find("\n---", 4)
    if j < 0:
        return None, None
    return text[4:j], text[j:]


def mo_ta(khoi):
    m = re.search(r"^description:\s*(.*)$", khoi, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1].replace('\\"', '"')
    return v


def doc_so():
    if os.path.isfile(SO):
        try:
            return json.load(open(SO, encoding="utf-8"))
        except ValueError:
            pass
    return {"dong_goi": {}, "da_luu": {}}


def ghi_so(so):
    with open(SO, "w", encoding="utf-8") as f:
        json.dump(so, f, ensure_ascii=False, indent=1)


def dong_goi_mot(d, tt, bang, ra, duoi):
    ten = ten_tai_khoan(d, tt)
    if not TEN_HOP_LE.match(ten):
        sys.exit(f"! Tên '{ten}' không hợp lệ cho skill tài khoản (chữ thường, số, gạch ngang, tối đa 64).")
    text = bo_dau(open(os.path.join(d, "SKILL.md"), encoding="utf-8").read()).rstrip() + "\n"
    khoi, sau = tach_dau_yaml(text)
    if khoi is None:
        sys.exit(f"! {os.path.basename(d)}/SKILL.md thiếu phần đầu YAML (--- name, description ---).")
    khoi = re.sub(r"^name:.*$", f'name: "{ten}"', khoi, count=1, flags=re.M)
    khoi = doi_ten(khoi, bang)
    mt = mo_ta(khoi)
    loi = []
    if not mt:
        loi.append("thiếu description")
    if len(mt) > 1024:
        loi.append(f"description {len(mt)} ký tự (trần 1024)")
    if "<" in mt or ">" in mt:
        loi.append("description chứa ngoặc nhọn")
    if loi:
        sys.exit(f"! {ten}: " + "; ".join(loi) + ". Sửa nguồn rồi đóng gói lại.")
    ma = ma_skill(d)
    hom_nay = dt.date.today().isoformat()
    than = "---\n" + khoi + doi_ten(sau, bang).rstrip() + f"\n\n<!-- ban-nguon: {ten} {hom_nay} {ma} -->\n"
    p = os.path.join(ra, ten + duoi)
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{ten}/SKILL.md", than)
        for f in sorted(glob.glob(os.path.join(d, "**", "*"), recursive=True)):
            rel = os.path.relpath(f, d)
            if rel == "SKILL.md" or os.path.isdir(f) or os.path.basename(f).startswith("."):
                continue
            if f.endswith(".md"):
                z.writestr(f"{ten}/{rel}", doi_ten(open(f, encoding="utf-8").read(), bang))
            else:
                z.write(f, f"{ten}/{rel}")
    return ten, ma, hom_nay, p


DOC_TRUOC = """# Skill vừa đóng gói: lưu vào tài khoản AI của bạn

Mỗi tệp `.skill` là một quy trình chuẩn của xưởng. Lưu vào tài khoản thì ở mọi phiên làm việc, AI tự nhận ra
việc bạn nhờ (ví dụ "cắt clip ngắn") và làm đúng quy trình, không cần bạn nhắc tên skill.

Cách lưu (app Claude):
1. Trong cuộc trò chuyện, bấm nút lưu skill trên thẻ của từng tệp (nếu app hiện nút này), hoặc
2. Vào Customize > Skills, bấm "+", chọn "Create skill" rồi "Upload a skill", chọn tệp. Nếu hộp chọn tệp
   không nhận đuôi .skill, đổi đuôi thành .zip (nội dung giống hệt) rồi tải lên.
3. Skill cùng tên đã có trong tài khoản: chọn thay bản cũ; nếu app tạo thành hai bản, xoá bản cũ.
4. Bật skill (công tắc bên cạnh tên). Cần bật "Code execution and file creation" trong Settings > Capabilities.

Lưu xong, báo AI "đã lưu skill" để nó ghi sổ (python3 tools/dong-goi-skill.py --da-luu).
Thư mục này là việc tạm: xoá lúc nào cũng được, đóng gói lại bằng python3 tools/dong-goi-skill.py --lam.

Các tệp trong lượt này:
"""


def lam(a, tt):
    bang = bang_ten(tt)
    tat = cac_skill()
    so = doc_so()
    if a.ten:
        muon = set(a.ten)
        chon = [d for d in tat if os.path.basename(d) in muon or ten_tai_khoan(d, tt) in muon]
        thieu = muon - {os.path.basename(d) for d in chon} - {ten_tai_khoan(d, tt) for d in chon}
        if thieu:
            sys.exit("! Không có skill: " + ", ".join(sorted(thieu)))
    elif a.tat_ca:
        chon = tat
    else:
        chon = [d for d in tat if so["da_luu"].get(ten_tai_khoan(d, tt), {}).get("ma") != ma_skill(d)]
    if not chon:
        print("Mọi skill trong tài khoản đã khớp nguồn theo sổ; không có gì cần đóng gói. (--tat-ca để đóng gói lại tất cả)")
        return 0
    # mỗi lượt một thư mục mới theo giờ: không lẫn bản cũ, không cần quyền xoá
    ra = os.path.abspath(a.ra) if a.ra else CH.tam("goi-skill", dt.datetime.now().strftime("%Y-%m-%d %H%M"))
    if CH.trong_repo(ra):
        sys.exit("! Không ghi gói skill vào trong repo; dùng thư mục tạm (mặc định Du an/_tam/goi-skill/).")
    os.makedirs(ra, exist_ok=True)
    duoi = ".zip" if a.zip else ".skill"
    dong = []
    for d in chon:
        ten, ma, ngay, p = dong_goi_mot(d, tt, bang, ra, duoi)
        so["dong_goi"][ten] = {"nguon": os.path.relpath(d, GOC), "ma": ma, "ngay": ngay}
        dong.append(f"- `{os.path.basename(p)}` (nguồn {os.path.relpath(d, GOC)}, mã {ma})")
        print(f"  ✓ {os.path.basename(p)}  {ma}")
    with open(os.path.join(ra, "DOC-TRUOC.md"), "w", encoding="utf-8") as f:
        f.write(DOC_TRUOC + "\n".join(dong) + "\n")
    ghi_so(so)
    print(f"\nĐã đóng gói {len(chon)} skill vào {ra}")
    print("Bước tiếp: gửi các tệp cho người dùng lưu vào tài khoản (xem DOC-TRUOC.md trong thư mục đó), rồi --da-luu.")
    return 0


def da_luu(a, tt):
    so = doc_so()
    tat = {ten_tai_khoan(d, tt): d for d in cac_skill()}
    if a.ten:
        ten = [t if t in tat else ten_tai_khoan(os.path.join(thu_muc_skill(), t), tt) for t in a.ten]
    elif a.tat_ca:
        ten = list(tat)
    else:
        ten = list(so["dong_goi"])
    hom_nay = dt.date.today().isoformat()
    for t in ten:
        if t not in tat:
            sys.exit(f"! Không có skill '{t}'")
        goi = so["dong_goi"].get(t)
        ma = ma_skill(tat[t])
        if goi and goi["ma"] != ma:
            print(f"  ! {t}: nguồn đã đổi sau lần đóng gói; ghi nhận theo bản đã đóng gói ({goi['ma']}), nhớ đóng gói lại")
            ma = goi["ma"]
        so["da_luu"][t] = {"ma": ma, "ngay": hom_nay}
        print(f"  ✓ đã lưu: {t} {ma}")
    ghi_so(so)
    return 0


def trang_thai(tt):
    so = doc_so()
    can = 0
    print("Skill của xưởng và bản trong tài khoản (theo sổ tools/.dong-goi-skill.json):")
    for d in cac_skill():
        t = ten_tai_khoan(d, tt)
        ma = ma_skill(d)
        luu = so["da_luu"].get(t)
        if not luu:
            print(f"  ? {t}: chưa lưu vào tài khoản lần nào")
            can += 1
        elif luu["ma"] == ma:
            print(f"  = {t} {ma} (lưu {luu['ngay']})")
        else:
            print(f"  ≠ {t}: tài khoản giữ {luu['ma']} ({luu['ngay']}), nguồn nay {ma}: cần lưu lại")
            can += 1
    print(f"\n{can} skill cần đóng gói và lưu (lại): python3 tools/dong-goi-skill.py --lam" if can
          else "\nMọi skill trong tài khoản khớp nguồn.")
    return 0


def so_voi(thu_muc, tt):
    lech = 0
    for d in cac_skill():
        t = ten_tai_khoan(d, tt)
        ma = ma_skill(d)
        p = os.path.join(thu_muc, t, "SKILL.md")
        if not os.path.isfile(p):
            print(f"  ? {t}: chưa cài")
            lech += 1
            continue
        cai = open(p, encoding="utf-8").read()
        dau = DAU.findall(cai)
        ma_cai = dau[-1][2] if dau else None
        khoi_cai, _ = tach_dau_yaml(cai)
        khoi_nguon, _ = tach_dau_yaml(open(os.path.join(d, "SKILL.md"), encoding="utf-8").read())
        mt_cai = mo_ta(khoi_cai or "")
        mt_nguon = mo_ta(doi_ten(khoi_nguon or "", bang_ten(tt)))
        if ma_cai != ma:
            print(f"  ≠ {t}: đã cài {dau[-1][1] + ' ' + ma_cai if dau else '(không có dấu phiên bản)'}, nguồn {ma}")
            lech += 1
        elif mt_cai != mt_nguon:
            print(f"  ~ {t}: cùng phiên bản {ma} nhưng mô tả kích hoạt khác nguồn ({len(mt_cai)} so với {len(mt_nguon)} ký tự)")
            lech += 1
        else:
            print(f"  = {t} {ma}")
    print(f"\n{lech} skill cần lưu lại." if lech else "\nMọi skill đã cài khớp nguồn.")
    return 1 if lech else 0


def main():
    ap = argparse.ArgumentParser(description="Đóng gói skill của xưởng để lưu vào tài khoản AI")
    ap.add_argument("ten", nargs="*", help="tên skill (thư mục hoặc tên tài khoản)")
    ap.add_argument("--lam", action="store_true", help="đóng gói")
    ap.add_argument("--da-luu", action="store_true", help="ghi nhận đã lưu vào tài khoản")
    ap.add_argument("--so-voi", metavar="THU_MUC", help="đối chiếu với thư mục skill đã cài")
    ap.add_argument("--tat-ca", action="store_true")
    ap.add_argument("--zip", action="store_true", help="đuôi .zip thay .skill")
    ap.add_argument("--ra", help="thư mục ra (mặc định Du an/_tam/goi-skill)")
    a = ap.parse_args()
    tt = tien_to()
    if a.lam:
        return lam(a, tt)
    if a.da_luu:
        return da_luu(a, tt)
    if a.so_voi:
        return so_voi(os.path.expanduser(a.so_voi), tt)
    return trang_thai(tt)


if __name__ == "__main__":
    sys.exit(main())
