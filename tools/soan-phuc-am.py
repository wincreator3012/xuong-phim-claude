#!/usr/bin/env python3
"""Bản phúc âm nhiều bè "Mùa thương" (xưởng tự soạn): piano hát chính, organ, bè dây,
kèn cor đi bè đối, bass, trống mềm và vỗ tay; điệp khúc cuối nâng giọng.

Cảm hứng không khí từ ballad phúc âm kiểu "Seasons of Love" (nhiều bè dày, ấm, cộng đồng);
giai điệu, hoà âm, giọng (La giáng trưởng, nâng lên Si giáng) đều mới.
Piano: Salamander Grand Piano V3 (Alexander Holm, CC BY 3.0, phải ghi công khi dùng MP3).
Organ, bè dây, kèn cor: VSCO 2 Community Edition (CC0). Bass, trống, vỗ tay: tổng hợp bằng code.
  python3 soan-phuc-am.py --mau <mẫu Salamander> --vsco <VSCO-2-CE> --ra <thư mục>
Cần soan-piano-mau.py, soan-violin-mau.py, soan-pop-rock.py cùng thư mục (cần thêm
"/Keys/Organ/" và "/Brass/F Horn/sus/" trong sparse-checkout của VSCO).
"""
import argparse, importlib.util, itertools, os, re, json, wave
import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


P = _load("piano_mau", "soan-piano-mau.py")
V = _load("violin_mau", "soan-violin-mau.py")
R = _load("pop_rock", "soan-pop-rock.py")
SR = P.SR
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "Fb": 4, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11, "Cb": 11}
QUAL = {"": [0, 4, 7], "m": [0, 3, 7], "7": [0, 4, 7, 10], "maj7": [0, 4, 7, 11], "m7": [0, 3, 7, 10],
        "7sus": [0, 5, 7, 10], "m6": [0, 3, 7, 9], "mmaj7": [0, 3, 7, 11], "6": [0, 4, 7, 9], "add9": [0, 4, 7, 14]}


def nm(s):
    m = re.fullmatch(r"([A-G][b#]?)(-?\d)", s)
    return 12 * (int(m.group(2)) + 1) + NOTE[m.group(1)]


def chord(name, tr=0):
    """'Ab7/Gb' -> (các cao độ lớp [pc], bậc 3, bậc 7 hoặc 6, nốt bass pc)"""
    m = re.fullmatch(r"([A-G][b#]?)([a-z0-9]*)(?:/([A-G][b#]?))?", name)
    root = (NOTE[m.group(1)] + tr) % 12
    iv = QUAL[m.group(2)]
    pcs = [(root + i) % 12 for i in iv]
    third = (root + iv[1]) % 12
    sev = (root + iv[3]) % 12 if len(iv) > 3 else (root + iv[2]) % 12
    bass = (NOTE[m.group(3)] + tr) % 12 if m.group(3) else root
    return pcs, third, sev, bass


def voice(pcs, prev, n, lo, hi, must=(), avoid=()):
    """Dẫn bè: chọn n nốt hợp âm trong [lo, hi], chạy ít nhất so với bè trước, đủ bậc 3 và 7,
    tránh các lớp cao độ cách giai điệu nửa cung (avoid)."""
    cands = [m for m in range(lo, hi + 1) if m % 12 in pcs and m % 12 not in avoid]
    if len(cands) < n + 1:
        cands = [m for m in range(lo, hi + 1) if m % 12 in pcs]
    best, bs = None, 1e9
    for combo in itertools.combinations(cands, n):
        if max(combo) - min(combo) > 14:
            continue
        got = {c % 12 for c in combo}
        sc = 0 if prev is None else sum(abs(a - b) for a, b in zip(combo, prev))
        sc += 9 * sum(1 for p in must if p not in got) + 3 * (n - len(got))
        if prev is None:
            sc += abs(np.mean(combo) - (lo + hi) / 2) * 0.5
        if sc < bs:
            best, bs = list(combo), sc
    return best


