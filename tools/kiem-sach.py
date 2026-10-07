#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIỂM SẠCH: repo xưởng phim chỉ chứa NĂNG LỰC (công cụ, studio, skill, tài liệu, thương hiệu, nhạc, hiệu ứng).
Hồ sơ dự án, thành phẩm, việc tạm luôn nằm NGOÀI repo (tools/cau_hinh.py: "../Du an", "../Thanh pham", "../Du an/_tam").
Chạy ở đầu và cuối mỗi phiên làm việc; cuối phiên phải ĐẠT mới được báo "xong". (Chuyển từ xưởng thiết kế.)

    python3 tools/kiem-sach.py          # kiểm, liệt kê; thoát 1 nếu còn nháp lạc hoặc file lạ
    python3 tools/kiem-sach.py --xoa    # xoá phần NHÁP LẠC (chỉ chạy khi anh đã cho phép xoá); file LẠ không bao giờ tự xoá

Hai nhóm kết quả:
  DỰ ÁN KIỂU CŨ  thư mục du-an/ trong repo (bản cũ để dự án trong repo): KHÔNG BAO GIỜ tự xoá; dời từng dự án sang
            thư mục Du an cạnh repo (mv, giữ nguyên bên trong), rồi xoá du-an/ rỗng.
  NHÁP LẠC  chắc chắn là rác của phiên: .tam, .tmp_check, tmp-*, Claude outputs, _to_delete,
            xuat-nhap, xuat-hoan-chinh, proxy, __pycache__; bản sao lưu *.truoc-*, file nén, .pyc, .DS_Store, log, bản vá.
  LẠ        ảnh, PDF, video nằm ngoài các thư mục tài nguyên, hoặc file lớn bất thường: hỏi anh là tài nguyên mới hay nháp.
