#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DUYỆT: khi người dùng nói "duyệt" sau khi xong các clip thành phẩm của một dự án.

Một lệnh gọn, ghép từ giao-thanh-pham.py và don-tuan.py, đích là thư mục giao `thuMucGiao` trong cau-hinh.json
(tên và vị trí do từng máy tự đặt: máy MBA của người dùng là `Thanh pham AI MBA`; máy khác có thể tên khác, xem mục
"Đặt thư mục giao" bên dưới). Kết quả: MỘT thư mục cho dự án, trong đó thư mục con đánh số (`00 Video day du`,
`Short NN <slug>`), mỗi thư mục con tự đủ: video, nghiem-thu.json, dang-tai/, transcript/. Rồi dọn nháp cho trống ổ.

    python3 tools/duyet.py "<tên dự án>"                    # XEM kế hoạch, không đổi gì (mặc định)
    python3 tools/duyet.py "<tên dự án>" chuyen             # ghi dấu duyệt, chép + transcript, đối chiếu. Lặp tới XONG-CHUYEN
    python3 tools/duyet.py "<tên dự án>" don                # XEM việc xoá bản Thành phẩm và nháp
    python3 tools/duyet.py "<tên dự án>" don --ghi          # xoá thật (cần quyền xoá: device_request_delete_permission)

Đặt thư mục giao (một lần mỗi máy, hoặc khi đổi chỗ):
    python3 tools/duyet.py --dat-dich "<đường dẫn thư mục giao>"   # ghi vào cau-hinh.json (thuMucGiao)
    python3 tools/duyet.py "<tên dự án>" chuyen --dich "<đường dẫn>"   # hoặc chỉ dùng một lần, không ghi cấu hình
    python3 tools/cau_hinh.py                                        # xem thư mục giao hiện tại ("Giao")
Đường dẫn trong VM Cowork có dạng `$HOME/mnt/<tên thư mục đã gắn>`; trên Mac thật là đường dẫn của Mac.

<tên dự án> là tên thư mục trong thư mục Thành phẩm (`thuMucThanhPham`, xem `python3 tools/cau_hinh.py`) (trùng tên hồ sơ trong `Du an/`), vd "2026-10 một clip giới thiệu chương trình.0 MC1 Dinh vi ban than".
`chuyen` chạy lặp được: hết giới hạn thời gian thì thoát mã 75, gọi lại y nguyên để chép tiếp.
`don` chỉ xoá bản trên Thanh pham/ sau khi đối chiếu lại cỡ mọi tệp và mã băm mẫu mọi video với bản ở thư mục giao.

Giữ lại luôn: nguồn quay thô (`Du an/<dự án>/nguon/`), timeline, gỡ băng, đồ hoạ, cảnh, nhạc, dang-tai và NGUON-O-DAU.md.
Dọn: rác (R), nháp của dự án đã duyệt (N: .tam, xuat-nhap, xuat-hoan-chinh trùng với bản đã giao, ảnh thử, log, _khuc);
nhóm H (video không trùng đâu) không bao giờ tự xoá.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import cau_hinh as CH  # noqa: E402

XUONG = os.path.dirname(CH.GOC)


def dep(n):
    for d in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or d == 'GB':
            return f'{n:.1f} {d}' if d != 'B' else f'{n} B'
        n /= 1024


def chay(script, *args):
    lenh = [sys.executable, os.path.join(TOOLS, script), *args]
    print('$ ' + ' '.join(['python3', 'tools/' + script, *args]), flush=True)
    r = subprocess.run(lenh, capture_output=True, text=True)
    out = (r.stdout or '') + (r.stderr or '')
    print(out, end='' if out.endswith('\n') else '\n', flush=True)
    return r.returncode, out


def dich_giao():
    g = CH.giao()
    if not g or not os.path.isdir(g):
        sys.exit('Chưa thấy thư mục giao (thuMucGiao trong cau-hinh.json): ' + str(g) +
                 '\nMáy này chưa đặt, hoặc phiên chưa gắn thư mục đó. Hỏi anh tên và nơi để thư mục giao thành phẩm, '
                 'gắn vào phiên (device_request_folder_access), rồi chạy: python3 tools/duyet.py --dat-dich "<đường dẫn>"')
    return g