DAU = ("mo-dau", "doan-1", "doan-2")   # phần đầu đã chải lại bè (2026-11-02)


def co_hoa_am(name, md):
    """Nốt hoà âm dưới giai điệu: không có ở phần mở và đoạn 1, đoạn 2 chỉ ở nốt dài."""
    if name in ("mo-dau", "doan-1"):
        return False
    if name == "doan-2":
        return md >= 2
    return md >= 1


def bass_note(pc, lo=31):
    return lo + (pc - lo) % 12


# ---------------------------------------------------------------- bản nhạc (4/4, phách chia ba)
T3 = 1 / 3
INTRO = [[(0, "Dbmaj7")], [(0, "Cm7"), (2, "F7")], [(0, "Bbm7")], [(0, "Db/Eb")]]
INTRO_MEL = [[(0, 2, "C6"), (2, 2, "Ab5")], [(0, 2, "G5"), (2, 2, "A5")], [(0, 2, "Db6"), (2, 2, "F5")],
             [(0, 3, "F5"), (3, 1, "Eb5")]]
VERSE = [[(0, "Ab"), (2, "Fm7")], [(0, "Dbmaj7"), (2, "Eb/Db")], [(0, "Cm7"), (2, "Fm7")],
         [(0, "Bbm7"), (2, "Eb7sus"), (3, "Eb7")], [(0, "Ab"), (2, "Ab7/Gb")], [(0, "Db/F"), (2, "Dbm6/E")],
         [(0, "Ab/Eb"), (2, "F7")], [(0, "Bbm7"), (2, "Eb7sus"), (3, "Eb7")]]
V1_MEL = [
    [(0, 1, "C5"), (1, 2 * T3, "Eb5"), (1 + 2 * T3, T3, "F5"), (2, 2, "Eb5")],
    [(0, 1.5, "F5"), (1.5, .5, "Eb5"), (2, 1, "Db5"), (3, 1, "Bb4")],
    [(0, 1, "C5"), (1, 1, "Bb4"), (2, 1.5, "Ab4"), (3.5, .5, "Bb4")],
    [(0, 2, "C5"), (2, 1, "Db5"), (3, 1, "Eb5")],
    [(0, 1, "C5"), (1, 2 * T3, "Eb5"), (1 + 2 * T3, T3, "F5"), (2, 1, "Ab5"), (3, 1, "Gb5")],
    [(0, 1.5, "F5"), (1.5, .5, "Eb5"), (2, 1.5, "E5"), (3.5, .5, "Db5")],
    [(0, 1.5, "C5"), (1.5, .5, "Eb5"), (2, 1, "C5"), (3, 1, "A4")],
    [(0, 1, "Bb4"), (1, 1, "Db5"), (2, 2, "C5")],
]
V2_MEL = V1_MEL[:4] + [
    [(0, 1, "Eb5"), (1, 2 * T3, "F5"), (1 + 2 * T3, T3, "G5"), (2, 1, "Ab5"), (3, 1, "Bb5")],
    [(0, 1.5, "Ab5"), (1.5, .5, "F5"), (2, 2, "Ab5")],
    [(0, 1.5, "Eb5"), (1.5, .5, "C5"), (2, 2, "Eb5")],
    [(0, 1, "Db5"), (1, 1, "C5"), (2, 2, "Bb4")],
]
CHORUS = [[(0, "Db"), (2, "Eb/Db")], [(0, "Cm7"), (2, "F7")], [(0, "Bbm7"), (2, "Cm7")], [(0, "Db"), (2, "Eb7sus")],
          [(0, "Db"), (2, "Eb/Db")], [(0, "Cm7"), (2, "Fm7")], [(0, "Bbm7"), (2, "Db/Eb")], [(0, "Ab")]]
