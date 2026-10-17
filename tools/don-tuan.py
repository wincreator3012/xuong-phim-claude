#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DỌN XƯỞNG ĐỊNH KỲ TUẦN: chuyển thành phẩm đã duyệt sang ổ lưu trữ, dọn rác và nháp, giữ ổ Mac nhẹ.

Người dùng chốt 2026-10-13: mỗi tuần rà toàn xưởng; thành phẩm đã duyệt dời từ `Thanh pham/` sang thư mục lưu trữ
trên ổ lưu trữ (`thuMucLuuTru` trong cau-hinh.json),
giữ nguyên cấu trúc `<YYYY-MM tên dự án>/00 Video day du/`, `Short NN <slug>/`.

    python3 tools/don-tuan.py                          # XEM: báo cáo toàn cảnh, không đổi gì
    python3 tools/don-tuan.py chuyen [--du-an X] [--ngan-sach 150]
                                                       # chép thành phẩm đã duyệt sang lưu trữ (chạy lặp tới khi XONG),
                                                       # rồi đối chiếu cỡ từng tệp và mã băm mẫu của video, ghi sổ
    python3 tools/don-tuan.py xoa-thanh-pham [--ghi]   # xoá bản trên Mac của dự án ĐÃ ĐỐI CHIẾU KHỚP (đối chiếu lại trước khi xoá)
    python3 tools/don-tuan.py don [--ghi] [--nhom R,N] # dọn rác (R) và nháp của dự án đã duyệt (N)

Chỉ chạy `--ghi` của hai lệnh xoá khi anh đã cho phép xoá (device_request_delete_permission). Không bao giờ xoá nguồn
quay thô, timeline, gỡ băng, đồ hoạ, nhạc, cảnh, transcript, dang-tai, NGUON-O-DAU.md.

Dấu duyệt của một dự án: `Du an/<cùng tên>/NGUON-O-DAU.md` (ghi ở bước 5 khi anh nói "duyệt"). Thành phẩm chưa có dấu này
không tự chuyển; đã chắc anh duyệt thì nêu tên bằng `--du-an "<tên>"` (lặp được).

