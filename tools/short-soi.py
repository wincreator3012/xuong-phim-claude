#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOI MÉP CẮT cho short dọc: xem âm tiết, năng lượng tiếng, khoảng lặng, lời large-v3, độ khớp chữ quanh một đoạn nguồn.
Mọi mốc là GIÂY TRONG FILE NGUỒN. Chạy từ gốc xưởng, trỏ hồ sơ dự án bằng --du-an (mặc định thư mục hiện tại):

  python3 tools/short-soi.py tu   <kd> A B --du-an "../Du an/<x>"   âm tiết [mốc đầu], khoảng lặng trước từ <giây> (>= 0,08 s), xuống dòng khi lặng >= 0,25 s
  python3 tools/short-soi.py nl   <kd> A B ...                      năng lượng dB mỗi 40 ms + âm tiết (sàn ồn ở dòng đầu)
  python3 tools/short-soi.py lang <kd> A B [ngưỡng dB, mặc định -48] các quãng LẶNG (liên tục dưới ngưỡng): chỗ cắt an toàn
  python3 tools/short-soi.py lv3  A B [--tep transcript-large-v3/toan-audio.txt]   lời large-v3 trong khoảng A-B (để đọc hiểu, không dùng làm mốc)
  python3 tools/short-soi.py chu  <kd> A B "giả thuyết 1" "giả thuyết 2" ...  độ khớp CTC của từng giả thuyết chữ với tiếng (cao hơn = khớp hơn); chọn chữ, không đổi mốc

Quy tắc chọn mép (BAI-HOC chủ đề short mặt trên): đầu đoạn đặt ở mẫu lặng cuối cùng trước từ đầu; cuối đoạn đặt ở mẫu lặng đầu tiên sau từ cuối
cộng 0,02 s; không cắt giữa quãng nói liên tục (không có quãng lặng) mà bỏ đoạn đó. short-dung.py snap có chế độ exact nhận mép tuyệt đối này.
<kd> là tên khúc gỡ băng trong <dự án>/transcript/<kd>.tu.json (tools/moc-tu.py); mốc lệch khúc ở transcript/off.json (xem short-dung.py)."""
import argparse
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True


def _dung():
    spec = importlib.util.spec_from_file_location('short_dung', os.path.join(HERE, 'short-dung.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cmd_tu(a):
    D = _dung()
    syl, db, off, fl = D.load_syl(a.kd)
    prev = None
    out = []
    for w, s, e in syl:
        if e < a.A or s > a.B:
            prev = (s, e)
            continue
        gap = (s - prev[1]) if prev else 0
        out.append(('\n' if gap >= 0.25 else '') + f"{w}[{s:.2f}]" + (f"<{gap:.2f}>" if gap >= 0.08 else ''))
        prev = (s, e)
    print(' '.join(out))


def cmd_nl(a):
    D = _dung()
    syl, db, off, fl = D.load_syl(a.kd)
    print(f'sàn {fl}')
    n = int((a.B - a.A) / 0.04) + 1
    print(' '.join(f'{a.A + 0.04 * i:.2f}:{D.edb(db, off, a.A + 0.04 * i)}' for i in range(n)))
    print(' | '.join(f'{w}[{s:.2f}-{e:.2f}]' for w, s, e in syl if a.A - 0.1 <= s <= a.B))


def cmd_lang(a):
    D = _dung()
    syl, db, off, fl = D.load_syl(a.kd)
    th = a.nguong
    n = int((a.B - a.A) / 0.04) + 1
    runs, cur = [], None
    for i in range(n):
        t = a.A + 0.04 * i
        v = D.edb(db, off, t)
        if v is None:
            continue
        if v <= th:
            if cur is None:
                cur = [t, t, v]
            else:
                cur[1] = t
                cur[2] = min(cur[2], v)
        elif cur:
            runs.append(cur)
            cur = None
    if cur:
        runs.append(cur)
    for r in runs:
        print(f'{r[0]:.2f}-{r[1]+0.04:.2f} min {r[2]}')


def cmd_lv3(a):
    def sec(s):
        p = s.split(':')
        return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])
    for ln in open(a.tep, encoding='utf-8'):
        m = re.match(r'\[(\S+) - (\S+)\] (.*)', ln.strip())
        if m and sec(m.group(2)) >= a.A and sec(m.group(1)) <= a.B:
            print(f'{sec(m.group(1)):8.1f} {sec(m.group(2)):8.1f}  {m.group(3)}')


def cmd_chu(a):
    spec = importlib.util.spec_from_file_location('mt', os.path.join(HERE, 'moc-tu.py'))
    mt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mt)
    nguon = a.nguon
    if not nguon:
        import json
        c = os.path.join('clip-ngan', 'short.json')
        nguon = json.load(open(c, encoding='utf-8')).get('nguon') if os.path.isfile(c) else None
        nguon = nguon or 'nguon/mat.mp4'
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, 'x.wav')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(a.A), '-t', str(a.B - a.A), '-i', nguon, '-ac', '1', '-ar', str(mt.SR), w], check=True)
        x = mt.doc_wav(w)
    bm = mt.BoMoc()
    for h in a.gia_thuyet:
        words = [unicodedata.normalize('NFC', t.lower()) for t in h.split()]
        r = bm.can(x, a.A, words)
        cs = [q['c'] for q in r]
        print(f"{sum(cs)/len(cs):.3f}  {h}   " + ' '.join(f"{q['w']}:{q['c']}" for q in r))


def main():
    ap = argparse.ArgumentParser(description='Soi mép cắt short dọc')
    ap.add_argument('--du-an', default='.', help='thư mục dự án (mặc định: thư mục hiện tại)')
    sp = ap.add_subparsers(dest='lenh', required=True)
    for ten, f in (('tu', cmd_tu), ('nl', cmd_nl), ('lang', cmd_lang)):
        q = sp.add_parser(ten)
        q.add_argument('kd')
        q.add_argument('A', type=float)
        q.add_argument('B', type=float)
        if ten == 'lang':
            q.add_argument('nguong', type=float, nargs='?', default=-48.0)
        q.set_defaults(f=f)
    q = sp.add_parser('lv3')
    q.add_argument('A', type=float)
    q.add_argument('B', type=float)
    q.add_argument('--tep', default='transcript-large-v3/toan-audio.txt')
    q.set_defaults(f=cmd_lv3)
    q = sp.add_parser('chu')
    q.add_argument('kd')
    q.add_argument('A', type=float)
    q.add_argument('B', type=float)
    q.add_argument('gia_thuyet', nargs='+')
    q.add_argument('--nguon', default=None)
    q.set_defaults(f=cmd_chu)
    a = ap.parse_args()
    # ap.parse_args đặt --du-an trước lệnh con
    os.chdir(a.du_an)
    a.f(a)


if __name__ == '__main__':
    main()