Thư mục cài đặt (tools/models, tools/pylib, studio/node_modules, studio/public/brand) được bỏ qua.
Ngoài ra báo nếu cau-hinh.json trỏ thư mục dự án, thành phẩm, tạm vào trong repo.
"""
import argparse
import fnmatch
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True  # không để __pycache__ trong repo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cau_hinh as CH  # noqa: E402

GOC = CH.GOC
DU_AN_CU = []
THU_MUC_NHAP = ['.tam', '.tmp_check', 'tmp-*', 'Claude outputs', '_to_delete', '_tam', 'xuat-nhap',
                'xuat-hoan-chinh', 'proxy', 'go-bang', '__pycache__', '.pytest_cache', '.ipynb_checkpoints']
TEN_NHAP = ['*.truoc-*', '*.tgz', '*.tar', '*.tar.gz', '*.zip', '*.pyc', '*.bak', '*.orig', '*.rej', '*.tmp', '*.swp',
            '*~', '.DS_Store', '*.log', '*.patch', 'git-index.lock*']
BO_QUA = {'.git', os.path.join('tools', 'models'), os.path.join('tools', 'pylib'),
          os.path.join('studio', 'node_modules'), os.path.join('studio', 'public', 'brand')}
THU_MUC_TAI_NGUYEN = ('brand', 'nhac-nen', 'hieu-ung', 'do-hoa-chung', 'phong-cach', 'docs', 'skills-nguon',
                      os.path.join('studio', 'public'), os.path.join('studio', 'src'),
                      os.path.join('tools', 'mau-du-an'), os.path.join('tools', 'ban-dung'))
DUOI_MEDIA = {'.png', '.jpg', '.jpeg', '.webp', '.heic', '.gif', '.pdf', '.psd', '.mp4', '.mov', '.webm', '.mp3',
              '.wav', '.m4a', '.aac', '.mkv'}
NGUONG_LON = 5 * 1024 * 1024


def kich_thuoc(p):
    if os.path.isfile(p):
        return os.path.getsize(p)
    tong = 0
    for dp, _, fn in os.walk(p):
        for f in fn:
            try:
                tong += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    return tong


def dep(n):
    for d in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or d == 'GB':
            return f'{n:.0f} {d}' if d == 'B' else f'{n:.1f} {d}'
        n /= 1024


def trong_tai_nguyen(rel):
    return any(rel == t or rel.startswith(t + os.sep) for t in THU_MUC_TAI_NGUYEN)


def quet():
    nhap, la = [], []
    global DU_AN_CU
    DU_AN_CU = [d for d in ('du-an',) if os.path.isdir(os.path.join(GOC, d))]
    for dp, dn, fn in os.walk(GOC):
        rel_dir = os.path.relpath(dp, GOC)
        giu = []
        for d in sorted(dn):
            rel = os.path.normpath(os.path.join(rel_dir, d))
            if rel in BO_QUA or rel in DU_AN_CU:
                continue
            if any(fnmatch.fnmatch(d, g) for g in THU_MUC_NHAP):
                nhap.append((rel, 'thư mục nháp, tạm, dự án lạc'))
                continue
            giu.append(d)
        dn[:] = giu
        for f in sorted(fn):
            rel = os.path.normpath(os.path.join(rel_dir, f))
            if any(fnmatch.fnmatch(f, g) for g in TEN_NHAP):
                nhap.append((rel, 'file nháp, sao lưu, nén, rác hệ thống'))
                continue
            if trong_tai_nguyen(rel):
                continue
            p = os.path.join(dp, f)
            if os.path.splitext(f)[1].lower() in DUOI_MEDIA:
                la.append((rel, 'ảnh, PDF, video, âm thanh ngoài thư mục tài nguyên'))
            elif kich_thuoc(p) > NGUONG_LON:
                la.append((rel, f'file lớn bất thường ({dep(kich_thuoc(p))})'))
    return nhap, la


def cau_hinh_trong_repo():
    loi = []
    for ten, d in (('thuMucDuAn', CH.du_an()), ('thuMucThanhPham', CH.thanh_pham()), ('thuMucTam', CH.tam(tao=False))):
        if CH.trong_repo(d):
            loi.append(f'cau-hinh.json > {ten} trỏ vào trong repo ({d}): đổi ra ngoài repo (ví dụ "../Du an")')
    return loi


def chua_vao_git():
    if not os.path.isdir(os.path.join(GOC, '.git')):
        return []
    try:
        r = subprocess.run(['git', '-C', GOC, 'status', '--porcelain'], capture_output=True, text=True, timeout=60)
    except Exception:
        return []
    return [ln[3:].strip().strip('"') for ln in r.stdout.splitlines() if ln.startswith('??')]


def xoa(muc):
    for rel, _ in muc:
        p = os.path.join(GOC, rel)
        try:
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
            print(f'  đã xoá: {rel}')
        except OSError as e:
            print(f'  KHÔNG xoá được {rel}: {e.strerror} (cần anh cho phép xoá trong thư mục này)')


def in_ds(tieu_de, ds):
    print(f'\n{tieu_de} ({len(ds)})')
    for rel, vi_sao in ds:
        print(f'  {rel}  [{dep(kich_thuoc(os.path.join(GOC, rel)))}]  {vi_sao}')


def main():
    ap = argparse.ArgumentParser(description='Kiểm repo xưởng phim sạch: chỉ chứa năng lực.')
    ap.add_argument('--xoa', action='store_true', help='xoá phần NHÁP LẠC (anh đã cho phép xoá)')
    a = ap.parse_args()
    nhap, la = quet()
    if a.xoa and nhap:
        print('Xoá nháp lạc trong repo:')
        xoa(nhap)
        nhap, la = quet()
    cfg = cau_hinh_trong_repo()
    for d in DU_AN_CU:
        con = sorted(x for x in os.listdir(os.path.join(GOC, d)) if not x.startswith('.'))
        print(f'\nDỰ ÁN KIỂU CŨ trong repo: {d}/ ({len(con)} mục, {dep(kich_thuoc(os.path.join(GOC, d)))}). KHÔNG xoá.')
        print(f'  Dời từng dự án sang {CH.du_an() if not CH.trong_repo(CH.du_an()) else "../Du an"} (mv, giữ nguyên bên trong), rồi bỏ {d}/ rỗng:')
        for x in con[:12]:
            print(f'    {x}')
    if nhap:
        in_ds('NHÁP LẠC trong repo, cần xoá', nhap)
    if la:
        in_ds('FILE LẠ, hỏi anh là tài nguyên mới hay nháp', la)
    for c in cfg:
        print(f'\nCẤU HÌNH: {c}')
    ngoai_git = [p for p in chua_vao_git() if not any(p.rstrip('/') == r or p.startswith(r + '/') for r, _ in nhap + la)]
    if ngoai_git:
        print(f'\nChưa vào git (thông tin): {len(ngoai_git)} mục')
        for p in ngoai_git[:12]:
            print(f'  {p}')
    sach = not (nhap or la or cfg or DU_AN_CU)
    print('\nREPO SẠCH: ĐẠT' if sach else f'\nREPO CHƯA SẠCH: {len(nhap)} nháp lạc, {len(la)} file lạ' + (', còn du-an/ kiểu cũ' if DU_AN_CU else '')
          + (', cấu hình sai' if cfg else '')
          + ('. Xin phép anh xoá rồi chạy lại với --xoa.' if nhap else '.'))
    sys.exit(0 if sach else 1)


if __name__ == '__main__':
    main()