Ba nhóm khi dọn:
  R  rác chắc chắn, dọn lúc nào cũng được: .DS_Store, __pycache__, *.pyc ở mọi nơi; mọi thứ trong `Du an/_tam/`
     (trừ liên kết dung-dai-tam đang dùng); ở gốc xưởng: `Claude outputs`, `_to_delete*`, log chẩn đoán *.txt/*.log.
  N  nháp của dự án ĐÃ DUYỆT: `.tam`, `_tam-kiem`, `.manh*`, `_frames`, `proxy`, `*.truoc-*`, `*.bak-*`; video trong
     `xuat-nhap/`, `xuat-hoan-chinh/` trùng cỡ và mã băm mẫu với một video ở Thành phẩm hoặc lưu trữ; bản cũ đã có
     bản mới hơn cùng gốc tên trong cùng thư mục (`x-nhap1.mp4`, `x.v2.mp4` khi đã có `x.mp4` mới hơn).
  H  cần anh quyết: mọi nháp của dự án chưa có dấu duyệt; video trong `xuat-nhap/`, `xuat-hoan-chinh/` không trùng đâu
     và không có bản mới hơn (có thể là bản dựng duy nhất, như hoạt hình một dự án bài giảng). Không bao giờ tự xoá.
"""
import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cau_hinh as CH  # noqa: E402

XUONG = os.path.dirname(CH.GOC)          # thư mục mẹ "Xuong phim AI"
DU_AN = CH.du_an()
TP = CH.thanh_pham()
DUOI_VIDEO = {'.mp4', '.mov', '.mkv', '.webm', '.m4v'}
SO = 'SO-LUU-TRU.json'
MUC_LUC = 'MUC-LUC-LUU-TRU.md'

RAC_TEN = ['.DS_Store', '*.pyc']
RAC_THU_MUC = ['__pycache__']
RAC_GOC = ['Claude outputs', '_to_delete*', 'bird-*.txt', '*.log']
NHAP_THU_MUC = ['.tam', '_tam-kiem', '.manh*', '_frames', 'proxy', '_to_delete*', '_khuc']
ANH_THU_DUOI = {'.jpg', '.jpeg', '.png', '.log'}   # ảnh lưới soát, ảnh thử, log chạy trong xuat-nhap / xuat-hoan-chinh
LUU_TRU_GHI_DE = None        # --luu-tru: ghi đè thuMucLuuTru (tools/duyet.py dùng chung thư mục giao)
DUYET_GIA_DINH = set()       # --du-an: các dự án anh đã nói "duyệt" (coi như đã có dấu duyệt)
NHAP_TEN = ['*.truoc-*', '*.bak-*', '*.bak']


def luu_tru():
    if LUU_TRU_GHI_DE:
        return LUU_TRU_GHI_DE if os.path.isdir(LUU_TRU_GHI_DE) else None
    v = CH.doc().get('thuMucLuuTru') or []
    for c in ([v] if isinstance(v, str) else v):
        p = CH._tuyet_doi(c)
        if os.path.isdir(p):
            return p
    return None


def co(p):
    if os.path.islink(p):
        return 0
    if os.path.isfile(p):
        return os.path.getsize(p)
    t = 0
    for dp, dn, fn in os.walk(p):
        for f in fn:
            q = os.path.join(dp, f)
            if not os.path.islink(q):
                try:
                    t += os.path.getsize(q)
                except OSError:
                    pass
    return t


def dep(n):
    for d in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or d == 'GB':
            return f'{n:.1f} {d}' if d != 'B' else f'{n} B'
        n /= 1024


def khop(ten, mau):
    return any(fnmatch.fnmatch(ten, m) for m in mau)


def bam_mau(p, khuc=4 << 20):
    """Mã băm mẫu: đầu, giữa, cuối mỗi chỗ 4 MB cộng cỡ tệp (cách Đợt 4 dùng để đối chiếu nguồn)."""
    n = os.path.getsize(p)
    h = hashlib.sha1(str(n).encode())
    with open(p, 'rb') as f:
        for vt in sorted({0, max(0, n // 2 - khuc // 2), max(0, n - khuc)}):
            f.seek(vt)
            h.update(f.read(khuc))
    return h.hexdigest()


def da_duyet(ten):
    return ten in DUYET_GIA_DINH or os.path.isfile(os.path.join(DU_AN, ten, 'NGUON-O-DAU.md'))


def du_an_tp():
    if not os.path.isdir(TP):
        return []
    return sorted(d for d in os.listdir(TP) if os.path.isdir(os.path.join(TP, d)) and not d.startswith('.'))


def tep_tuong_doi(goc):
    kq = {}
    for dp, dn, fn in os.walk(goc):
        dn[:] = [d for d in dn if d not in RAC_THU_MUC]
        for f in fn:
            if khop(f, RAC_TEN):
                continue
            q = os.path.join(dp, f)
            if os.path.islink(q):
                continue
            # khoá chuẩn NFC: ổ exFAT trả tên dạng NFD, Mac giữ NFC; cùng một tên tiếng Việt phải khớp nhau
            kq[unicodedata.normalize('NFC', os.path.relpath(q, goc))] = (os.path.getsize(q), q)
    return kq


def doc_so(lt):
    p = os.path.join(lt, SO)
    for lan in range(5):     # cầu nối tới ổ exFAT có lúc chưa thấy tệp vừa đổi tên
        try:
            return json.load(open(p, encoding='utf-8'))
        except ValueError:
            break
        except OSError:
            time.sleep(0.6 * (lan + 1))
    return {'_ghi_chu': 'Sổ lưu trữ thành phẩm do tools/don-tuan.py ghi. Mỗi dự án: ngày chuyển, số tệp, dung lượng, '
                        'đối chiếu, ngày xoá bản trên Mac.', 'du_an': {}}


def ghi_tep(p, nd):
    """Ghi qua tệp tạm rồi đổi tên; thử lại vì ổ exFAT gắn qua cầu nối thỉnh thoảng báo ENOENT nhất thời."""
    for lan in range(5):
        try:
            with open(p + '.moi', 'w', encoding='utf-8') as f:
                f.write(nd)
            os.replace(p + '.moi', p)
            return
        except OSError:
            if lan == 4:
                raise
            time.sleep(0.5 * (lan + 1))


def ghi_so(lt, so):
    ghi_tep(os.path.join(lt, SO), json.dumps(so, ensure_ascii=False, indent=1))
    # mục lục đọc được bằng mắt
    dong = ['# Mục lục thành phẩm lưu trữ', '',
            'Do `tools/don-tuan.py` ghi lại sau mỗi lần chuyển. Mỗi dự án một thư mục, bên trong `00 Video day du/` và '
            '`Short NN <slug>/` tự đủ (video, nghiệm thu, `dang-tai/`, `transcript/`).', '',
            '| Dự án | Số tệp | Dung lượng | Video | Chuyển ngày | Đã xoá trên Mac |', '|---|---|---|---|---|---|']
    for ten in sorted(so['du_an']):
        m = so['du_an'][ten]
        dong.append(f"| {ten} | {m.get('so_tep', '')} | {dep(m.get('byte', 0))} | {m.get('so_video', '')} | "
                    f"{m.get('ngay_chuyen', '')} | {m.get('ngay_xoa_mac', '') or 'chưa'} |")
    ghi_tep(os.path.join(lt, MUC_LUC), '\n'.join(dong) + '\n')


def doi_chieu(nguon, dich):
    """Trả (ok, thông điệp, số tệp, byte, số video)."""
    a, b = tep_tuong_doi(nguon), tep_tuong_doi(dich)
    thieu = [k for k in a if k not in b]
    lech = [k for k in a if k in b and a[k][0] != b[k][0]]
    if thieu or lech:
        return False, f'thiếu {len(thieu)} tệp, lệch cỡ {len(lech)} tệp (vd {(thieu + lech)[:3]})', len(a), 0, 0
    vids = [k for k in a if os.path.splitext(k)[1].lower() in DUOI_VIDEO]
    for k in vids:
        if bam_mau(a[k][1]) != bam_mau(b[k][1]):
            return False, f'mã băm mẫu khác: {k}', len(a), 0, 0
    return True, 'khớp cỡ mọi tệp và mã băm mẫu mọi video', len(a), sum(v[0] for v in a.values()), len(vids)


# ---------------------------------------------------------------- XEM

def quet_rac():
    """Trả danh sách (nhóm, đường dẫn, cỡ, lý do)."""
    kq = []
    # gốc xưởng
    for ten in sorted(os.listdir(XUONG)):
        p = os.path.join(XUONG, ten)
        if khop(ten, RAC_GOC) or ten == '.DS_Store':
            kq.append(('R', p, co(p), 'rác ở gốc xưởng'))
    # _tam
    tam = CH.tam(tao=False)
    if os.path.isdir(tam):
        for ten in sorted(os.listdir(tam)):
            p = os.path.join(tam, ten)
            kq.append(('R', p, co(p), 'việc tạm (Du an/_tam, xoá lúc nào cũng được)'))
    # rác lặt vặt trong Du an và Thanh pham
    for goc in (DU_AN, TP):
        for dp, dn, fn in os.walk(goc):
            if os.path.realpath(dp).startswith(os.path.realpath(tam)):
                dn[:] = []
                continue
            for d in list(dn):
                if d in RAC_THU_MUC:
                    p = os.path.join(dp, d)
                    kq.append(('R', p, co(p), '__pycache__'))
                    dn.remove(d)
            for f in fn:
                if khop(f, RAC_TEN):
                    p = os.path.join(dp, f)
                    kq.append(('R', p, os.path.getsize(p), f))
    return kq


def chi_muc_video_thanh_pham(lt):
    """{cỡ: [đường dẫn]} của video ở Thành phẩm và lưu trữ, để nhận ra bản trùng trong hồ sơ dự án."""
    m = {}
    for goc in [TP] + ([lt] if lt else []):
        for dp, dn, fn in os.walk(goc):
            for f in fn:
                if os.path.splitext(f)[1].lower() in DUOI_VIDEO:
                    q = os.path.join(dp, f)
                    m.setdefault(os.path.getsize(q), []).append(q)
    return m


def goc_ten(f):
    """Tên gốc của một bản dựng, bỏ dấu phiên bản: an-lac-nhap1.mp4, an-lac.v2.mp4, an-lac.mp4 cùng gốc an-lac."""
    b = os.path.splitext(f)[0].lower()
    for _ in range(3):
        b = re.sub(r'([-_.](nhap|draft|test)\d*|[-_.]v\d+|[-_.]lan\d+)$', '', b)
    return b


def ban_moi_hon(p):
    """Video cùng gốc tên, cùng thư mục, mới hơn p (thì p là bản cũ bị thay thế)."""
    d, f = os.path.split(p)
    g, t = goc_ten(f), os.path.getmtime(p)
    for k in os.listdir(d):
        q = os.path.join(d, k)
        if k != f and os.path.splitext(k)[1].lower() in DUOI_VIDEO and goc_ten(k) == g and os.path.getmtime(q) > t:
            return q
    return None


def quet_nhap(lt):
    kq = []
    vmap = chi_muc_video_thanh_pham(lt)
    for ten in sorted(os.listdir(DU_AN)):
        da = os.path.join(DU_AN, ten)
        if ten.startswith(('_', '.')) or not os.path.isdir(da):
            continue
        nhom = 'N' if da_duyet(ten) else 'H'
        for dp, dn, fn in os.walk(da):
            for d in list(dn):
                if khop(d, NHAP_THU_MUC):
                    p = os.path.join(dp, d)
                    kq.append((nhom, p, co(p), f'thư mục nháp {d}'))
                    dn.remove(d)
            dn[:] = [d for d in dn if d not in RAC_THU_MUC]
            for f in fn:
                p = os.path.join(dp, f)
                if os.path.islink(p):
                    continue
                if khop(f, NHAP_TEN):
                    kq.append((nhom, p, os.path.getsize(p), 'bản sao lưu'))
                    continue
                if os.path.splitext(f)[1].lower() in ANH_THU_DUOI and os.path.basename(dp) in ('xuat-nhap', 'xuat-hoan-chinh'):
                    kq.append((nhom, p, os.path.getsize(p), 'ảnh lưới soát, ảnh thử hoặc log chạy'))
                    continue
                if os.path.splitext(f)[1].lower() not in DUOI_VIDEO:
                    continue
                cha = os.path.basename(dp)
                if cha not in ('xuat-nhap', 'xuat-hoan-chinh'):
                    continue
                n = os.path.getsize(p)
                trung = None
                for q in vmap.get(n, []):
                    if bam_mau(q) == bam_mau(p):
                        trung = q
                        break
                if trung:
                    kq.append((nhom, p, n, 'trùng ' + os.path.relpath(trung, XUONG)))
                    continue
                if cha == 'xuat-nhap':      # bản trung gian (chưa burn phụ đề, chưa chuẩn âm lượng): bản hoàn chỉnh cùng tên đã giao
                    anh_em = os.path.join(os.path.dirname(dp), 'xuat-hoan-chinh', f)
                    if os.path.isfile(anh_em) and any(bam_mau(q) == bam_mau(anh_em) for q in vmap.get(os.path.getsize(anh_em), [])):
                        kq.append((nhom, p, n, 'bản trung gian, bản hoàn chỉnh cùng tên đã giao'))
                        continue
                moi_hon = ban_moi_hon(p)
                if moi_hon:
                    kq.append((nhom, p, n, 'bản cũ, đã có bản mới hơn ' + os.path.basename(moi_hon)))
                elif n > 1 << 20:
                    kq.append(('H', p, n, f'video trong {cha} không trùng Thành phẩm: có thể là bản dựng duy nhất'))
    return kq


def xem(a):
    lt = luu_tru()
    print('== DUNG LƯỢNG')
    for ten, p in (('Du an', DU_AN), ('Thanh pham', TP)):
        print(f'  {ten}: {dep(co(p))}')
    du = shutil.disk_usage(XUONG)
    print(f'  ổ Mac còn trống: {dep(du.free)} / {dep(du.total)}')
    print(f'  thư mục lưu trữ: {lt or "CHƯA THẤY (gắn ổ lưu trữ, kiểm thuMucLuuTru trong cau-hinh.json)"}')
    so = doc_so(lt) if lt else {'du_an': {}}

    print('\n== THÀNH PHẨM TRÊN MAC')
    for ten in du_an_tp():
        m = so['du_an'].get(ten, {})
        tt = ('ĐÃ ĐỐI CHIẾU, chờ xoá bản Mac' if m.get('doi_chieu') == 'khop' else
              'đã chép một phần' if m else 'chưa chuyển')
        dau = 'đã duyệt' if da_duyet(ten) else 'CHƯA THẤY DẤU DUYỆT'
        print(f'  {dep(co(os.path.join(TP, ten))):>9}  {ten}  [{dau}; {tt}]')

    rac = quet_rac() + quet_nhap(lt)
    for nhom, tieu in (('R', 'RÁC (dọn lúc nào cũng được)'), ('N', 'NHÁP CỦA DỰ ÁN ĐÃ DUYỆT'),
                       ('H', 'CẦN ANH QUYẾT (không tự xoá)')):
        ds = [r for r in rac if r[0] == nhom]
        print(f'\n== {tieu}: {len(ds)} mục, {dep(sum(r[2] for r in ds))}')
        for _, p, n, ly in sorted(ds, key=lambda r: -r[2])[: (a.toi_da or 10 ** 6)]:
            print(f'  {dep(n):>9}  {os.path.relpath(p, XUONG)}  ({ly})')
    if a.json:
        json.dump([{'nhom': r[0], 'duong': os.path.relpath(r[1], XUONG), 'byte': r[2], 'ly_do': r[3]} for r in rac],
                  open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- CHUYỂN

def chuyen(a):
    lt = luu_tru()
    if not lt:
        sys.exit('Chưa thấy thư mục lưu trữ: gắn ổ lưu trữ vào phiên, kiểm thuMucLuuTru trong cau-hinh.json.')
    if not shutil.which('rsync'):
        sys.exit('Thiếu rsync.')
    so = doc_so(lt)
    bat_dau = time.time()
    chon = du_an_tp()
    if a.du_an:
        chon = [d for d in chon if d in a.du_an]
    for ten in chon:
        if not (da_duyet(ten) or (a.du_an and ten in a.du_an)):
            print(f'BỎ QUA (chưa thấy dấu duyệt): {ten}')
            continue
        m = so['du_an'].get(ten, {})
        if m.get('doi_chieu') == 'khop' and not a.lai:
            continue
        con = a.ngan_sach - (time.time() - bat_dau)
        if con < 15:
            print('HẾT NGÂN SÁCH: chạy lại lệnh để chép tiếp.')
            return
        nguon, dich = os.path.join(TP, ten), os.path.join(lt, ten)
        print(f'CHÉP {ten} ({dep(co(nguon))}) ...', flush=True)
        lenh = ['timeout', str(int(con)), 'rsync', '-rt', '--modify-window=2', '--partial',
                '--exclude=.DS_Store', '--exclude=__pycache__', '--exclude=*.pyc', nguon + '/', dich + '/']
        r = subprocess.run(lenh)
        so['du_an'].setdefault(ten, {})['ngay_chuyen'] = dt.date.today().isoformat()
        if r.returncode != 0:
            ghi_so(lt, so)
            print(f'  dừng giữa chừng (mã {r.returncode}); chạy lại lệnh để chép tiếp.')
            return
        ok, tb, n, b, v = doi_chieu(nguon, dich)
        so['du_an'][ten].update({'so_tep': n, 'byte': b, 'so_video': v, 'doi_chieu': 'khop' if ok else 'lech',
                                 'ghi_chu': tb})
        ghi_so(lt, so)
        print(f'  {"KHỚP" if ok else "LỆCH"}: {tb}')
    print('XONG-CHUYEN')


def ghi_noi_luu(ten, lt):
    """Thêm một dòng vào NGUON-O-DAU.md của hồ sơ dự án: thành phẩm nay ở ổ lưu trữ."""
    p = os.path.join(DU_AN, ten, 'NGUON-O-DAU.md')
    if not os.path.isfile(p):
        return
    noi = f'{os.path.basename(lt)}/{ten}/'
    dong = (f'- {dt.date.today().isoformat()}: thành phẩm dời khỏi `Thanh pham/` sang `{noi}` '
            f'(đối chiếu cỡ và mã băm mẫu khớp; sổ `SO-LUU-TRU.json` ở đó).')
    nd = open(p, encoding='utf-8').read()
    if noi not in nd:
        with open(p, 'a', encoding='utf-8') as f:
            f.write(('' if nd.endswith('\n') else '\n') + dong + '\n')


def xoa_thanh_pham(a):
    lt = luu_tru()
    if not lt:
        sys.exit('Chưa thấy thư mục lưu trữ.')
    so = doc_so(lt)
    tong = 0
    for ten in du_an_tp():
        if a.du_an and ten not in a.du_an:
            continue
        m = so['du_an'].get(ten, {})
        if m.get('doi_chieu') != 'khop':
            continue
        nguon, dich = os.path.join(TP, ten), os.path.join(lt, ten)
        ok, tb, *_ = doi_chieu(nguon, dich)          # đối chiếu lại ngay trước khi xoá
        if not ok:
            print(f'KHÔNG XOÁ {ten}: {tb}')
            continue
        n = co(nguon)
        tong += n
        print(f'{"XOÁ" if a.ghi else "sẽ xoá"} {dep(n):>9}  Thanh pham/{ten}')
        if a.ghi:
            shutil.rmtree(nguon)
            m['ngay_xoa_mac'] = dt.date.today().isoformat()
            ghi_so(lt, so)
            ghi_noi_luu(ten, lt)
    print(f'{"Đã giải phóng" if a.ghi else "Sẽ giải phóng"}: {dep(tong)}')


def don(a):
    lt = luu_tru()
    nhom = set((a.nhom or 'R,N').split(','))
    nhom.discard('H')
    tam_link = os.path.realpath(os.path.expanduser('~/.dung-dai-tam'))
    ds = [r for r in quet_rac() + quet_nhap(lt) if r[0] in nhom]
    tong = 0
    for _, p, n, ly in sorted(ds, key=lambda r: r[1]):
        if not os.path.lexists(p):
            continue
        if os.path.realpath(p) == tam_link:     # thư mục tạm của dung-dai.py: giữ thư mục, dọn bên trong
            tong += n
            print(f'{"DỌN TRONG" if a.ghi else "sẽ dọn trong"} {dep(n):>9}  {os.path.relpath(p, XUONG)}  ({ly})')
            if a.ghi:
                for k in os.listdir(p):
                    q = os.path.join(p, k)
                    shutil.rmtree(q) if os.path.isdir(q) and not os.path.islink(q) else os.remove(q)
            continue
        tong += n
        print(f'{"XOÁ" if a.ghi else "sẽ xoá"} {dep(n):>9}  {os.path.relpath(p, XUONG)}  ({ly})')
        if a.ghi:
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
    print(f'{"Đã giải phóng" if a.ghi else "Sẽ giải phóng"}: {dep(tong)}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('lenh', nargs='?', default='xem', choices=['xem', 'chuyen', 'xoa-thanh-pham', 'don'])
    ap.add_argument('--du-an', action='append', help='chỉ dự án này (lặp được); cũng là xác nhận đã duyệt')
    ap.add_argument('--ngan-sach', type=int, default=150, help='giây tối đa mỗi lần chạy lệnh chuyen')
    ap.add_argument('--lai', action='store_true', help='chép và đối chiếu lại cả dự án đã khớp')
    ap.add_argument('--ghi', action='store_true', help='xoá thật (mặc định chỉ xem trước)')
    ap.add_argument('--nhom', help='nhóm dọn, mặc định R,N (H không bao giờ tự xoá)')
    ap.add_argument('--toi-da', type=int, default=25, help='số dòng tối đa mỗi nhóm khi xem')
    ap.add_argument('--json', help='ghi danh sách rác và nháp ra tệp JSON')
    ap.add_argument('--luu-tru', help='thư mục lưu trữ, ghi đè thuMucLuuTru (tools/duyet.py truyền thư mục giao vào đây)')
    a = ap.parse_args()
    global LUU_TRU_GHI_DE, DUYET_GIA_DINH
    if a.luu_tru:
        LUU_TRU_GHI_DE = CH._tuyet_doi(a.luu_tru)
    DUYET_GIA_DINH = set(a.du_an or [])
    {'xem': xem, 'chuyen': chuyen, 'xoa-thanh-pham': xoa_thanh_pham, 'don': don}[a.lenh](a)


if __name__ == '__main__':
    main()