def doc_so(dich):
    try:
        return json.load(open(os.path.join(dich, 'SO-LUU-TRU.json'), encoding='utf-8'))
    except (OSError, ValueError):
        return {'du_an': {}}


def ghi_dau_duyet(ten, dich):
    p = os.path.join(CH.du_an(), ten, 'NGUON-O-DAU.md')
    if os.path.isfile(p):
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(
        f'# Dấu duyệt và nơi để nguồn: {ten}\n\n'
        f'- {dt.date.today().isoformat()}: người dùng duyệt. Thành phẩm giao trọn gói sang `{os.path.basename(dich)}/{ten}/` '
        f'(mục lục `MUC-LUC.md` ở đó).\n'
        f'- Nguồn quay thô giữ nguyên ở `Du an/{ten}/nguon/` trên máy này; hồ sơ dựng lại (timeline, gỡ băng, cảnh) ở cùng hồ sơ.\n')
    print('Đã ghi dấu duyệt:', p)


def ke_hoach(ten, dich):
    tp = os.path.join(CH.thanh_pham(), ten)
    print(f'== KẾ HOẠCH DUYỆT: {ten}')
    print(f'   thư mục giao: {dich}')
    if os.path.isdir(tp):
        for con in sorted(os.listdir(tp)):
            q = os.path.join(tp, con)
            if os.path.isdir(q):
                n = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(q) for f in fs)
                print(f'   - {con}  ({dep(n)})')
    else:
        print('   (không còn thư mục trong Thanh pham/: có thể đã chuyển rồi)')
    print('\n== 1. CHÉP + TRANSCRIPT (chưa ghi gì, xem trước)')
    chay('giao-thanh-pham.py', ten)
    print('== 2. XOÁ BẢN Ở Thanh pham/ VÀ DỌN NHÁP (xem trước; nhóm R, N sẽ xoá, nhóm H sẽ hỏi anh)')
    chay('don-tuan.py', 'xem', '--du-an', ten, '--luu-tru', dich, '--toi-da', '15')
    print('Nói "duyệt" thì chạy: chuyen (lặp tới XONG-CHUYEN), rồi xin quyền xoá và chạy don --ghi.')


def chuyen(ten, dich, ngan_sach):
    t0 = time.time()
    tp = os.path.join(CH.thanh_pham(), ten)
    if not os.path.isdir(tp) and doc_so(dich)['du_an'].get(ten, {}).get('doi_chieu') != 'khop':
        sys.exit('Không thấy thành phẩm: ' + tp)
    ghi_dau_duyet(ten, dich)
    if os.path.isdir(tp):
        mã, out = chay('giao-thanh-pham.py', ten, '--ghi', '--gioi-han-giay', str(max(30, int(ngan_sach * 0.7))))
        if mã != 0:
            sys.exit(f'giao-thanh-pham lỗi (mã {mã})')
        if 'HẾT GIỜ' in out:
            print('CON-VIEC: hết giờ lượt này, chạy lại y nguyên lệnh để chép tiếp.')
            sys.exit(75)
        con = int(ngan_sach - (time.time() - t0))
        if con < 20:
            print('CON-VIEC: còn bước đối chiếu, chạy lại y nguyên lệnh.')
            sys.exit(75)
        mã, out = chay('don-tuan.py', 'chuyen', '--du-an', ten, '--luu-tru', dich, '--ngan-sach', str(con))
        if 'HẾT NGÂN SÁCH' in out or 'dừng giữa chừng' in out:
            print('CON-VIEC: chạy lại y nguyên lệnh.')
            sys.exit(75)
    m = doc_so(dich)['du_an'].get(ten, {})
    if m.get('doi_chieu') == 'khop':
        print(f'XONG-CHUYEN: {m.get("so_tep")} tệp, {dep(m.get("byte", 0))}, {m.get("so_video")} video, đối chiếu KHỚP. '
              f'Bước kế: xin quyền xoá rồi `duyet.py "{ten}" don --ghi`.')
    else:
        sys.exit('ĐỐI CHIẾU LỆCH hoặc chưa xong: ' + str(m.get('ghi_chu')))


