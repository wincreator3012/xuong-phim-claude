#!/usr/bin/env python3
"""Soạn bản violin nguyên bản bằng mẫu nhạc cụ thật VSCO 2 Community Edition (CC0).

Bản nhạc (giai điệu, hoà âm, cấu trúc) do xưởng viết mới. Tiếng đàn: violin độc tấu,
bè dây violin, viola, cello và piano đứng từ VSCO 2 CE (Versilian Studios, CC0 1.0,
không cần ghi công). Mẫu là nốt đơn lẻ, không phải bản thu nhạc của ai.

Dùng:
  python3 soan-violin-mau.py --vsco <thư mục VSCO-2-CE> --ra <thư mục> [--hat 1]
Lấy mẫu (chỉ phần cần, khoảng 530 MB):
  git clone --filter=blob:none --no-checkout --depth 1 https://github.com/sgossner/VSCO-2-CE
  cd VSCO-2-CE && git sparse-checkout set --no-cone "/Strings/Solo Violin/Arco Vib/" \\
     "/Strings/Violin Section/susVib/" "/Strings/Viola Section/susvib/" \\
     "/Strings/Cello Section/susvib/" "/Keys/Upright Piano/" && git checkout
Cần: numpy, scipy, mido, ffmpeg.
"""
import argparse, os, re, json, wave
from fractions import Fraction
import numpy as np
from scipy.signal import resample_poly, oaconvolve, butter, sosfilt

SR = 44100
PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def n(s):
    m = re.fullmatch(r"([A-G]#?)(-?\d)", s)
    return 12 * (int(m.group(2)) + 1) + PC[m.group(1)]


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- nạp mẫu

def read_wav(path):
    import subprocess
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()
    a = np.abs(x).max(0)
    thr = 0.02 * a.max()
    i = int(np.argmax(a > thr))
    return x[:, max(0, i - int(0.004 * SR)):]


def detect_midi(x, guess):
    seg = x.mean(0)[int(0.3 * SR): int(1.3 * SR)]
    if len(seg) < SR // 4:
        seg = x.mean(0)
    N = 1 << 18
    X = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), N))
    fr = np.fft.rfftfreq(N, 1 / SR)
    best, bs = guess, -1
    for k in (-12, 0, 12):
        f = mtof(guess + k)
        sc = 0
        for h in range(1, 9):
            band = (fr > h * f * 0.985) & (fr < h * f * 1.015)
            if band.any():
                sc += X[band].max() / h ** 0.5
        if sc > bs:
            best, bs = guess + k, sc
    return best


def load_set(folder, pattern, layer_of):
    """Trả về {(midi, lớp): mảng}. Tự sửa lệch quãng tám trong tên file bằng đo cao độ."""
    S, offs = {}, []
    for f in sorted(os.listdir(folder)):
        m = re.fullmatch(pattern, f)
        if not m:
            continue
        g = m.groupdict()
        midi = 21 + 2 * int(g["i"]) if g.get("i") else 12 * (int(g["oct"]) + 1) + PC[g["nn"]]
        lay = layer_of(g)
        if lay is None:
            continue
        x = read_wav(os.path.join(folder, f))
        S[(midi, lay)] = x
        offs.append(detect_midi(x, midi) - midi)
    off = max(set(offs), key=offs.count)
    if off:
        S = {(m + off, l): v for (m, l), v in S.items()}
    for k, x in S.items():
        DEV[(id(S), k)] = cents(x, k[0])
    return S, off


DEV = {}


def cents(x, m):
    """Độ lệch cao độ của mẫu so với chuẩn A440, tính bằng cent (đo trên đoạn giữa, đã gồm rung)."""
    seg = x.mean(0)[int(0.4 * SR): int(1.9 * SR)]
    if len(seg) < SR // 2:
        seg = x.mean(0)[: SR]
    N = 1 << 20
    X = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), N))
    fr = np.fft.rfftfreq(N, 1 / SR)
    tot = 0.0
    for h in (1, 2, 3):
        e = mtof(m) * h
        b = (fr > e * 0.965) & (fr < e * 1.035)
        pk = fr[b][np.argmax(X[b])]
        tot += 1200 * np.log2(pk / e)
    c = tot / 3
    return float(np.clip(c, -45, 45))


