#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DỰ ÁN MỚI: tạo hồ sơ một dự án phim NGOÀI repo (repo chỉ chứa năng lực).

    python3 tools/du-an-moi.py "Bai giang thang 11" [--loai bai-giang|infomotion|tai-lieu-phong-van] [--thang 2026-11]

Tạo <thư mục Du an>/<YYYY-MM tên>/ (cau-hinh.json > thuMucDuAn, mặc định "../Du an") từ khuôn tools/mau-du-an/:
    project.json         tên, mô tả, tông sáng tối, đầu ra (Claude điền cùng anh)
    timeline.json        timeline mẫu (cắt, intro, outro, overlay, insert)
    do-hoa/job-do-hoa.json   job đồ họa mẫu, brandFile "@xuong/brand/brand.json" (gốc xưởng)
    nguon/  transcript/  GHI-CHU.md (theo loại dự án, nếu có)
In ra đường dẫn dự án dạng tương đối từ gốc xưởng để dùng trong lệnh: "../Du an/<YYYY-MM tên>".
Thành phẩm sau khi anh duyệt vào <Thanh pham>/<YYYY-MM tên dự án>/ (CLAUDE.md quy tắc 11).
"""
import argparse
import datetime
import os
import re
import shutil
import sys
import unicodedata

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cau_hinh as CH  # noqa: E402

MAU = os.path.join(CH.TOOLS, "mau-du-an")


def ten_an_toan(s):
    s = unicodedata.normalize("NFD", s).replace("đ", "d").replace("Đ", "D")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^A-Za-z0-9 ._-]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser(description="Tạo hồ sơ dự án phim ngoài repo")
    ap.add_argument("ten", help="tên dự án (không dấu sẽ an toàn hơn cho dòng lệnh; có dấu được tự bỏ dấu)")
    ap.add_argument("--loai", default="bai-giang", choices=["bai-giang", "infomotion", "tai-lieu-phong-van"])
    ap.add_argument("--thang", help="YYYY-MM đặt trước tên (mặc định tháng hiện tại)")
    a = ap.parse_args()

    thang = a.thang or datetime.date.today().strftime("%Y-%m")
    ten = ten_an_toan(a.ten)
    if not re.match(r"^\d{4}-\d{2} ", ten):
        ten = f"{thang} {ten}"
    goc = CH.du_an()
    if CH.trong_repo(goc):
        sys.exit("DỪNG: thư mục Du an đang trỏ vào trong repo; sửa cau-hinh.json > thuMucDuAn ra ngoài repo")
    da = os.path.join(goc, ten)
    if os.path.exists(da):
        sys.exit(f"DỪNG: đã có dự án {da}")
    os.makedirs(da)
    for f in ("project.json", "timeline.json"):
        shutil.copy2(os.path.join(MAU, f), os.path.join(da, f))
    os.makedirs(os.path.join(da, "do-hoa"))
    s = open(os.path.join(MAU, "do-hoa", "job-do-hoa.json"), encoding="utf-8").read()
    open(os.path.join(da, "do-hoa", "job-do-hoa.json"), "w", encoding="utf-8").write(s)
    for d in ("nguon", "transcript"):
        os.makedirs(os.path.join(da, d))
    ghi_chu = os.path.join(MAU, a.loai, "GHI-CHU.md")
    if os.path.isfile(ghi_chu):
        shutil.copy2(ghi_chu, os.path.join(da, "GHI-CHU.md"))
    print("✓ Đã tạo hồ sơ dự án:", da)
    print("  Dùng trong lệnh (từ gốc xưởng):", f'"{os.path.relpath(da, CH.GOC)}"')
    print("  Thả tư liệu vào:", os.path.join(da, "nguon"))


if __name__ == "__main__":
    main()
