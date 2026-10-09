#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DỰNG SHORT DỌC "mặt trên, cảnh dưới" (layout mat-tren): chốt mép cắt theo âm tiết, sinh timeline, phụ đề.

Quy trình đầy đủ ở skills/phim-clip-ngan/references/short-mat-tren.md. Chạy từ gốc xưởng:

  python3 tools/short-dung.py snap <slug> --du-an "../Du an/<x>"
      đọc <dự án>/clip-ngan/<slug>/spec.json, chốt điểm cắt theo âm tiết (kiểm năng lượng tiếng ở mép), ghi
      snap.json, timeline.json, phu-de/cues.json, canh/spec-gen.json
  python3 tools/short-dung.py ass  <slug> --du-an "../Du an/<x>"
      tạo phụ đề .ass từ xuat-nhap/<slug>-doc.map.json (assemble.py ghi) và cues.json; báo dòng dài, cue ngoài đoạn

spec.json: {"slug", "kd": "<tên khúc gỡ băng>", "tieu_de", "hook": [A,B] hoặc [[A,B],...], "parts": [[A,B],...],
            "focus": [x,y], "zoom": 1.0, "paneH": 960, "cues": [[a,b,"chữ"],...], "scene": {...}, "hook_scene": {...},
            "part0_at": giây-trong-phần-đầu (tuỳ chọn), "intro_s", "outro_s"}
  A = đầu âm tiết đầu, B = cuối âm tiết cuối (giây trong file nguồn; xem tools/short-soi.py tu).
  parts[0] phải dài >= ~4,7 s nếu muốn thẻ bảng tên (0,3 s) rồi cảnh (4,7 s) trong phần thân.

