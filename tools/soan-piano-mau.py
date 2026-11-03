#!/usr/bin/env python3
"""Soạn bản piano nguyên bản bằng mẫu tiếng đàn thật (Salamander Grand Piano V3).

Bản nhạc (giai điệu, hoà âm, cấu trúc) do xưởng viết mới. Tiếng đàn lấy từ bộ mẫu
Salamander Grand Piano V3 của Alexander Holm (CC BY 3.0): mỗi mẫu là một nốt đơn lẻ,
không phải bản thu nhạc của ai, nên không có dấu vân âm thanh để Content ID so khớp.
Dùng bản MP3 này phải ghi công tiếng đàn; dùng file MIDI để tự phát bằng đàn khác
(GarageBand, Logic) thì không cần ghi công.

Dùng:
  python3 soan-piano-mau.py --mau <thư mục mẫu mp3> --ra <thư mục> [--hat 1]
Cần: numpy, scipy, mido, ffmpeg. Mẫu: npm pack @audio-samples/piano-mp3-velocity{4,8,12}
"""
import argparse, os, re, subprocess, json
import numpy as np
from scipy.signal import resample_poly, oaconvolve, butter, sosfilt

SR = 44100
PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def n(s):
    m = re.fullmatch(r"([A-G]#?)(-?\d)", s)
    return 12 * (int(m.group(2)) + 1) + PC[m.group(1)]


# ---------------------------------------------------------------- bản nhạc
# Tay trái: mỗi hợp âm là 5 nốt xếp từ trầm lên, rải theo móc đơn.
V = {
    "E":     [40, 47, 52, 54, 56],      # E2 B2 E3 F#3 G#3 (thêm bậc 9)
    "B/D#":  [39, 42, 47, 49, 51],      # D#2 F#2 B2 C#3 D#3
    "C#m7":  [37, 44, 49, 52, 59],      # C#2 G#2 C#3 E3 B3
    "G#m/B": [35, 44, 47, 51, 54],      # B1 G#2 B2 D#3 F#3
    "A7M":   [45, 52, 56, 59, 61],      # A2 E3 G#3 B3 C#4
    "E/G#":  [44, 47, 52, 54, 56],      # G#2 B2 E3 F#3 G#3
    "F#m7":  [42, 49, 52, 56, 57],      # F#2 C#3 E3 G#3 A3
    "B7sus": [35, 47, 52, 54, 57],      # B1 B2 E3 F#3 A3
    "B7":    [35, 47, 51, 54, 57],      # B1 B2 D#3 F#3 A3
    "B6":    [35, 47, 54, 56, 63],      # B1 B2 F#3 G#3 D#4
    "G#m7":  [44, 51, 54, 56, 59],      # G#2 D#3 F#3 G#3 B3
    "Am6":   [45, 52, 54, 57, 60],      # A2 E3 F#3 A3 C4 (mượn từ giọng thứ)
}


def M(*xs):
    return [(b, d, x) for b, d, x in xs]


