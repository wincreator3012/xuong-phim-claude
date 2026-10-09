#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SINH CẢNH HTML (nửa dưới khung dọc) từ clip-ngan/<slug>/canh/spec-gen.json (short-dung.py snap ghi file này). Từ gốc xưởng:
  python3 tools/short-canh.py <slug> --du-an "../Du an/<x>"
Mốc trong spec là GIÂY NGUỒN; parts = các đoạn đã chốt (snap), mỗi đoạn một file cảnh (overlay). Khung: do-hoa-chung/canh-kit/mau/canh-short.html.
Ghi canh/<tag><k>.html và canh/cau-hinh.json (danh sách cảnh cần chụp: tools/short-render-canh.sh)."""
import argparse, json, os, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument('slug')
ap.add_argument('--du-an', default='.')
_a = ap.parse_args()
slug = _a.slug
os.chdir(_a.du_an)
base = os.path.join('clip-ngan', slug, 'canh')
spec = json.load(open(os.path.join(base, 'spec-gen.json'), encoding='utf-8'))
tpl = open(os.path.join(ROOT, 'do-hoa-chung', 'canh-kit', 'mau', 'canh-short.html'), encoding='utf-8').read()

def build(grp, tag, spec_grp):
    parts = spec_grp['parts']
    cum = []; c = 0.0
    for p_ in parts:
        cum.append(c); c += p_[1] - p_[0]
    def conv(P):
        for i, p_ in enumerate(parts):
            if p_[0] - 0.05 <= P <= p_[1] + 0.05:
                return round(cum[i] + min(max(P, p_[0]), p_[1]) - p_[0], 3)
            if P < p_[0]:
                return round(cum[i], 3)
        return round(c, 3)
    def ci(x):
        return [conv(x[0])] + x[1:] if isinstance(x, list) else x
    def conv_item(it):
        o = dict(it)
        for k in ('at', 'out', 'fadeAt'):
            if k in o: o[k] = conv(o[k])
        if 't' in o: o['t'] = [conv(v) for v in o['t']]
        for k in ('mv', 'sc', 'fill'):
            if k in o: o[k] = [ci(m) for m in o[k]]
        for k in ('halo', 'pulse'):
            if k in o and isinstance(o[k], list): o[k] = [conv(v) for v in o[k]]
        return o
    data = {'kicker': spec_grp.get('kicker', ''), 'items': [conv_item(i) for i in spec_grp['items']],
            'caps': [ci(x) for x in spec_grp.get('caps', [])], 'side': [ci(x) for x in spec_grp.get('side', [])]}
    def at_of(k):
        p_ = parts[k]
        if len(p_) > 2: return p_[2]
        return 4.7 if (grp == 'p' and k == 0) else 0.0
    def dur_of(k):
        p_ = parts[k]
        return math.floor((p_[1] - p_[0] - at_of(k) - 0.06) * 30) / 30.0
    first = next((k for k in range(len(parts)) if dur_of(k) > 0.5), 0)
    out = []
    for k, p_ in enumerate(parts):
        dur = dur_of(k)
        if dur <= 0.5:
            print(f'  ({tag}{k}: ngắn {dur:.2f} s, bỏ cảnh)'); continue
        d = dict(data); d['card'] = conv(spec_grp['card']) if k == first else None
        t0 = cum[k] + at_of(k)
        h = (tpl.replace('__TITLE__', f"{spec.get('title', slug)} {tag}{k}").replace('__DATA__', json.dumps(d, ensure_ascii=False))
                .replace('__T0__', str(round(t0, 3))).replace('__DUR__', str(round(dur, 3))))
        fn = os.path.join(base, f'{tag}{k}.html')
        open(fn, 'w', encoding='utf-8').write(h)
        out.append({'file': fn, 'out': f"canh-{'h' if grp == 'h' else 'p'}{k}.webm", 'at': at_of(k), 'dur': round(dur, 3), 't0': round(t0, 3)})
        print(f'  {fn}: at {at_of(k)} dur {dur:.3f} T0 {t0:.3f}')
    return out

cfg = []
if 'hook' in spec:
    cfg += build('h', 'h', spec['hook'])
cfg += build('p', 'p', spec)
json.dump(cfg, open(os.path.join(base, 'cau-hinh.json'), 'w'), ensure_ascii=False, indent=1)
