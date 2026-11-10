#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CẤU HÌNH ĐƯỜNG DẪN của xưởng: repo chỉ chứa NĂNG LỰC; hồ sơ dự án, thành phẩm, việc tạm nằm NGOÀI repo, cạnh nó.

    <thư mục mẹ>/
      <repo xưởng>/     công cụ, studio, skill, tài liệu, thương hiệu, nhạc
      Du an/            hồ sơ dự án: <YYYY-MM tên>/ (nguon/, transcript/, timeline, clip-ngan/, do-hoa/, xuat-nhap/ ...)
      Du an/_tam/       việc tạm của công cụ và Claude (dự án thử, hàng đợi gỡ băng, bản vá đồng bộ); xoá lúc nào cũng được
      Thanh pham/       <YYYY-MM tên dự án>/00 Video day du/, Short NN <slug>/ (mỗi thư mục tự đủ)
      (thư mục giao)    nơi giao trọn gói thành phẩm sau khi anh duyệt (thuMucGiao, vd thư mục đồng bộ Google Drive); không bắt buộc

Đường dẫn đọc từ cau-hinh.json ở gốc repo (chép từ cau-hinh.mau.json, không lên git), tương đối tính từ gốc repo.
Thiếu cau-hinh.json thì dùng mặc định bên dưới. Máy còn kiểu cũ (du-an/ trong repo, chưa có "../Du an") thì dùng du-an/.

    import cau_hinh as CH
    CH.du_an()            # thư mục hồ sơ dự án (tuyệt đối)
    CH.thanh_pham()       # thư mục thành phẩm
    CH.giao()             # thư mục giao thành phẩm (None nếu chưa cấu hình thuMucGiao)
    CH.tam("go-bang")     # thư mục tạm (tạo nếu chưa có)
    CH.trong_repo(p)      # p có nằm trong repo không
    CH.cho_phep(p)        # p nằm trong repo, Du an hoặc Thanh pham
    CH.ban_nhap()         # kiểu bản nháp: "ban-giao" (cùng thông số bản giao) hoặc "480p"
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


def giao():
    """Thư mục giao thành phẩm. `thuMucGiao` là một đường dẫn hoặc DANH SÁCH đường dẫn (lấy cái đầu tiên tồn tại,
    để cùng một cau-hinh.json chạy được cả trong VM Cowork lẫn trên Mac thật). Biến môi trường LDN_GIAO ghi đè khi chạy thử."""
    e = (os.environ.get("LDN_GIAO") or "").strip()
    if e:
        return _tuyet_doi(e)
    v = doc().get("thuMucGiao") or ""
    ds = [v] if isinstance(v, str) else list(v)
    ps = [_tuyet_doi(c.strip()) for c in ds if isinstance(c, str) and c.strip()]
    if not ps:
        return None
    for p in ps:
        if os.path.isdir(p):
            return p
    return ps[0]


# Kiểu bản nháp (khoá "banNhap" trong cau-hinh.json), quyết định cách assemble.py --preview dựng nháp:
#   "ban-giao": nháp đúng thông số bản giao (1920x1080 hoặc 1080x1920, CRF 18). Bản nháp được duyệt chốt
#               thành bản chính bằng `assemble.py --chot <tên nháp>`, không render lại. Hợp máy mạnh.
#   "480p":     nháp 854x480 encode nhanh để duyệt nhịp và nội dung; bản chính render lại 1080p.
#               Hợp máy yếu, máy ảo giới hạn thời gian mỗi lệnh, phim rất dài.
KIEU_NHAP = ("ban-giao", "480p")
BAN_NHAP_MAC_DINH = ""  # bản thiết kế không chọn thay người dùng: hỏi lúc thiết lập rồi ghi banNhap
_DA_BAO = []


def ban_nhap(bao=True):
    """Kiểu bản nháp đang dùng. Chưa chọn thì tạm dùng "480p" (an toàn cho mọi máy) và nhắc hỏi người dùng."""
    v = str(doc().get("banNhap") or BAN_NHAP_MAC_DINH or "").strip().lower()
    v = {"1080": "ban-giao", "1080p": "ban-giao", "giao": "ban-giao", "ban-chinh": "ban-giao", "480": "480p"}.get(v, v)
    if v in KIEU_NHAP:
        return v
    if bao and not _DA_BAO:
        _DA_BAO.append(1)
        print("  (Chưa chọn kiểu bản nháp: khoá banNhap trong cau-hinh.json còn trống, tạm dựng nháp 480p. "
              "Hỏi người dùng rồi ghi \"ban-giao\" (nháp cùng thông số bản giao, chốt không render lại; máy mạnh) "
              "hoặc \"480p\" (nháp nhẹ, bản chính render lại; máy yếu).)", flush=True)
    return "480p"


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
    print("Giao       :", giao() or "(chưa cấu hình thuMucGiao)")
    print("Tạm        :", tam(tao=False))
    print("Bản nháp   :", ban_nhap(bao=False), "(banNhap)" if doc().get("banNhap") else "(mặc định)")