INTRO = [
    ([(0, "A7M")], M((0, 1.5, "G#5"), (1.5, .5, "B5"), (2, 2, "C#6"))),
    ([(0, "B6")], M((0, 1.5, "B5"), (1.5, .5, "A5"), (2, 1, "G#5"), (3, 1, "F#5"))),
    ([(0, "G#m7"), (2, "C#m7")], M((0, 2, "D#5"), (2, 1, "E5"), (3, 1, "G#5"))),
    ([(0, "F#m7"), (2, "B7sus")], M((0, 1.5, "A5"), (1.5, .5, "G#5"), (2, 2, "F#5"))),
]
A1 = [
    ([(0, "E")], M((1, .5, "B4"), (1.5, .5, "E5"), (2, 1.5, "G#5"), (3.5, .5, "F#5"))),
    ([(0, "B/D#")], M((0, 1, "F#5"), (1, .5, "E5"), (1.5, 1, "D#5"), (2.5, .5, "E5"), (3, 1, "F#5"))),
    ([(0, "C#m7")], M((0, 1.5, "E5"), (1.5, .5, "C#5"), (2, 2, "B4"))),
    ([(0, "G#m/B")], M((1, .5, "G#4"), (1.5, .5, "B4"), (2, 2, "D#5"))),
    ([(0, "A7M")], M((0, .5, "E5"), (.5, .5, "F#5"), (1, 2, "G#5"), (3, .5, "F#5"), (3.5, .5, "E5"))),
    ([(0, "E/G#")], M((0, 2, "E5"), (2, .5, "D#5"), (2.5, .5, "E5"), (3, 1, "F#5"))),
    ([(0, "F#m7")], M((0, 1.5, "A5"), (1.5, .5, "G#5"), (2, 1, "F#5"), (3, 1, "C#5"))),
    ([(0, "B7sus"), (2, "B7")], M((0, 2, "E5"), (2, 2, "D#5"))),
]
A2 = [
    ([(0, "E")], M((1, .5, "B4"), (1.5, .5, "E5"), (2, 1.5, "G#5"), (3.5, .5, "B5"))),
    ([(0, "B/D#")], M((0, 1.5, "A5"), (1.5, .5, "G#5"), (2, 1, "F#5"), (3, 1, "D#5"))),
    ([(0, "C#m7")], M((0, 1, "E5"), (1, .5, "G#5"), (1.5, 1.5, "C#6"), (3, .5, "B5"), (3.5, .5, "G#5"))),
    ([(0, "G#m/B")], M((0, 2, "F#5"), (2, .5, "E5"), (2.5, .5, "D#5"), (3, 1, "B4"))),
    ([(0, "A7M")], M((0, .5, "C#5"), (.5, .5, "E5"), (1, 1.5, "A5"), (2.5, .5, "G#5"), (3, 1, "E5"))),
    ([(0, "E/G#")], M((0, 1, "F#5"), (1, 1, "G#5"), (2, 2, "B5"))),
    ([(0, "F#m7"), (2, "B7")], M((0, 1.5, "C#6"), (1.5, .5, "B5"), (2, 1, "A5"), (3, 1, "F#5"))),
    ([(0, "E")], M((0, 4, "G#5"), (0, 4, "E5"))),
]
B = [
    ([(0, "A7M")], M((0, .5, "G#5"), (.5, .5, "A5"), (1, 2, "B5"), (3, .5, "C#6"), (3.5, .5, "B5"))),
    ([(0, "B6")], M((0, 2, "G#5"), (2, .5, "F#5"), (2.5, .5, "G#5"), (3, 1, "B5"))),
    ([(0, "G#m7")], M((0, 1.5, "D#6"), (1.5, .5, "C#6"), (2, 2, "B5"))),
    ([(0, "C#m7")], M((0, 1, "C#6"), (1, .5, "B5"), (1.5, 1.5, "G#5"), (3, .5, "E5"), (3.5, .5, "F#5"))),
    ([(0, "F#m7")], M((0, 1.5, "A5"), (1.5, .5, "G#5"), (2, 1, "F#5"), (3, .5, "E5"), (3.5, .5, "F#5"))),
    ([(0, "G#m7")], M((0, 1.5, "B5"), (1.5, .5, "C#6"), (2, 2, "D#6"))),
    ([(0, "A7M")], M((0, 2, "E6"), (2, .5, "C#6"), (2.5, .5, "B5"), (3, 1, "C#6"))),
    ([(0, "B7sus"), (2, "B7")], M((0, 1.5, "B5"), (1.5, .5, "A5"), (2, 2, "F#5"))),
]
INTER = [
    ([(0, "C#m7")], M((0, 1.5, "G#5"), (1.5, .5, "B5"), (2, 2, "E6"))),
    ([(0, "A7M")], M((0, 1.5, "C#6"), (1.5, .5, "B5"), (2, 2, "G#5"))),
    ([(0, "F#m7")], M((0, 1.5, "A5"), (1.5, .5, "G#5"), (2, 1, "F#5"), (3, 1, "C#5"))),
    ([(0, "B7sus")], M((0, 4, "E5"))),
]
A3 = A1[:7] + [([(0, "F#m7"), (2, "B7")], A1[7][1])]
OUTRO = [
    ([(0, "E")], M((0, 1.5, "G#5"), (1.5, .5, "B5"), (2, 2, "E6"))),
    ([(0, "A7M")], M((0, 1.5, "C#6"), (1.5, .5, "B5"), (2, 2, "G#5"))),
    ([(0, "Am6")], M((0, 1.5, "C6"), (1.5, .5, "B5"), (2, 2, "A5"))),
    ([(0, "E/G#")], M((0, 2, "G#5"), (2, 2, "E5"))),
    ([(0, "F#m7"), (2, "B7sus")], M((0, 1.5, "A5"), (1.5, .5, "G#5"), (2, 2, "F#5"))),
]