# ---------------------------------------------------------------- bản nhạc (3/4, Si thứ)

PIANO_V = {
    "Bm":    [35, 42, 47, 50, 54],
    "G":     [43, 50, 55, 57, 59],
    "D":     [38, 45, 50, 54, 57],
    "A":     [45, 52, 57, 59, 61],
    "A/C#":  [37, 45, 52, 57, 61],
    "Em7":   [40, 47, 50, 55, 59],
    "F#sus": [42, 49, 54, 59, 61],
    "F#":    [42, 49, 54, 58, 61],
    "D/F#":  [42, 45, 50, 54, 57],
    "F#m7":  [42, 49, 52, 57, 61],
    "Bm9":   [35, 42, 49, 50, 54],
}
# bè dây: cello, viola, violin 2, violin 1
PAD_V = {
    "Bm":    [47, 54, 62, 66],
    "G":     [43, 59, 62, 67],
    "D":     [38, 57, 62, 66],
    "A":     [45, 57, 61, 64],
    "A/C#":  [49, 57, 64, 69],
    "Em7":   [40, 59, 62, 67],
    "F#sus": [42, 54, 61, 71],
    "F#":    [42, 54, 58, 61],
    "D/F#":  [42, 57, 62, 66],
    "F#m7":  [42, 57, 61, 64],
    "Bm9":   [47, 54, 61, 62],
}


def M(*xs):
    return [x if len(x) == 4 else (*x, "") for x in xs]


A_CH = [[(0, "Bm")], [(0, "G")], [(0, "D")], [(0, "A")], [(0, "Bm")], [(0, "G")], [(0, "Em7")],
        [(0, "F#sus"), (2, "F#")], [(0, "Bm")], [(0, "G")], [(0, "D")], [(0, "A/C#")], [(0, "G")],
        [(0, "Em7")], [(0, "F#sus"), (2, "F#")], [(0, "Bm")]]
A_MEL = [
    M((0, 1.5, "F#4"), (1.5, .5, "A4"), (2, 1, "B4")),
    M((0, 2, "D5"), (2, .5, "C#5"), (2.5, .5, "B4")),
    M((0, 1, "A4"), (1, 1, "F#4"), (2, 1, "A4")),
    M((0, 2.5, "E4", "g"), (2.5, .5, "F#4")),
    M((0, 1.5, "B4"), (1.5, .5, "C#5"), (2, 1, "D5")),
    M((0, 1, "E5"), (1, 1, "D5"), (2, 1, "B4")),
    M((0, 1.5, "D5"), (1.5, .5, "E5"), (2, 1, "G5")),
    M((0, 1.5, "F#5", "g"), (1.5, .5, "E5"), (2, 1, "C#5")),
    M((0, 1.5, "D5"), (1.5, .5, "C#5"), (2, 1, "B4")),
    M((0, 2, "G4"), (2, .5, "A4"), (2.5, .5, "B4")),
    M((0, 1.5, "D5"), (1.5, .5, "E5"), (2, 1, "F#5")),
    M((0, 2, "E5", "g"), (2, 1, "C#5")),
    M((0, 1, "D5"), (1, 1, "G5"), (2, 1, "F#5")),
    M((0, 1.5, "E5"), (1.5, .5, "D5"), (2, 1, "B4")),
    M((0, 2, "C#5"), (2, .5, "B4"), (2.5, .5, "A#4")),
    M((0, 3, "B4", "g")),
]
B_CH = [[(0, "G")], [(0, "A")], [(0, "D")], [(0, "Bm")], [(0, "G")], [(0, "A")], [(0, "D/F#")], [(0, "Bm")],
        [(0, "G")], [(0, "A")], [(0, "F#m7")], [(0, "Bm")], [(0, "Em7")], [(0, "A")], [(0, "D")], [(0, "D")]]