Cấu hình dự án (tuỳ chọn) <dự án>/clip-ngan/short.json, khoá nào thiếu dùng mặc định bên dưới (DEFAULT).
Gỡ băng: <dự án>/transcript/<kd>.tu.json và <kd>.nang-luong.bin (tools/moc-tu.py). Nếu <kd> là khúc cắt từ file nguồn
dài, mốc lệch (giây) của khúc ở transcript/off.json {"<kd>": giây}; không có thì lệch 0 (gỡ băng thẳng file nguồn)."""
import argparse
import json
import os
import sys

DEFAULT = {
    'nguon': 'nguon/mat.mp4',
    'hau-to': 'doc',
    'nen': '#FAF7F1',
    'fade': '0xFAF7F1',
    'nhac': 'nhac-nen/acoustic-am/xuong-guitar-am_xuong-rieng.mp3',
    'nhac-db': -23,
    'intro': 'clip-ngan/_chung/do-hoa/intro.mp4',
    'outro': 'clip-ngan/_chung/do-hoa/outro.mp4',
    'lt-nhan': 'clip-ngan/_chung/do-hoa/lt-nhan.webm',
    'font': 'DejaVu Sans', 'co-chu': 54, 'mau-chu': '&H002F3526', 'le-duoi': 110, 'le-duoi-nang': 230,
}
ASS_DAU = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{co},{mau},&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,2,60,60,{le1},1
Style: Raised,{font},{co},{mau},&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,2,60,60,{le2},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""


def J(p):
    return json.load(open(p, encoding='utf-8'))


def W(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(o, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def cau_hinh():
    c = dict(DEFAULT)
    if os.path.isfile('clip-ngan/short.json'):
        c.update(J('clip-ngan/short.json'))
    return c


def load_syl(kd):
    off = 0.0
    for p in ('transcript/off.json', '.tam/off.json'):
        if os.path.isfile(p):
            off = float(J(p).get(kd, 0.0))
            break
    d = J(f'transcript/{kd}.tu.json')
    syl = [(w['w'], w['s'] + off, w['e'] + off) for w in d['tu']]
    db = open(f'transcript/{kd}.nang-luong.bin', 'rb').read()   # 100 Hz, byte = dB + 100
    return syl, db, off, (d.get('nangLuong') or {}).get('san')


def edb(db, off, t):
    i = int(round((t - off) * 100))
    return (db[i] - 100) if 0 <= i < len(db) else None


def snap_range(syl, A, B, lead=0.12, tail=0.14):
    i0 = min(range(len(syl)), key=lambda i: abs(syl[i][1] - A))
    i1 = min(range(len(syl)), key=lambda i: abs(syl[i][2] - B))
    s0, e1 = syl[i0][1], syl[i1][2]
    prev_e = syl[i0 - 1][2] if i0 > 0 else -1e9
    next_s = syl[i1 + 1][1] if i1 + 1 < len(syl) else 1e9
    tin = max(prev_e + 0.05, s0 - lead)
    tout = min(next_s - 0.05, e1 + tail)
    if tin > s0 - 0.02:
        tin = s0 - 0.02
    return round(tin, 3), round(tout, 3), syl[i0][0], syl[i1][0], i0, i1


def cmd_snap(slug):
    C = cau_hinh()
    base = f'clip-ngan/{slug}'
    sp = J(f'{base}/spec.json')
    syl, db, off, floor = load_syl(sp['kd'])
    out = {'slug': slug, 'hook': None, 'parts': []}
    print(f'[{slug}] sàn ồn {floor} dB')

    def dip(t, lo, hi):
        # nếu t đang giữa tiếng (to hơn sàn + 14 dB) thì dời tới chỗ lõm gần nhất trong [lo, hi]
        cur = edb(db, off, t)
        if cur is None or floor is None or cur <= floor + 14:
            return t, False
        thr = max(floor + 14, cur - 25)
        best = None
        for i in range(0, 61):
            for sg in (1, -1):
                tt = round(t + sg * i * 0.01, 3)
                if tt < lo or tt > hi:
                    continue
                e_ = edb(db, off, tt)
                if e_ is not None and e_ <= thr:
                    best = tt
                    break
            if best is not None:
                break
        return (best, True) if best is not None else (t, False)

    def one(tag, A, B, lead=0.12, tail=0.14, exact=False):
        a, b, w0, w1, i0, i1 = snap_range(syl, A, B, lead, tail)
        a0, b0 = a, b
        if exact:  # exact=True: A, B là mép cắt tuyệt đối (đã chọn bằng short-soi.py lang), bỏ qua snap và dời mép
            a, b, ra, rb = A, B, False, False
        else:
            a, ra = dip(a, syl[i0][1] - 0.18, (syl[i0 + 1][1] if i0 + 1 < len(syl) else a + 1) - 0.02)
            b, rb = dip(b, (syl[i1 - 1][2] if i1 > 0 else b - 1) + 0.02, (syl[i1 + 1][1] if i1 + 1 < len(syl) else b + 1) - 0.02)
        if ra or rb:
            print(f'    ({tag} dời mép về chỗ lõm: {a0:.3f}->{a:.3f}, {b0:.3f}->{b:.3f})')
        ea, eb = edb(db, off, a), edb(db, off, b)
        flag = ''
        for e_ in (ea, eb):
            if e_ is not None and floor is not None and e_ > floor + 14:
                flag = '  !! NĂNG LƯỢNG CAO ở mép cắt'
        print(f'  {tag:6s} {a:9.3f} - {b:9.3f}  dài {b-a:6.2f}  [{w0} ... {w1}]  dB đầu/cuối {ea}/{eb}{flag}')
        return {'in': a, 'out': b, 'dur': round(b - a, 3), 'w0': w0, 'w1': w1}

    hk = sp['hook'] if isinstance(sp['hook'][0], list) else [sp['hook']]
    out['hook'] = [one(f'hook{k+1}', *r) for k, r in enumerate(hk)]
    for k, r in enumerate(sp['parts']):
        out['parts'].append(one(f'than{k+1}', *r))
    tot = sum(h['dur'] for h in out['hook']) + sum(p['dur'] for p in out['parts'])
    print(f'  tổng lời {tot:.2f} s (chưa tính intro {sp.get("intro_s", 3.2)} s và outro {sp.get("outro_s", 6.5)} s)')
    W(f'{base}/snap.json', out)
    # timeline
    t = {"aspect": "doc", "fps": 30, "fadeColor": C['fade'], "nen": C['nen'], "paneH": sp.get('paneH', 960),
         "music": {"src": C['nhac'], "mode": "full", "gainDb": C['nhac-db'], "duck": True, "fadeIn": 2, "fadeOut": 5}}
    fx, fy = sp.get('focus', [0.4, 0.5])

    def seg(label, a, b, ov=None, chapter=None):
        s = {"type": "video", "src": C['nguon'], "snap": False, "layout": "mat-tren", "cropFocus": fx, "cropFocusY": fy,
             "cropZoom": sp.get("zoom", 1.0), "in": a, "out": b, "label": label}
        if chapter:
            s["chapter"] = chapter
        s["fadeOut"] = 0.05
        if ov:
            s["overlay"] = ov
        return s
    segs = []
    for k, h in enumerate(out['hook']):
        ov = None
        if sp.get('hook_scene'):
            ov = [{"src": f"{base}/do-hoa/doc/canh-h{k}.webm", "at": 0.25 if k == 0 else 0.0}]
        segs.append(seg(f'hook{k+1}' if len(out['hook']) > 1 else 'hook', h['in'], h['out'], ov, 'Hook' if k == 0 else None))
    segs.append({"type": "insert", "src": C['intro'], "role": "intro"})
    for k, p in enumerate(out['parts']):
        if k == 0:
            ov = [{"src": C['lt-nhan'], "at": 0.3}]
            if (p['out'] - p['in']) - 4.7 >= 0.5:   # cảnh p0 chỉ có khi phần còn lại sau 4,7 s dài >= 0,5 s (khớp short-canh.py)
                ov.append({"src": f"{base}/do-hoa/doc/canh-p0.webm", "at": 4.7})
        else:
            ov = [{"src": f"{base}/do-hoa/doc/canh-p{k}.webm", "at": 0}]
        segs.append(seg(f'than{k+1}', p['in'], p['out'], ov, 'Than' if k == 0 else None))
    segs.append({"type": "insert", "src": C['outro'], "role": "outro"})
    t['segments'] = segs
    W(f'{base}/timeline.json', t)
    W(f'{base}/phu-de/cues.json', sp['cues'])
    # spec cho short-canh.py: parts theo mốc đã chốt (mốc cảnh trong spec.json viết theo giây nguồn)
    sc = dict(sp['scene'])
    sc['parts'] = [[p['in'], p['out']] + ([sp['part0_at']] if (k == 0 and sp.get('part0_at') is not None) else []) for k, p in enumerate(out['parts'])]
    sc['title'] = sp.get('tieu_de', slug)
    if sp.get('hook_scene'):
        hs = dict(sp['hook_scene'])
        hs['parts'] = [[h['in'], h['out']] + ([0.25] if k == 0 else [0.0]) for k, h in enumerate(out['hook'])]
        sc['hook'] = hs
    W(f'{base}/canh/spec-gen.json', sc)
    print('  đã ghi snap.json, timeline.json, phu-de/cues.json, canh/spec-gen.json')


def cmd_ass(slug):
    C = cau_hinh()
    base = f'clip-ngan/{slug}'
    M = J(f"xuat-nhap/{slug}-{C['hau-to']}.map.json")
    CUES = J(f'{base}/phu-de/cues.json')
    cuts = [pt for pt in M['parts'] if pt['kind'] == 'cut']
    nh = len(J(f'{base}/snap.json').get('hook', []))
    body = cuts[min(nh, len(cuts) - 1)]
    LT = (body['start'] + 0.3, body['start'] + 4.6)   # cửa sổ bảng tên: phụ đề nâng lên (Raised)

    def to_out(p):
        for pt in cuts:
            if pt['in'] - 0.03 <= p <= pt['out'] + 0.03:
                return pt['start'] + (min(max(p, pt['in']), pt['out']) - pt['in'])
        best = min(cuts, key=lambda pt: min(abs(p - pt['in']), abs(p - pt['out'])))
        d_ = min(abs(p - best['in']), abs(p - best['out']))
        if d_ <= 0.2:
            print(f'    (cue {p:.2f} lệch {d_:.2f}s so với mép đoạn, kéo vào)')
            return best['start'] + (min(max(p, best['in']), best['out']) - best['in'])
        raise ValueError(f'cue ngoài mọi đoạn: {p}')

    def two(t):
        if '\\N' in t or len(t) <= 30:
            return t
        w = t.split()
        best = None
        for k in range(1, len(w)):
            a, b = ' '.join(w[:k]), ' '.join(w[k:])
            sc = abs(len(a) - len(b)) - (14 if (w[k-1][-1] in ',.;?' and max(len(a), len(b)) <= 31) else 0)
            if max(len(a), len(b)) > 31:
                sc += 100
            if best is None or sc < best[0]:
                best = (sc, a + '\\N' + b)
        return best[1]

    def fmt(t):
        return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
    dau = ASS_DAU.format(font=C['font'], co=C['co-chu'], mau=C['mau-chu'], le1=C['le-duoi'], le2=C['le-duoi-nang'])
    lines = [dau]
    for a, b, txt in CUES:
        ta, tb = to_out(a), to_out(b)
        st = 'Raised' if (ta < LT[1] and tb > LT[0]) else 'Default'
        _t = two(txt)
        if st == 'Raised' and tb > LT[1] + 0.25 and ta < LT[1] - 0.25:
            # cue vắt qua mép bảng tên: phần sau bảng tên hạ về vị trí thường để không đè chữ cảnh
            lines.append(f"Dialogue: 0,{fmt(ta)},{fmt(LT[1])},Raised,,0,0,0,,{_t}")
            lines.append(f"Dialogue: 0,{fmt(LT[1])},{fmt(tb)},Default,,0,0,0,,{_t}")
        else:
            lines.append(f"Dialogue: 0,{fmt(ta)},{fmt(tb)},{st},,0,0,0,,{_t}")
        wmax = max(len(x) for x in _t.split('\\N'))
        print(f'{ta:6.2f}-{tb:6.2f} {st:7s} {_t!r}' + (f'   !! DÒNG DÀI {wmax} (>31)' if wmax > 31 else ''))
    open(f"{base}/phu-de/{slug}-{C['hau-to']}.ass", 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser(description='Dựng short dọc mặt trên + cảnh dưới')
    ap.add_argument('lenh', choices=['snap', 'ass'])
    ap.add_argument('slug')
    ap.add_argument('--du-an', default='.', help='thư mục dự án (mặc định: thư mục hiện tại)')
    a = ap.parse_args()
    os.chdir(a.du_an)
    {'snap': cmd_snap, 'ass': cmd_ass}[a.lenh](a.slug)


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