CH_MEL = [
    [(0, 1, "Ab5"), (1, 1, "F5"), (2, 1.5, "G5"), (3.5, .5, "Ab5")],
    [(0, 1.5, "Bb5"), (1.5, .5, "G5"), (2, 2, "A5")],
    [(0, 1, "F5"), (1, 1, "Ab5"), (2, 1.5, "G5"), (3.5, .5, "Eb5")],
    [(0, 1.5, "F5"), (1.5, .5, "Eb5"), (2, 2, "Db5")],
    [(0, 1, "Ab5"), (1, 1, "F5"), (2, 1, "G5"), (3, 1, "Bb5")],
    [(0, 2, "C6"), (2, 1, "Bb5"), (3, 1, "Ab5")],
    [(0, 1, "Db6"), (1, 1, "C6"), (2, 2, "Bb5")],
    [(0, 4, "Ab5")],
]
BRIDGE = [[(0, "Fm7"), (2, "Fm7/Eb")], [(0, "Dbmaj7"), (2, "C7")], [(0, "Fm7"), (2, "Fm7/Eb")],
          [(0, "Bbm7"), (2, "Eb7sus")], [(0, "Fm"), (2, "Fmmaj7/E")], [(0, "Fm7/Eb"), (2, "Bb7/D")],
          [(0, "Dbmaj7"), (2, "Dbm6")], [(0, "Ab/Eb"), (2, "Eb7sus")]]
BR_MEL = [
    [(0, 1.5, "Ab5"), (1.5, .5, "G5"), (2, 2, "F5")],
    [(0, 1.5, "F5"), (1.5, .5, "Eb5"), (2, 2, "E5")],
    [(0, 1, "F5"), (1, 1, "Ab5"), (2, 2, "C6")],
    [(0, 2, "Db6"), (2, 1, "C6"), (3, 1, "Bb5")],
    [(0, 1.5, "Ab5"), (1.5, .5, "G5"), (2, 2, "Ab5")],
    [(0, 1.5, "C6"), (1.5, .5, "Bb5"), (2, 2, "Ab5")],
    [(0, 1.5, "Ab5"), (1.5, .5, "F5"), (2, 2, "E5")],
    [(0, 2, "Eb5"), (2, 1, "F5"), (3, 1, "Bb5")],
]
PIVOT = [[(0, "Eb/F"), (2, "F7sus"), (3, "F7")]]
PIVOT_MEL = [[(0, 2, "Eb5"), (2, 1, "F5"), (3, 1, "A5")]]
OUTRO = [[(0, "Eb")], [(0, "Ebm6")], [(0, "Bb/D"), (2, "Gm7")], [(0, "Cm7"), (2, "F7sus")], [(0, "Eb/Bb")], [(0, "Bb")]]
OUT_MEL = [[(0, 2, "G5"), (2, 2, "Bb5")], [(0, 2, "Gb5"), (2, 2, "C6")], [(0, 2, "F5"), (2, 2, "D5")],
           [(0, 2, "Eb5"), (2, 2, "C5")], [(0, 4, "D5")], [(0, 8, "D5")]]

# tên, hợp âm, giai điệu, dịch giọng, lực piano, organ, dây, kèn, bass, trống (0-3), vỗ tay, nhịp
SECTIONS = [
    ("mo-dau", INTRO, INTRO_MEL, 0, 64, 0, 0, 0, 0, 0, 0, [70, 70, 70, 66]),
    ("doan-1", VERSE, V1_MEL, 0, 61, 1, 0, 0, 1, 0, 0, [72] * 8),
    ("doan-2", VERSE, V2_MEL, 0, 62, 0, 1, 1, 1, 1, 0, [72] * 8),
    ("diep-khuc-1", CHORUS, CH_MEL, 0, 72, 2, 2, 1, 2, 2, 1, [72] * 8),
    ("chuyen", BRIDGE, BR_MEL, 0, 66, 1, 2, 1, 1, 1, 0, [72] * 7 + [70]),
    ("diep-khuc-2", CHORUS, CH_MEL, 0, 76, 2, 2, 2, 2, 2, 1, [72] * 8),
    ("nang-giong", PIVOT, PIVOT_MEL, 0, 74, 2, 2, 2, 2, 2, 0, [70]),
    ("diep-khuc-3", CHORUS, CH_MEL, 2, 82, 3, 3, 3, 2, 3, 1, [72] * 7 + [70]),
    ("ket", OUTRO, OUT_MEL, 0, 60, 2, 2, 1, 1, 0, 0, [68, 66, 64, 60, 56, 50]),
]