# (tên đoạn, các ô nhịp, kiểu tay trái, lực tay phải, lực tay trái, nhịp độ, nhân đôi quãng tám)
SECTIONS = [
    ("intro", INTRO, "thua", 46, 36, [62, 62, 62, 60], False),
    ("A1", A1, "chay", 56, 42, [64] * 8, False),
    ("A2", A2, "chay", 60, 45, [64] * 7 + [62], False),
    ("B", B, "chay", 72, 52, [64] * 8, False),
    ("giaoduyen", INTER, "thua", 50, 38, [62, 62, 62, 60], False),
    ("A3", A3, "chay", 62, 46, [64] * 8, True),
    ("B2", B, "day", 80, 58, [65] * 7 + [62], True),
    ("ket", OUTRO, "thua", 52, 40, [60, 58, 55, 52, 50], False),
]


def build(seed=1):
    rng = np.random.default_rng(seed)
    notes = []      # (t_giây, dài_giây, midi, lực, tay, tick, dài_tick)
    pedal = []      # thời điểm đổi pedal (giây, tick)
    tempo = []      # (tick, bpm)
    marks = []
    t0, tick0 = 0.0, 0
    PPQ = 480

    def add(t, d, m, v, hand, tk, dtk, jit=0.006):
        v = int(np.clip(v + rng.normal(0, 2.5), 18, 118))
        notes.append((max(0.0, t + rng.normal(0, jit)), d, m, v, hand, tk, dtk))

    for name, bars, lh, rv, lv, bpms, octv in SECTIONS:
        marks.append((name, t0))
        nb = len(bars)
        for bi, ((chords, mel), bpm) in enumerate(zip(bars, bpms)):
            spb = 60.0 / bpm
            tempo.append((tick0, bpm))
            arc = 1.0 + 0.08 * np.sin(np.pi * (bi + 0.5) / nb)   # vòm cường độ trong đoạn
            # tay trái
            for ci, (cb, cname) in enumerate(chords):
                ce = chords[ci + 1][0] if ci + 1 < len(chords) else 4
                vo = V[cname]
                pedal.append((t0 + cb * spb, tick0 + int(cb * PPQ)))
                if lh == "thua":
                    pat = [(0, 0), (1, 2), (2, 4), (3, 3)] if ce - cb == 4 else [(0, 0), (1, 3)]
                    for k, (b, idx) in enumerate(pat):
                        bb = cb + b
                        add(t0 + bb * spb, (ce - bb) * spb, vo[idx], lv * arc + (5 if k == 0 else -2), "L",
                            tick0 + int(bb * PPQ), int((ce - bb) * PPQ))
                else:
                    idxs = [0, 1, 2, 3, 4, 3, 2, 1] if ce - cb == 4 else [0, 2, 3, 4]
                    for k, idx in enumerate(idxs):
                        bb = cb + 0.5 * k
                        acc = 7 if k == 0 else (2 if k % 2 == 0 else -3)
                        add(t0 + bb * spb, 0.5 * spb, vo[idx], lv * arc + acc, "L",
                            tick0 + int(bb * PPQ), int(0.5 * PPQ))
                    if lh == "day" and vo[0] - 12 >= 28:
                        add(t0 + cb * spb, (ce - cb) * spb, vo[0] - 12, lv * arc + 2, "L",
                            tick0 + int(cb * PPQ), int((ce - cb) * PPQ))
            # tay phải
            for b, d, x in mel:
                m = n(x)
                v = rv * arc * (1.06 if d >= 1.5 else 1.0) * (0.8 if (b, d) == (0, 4) and x == "E5" and name == "A2" else 1.0)
                lag = 0.012  # giai điệu trễ nhẹ sau tay trái, như người đàn thật
                add(t0 + b * spb + lag, d * spb, m, v, "R", tick0 + int(b * PPQ), int(d * PPQ))
                if octv and m - 12 >= 55:
                    add(t0 + b * spb + lag + 0.008, d * spb, m - 12, v * 0.72, "R",
                        tick0 + int(b * PPQ), int(d * PPQ))
            t0 += 4 * spb
            tick0 += 4 * PPQ

    # hợp âm kết: rải chậm từ trầm lên, ngân hai ô nhịp
    bpm = 48
    spb = 60.0 / bpm
    tempo.append((tick0, bpm))
    marks.append(("hop-am-ket", t0))
    pedal.append((t0, tick0))
    final_l = [28, 40, 47, 54, 56, 59]
    final_r = ["B4", "E5", "F#5", "G#5", "B5", "E6"]
    for k, m in enumerate(final_l):
        add(t0 + k * 0.11, 8 * spb, m, 44 - k * 2, "L", tick0 + k * 30, 8 * PPQ, jit=0.002)
    for k, x in enumerate(final_r):
        add(t0 + 0.7 + k * 0.12, 8 * spb, n(x), 40 + (6 if x == "E6" else 0), "R",
            tick0 + 720 + k * 34, 8 * PPQ - 720, jit=0.002)
    t_end = t0 + 8 * spb
    pedal.append((t_end + 3.0, tick0 + 8 * PPQ))
    return notes, pedal, tempo, marks, t_end