def don(ten, dich, ghi):
    m = doc_so(dich)['du_an'].get(ten, {})
    if m.get('doi_chieu') != 'khop' and os.path.isdir(os.path.join(CH.thanh_pham(), ten)):
        sys.exit('Chưa đối chiếu KHỚP: chạy `chuyen` trước, không xoá gì.')
    truoc = shutil.disk_usage(XUONG).free
    thêm = ['--ghi'] if ghi else []
    mã1, o1 = chay('don-tuan.py', 'xoa-thanh-pham', '--du-an', ten, '--luu-tru', dich, *thêm)
    mã2, o2 = chay('don-tuan.py', 'don', '--du-an', ten, '--luu-tru', dich, *thêm)
    if ghi and (mã1 or mã2 or 'Operation not permitted' in o1 + o2 or 'Permission' in o1 + o2):
        sys.exit('Xoá bị chặn: xin quyền xoá (device_request_delete_permission cho thư mục xưởng) rồi chạy lại y nguyên lệnh.')
    if ghi:
        sau = shutil.disk_usage(XUONG).free
        da = os.path.join(CH.du_an(), ten)
        n = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(da) for f in fs)
        print(f'XONG-DON: ổ trống thêm {dep(max(0, sau - truoc))}; hồ sơ Du an/{ten} còn {dep(n)}.')
    else:
        print('(xem trước, chưa xoá gì; thêm --ghi để xoá thật)')


def dat_dich(duong):
    p = CH._tuyet_doi(duong)
    if not os.path.isdir(p):
        sys.exit('Không thấy thư mục: ' + p + ' (phiên chưa gắn thư mục này, hoặc sai đường dẫn).')
    f = os.path.join(CH.GOC, 'cau-hinh.json')
    cfg = json.load(open(f, encoding='utf-8')) if os.path.isfile(f) else {}
    cu = cfg.get('thuMucGiao') or []
    cu = [cu] if isinstance(cu, str) else list(cu)
    # lưu dạng bền qua các phiên: cùng thư mục mẹ với thư mục xưởng -> đường dẫn tương đối; trong thư mục nhà -> ~/...
    real, me = os.path.realpath(p), os.path.realpath(os.path.dirname(CH.GOC))
    nha = os.path.realpath(os.path.expanduser('~'))
    if os.path.dirname(real) == os.path.dirname(me):
        luu = os.path.relpath(real, CH.GOC)
    elif real.startswith(nha + os.sep):
        luu = '~/' + os.path.relpath(real, nha)
    else:
        luu = real
    cfg['thuMucGiao'] = [luu] + [c for c in cu if c and c != luu and not c.startswith('/sessions/')]
    duong = luu
    json.dump(cfg, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('Đã đặt thư mục giao:', p, '(ghi vào cau-hinh.json, thuMucGiao)')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('du_an', nargs='?')
    ap.add_argument('lenh', nargs='?', default='ke-hoach', choices=['ke-hoach', 'chuyen', 'don'])
    ap.add_argument('--ghi', action='store_true')
    ap.add_argument('--ngan-sach', type=int, default=140, help='giây tối đa mỗi lượt chạy (chuyen)')
    ap.add_argument('--dich', help='thư mục giao dùng một lần (ghi đè thuMucGiao, không ghi cấu hình)')
    ap.add_argument('--dat-dich', help='đặt thư mục giao của máy này vào cau-hinh.json rồi thoát')
    a = ap.parse_args()
    if a.dat_dich:
        return dat_dich(a.dat_dich)
    if not a.du_an:
        ap.error('thiếu tên dự án (hoặc dùng --dat-dich)')
    if a.dich:
        os.environ['LDN_GIAO'] = a.dich      # giao-thanh-pham.py và CH.giao() đọc biến này, tiến trình con thừa hưởng
    dich = dich_giao()
    {'ke-hoach': lambda: ke_hoach(a.du_an, dich), 'chuyen': lambda: chuyen(a.du_an, dich, a.ngan_sach),
     'don': lambda: don(a.du_an, dich, a.ghi)}[a.lenh]()


if __name__ == '__main__':
    main()