B_MEL = [
    M((0, 1.5, "D5"), (1.5, .5, "E5"), (2, 1, "G5")),
    M((0, 2, "A5", "g"), (2, .5, "G5"), (2.5, .5, "F#5")),
    M((0, 1, "F#5"), (1, 1, "E5"), (2, 1, "D5")),
    M((0, 2.5, "F#5", "g"), (2.5, .5, "D5")),
    M((0, 1.5, "B5"), (1.5, .5, "A5"), (2, 1, "G5")),
    M((0, 1, "E5"), (1, 1, "A5"), (2, 1, "C#6")),
    M((0, 2, "D6", "g"), (2, .5, "C#6"), (2.5, .5, "B5")),
    M((0, 3, "F#5")),
    M((0, 1.5, "G5"), (1.5, .5, "A5"), (2, 1, "B5")),
    M((0, 2, "C#6", "g"), (2, 1, "A5")),
    M((0, 1.5, "C#6"), (1.5, .5, "B5"), (2, 1, "A5")),
    M((0, 2, "F#5"), (2, .5, "E5"), (2.5, .5, "D5")),
    M((0, 1.5, "E5"), (1.5, .5, "F#5"), (2, 1, "G5")),
    M((0, 1.5, "A5"), (1.5, .5, "B5"), (2, 1, "C#6")),
    M((0, 5, "D6", "g")),
    [],
]
INTRO_CH = A_CH[:7] + [[(0, "F#sus"), (2, "F#")]]
BRIDGE_CH = [[(0, "Bm")], [(0, "G")], [(0, "Em7")], [(0, "F#sus"), (2, "F#")]]
A2_MEL = [[(b, d, x[:-1] + str(int(x[-1]) + 1), g) for b, d, x, g in bar] for bar in A_MEL]
OUT_CH = [[(0, "G")], [(0, "D")], [(0, "Em7")], [(0, "F#sus"), (2, "F#")], [(0, "Bm")], [(0, "G")],
          [(0, "Bm9")], [(0, "Bm9")]]
OUT_MEL = [
    M((0, 1.5, "D5"), (1.5, .5, "C#5"), (2, 1, "B4")),
    M((0, 3, "A4", "g")),
    M((0, 1.5, "G4"), (1.5, .5, "A4"), (2, 1, "B4")),
    M((0, 2, "C#5"), (2, 1, "A#4")),
    M((0, 1.5, "F#4"), (1.5, .5, "A4"), (2, 1, "B4")),
    M((0, 3, "D5")),
    M((0, 3, "C#5")),
    M((0, 3.5, "B4")),
]

# tên, hợp âm, giai điệu, lực violin, lực piano, lực bè dây, mức bè (0 cello+viola, 1 đủ, 2 đủ + violin đôi), nhịp độ
SECTIONS = [
    ("mo-dau", INTRO_CH, [[]] * 8, 0, 50, 46, 0, [62] * 7 + [60]),
    ("A", A_CH, A_MEL, 60, 48, 50, 0, [63] * 15 + [61]),
    ("B", B_CH, B_MEL, 74, 56, 62, 1, [64] * 16),
    ("nghi", BRIDGE_CH, [[]] * 4, 0, 50, 48, 0, [62, 62, 61, 60]),
    ("A-cao-trao", A_CH, A2_MEL, 82, 60, 72, 2, [64] * 15 + [61]),
    ("ket", OUT_CH, OUT_MEL, 52, 44, 44, 0, [60, 58, 57, 55, 53, 51, 48, 46]),
]


