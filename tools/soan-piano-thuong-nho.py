#!/usr/bin/env python3
"""Bản piano độc tấu "Thương nhớ": giai điệu của bản violin cùng tên, soạn lại cho piano.

Dùng chung bộ phát mẫu Salamander của tools/soan-piano-mau.py và dữ liệu giai điệu, hoà âm
của tools/soan-violin-mau.py (hai file phải nằm cùng thư mục với file này).
  python3 soan-piano-thuong-nho.py --mau <thư mục mẫu Salamander> --ra <thư mục> [--hat 1]
Tiếng đàn: Salamander Grand Piano V3, Alexander Holm, CC BY 3.0 (phải ghi công khi dùng MP3).
"""
import argparse, importlib.util, os, json, wave
import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


P = _load("piano_mau", "soan-piano-mau.py")      # bộ phát Salamander
V = _load("violin_mau", "soan-violin-mau.py")    # giai điệu, hoà âm
SR = P.SR
n = V.n

# tay trái piano: dùng chung thế bấm của bản violin
LH = dict(V.PIANO_V)
CT = {k: {x % 12 for x in v} for k, v in V.PIANO_V.items()}

up12 = lambda mel: [[(b, d, x[:-1] + str(int(x[-1]) + 1), g) for b, d, x, g in bar] for bar in mel]
INTRO_MEL = [[]] * 4 + up12(V.A_MEL[12:16])

# tên, hợp âm, giai điệu, kiểu tay trái, lực phải, lực trái, nhịp độ, cao trào (quãng tám + hoà âm)
SECTIONS = [
    ("mo-dau", V.INTRO_CH, INTRO_MEL, "thua", 40, 33, [56] * 7 + [52], False),
    ("A", V.A_CH, V.A_MEL, "chay", 54, 39, [58, 58, 58, 55] * 3 + [58, 58, 57, 53], False),
    ("B", V.B_CH, V.B_MEL, "chay", 64, 46, [60, 60, 60, 57] * 3 + [60, 59, 56, 54], False),
    ("nghi", V.BRIDGE_CH, [[]] * 4, "thua", 44, 36, [56, 56, 55, 52], False),
    ("A-cao-trao", V.A_CH, up12(V.A_MEL), "day", 74, 52, [60, 60, 60, 57] * 3 + [59, 58, 56, 52], True),
    ("ket", V.OUT_CH, V.OUT_MEL, "thua", 46, 34, [54, 53, 52, 50, 48, 46, 44, 42], False),
]


def build(seed=1):
    rng = np.random.default_rng(seed)
    notes, pedal, tempo, marks = [], [], [], []
    t0, tick0, PPQ = 0.0, 0, 480

    def add(t, d, m, v, hand, tk, dtk, jit=0.006):
        v = int(np.clip(v + rng.normal(0, 2.5), 16, 118))
        notes.append((max(0.0, t + rng.normal(0, jit)), d, m, v, hand, tk, dtk))

    for name, chs, mels, lh, rv, lv, bpms, climax in SECTIONS:
        marks.append((name, round(t0, 2)))
        nb = len(chs)
        for bi, (ch, mel, bpm) in enumerate(zip(chs, mels, bpms)):
            spb = 60 / bpm
            tempo.append((tick0, bpm))
            arc = 1 + 0.08 * np.sin(np.pi * (bi + 0.5) / nb)
            for ci, (cb, cn) in enumerate(ch):
                ce = ch[ci + 1][0] if ci + 1 < len(ch) else 3
                vo = LH[cn]
                pedal.append((t0 + cb * spb, tick0 + int(cb * PPQ)))
                span = ce - cb
                if lh == "thua":
                    pat = [(0, 0), (.5, 1), (1, 2), (2, 3)] if span == 3 else ([(0, 0), (.5, 1), (1, 2)] if span == 2 else [(0, 0)])
                    dur = lambda b: span - b
                elif lh == "chay":
                    seq = [0, 1, 2, 3, 2, 1] if span == 3 else ([0, 1, 2, 3] if span == 2 else [0, 2])
                    pat = [(0.5 * k, i) for k, i in enumerate(seq)]
                    dur = lambda b: 0.5
                else:
                    seq = [0, 1, 2, 3, 4, 3] if span == 3 else ([0, 1, 2, 4] if span == 2 else [0, 2])
                    pat = [(0.5 * k, i) for k, i in enumerate(seq)]
                    dur = lambda b: 0.5
                    if vo[0] - 12 >= 21:
                        add(t0 + cb * spb, span * spb, vo[0] - 12, lv * arc - 2, "L", tick0 + int(cb * PPQ), int(span * PPQ))
                for k, (b, idx) in enumerate(pat):
                    bb = cb + b
                    acc = 6 if k == 0 else (-2 if k % 2 else 1)
                    add(t0 + bb * spb, dur(b) * spb, vo[idx], lv * arc + acc, "L", tick0 + int(bb * PPQ), int(dur(b) * PPQ))
            for b, d, x, g in mel:
                m = n(x)
                c = [cn for cb, cn in ch if cb <= b][-1]
                t = t0 + b * spb + 0.014
                v = rv * arc * (1.07 if d >= 2 else 1.0)
                if g and d >= 2:
                    # láy nhẹ: nốt bậc trên chạm rất nhanh rồi vào nốt chính
                    up = next(k for k in range(m + 1, m + 3) if k % 12 in (11, 1, 2, 4, 6, 7, 9))
                    add(t - 0.075, 0.07, up, v * 0.7, "R", tick0 + int(b * PPQ) - 40, 40, jit=0.002)
                add(t, d * spb, m, v, "R", tick0 + int(b * PPQ), int(d * PPQ))
                if climax:
                    add(t + 0.006, d * spb, m - 12, v * 0.74, "R", tick0 + int(b * PPQ), int(d * PPQ))
                    if d >= 1 and b in (0, 1, 2):
                        # nốt hoà âm thấp nhất trong hợp âm, nằm giữa hai quãng tám
                        inner = [k for k in range(m - 11, m - 2) if k % 12 in CT[c]]
                        if inner:
                            add(t + 0.01, d * spb, inner[-1], v * 0.6, "R", tick0 + int(b * PPQ), int(d * PPQ))
            t0 += 3 * spb
            tick0 += 3 * PPQ
    # hợp âm kết Si thứ thêm bậc 9, rải chậm từ trầm lên
    bpm, spb = 42, 60 / 42
    tempo.append((tick0, bpm))
    marks.append(("hop-am-ket", round(t0, 2)))
    pedal.append((t0, tick0))
    for k, m in enumerate([23, 35, 42, 50, 54]):
        add(t0 + k * 0.13, 6 * spb, m, 40 - k, "L", tick0 + k * 40, 6 * PPQ, jit=0.002)
    for k, m in enumerate([61, 66, 71, 73, 78]):
        add(t0 + 0.8 + k * 0.15, 6 * spb, m, 36 + (5 if k == 4 else 0), "R", tick0 + 900 + k * 45, 6 * PPQ - 900, jit=0.002)
    t_end = t0 + 6 * spb
    pedal.append((t_end + 3.0, tick0 + 6 * PPQ))
    return notes, pedal, tempo, marks, t_end