# ---------------------------------------------------------------- bộ phát mẫu

LAYERS = [(4, 38.0), (8, 64.0), (12, 92.0)]


def load_samples(d):
    S = {}
    for f in os.listdir(d):
        m = re.fullmatch(r"([A-G]#?)(\d)v(\d+)\.mp3", f)
        if not m:
            continue
        midi = 12 * (int(m.group(2)) + 1) + PC[m.group(1)]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(d, f), "-f", "f32le", "-ac", "2",
                              "-ar", str(SR), "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()
        S[(midi, int(m.group(3)))] = x
    return S


_cache = {}


def pitched(S, s, layer, shift):
    key = (s, layer, shift)
    if key not in _cache:
        x = S[(s, layer)]
        if shift == 0:
            y = x
        elif shift == 1:
            y = resample_poly(x, 84, 89, axis=1)
        elif shift == -1:
            y = resample_poly(x, 89, 84, axis=1)
        else:
            r = 2 ** (shift / 12)
            idx = np.arange(0, x.shape[1] - 1, r)
            y = np.stack([np.interp(idx, np.arange(x.shape[1]), x[c]) for c in range(2)])
        _cache[key] = y.astype(np.float32)
    return _cache[key]


LEVEL = {}


def render(notes, pedal, t_end, S):
    if not LEVEL:
        for k, x in S.items():
            LEVEL[k] = 10 * np.log10(np.mean(x[:, : int(0.4 * SR)] ** 2) + 1e-12)
    avail = sorted({k[0] for k in S})
    total = int((t_end + 9) * SR)
    out = np.zeros((2, total), np.float32)
    ped = sorted(p[0] for p in pedal)
    for t, d, m, v, hand, *_ in notes:
        s = min(avail, key=lambda a: (abs(a - m), a))
        shift = m - s
        # phần buông phím: phím vẫn được giữ hết độ dài nốt, pedal giữ tới lần đổi kế tiếp
        nxt = next((p for p in ped if p > t + 0.05), t + d + 4)
        off = max(t + d, nxt + 0.04)
        rel = 0.22 if m < 52 else (0.14 if m < 76 else 0.35)
        # một lớp mẫu theo lực (trộn hai lớp bị triệt pha), mức cân theo lớp giữa
        layer = 4 if v < 50 else (8 if v < 78 else 12)
        ref = LEVEL[(s, 8)]
        g_db = ref - LEVEL[(s, layer)] + 0.26 * (v - 64)
        ws = [(layer, 1.0, None)]
        i0 = int(t * SR)
        for layer, w, c in ws:
            if w <= 0.001:
                continue
            y = pitched(S, s, layer, shift)
            L = min(y.shape[1], int((off - t + rel * 5) * SR))
            env = np.ones(L, np.float32)
            k = int((off - t) * SR)
            if k < L:
                tt = np.arange(L - k) / SR
                env[k:] = np.exp(-tt / rel)
            g = 10 ** (g_db / 20)
            seg = y[:, :L] * env * g
            j = min(i0 + L, total)
            out[:, i0:j] += seg[:, : j - i0]
    return out