def build(seed=5):
    rng = np.random.default_rng(seed)
    piano, organ, strings, horn, bass, drums, marks = [], [], [], [], [], [], []
    t = 0.0
    prev_org = prev_str = None
    prev_horn = 60
    prev_shell = None
    hj = lambda: rng.normal(0, 0.006)
    vel = lambda v: int(np.clip(v + rng.normal(0, 2.5), 15, 120))
    for name, chs, mels, tr, pv, org, stg, hrn, bas, drm, clap, bpms in SECTIONS:
        marks.append((name, round(t, 2)))
        nb = len(chs)
        for bi, (ch, mel, bpm) in enumerate(zip(chs, mels, bpms)):
            sp = 60 / bpm
            arc = 1 + 0.07 * np.sin(np.pi * (bi + 0.5) / nb)
            last = name == "ket" and bi == nb - 1
            span_end = 8 if last else 4
            for ci, (cb, cn) in enumerate(ch):
                ce = ch[ci + 1][0] if ci + 1 < len(ch) else span_end
                span = ce - cb
                pcs, third, sev, bpc = chord(cn, tr)
                tc = t + cb * sp
                # giai điệu trong khoảng hợp âm này: bè đệm tránh nửa cung và nằm dưới giai điệu
                mm = []
                for mb, md, x in mel:
                    if mb < ce - 1e-6 and mb + md > cb + 1e-6:
                        q = nm(x) + tr
                        mm.append(q)
                        cq = [cn2 for cb2, cn2 in ch if cb2 <= mb + 1e-6][-1]
                        und = [k for k in range(q - 9, q - 2) if k % 12 in chord(cq, tr)[0]]
                        if und and co_hoa_am(name, md):
                            mm.append(und[-1])   # nốt hoà âm piano dưới giai điệu cũng cần tránh
                avoid = {(q + d) % 12 for q in mm for d in (1, -1)}
                top = min(mm) - 1 if mm else 99
                # piano tay trái: nốt bass, rồi hợp âm đệm ở phách ba nhịp nhàng (kiểu phúc âm)
                bn = bass_note(bpc, 36)
                piano.append((tc + hj(), span * sp, bn, vel(pv * arc - 8), "L"))
                if name in ("mo-dau", "doan-1"):
                    # hợp âm rải nhẹ đúng phách đổi hợp âm, giữ bằng pedal: không đảo phách khi chưa có trống
                    shell = voice(pcs, prev_shell, 3, 48, min(62, top - 2), must=(third, sev), avoid=avoid); prev_shell = shell
                    for o in ([0, 2] if span == 4 else [0]):
                        for k, m in enumerate(shell):
                            piano.append((tc + o * sp + 0.03 + k * 0.035 + hj() * 0.3, (span - o) * sp, m,
                                          vel(pv * arc - (18 if o == 0 else 23)), "L"))
                elif name == "doan-2":
                    # nhịp đều trên phách chính, một nhát lướt nhẹ trước phách 3 cho nhún chùm ba
                    shell = voice(pcs, prev_shell, 3, 48, min(62, top - 2), must=(third, sev), avoid=avoid); prev_shell = shell
                    for o in [b for b in (0, 1, 2, 3) if b < span - 0.1] + ([1 + 2 * T3] if span >= 3 else []):
                        for k, m in enumerate(shell):
                            acc = -16 if o == cb - cb else (-24 if o == 1 + 2 * T3 else -21)
                            piano.append((tc + o * sp + hj() + k * 0.003, 0.9 * sp, m, vel(pv * arc + acc), "L"))
                else:
                    shell = voice(pcs, None, 3, 50, min(64, top), must=(third, sev), avoid=avoid)
                    offs = [2 * T3, 1 + 2 * T3, 2 + 2 * T3, 3 + 2 * T3]
                    for o in offs:
                        if o < span - 0.1:
                            for k, m in enumerate(shell):
                                piano.append((tc + o * sp + hj() + k * 0.003, (min(span - o, 1) - 0.1) * sp, m,
                                              vel(pv * arc - 20 + (4 if o < 1 else 0)), "L"))
                # organ: hợp âm ngân dẫn bè mượt
                if org:
                    if name == "doan-1":
                        vo = voice(pcs, prev_org, 3, 50, min(63, top - 2), must=(third, sev), avoid=avoid)
                    else:
                        vo = voice(pcs, prev_org, 4, 50, min(70, top), must=(third, sev), avoid=avoid)
                    prev_org = vo
                    for m in vo:
                        organ.append((tc, span * sp + 0.05, m, [0, 50, 62, 70][org] * arc, ""))
                # bè dây: cello giữ bass, viola và violin dẫn bè
                if stg:
                    vs = voice(pcs, prev_str, 3, 52, min(74, top), must=(third, sev), avoid=avoid); prev_str = vs
                    lv = [0, 54, 64, 74][stg] * arc
                    strings.append((tc, span * sp + 0.1, bass_note(bpc, 36), lv, "vc"))
                    strings.append((tc, span * sp + 0.1, vs[0], lv, "va"))
                    for m in vs[1:]:
                        strings.append((tc, span * sp + 0.1, m, lv - 3, "vn"))
                # kèn cor: bè đối theo nốt dẫn (bậc 3 hoặc 7), chạy gần nhất
                if hrn:
                    opts = [m for m in range(53, min(68, top)) if m % 12 in (third, sev) and m % 12 not in avoid] \
                        or [m for m in range(53, 68) if m % 12 in (third, sev)]
                    hm = min(opts, key=lambda m: (abs(m - prev_horn), m))
                    lvh = [0, 56, 64, 74][hrn] * arc
                    if horn and horn[-1][2] == hm and abs(horn[-1][0] + horn[-1][1] - tc) < 0.05:
                        tt0, dd, mm, vv, ff = horn[-1]; horn[-1] = (tt0, dd + span * sp, mm, vv, ff)
                    else:
                        horn.append((tc, span * sp, hm, lvh, ""))
                    prev_horn = hm
                # bass: nốt gốc, nốt tiến dần sang hợp âm sau ở phách ba cuối
                if bas:
                    b0 = bass_note(bpc, 28)
                    bass.append((tc, (span - T3) * sp * 0.95, b0, 0.7 + 0.1 * bas, 0, 0))
                    nxt_pc = None
                    if ci + 1 < len(ch):
                        nxt_pc = chord(ch[ci + 1][1], tr)[3]
                    if nxt_pc is not None and span >= 1 and name != "doan-1":
                        tgt = bass_note(nxt_pc, 28)
                        app = tgt - 1 if tgt - 1 != b0 else tgt + 1
                        bass.append((tc + (span - T3) * sp, T3 * sp * 0.9, app, 0.6, 0, 0))
            # giai điệu piano, có nốt hoà âm bên dưới (quãng ba, quãng sáu) và quãng tám ở điệp khúc lớn
            for mb, md, x in mel:
                m = nm(x) + tr
                c = [cn for cb, cn in ch if cb <= mb + 1e-6][-1]
                pcs = chord(c, tr)[0]
                tt = t + mb * sp + 0.012
                v = pv * arc * (1.06 if md >= 2 else 1)
                piano.append((tt, md * sp, m, vel(v), "M"))
                if co_hoa_am(name, md):
                    under = [k for k in range(m - 9, m - 2) if k % 12 in pcs]
                    if under:
                        piano.append((tt + 0.008, md * sp, under[-1], vel(v - 16), "M"))
                if name in ("diep-khuc-2", "diep-khuc-3"):
                    piano.append((tt + 0.005, md * sp, m - 12, vel(v - 12), "M"))
            # trống mềm và vỗ tay
            def hit(kind, b, v):
                drums.append((t + b * sp + rng.normal(0, 0.004), kind, v * (1 + rng.normal(0, .06))))
            if drm >= 1:
                for k in range(12):
                    hit("hat", k * T3, (0.28 if k % 3 else 0.4) * (0.8 if drm == 1 else 1))
                hit("kick", 0, 0.55 + 0.1 * drm)
                hit("snare", 1, 0.25 + 0.12 * drm); hit("snare", 3, 0.25 + 0.12 * drm)
                if drm >= 2:
                    hit("kick", 2, 0.5); hit("kick", 2 + 2 * T3, 0.35)
                if drm >= 2 and bi % 4 == 0:
                    hit("crash", 0, 0.45 if drm == 2 else 0.65)
                if clap:
                    hit("clap", 1, 0.6); hit("clap", 3, 0.65)
            if name in ("nang-giong",):
                for k in range(6):
                    hit("tom", 2 + k * T3, 0.4 + 0.06 * k)
                hit("crash", 4, 0.8)
            t += 4 * sp
    return piano, organ, strings, horn, bass, drums, marks, t


