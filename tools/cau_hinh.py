#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CẤU HÌNH ĐƯỜNG DẪN của xưởng: repo chỉ chứa NĂNG LỰC; hồ sơ dự án, thành phẩm, việc tạm nằm NGOÀI repo, cạnh nó.

    <thư mục mẹ>/
      <repo xưởng>/     công cụ, studio, skill, tài liệu, thương hiệu, nhạc
      Du an/            hồ sơ dự án: <YYYY-MM tên>/ (nguon/, transcript/, timeline, clip-ngan/, do-hoa/, xuat-nhap/ ...)
      Du an/_tam/       việc tạm của công cụ và Claude (dự án thử, hàng đợi gỡ băng, bản vá đồng bộ); xoá lúc nào cũng được
      Thanh pham/       <YYYY-MM tên dự án>/00 Video day du/, Short NN <slug>/ (mỗi thư mục tự đủ)

Đường dẫn đọc từ cau-hinh.json ở gốc repo (chép từ cau-hinh.mau.json, không lên git), tương đối tính từ gốc repo.
Thiếu cau-hinh.json thì dùng mặc định bên dưới. Máy còn kiểu cũ (du-an/ trong repo, chưa có "../Du an") thì dùng du-an/.

    import cau_hinh as CH
    CH.du_an()            # thư mục hồ sơ dự án (tuyệt đối)
    CH.thanh_pham()       # thư mục thành phẩm
    CH.tam("go-bang")     # thư mục tạm (tạo nếu chưa có)
    CH.trong_repo(p)      # p có nằm trong repo không
    CH.cho_phep(p)        # p nằm trong repo, Du an hoặc Thanh pham
"""
import json
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(TOOLS)
MAC_DINH = {"thuMucDuAn": "../Du an", "thuMucThanhPham": "../Thanh pham", "thuMucTam": "../Du an/_tam"}


def doc():
    cfg = dict(MAC_DINH)
    p = os.path.join(GOC, "cau-hinh.json")
    if os.path.isfile(p):
        try:
            cfg.update({k: v for k, v in json.load(open(p, encoding="utf-8")).items() if not k.startswith("_")})
        except ValueError:
            pass
    return cfg


def _tuyet_doi(v):
    v = os.path.expanduser(v)
    return os.path.normpath(v if os.path.isabs(v) else os.path.join(GOC, v))


def du_an():
    d = _tuyet_doi(doc()["thuMucDuAn"])
    cu = os.path.join(GOC, "du-an")
    if not os.path.isdir(d) and os.path.isdir(cu):  # máy chưa chuyển sang kiểu mới
        return cu
    return d


def thanh_pham():
    return _tuyet_doi(doc()["thuMucThanhPham"])


def tam(*con, tao=True):
    d = _tuyet_doi(doc()["thuMucTam"])
    if not os.path.isdir(os.path.dirname(d)) and os.path.isdir(os.path.join(GOC, "du-an")):
        d = os.path.join(GOC, "du-an", "_tam")  # kiểu cũ
    d = os.path.join(d, *con)
    if tao:
        os.makedirs(d, exist_ok=True)
    return d


def trong(goc, path):
    goc = os.path.realpath(goc)
    p = os.path.realpath(path)
    return p == goc or p.startswith(goc + os.sep)


def trong_repo(path):
    return trong(GOC, path)


def cho_phep(path):
    return trong_repo(path) or trong(du_an(), path) or trong(thanh_pham(), path)


if __name__ == "__main__":
    print("Repo xưởng :", GOC)
    print("Du an      :", du_an())
    print("Thanh pham :", thanh_pham())
    print("Tạm        :", tam(tao=False))