def reverb(x, rt60=2.4, wet=0.22, seed=11):
    rng = np.random.default_rng(seed)
    nn = int(rt60 * 1.15 * SR)
    t = np.arange(nn) / SR
    sos = butter(2, 5600, btype="low", fs=SR, output="sos")
    y = x.copy()
    for ch in range(2):
        ir = rng.standard_normal(nn) * np.exp(-6.9 * t / rt60)
        ir = sosfilt(sos, ir)
        pd = int(0.024 * SR)
        ir[:pd] = 0
        ir[pd: pd + int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        y[ch] += wet * oaconvolve(x[ch], ir)[: x.shape[1]].astype(np.float32)
    return y


def write_midi(notes, pedal, tempo, path):
    import mido
    mf = mido.MidiFile(ticks_per_beat=480)
    for name, hand in (("Tay phai", "R"), ("Tay trai", "L")):
        tr = mido.MidiTrack()
        mf.tracks.append(tr)
        tr.append(mido.MetaMessage("track_name", name=name, time=0))
        ev = []
        if hand == "R":
            for tk, bpm in tempo:
                ev.append((tk, 0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))))
            ev.append((0, 0, mido.MetaMessage("time_signature", numerator=4, denominator=4)))
            ev.append((0, 0, mido.MetaMessage("key_signature", key="E")))
        else:
            for _, tk in pedal:
                ev.append((max(0, tk - 10), 1, mido.Message("control_change", control=64, value=0)))
                ev.append((tk + 40, 2, mido.Message("control_change", control=64, value=127)))
        for t, d, m, v, h, tk, dtk in notes:
            if h != hand:
                continue
            ev.append((tk, 3, mido.Message("note_on", note=m, velocity=v)))
            ev.append((tk + max(30, dtk - 20), 0, mido.Message("note_off", note=m, velocity=0)))
        ev.sort(key=lambda e: (e[0], e[1]))
        last = 0
        for tk, _, msg in ev:
            msg.time = tk - last
            last = tk
            tr.append(msg)
    mf.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mau", required=True)
    ap.add_argument("--ra", required=True)
    ap.add_argument("--ten", default="xuong-piano-ngay-xuan")
    ap.add_argument("--hat", type=int, default=1)
    a = ap.parse_args()
    os.makedirs(a.ra, exist_ok=True)
    notes, pedal, tempo, marks, t_end = build(a.hat)
    S = load_samples(a.mau)
    x = render(notes, pedal, t_end, S)
    hp = butter(2, 32, btype="high", fs=SR, output="sos")
    lp = butter(1, 10500, btype="low", fs=SR, output="sos")
    x = sosfilt(lp, sosfilt(hp, x, axis=1), axis=1).astype(np.float32)
    x = reverb(x)
    # cắt đuôi, mờ dần 2,5 giây cuối
    end = int((t_end + 4.5) * SR)
    x = x[:, :end]
    f = int(2.5 * SR)
    x[:, -f:] *= np.linspace(1, 0, f) ** 2
    x /= np.max(np.abs(x)) + 1e-9
    x *= 0.7
    wav = os.path.join(a.ra, a.ten + "_tho.wav")
    import wave
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x.T, -1, 1) * 32767).astype("<i2").tobytes())
    write_midi(notes, pedal, tempo, os.path.join(a.ra, a.ten + ".mid"))
    json.dump({"moc": [(k, round(v, 2)) for k, v in marks], "dai": round(end / SR, 2), "so_not": len(notes)},
              open(os.path.join(a.ra, a.ten + "_moc.json"), "w"), ensure_ascii=False, indent=1)
    print("xong", wav, round(end / SR, 1), "giây,", len(notes), "nốt")
    for k, v in marks:
        print(f"  {k:12s} {int(v // 60)}:{v % 60:05.2f}")


if __name__ == "__main__":
    main()