def build(seed=1):
    rng = np.random.default_rng(seed)
    vio, pia, pad, ens = [], [], [], []      # (t, dài, midi, lực, cờ)
    marks, tempo, pedal = [], [], []
    t0, tick0 = 0.0, 0
    PPQ = 480
    midi_ev = []

    def rec(track, t, d, m, v, tk, dtk, flag=""):
        v = int(np.clip(v + rng.normal(0, 2), 15, 120))
        track.append((t, d, m, v, flag))
        ti = 0 if track is vio else (1 if track is pia else 2)
        midi_ev.append((ti, tk, dtk, m, v))

    for name, chs, mels, vv, pv, sv, lvl, bpms in SECTIONS:
        marks.append((name, round(t0, 2)))
        nb = len(chs)
        for bi, (ch, mel, bpm) in enumerate(zip(chs, mels, bpms)):
            spb = 60 / bpm
            tempo.append((tick0, bpm))
            arc = 1 + 0.09 * np.sin(np.pi * (bi + 0.5) / nb)
            for ci, (cb, cn) in enumerate(ch):
                ce = ch[ci + 1][0] if ci + 1 < len(ch) else 3
                pedal.append((t0 + cb * spb, tick0 + int(cb * PPQ)))
                pv5 = PIANO_V[cn]
                idx = [0, 1, 2, 3, 2, 1] if lvl < 2 else [0, 1, 2, 3, 4, 3]
                steps = int(round((ce - cb) * 2))
                for k in range(steps):
                    b = cb + 0.5 * k
                    acc = 6 if k == 0 else (-1 if k % 2 else 1)
                    rec(pia, t0 + b * spb + rng.normal(0, .006), .5 * spb, pv5[idx[k % 6]], pv * arc + acc,
                        tick0 + int(b * PPQ), PPQ // 2)
                voc = PAD_V[cn]
                parts = voc[:2] if lvl == 0 else voc
                for j, m in enumerate(parts):
                    rec(pad, t0 + cb * spb, (ce - cb) * spb, m, sv * arc - (4 if j >= 2 else 0),
                        tick0 + int(cb * PPQ), int((ce - cb) * PPQ), flag=["vc", "va", "vn", "vn"][j])
            for b, d, x, g in mel:
                m = n(x)
                t = t0 + b * spb
                v = vv * arc * (1.05 if d >= 2 else 1)
                if g:
                    # luyến láy Celtic: nốt bậc trên lướt nhanh vào nốt chính
                    up = next(k for k in range(m + 1, m + 3) if k % 12 in (11, 1, 2, 4, 6, 7, 9))
                    rec(vio, t - 0.11, 0.11, up,
                        v * 0.85, tick0 + int(b * PPQ) - 50, 50, flag="lay")
                rec(vio, t, d * spb, m, v, tick0 + int(b * PPQ), int(d * PPQ))
                if lvl == 2:
                    rec(ens, t + 0.01, d * spb, m - 12, v * 0.8, tick0 + int(b * PPQ), int(d * PPQ), flag="vn")
            t0 += 3 * spb
            tick0 += 3 * PPQ
    end = t0
    return vio, pia, pad, ens, marks, tempo, pedal, end, midi_ev


# ---------------------------------------------------------------- bộ phát

RATIO = {k: Fraction(2 ** (-k / 12)).limit_denominator(100) for k in range(-3, 4)}
_cache = {}


def pitched(S, key, shift):
    ck = (id(S), key, shift)
    if ck not in _cache:
        x = S[key]
        semis = shift - DEV.get((id(S), key), 0.0) / 100.0
        if abs(semis) < 0.02:
            y = x
        else:
            r = Fraction(2 ** (-semis / 12)).limit_denominator(600)
            y = resample_poly(x, r.numerator, r.denominator, axis=1)
        _cache[ck] = y.astype(np.float32)
    return _cache[ck]


def levels(S, a=0.1, b=1.2):
    return {k: 10 * np.log10(np.mean(x[:, int(a * SR): int(b * SR)] ** 2) + 1e-12) for k, x in S.items()}


def pick(S, m, layer):
    avail = sorted({k[0] for k in S if k[1] == layer})
    s = min(avail, key=lambda a: (abs(a - m), a))
    return s, m - s


def place(out, seg, t):
    i = int(t * SR)
    if i < 0:
        seg, i = seg[:, -i:], 0
    j = min(i + seg.shape[1], out.shape[1])
    if j > i:
        out[:, i:j] += seg[:, : j - i]


_sus = {}


def sus_start(y, key):
    """Chỗ mẫu đã nở đủ tiếng (đạt -3 dB so với phần ngân)."""
    if key not in _sus:
        x = y.mean(0)
        fr = int(0.02 * SR)
        e = np.sqrt((x[: len(x) // fr * fr] ** 2).reshape(-1, fr).mean(1))
        sus = np.median(e[25:100])
        _sus[key] = int(np.argmax(e >= 0.7 * sus)) * fr
    return _sus[key]


_lev = {}


def sus_level(y, key):
    if key not in _lev:
        i = sus_start(y, key)
        _lev[key] = 10 * np.log10(np.mean(y[:, i: i + SR] ** 2) + 1e-12)
    return _lev[key]


def render_violin(notes, S, L, total):
    out = np.zeros((2, total), np.float32)
    notes = sorted(notes)
    for i, (t, d, m, v, flag) in enumerate(notes):
        layer = "f"   # mẫu lực mạnh đều và ổn định; sắc thái tạo bằng mức và độ tối
        s, sh = pick(S, m, layer)
        y = pitched(S, (s, layer), sh)
        nxt = notes[i + 1][0] if i + 1 < len(notes) else 1e9
        prv_end = notes[i - 1][0] + notes[i - 1][1] if i > 0 else -1
        legato_in = t - prv_end < 0.03
        legato_out = nxt - (t + d) < 0.03
        si = sus_start(y, (s, layer, sh))
        if (legato_in and flag != "lay") or flag == "lay":
            skip = max(0, si - int(0.02 * SR))          # luyến: vào thẳng phần ngân
        else:
            skip = max(0, si - int(0.22 * SR))          # mở câu: giữ đoạn nở ngắn tự nhiên
        hold = d + (0.03 if legato_out else 0.0)
        rel = 0.07 if legato_out else (0.06 if flag == "lay" else 0.45)
        Ln = min(y.shape[1] - skip, int((hold + rel * 3) * SR))
        seg = y[:, skip: skip + Ln].copy()
        tt = np.arange(Ln) / SR
        att = 0.06 if legato_in else (0.02 if flag == "lay" else 0.05)
        env = np.clip(tt / att, 0, 1)
        if d >= 1.0 and flag != "lay":
            # thở theo nốt dài: nở nhẹ ở giữa, rút nhẹ cuối
            p = np.clip(tt / max(d, 1e-3), 0, 1)
            env *= 0.88 + 0.22 * np.sin(np.pi * np.clip(p * 0.9 + 0.05, 0, 1))
        k = int(hold * SR)
        if k < Ln:
            env[k:] *= np.exp(-(tt[k:] - hold) / rel)
        g = 10 ** ((-24.0 - sus_level(y, (s, layer, sh)) + 0.3 * (v - 64)) / 20)
        fc = float(np.clip(3600 + (v - 45) * 140, 3600, 9500))
        seg = sosfilt(butter(2, fc, btype="low", fs=SR, output="sos"), seg, axis=1)
        place(out, seg * env * g, t - (0.03 if legato_in else 0.0))
    return out


def render_simple(notes, S, L, total, layer_fn, ref_layer, att=0.003, rel=0.25, pedal=None, rel_fn=None):
    out = np.zeros((2, total), np.float32)
    ped = sorted(pedal) if pedal else None
    for t, d, m, v, flag in notes:
        layer = layer_fn(v, flag)
        s, sh = pick(S, m, layer)
        y = pitched(S, (s, layer), sh)
        off = d
        if ped:
            nx = next((p for p in ped if p > t + 0.05), t + d + 3)
            off = max(d, nx - t + 0.03)
        r = rel_fn(m) if rel_fn else rel
        Ln = min(y.shape[1], int((off + r * 4) * SR))
        tt = np.arange(Ln) / SR
        env = np.clip(tt / att, 0, 1)
        k = int(off * SR)
        if k < Ln:
            env[k:] *= np.exp(-(tt[k:] - off) / r)
        g = 10 ** ((L[(s, ref_layer)] - L[(s, layer)] + 0.28 * (v - 64)) / 20)
        place(out, y[:, :Ln] * env * g, t)
    return out


def rms_db(x):
    e = np.mean(x ** 2, axis=0)
    fr = e[: len(e) // 4410 * 4410].reshape(-1, 4410).mean(1)
    act = fr[fr > 10 ** (-60 / 10) * fr.max()]
    return 10 * np.log10(np.mean(act) + 1e-12)


def reverb(x, rt60=3.1, seed=5):
    rng = np.random.default_rng(seed)
    nn = int(rt60 * 1.15 * SR)
    t = np.arange(nn) / SR
    sos = butter(2, 5000, btype="low", fs=SR, output="sos")
    y = np.zeros_like(x)
    for ch in range(2):
        ir = sosfilt(sos, rng.standard_normal(nn)) * np.exp(-6.9 * t / rt60)
        pd = int(0.03 * SR)
        ir[:pd] = 0
        ir[pd: pd + int(0.04 * SR)] *= np.linspace(0, 1, int(0.04 * SR))
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        y[ch] = oaconvolve(x[ch], ir)[: x.shape[1]]
    return y


def write_midi(midi_ev, tempo, pedal, path):
    import mido
    mf = mido.MidiFile(ticks_per_beat=480)
    names = ["Violin", "Piano", "Strings"]
    progs = [40, 0, 48]
    for tr_i in range(3):
        tr = mido.MidiTrack(); mf.tracks.append(tr)
        tr.append(mido.MetaMessage("track_name", name=names[tr_i], time=0))
        ev = [(0, 0, mido.Message("program_change", program=progs[tr_i], channel=tr_i))]
        if tr_i == 0:
            ev += [(tk, 0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(b))) for tk, b in tempo]
            ev += [(0, 0, mido.MetaMessage("time_signature", numerator=3, denominator=4)),
                   (0, 0, mido.MetaMessage("key_signature", key="Bm"))]
        if tr_i == 1:
            for _, tk in pedal:
                ev.append((max(0, tk - 10), 1, mido.Message("control_change", control=64, value=0, channel=1)))
                ev.append((tk + 40, 2, mido.Message("control_change", control=64, value=127, channel=1)))
        for ti, tk, dtk, m, v in midi_ev:
            if (ti if ti < 2 else 2) != tr_i:
                continue
            tk = max(0, tk)
            ev.append((tk, 3, mido.Message("note_on", note=m, velocity=v, channel=tr_i)))
            ev.append((tk + max(20, dtk - 10), 0, mido.Message("note_off", note=m, velocity=0, channel=tr_i)))
        ev.sort(key=lambda e: (e[0], e[1]))
        last = 0
        for tk, _, msg in ev:
            msg.time = tk - last; last = tk; tr.append(msg)
    mf.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vsco", required=True)
    ap.add_argument("--ra", required=True)
    ap.add_argument("--ten", default="xuong-violin-thuong-nho")
    ap.add_argument("--hat", type=int, default=1)
    a = ap.parse_args()
    os.makedirs(a.ra, exist_ok=True)
    V = a.vsco
    VI, o1 = load_set(os.path.join(V, "Strings/Solo Violin/Arco Vib"),
                      r"LLVln_ArcoVib_(?P<nn>[A-G]#?)(?P<oct>\d)_(?P<l>[pf])\.wav", lambda g: g["l"])
    VN, o2 = load_set(os.path.join(V, "Strings/Violin Section/susVib"),
                      r"VlnEns_susVib_(?P<nn>[A-G]#?)(?P<oct>\d)_v(?P<l>\d)\.wav", lambda g: int(g["l"]))
    VA, o3 = load_set(os.path.join(V, "Strings/Viola Section/susvib"),
                      r"ViolaEns_susvib_(?P<nn>[A-G]#?)(?P<oct>\d)_v(?P<l>\d)_1\.wav", lambda g: int(g["l"]))
    VC, o4 = load_set(os.path.join(V, "Strings/Cello Section/susvib"),
                      r"susvib_(?P<nn>[A-G]#?)(?P<oct>\d)_v(?P<l>\d)_1\.wav", lambda g: int(g["l"]))
    PI, o5 = load_set(os.path.join(V, "Keys/Upright Piano"), r"Player_dyn(?P<l>\d)_rr1_(?P<i>\d{3})\.wav",
                      lambda g: int(g["l"]))
    print("lệch quãng tám theo tên file:", dict(violin=o1, vln_ens=o2, viola=o3, cello=o4, piano=o5))
    vio, pia, pad, ens, marks, tempo, pedal, end, midi_ev = build(a.hat)
    total = int((end + 10) * SR)
    LV, LN, LA, LC, LP = levels(VI, .3, 1.5), levels(VN, .4, 1.6), levels(VA, .4, 1.6), levels(VC, .4, 1.6), levels(PI, 0, .6)

    bus_v = render_violin(vio, VI, LV, total)
    bus_p = render_simple(pia, PI, LP, total, lambda v, f: 1 if v < 46 else (2 if v < 66 else 3), 2,
                          pedal=[p[0] for p in pedal], rel_fn=lambda m: 0.25 if m < 50 else 0.15)
    pad_vc = [x for x in pad if x[4] == "vc"]
    pad_va = [x for x in pad if x[4] == "va"]
    pad_vn = [x for x in pad if x[4] == "vn"]
    padbus = (render_simple(pad_vc, VC, LC, total, lambda v, f: 1 if v < 66 else 3, 1, att=0.6, rel=0.7)
              + render_simple(pad_va, VA, LA, total, lambda v, f: 1 if v < 66 else 2, 1, att=0.6, rel=0.7)
              + render_simple(pad_vn, VN, LN, total, lambda v, f: 1 if v < 66 else 2, 1, att=0.7, rel=0.7))
    bus_e = render_simple(ens, VN, LN, total, lambda v, f: 1 if v < 70 else 2, 1, att=0.12, rel=0.35)

    def norm(x, db):
        return x * 10 ** ((db - rms_db(x)) / 20)

    bus_v = norm(bus_v, -17.0)
    bus_p = norm(bus_p, -24.0)
    padbus = norm(padbus, -26.5)
    bus_e = norm(bus_e, -25.0)
    lp = butter(2, 9000, btype="low", fs=SR, output="sos")
    bus_v = sosfilt(lp, bus_v, axis=1)
    dry = bus_v + bus_p + padbus + bus_e
    send = 0.34 * bus_v + 0.24 * bus_p + 0.38 * padbus + 0.38 * bus_e
    x = dry + 0.55 * reverb(send)
    hp = butter(2, 30, btype="high", fs=SR, output="sos")
    x = sosfilt(hp, x, axis=1)
    e = int((end + 5.5) * SR)
    x = x[:, :e]
    f = int(3.0 * SR)
    x[:, -f:] *= np.linspace(1, 0, f) ** 2
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.7
    wav = os.path.join(a.ra, a.ten + "_tho.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x.T, -1, 1) * 32767).astype("<i2").tobytes())
    write_midi(midi_ev, tempo, pedal, os.path.join(a.ra, a.ten + ".mid"))
    json.dump({"moc": marks, "dai": round(e / SR, 2)}, open(os.path.join(a.ra, a.ten + "_moc.json"), "w"),
              ensure_ascii=False, indent=1)
    print("xong", wav, round(e / SR, 1), "giây")
    for k, v in marks:
        print(f"  {k:12s} {int(v // 60)}:{v % 60:05.2f}")


if __name__ == "__main__":
    main()