def write_midi(notes, pedal, tempo, path):
    import mido
    mf = mido.MidiFile(ticks_per_beat=480)
    for name, hand in (("Tay phai", "R"), ("Tay trai", "L")):
        tr = mido.MidiTrack(); mf.tracks.append(tr)
        tr.append(mido.MetaMessage("track_name", name=name, time=0))
        ev = []
        if hand == "R":
            ev += [(tk, 0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(b))) for tk, b in tempo]
            ev += [(0, 0, mido.MetaMessage("time_signature", numerator=3, denominator=4)),
                   (0, 0, mido.MetaMessage("key_signature", key="Bm"))]
        else:
            for _, tk in pedal:
                ev.append((max(0, tk - 10), 1, mido.Message("control_change", control=64, value=0)))
                ev.append((tk + 40, 2, mido.Message("control_change", control=64, value=127)))
        for t, d, m, v, h, tk, dtk in notes:
            if h == hand:
                tk = max(0, tk)
                ev.append((tk, 3, mido.Message("note_on", note=m, velocity=v)))
                ev.append((tk + max(30, dtk - 20), 0, mido.Message("note_off", note=m, velocity=0)))
        ev.sort(key=lambda e: (e[0], e[1]))
        last = 0
        for tk, _, msg in ev:
            msg.time = tk - last; last = tk; tr.append(msg)
    mf.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mau", required=True)
    ap.add_argument("--ra", required=True)
    ap.add_argument("--ten", default="xuong-piano-thuong-nho")
    ap.add_argument("--hat", type=int, default=1)
    a = ap.parse_args()
    os.makedirs(a.ra, exist_ok=True)
    notes, pedal, tempo, marks, t_end = build(a.hat)
    S = P.load_samples(a.mau)
    x = P.render(notes, pedal, t_end, S)
    hp = butter(2, 30, btype="high", fs=SR, output="sos")
    lp = butter(1, 9500, btype="low", fs=SR, output="sos")
    x = sosfilt(lp, sosfilt(hp, x, axis=1), axis=1).astype(np.float32)
    x = P.reverb(x, rt60=2.9, wet=0.27)
    end = int((t_end + 5.0) * SR)
    x = x[:, :end]
    f = int(3.0 * SR)
    x[:, -f:] *= np.linspace(1, 0, f) ** 2
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.7
    wav = os.path.join(a.ra, a.ten + "_tho.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x.T, -1, 1) * 32767).astype("<i2").tobytes())
    write_midi(notes, pedal, tempo, os.path.join(a.ra, a.ten + ".mid"))
    json.dump({"moc": marks, "dai": round(end / SR, 2)}, open(os.path.join(a.ra, a.ten + "_moc.json"), "w"),
              ensure_ascii=False, indent=1)
    print("xong", wav, round(end / SR, 1), "giây,", len(notes), "nốt")
    for k, v in marks:
        print(f"  {k:12s} {int(v // 60)}:{v % 60:05.2f}")


if __name__ == "__main__":
    main()
