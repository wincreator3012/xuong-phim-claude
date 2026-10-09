#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LẬP BẢN ĐỒ TỆP của bản thiết kế (chỉ dùng ở repo công khai, không chép sang xưởng của người dùng).

Repo này là BẢN THIẾT KẾ: AI của người dùng đọc nó trên GitHub rồi dựng một xưởng riêng trên máy họ
(xem DUNG-XUONG.md), không clone, không tải ZIP. BAN-DO-TEP.json cho AI đó biết từng tệp: đường dẫn,
cỡ, mã git (sha1 của blob, để tự kiểm tệp lấy về có nguyên vẹn không), tệp nhị phân hay chữ, tệp có
quyền chạy không, và VAI của tệp:
  chep      năng lực của xưởng: chép nguyên văn vào xưởng mới, rồi tools/cai-dat.py --dung-xuong cá nhân hoá
  ban-mau   chỉ để giới thiệu và bảo trì bản thiết kế (README, DUNG-XUONG, THAY-DOI, bản đồ này...): không chép

    python3 tools/lap-ban-do-tep.py          # ghi lại BAN-DO-TEP.json theo các tệp hiện có (git ls-files)
    python3 tools/lap-ban-do-tep.py --kiem   # thoát 1 nếu bản đồ cũ hơn tệp thật (chạy trước khi commit)
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(TOOLS)
BAN_DO = os.path.join(GOC, "BAN-DO-TEP.json")
REPO = "wincreator3012/xuong-phim-claude"
BAN_MAU = {"README.md", "BAT-DAU.md", "DUNG-XUONG.md", "THAY-DOI.md", "BAN-DO-TEP.json", ".gitattributes",
           "tools/lap-ban-do-tep.py", ".dong-bo.json"}
DUOI_NHI_PHAN = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".pdf", ".woff", ".woff2", ".ttf", ".otf",
                 ".onnx", ".mp3", ".wav", ".m4a", ".mp4", ".zip")


def cac_tep():
    out = subprocess.run(["git", "ls-files", "-s", "--cached", "--others", "--exclude-standard"], cwd=GOC,
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("! Cần git để lập bản đồ (chạy trong thư mục repo).")
    tep = {}
    for dong in out.stdout.splitlines():
        if "\t" in dong:  # tệp đã theo dõi: "<mode> <sha> <stage>\t<path>"
            dau, p = dong.split("\t", 1)
            tep[p] = dau.split()[0] == "100755"
        else:  # tệp mới chưa add
            tep[dong] = os.access(os.path.join(GOC, dong), os.X_OK)
    return {p: x for p, x in tep.items() if os.path.isfile(os.path.join(GOC, p))}


def sha_git(p):
    with open(p, "rb") as f:
        b = f.read()
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest(), len(b), b


def lap():
    ds = []
    for p, chay in sorted(cac_tep().items()):
        if p == "BAN-DO-TEP.json":
            continue
        sha, co, b = sha_git(os.path.join(GOC, p))
        muc = {"p": p, "c": co, "sha": sha, "vai": "ban-mau" if p in BAN_MAU else "chep"}
        if p.lower().endswith(DUOI_NHI_PHAN) or b"\0" in b[:4096]:
            muc["nhi_phan"] = True
        if chay:
            muc["chay"] = True
        ds.append(muc)
    return {
        "_huong-dan": "Bản đồ tệp của bản thiết kế xưởng phim. AI dựng xưởng: đọc DUNG-XUONG.md; lấy từng tệp vai 'chep' "
                      "theo mẫu địa chỉ 'raw' (thay {ref} bằng mã commit đang dùng hoặc 'main', {p} bằng đường dẫn đã mã hoá URL), "
                      "kiểm 'sha' (sha1 của 'blob <cỡ>\\0' + nội dung, giống git hash-object), tệp 'chay' thì cấp quyền chạy. "
                      "Tệp vai 'ban-mau' không chép. Bản đồ này không tự liệt kê mình.",
        "repo": f"https://github.com/{REPO}",
        "raw": f"https://raw.githubusercontent.com/{REPO}/{{ref}}/{{p}}",
        "so_tep": len(ds),
        "so_tep_chep": sum(1 for m in ds if m["vai"] == "chep"),
        "tep": ds,
    }


def main():
    ap = argparse.ArgumentParser(description="Lập bản đồ tệp cho AI dựng xưởng từ bản thiết kế")
    ap.add_argument("--kiem", action="store_true")
    a = ap.parse_args()
    moi = lap()
    if a.kiem:
        if not os.path.isfile(BAN_DO):
            print("BẢN ĐỒ TỆP: KHÔNG ĐẠT (chưa có BAN-DO-TEP.json)")
            return 1
        cu = json.load(open(BAN_DO, encoding="utf-8"))
        a_cu = {m["p"]: m for m in cu.get("tep", [])}
        a_moi = {m["p"]: m for m in moi["tep"]}
        khac = sorted(p for p in set(a_cu) | set(a_moi) if a_cu.get(p) != a_moi.get(p))
        if khac:
            print(f"BẢN ĐỒ TỆP: KHÔNG ĐẠT ({len(khac)} tệp lệch, vd {', '.join(khac[:5])}); chạy python3 tools/lap-ban-do-tep.py")
            return 1
        print(f"BẢN ĐỒ TỆP: ĐẠT ({len(a_moi)} tệp)")
        return 0
    with open(BAN_DO, "w", encoding="utf-8") as f:
        json.dump(moi, f, ensure_ascii=False, indent=0)
        f.write("\n")
    print(f"✓ BAN-DO-TEP.json: {moi['so_tep']} tệp, {moi['so_tep_chep']} tệp năng lực để chép")
    return 0


if __name__ == "__main__":
    sys.exit(main())