# ---------------------------------------------------------------- nạp mẫu VSCO

def load_organ(folder):
    S = {}
    for f in os.listdir(folder):
        m = re.fullmatch(r"NT5_Man3Quiet_(\d+)_rr1\.wav", f)
        if m:
            S[(int(m.group(1)) - 86, 1)] = V.read_wav(os.path.join(folder, f))
    for k, x in S.items():
        V.DEV[(id(S), k)] = V.cents(x, k[0])
    return S


def clap(v, rng):
    N = int(0.3 * SR); t = np.arange(N) / SR
    x = sosfilt(butter(2, [900, 5000], btype="band", fs=SR, output="sos"), rng.standard_normal(N))
    env = np.zeros(N)
    for d0 in (0, 0.011, 0.022):
        i = int(d0 * SR); env[i:] += np.exp(-(t[: N - i]) / (0.008 if d0 < 0.02 else 0.12))
    return x * env * v * 0.6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mau", required=True)
    ap.add_argument("--vsco", required=True)
    ap.add_argument("--ra", required=True)
    ap.add_argument("--ten", default="xuong-phuc-am-mua-thuong")
    a = ap.parse_args()
    os.makedirs(a.ra, exist_ok=True)
    rng = np.random.default_rng(11)
    piano, organ, strings, horn, bass, drums, marks, t_end = build()
    total = int((t_end + 7) * SR)
    VS = a.vsco
    OR = load_organ(os.path.join(VS, "Keys/Organ/Quiet"))
    VN, _ = V.load_set(os.path.join(VS, "Strings/Violin Section/susVib"),
                       r"VlnEns_susVib_(?P<nn>[A-G]#?)(?P<oct>\d)_v(?P<l>\d)\.wav", lambda g: int(g["l"]))
    VA, _ = V.load_set(os.path.join(VS, "Strings/Viola Section/susvib"),
                       r"ViolaEns_susvib_(?P<nn>[A-G]#?)(?P<oct>\d)_v(?P<l>\d)_1\.wav", lambda g: int(g["l"]))
    VC, _ = V.load_set(os.path.join(VS, "Strings/Cello Section/susvib"),
                       r"susvib_(?P<nn>[A-G]#?)(?P<oct>\d)_v(?P<l>\d)_1\.wav", lambda g: int(g["l"]))
    HN, ho = V.load_set(os.path.join(VS, "Brass/F Horn/sus"),
                        r"MOHorn_sus_(?P<nn>[A-G]#?)(?P<oct>\d)_v(?P<l>\d)_1\.wav", lambda g: int(g["l"]) if g["l"] in "123" else None)
    print("lệch quãng tám kèn cor:", ho, " tầm kèn:", min(k[0] for k in HN), max(k[0] for k in HN))
    S = P.load_samples(a.mau)
    # piano: pedal đổi theo từng hợp âm
    ped = sorted({round(x[0], 2) for x in piano if x[4] == "L" and x[2] < 48})
    pn = [(max(0.0, t), d, m, v, h, 0, 0) for t, d, m, v, h in piano]
    bp = P.render(pn, [(p, 0) for p in ped], t_end, S)
    bp = np.pad(bp, ((0, 0), (0, max(0, total - bp.shape[1]))))[:, :total]
    LO = V.levels(OR, .3, 1.5)
    bo = V.render_simple(organ, OR, LO, total, lambda v, f: 1, 1, att=0.25, rel=0.5)
    LN, LA, LC = V.levels(VN, .4, 1.6), V.levels(VA, .4, 1.6), V.levels(VC, .4, 1.6)
    bs = (V.render_simple([x for x in strings if x[4] == "vc"], VC, LC, total, lambda v, f: 1 if v < 66 else 3, 1, att=0.45, rel=0.6)
          + V.render_simple([x for x in strings if x[4] == "va"], VA, LA, total, lambda v, f: 1 if v < 66 else 2, 1, att=0.45, rel=0.6)
          + V.render_simple([x for x in strings if x[4] == "vn"], VN, LN, total, lambda v, f: 1 if v < 66 else 2, 1, att=0.5, rel=0.6))
    LH = V.levels(HN, .3, 1.5)
    bh = V.render_simple(horn, HN, LH, total, lambda v, f: 1 if v < 60 else (2 if v < 72 else 3), 1, att=0.3, rel=0.55)
    bb = np.zeros((2, total)); bd = np.zeros((2, total))
    for t, d, m, v, *_ in bass:
        sig = R.synth_bass(m, d, v)
        sig = sosfilt(butter(2, 700, btype="low", fs=SR, output="sos"), sig)   # bass tròn, ấm
        R.place(bb, sig, t)
    pan = {"kick": 0, "snare": 0.05, "hat": 0.3, "crash": -0.35, "tom": -0.2, "clap": -0.1}
    for t, kind, v in drums:
        if kind == "clap":
            sig = clap(v, rng)
        elif kind == "snare":
            sig = sosfilt(butter(2, 5000, btype="low", fs=SR, output="sos"), R.snare(v, rng))   # snare mềm như chổi
        elif kind == "hat":
            sig = R.hat(v, rng) * 0.8
        else:
            sig = {"kick": lambda: R.kick(v) * 0.8, "crash": lambda: R.crash(v, rng), "tom": lambda: R.tom(v)}[kind]()
        R.place(bd, sig, t, pan[kind])
    norm = lambda x, db: x * 10 ** ((db - R.rms_db(x)) / 20) if np.any(x) else x
    bp = bp + 0.25 * sosfilt(butter(2, 2500, btype="high", fs=SR, output="sos"), bp, axis=1)
    bp = norm(bp, -17.5); bo = norm(bo, -27.5); bs = norm(bs, -26.0); bh = norm(bh, -27.5)
    bb = norm(bb, -24.0); bd = norm(bd, -26.0)
    bh = sosfilt(butter(2, 5000, btype="low", fs=SR, output="sos"), bh, axis=1)
    dry = bp + bo + bs + bh + bb + bd
    send = 0.24 * bp + 0.3 * bo + 0.38 * bs + 0.4 * bh + 0.18 * bd
    x = dry + 0.55 * (P.reverb(send, rt60=2.6, wet=1.0)[:, :total] - send)
    x = sosfilt(butter(2, 28, btype="high", fs=SR, output="sos"), x, axis=1)
    e = int((t_end + 5) * SR); x = x[:, :e]
    f = int(3.5 * SR); x[:, -f:] *= np.linspace(1, 0, f) ** 2
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.7
    wav = os.path.join(a.ra, a.ten + "_tho.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x.T, -1, 1) * 32767).astype("<i2").tobytes())
    json.dump({"moc": marks, "dai": round(e / SR, 2)}, open(os.path.join(a.ra, a.ten + "_moc.json"), "w"), ensure_ascii=False)
    print("xong", round(e / SR, 1), "giây")
    for k, v in marks:
        print(f"  {k:12s} {int(v // 60)}:{v % 60:05.2f}")


if __name__ == "__main__":
    main()
