#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TẢI CHẤT LIỆU ÂM THANH theo mẫu phong cách, từ danh mục đã kiểm định thu-vien/am-thanh.json.

    python3 tools/tai-chat-lieu.py --mau tinh-lang          # tải những gì hợp mẫu, in việc còn lại
    python3 tools/tai-chat-lieu.py --mau am-ap --chi-liet-ke # chỉ in danh sách, không tải
    python3 tools/tai-chat-lieu.py --tat-ca                  # mọi track trong danh mục
    python3 tools/tai-chat-lieu.py --danh-sach-link          # in link để người dùng tự bấm tải

Cách hoạt động:
  - Track có link tải thẳng (Kevin MacLeod, incompetech.com) → thử curl về nhac-nen/<nhóm>/.
    Mạng của máy ảo có thể chặn; lỗi thì ghi vào danh sách "tải bằng trình duyệt".
  - Track Pixabay KHÔNG tải thẳng được (trang yêu cầu bấm nút). Script in danh sách trang
    để Claude mở bằng trình duyệt (bấm "Free download", chờ 6-8 giây mỗi track) hoặc
    gửi người dùng tự bấm. File về ~/Downloads → chạy:
        python3 tools/nhap-am-thanh.py --tu ~/Downloads
    để chuyển vào đúng nhóm, đặt tên đúng mẫu, đo LUFS, ghi nhac-nen/THU-VIEN.md.
Sau mọi lượt tải, luôn chạy nhap-am-thanh.py để danh mục thật của máy khớp với file có mặt.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
CATALOG = os.path.join(ROOT, "thu-vien", "am-thanh.json")


def da_co(muc, loai):
    thu_muc = os.path.join(ROOT, "nhac-nen" if loai == "nhac" else "hieu-ung", muc["nhom"])
    if not os.path.isdir(thu_muc):
        return None
    for f in os.listdir(thu_muc):
        if os.path.splitext(f)[0] == muc["id"] and os.path.getsize(os.path.join(thu_muc, f)) > 10000:
            return os.path.join(thu_muc, f)
    return None


def tai_thang(url, dst, timeout=120):
    if shutil.which("curl"):
        p = subprocess.run(["curl", "-sL", "--fail", "--max-time", str(timeout), "-A", "Mozilla/5.0",
                            "-o", dst, url], capture_output=True, text=True)
        okk = p.returncode == 0 and os.path.isfile(dst) and os.path.getsize(dst) > 100000
    else:
        import urllib.request
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r, open(dst, "wb") as f:
                shutil.copyfileobj(r, f)
            okk = os.path.getsize(dst) > 100000
        except Exception:  # noqa: BLE001
            okk = False
    if not okk and os.path.isfile(dst):
        try:
            os.remove(dst)
        except OSError:
            open(dst, "w").close()
    return okk


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mau", help="tên mẫu phong cách (tinh-lang | am-ap | hien-dai | hoc-thuat)")
    ap.add_argument("--tat-ca", action="store_true")
    ap.add_argument("--chi-liet-ke", action="store_true")
    ap.add_argument("--danh-sach-link", action="store_true")
    args = ap.parse_args()
    if not (args.mau or args.tat_ca or args.danh_sach_link):
        ap.error("cần --mau <tên> hoặc --tat-ca hoặc --danh-sach-link")

    with open(CATALOG, encoding="utf-8") as f:
        cat = json.load(f)

    def loc(ds):
        if args.tat_ca or args.danh_sach_link and not args.mau:
            return ds
        return [m for m in ds if args.mau in m.get("mau", [])]

    nhac = loc(cat["nhac"])
    sfx = loc(cat["hieu_ung"])
    print(f"Danh mục: {len(nhac)} track nhạc, {len(sfx)} hiệu ứng" + (f" hợp mẫu '{args.mau}'" if args.mau and not args.tat_ca else ""))

    trinh_duyet, xong, loi = [], [], []
    for loai, ds in (("nhac", nhac), ("sfx", sfx)):
        for m in ds:
            co = da_co(m, loai)
            if co:
                xong.append((m, co))
                continue
            if args.chi_liet_ke or args.danh_sach_link:
                trinh_duyet.append((loai, m))
                continue
            if m.get("truc_tiep"):
                thu_muc = os.path.join(ROOT, "nhac-nen" if loai == "nhac" else "hieu-ung", m["nhom"])
                os.makedirs(thu_muc, exist_ok=True)
                dst = os.path.join(thu_muc, m["id"] + ".mp3")
                print(f"  → tải thẳng {m['id']} …", end=" ", flush=True)
                if tai_thang(m["truc_tiep"], dst):
                    print("✓")
                    xong.append((m, dst))
                else:
                    print("không được (mạng chặn?) → tải bằng trình duyệt")
                    trinh_duyet.append((loai, m))
            else:
                trinh_duyet.append((loai, m))

    if xong:
        print(f"\nĐÃ CÓ TRÊN MÁY ({len(xong)}):")
        for m, p in xong:
            print(f"  ✓ {os.path.relpath(p, ROOT)}")
    if trinh_duyet:
        print(f"\nCẦN TẢI BẰNG TRÌNH DUYỆT ({len(trinh_duyet)}) - mở trang, bấm 'Free download' (Pixabay) hoặc nút tải MP3 (incompetech), chờ 6-8 giây mỗi file:")
        for loai, m in trinh_duyet:
            ten = m.get("ten_goc", m["id"])
            print(f"  [{'nhạc' if loai == 'nhac' else 'SFX'} · {m['nhom']}] {ten} - {m.get('tac_gia', '')}")
            print(f"      {m['trang']}")
            print(f"      → đặt tên: {m['id']}.mp3")
        print("\nSau khi file về ~/Downloads:  python3 tools/nhap-am-thanh.py --tu ~/Downloads")
        print("(script tự nhận diện theo id Pixabay trong tên file tải về, đổi tên và xếp vào đúng nhóm)")
    if not trinh_duyet and not args.chi_liet_ke:
        print("\n✓ Đủ chất liệu cho mẫu này. Chạy tiếp: python3 tools/nhap-am-thanh.py  (đo LUFS, ghi danh mục)")
    # mã thoát 3 = còn việc cần trình duyệt/người dùng
    sys.exit(3 if trinh_duyet and not (args.chi_liet_ke or args.danh_sach_link) else 0)


if __name__ == "__main__":
    main()
