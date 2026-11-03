#!/usr/bin/env python3
"""Bản piano độc tấu "Thiết tha" (xưởng tự soạn): ballad dịu dàng, bass đi xuống từng bậc,
hợp âm đệm nhẹ đều trên phách, giai điệu hát chậm.

Cảm hứng không khí từ ballad piano kiểu "Make You Feel My Love"; giai điệu, hoà âm cụ thể,
giọng (Rê giáng trưởng) và nhịp (70) đều mới.
Piano: Salamander Grand Piano V3 (Alexander Holm, CC BY 3.0, phải ghi công khi dùng MP3).
  python3 soan-piano-tha-thiet.py --mau <thư mục mẫu Salamander> --ra <thư mục>
Cần soan-piano-mau.py và soan-phuc-am.py (cùng các file nó cần) trong cùng thư mục.
"""
import argparse, importlib.util, os, json, wave
import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


P = _load("piano_mau", "soan-piano-mau.py")
G = _load("phuc_am", "soan-phuc-am.py")      # chord(), voice(), nm(), bass_note()
SR = P.SR
chord, voice, nm, bass_note = G.chord, G.voice, G.nm, G.bass_note

VERSE = [[(0, "Db"), (2, "Db/C")], [(0, "Bbm7"), (2, "Db/Ab")], [(0, "Gb"), (2, "Gbm6")], [(0, "Db/F"), (2, "Eb7")],
         [(0, "Gbmaj7"), (2, "F7")], [(0, "Bbm"), (2, "Bbm/Ab")], [(0, "Eb7/G"), (2, "Gbm6")],
         [(0, "Db/Ab"), (2, "Ab7sus"), (3, "Ab7")]]
A1 = [
    [(1, .5, "Ab4"), (1.5, .5, "Db5"), (2, 1.5, "F5"), (3.5, .5, "Eb5")],
    [(0, 1.5, "Db5"), (1.5, .5, "C5"), (2, 2, "Ab4")],
    [(0, .5, "Bb4"), (.5, .5, "Db5"), (1, 1.5, "Gb5"), (2.5, 1.5, "Eb5")],
    [(0, 1.5, "Db5"), (1.5, .5, "Eb5"), (2, 2, "G5")],
    [(0, 1, "Gb5"), (1, .5, "F5"), (1.5, .5, "Db5"), (2, 2, "Eb5")],
    [(0, 1.5, "Db5"), (1.5, .5, "C5"), (2, 1, "Bb4"), (3, 1, "F5")],
    [(0, 2, "Eb5"), (2, 2, "Db5")],
    [(0, 2, "F5"), (2, 1, "Eb5"), (3, 1, "C5")],
]
A2 = A1[:4] + [
    [(0, 1, "Bb5"), (1, .5, "Ab5"), (1.5, .5, "F5"), (2, 2, "A5")],
    [(0, 1.5, "Bb5"), (1.5, .5, "Ab5"), (2, 1, "F5"), (3, 1, "Db5")],
    [(0, 2, "Eb5"), (2, 1.5, "Db5"), (3.5, .5, "Eb5")],
    [(0, 3, "Db5"), (3, 1, "C5")],
]
BRIDGE = [[(0, "Gbmaj7"), (2, "Fm7")], [(0, "Ebm7"), (2, "Db")], [(0, "Gbmaj7"), (2, "Fm7")], [(0, "Bbm7"), (2, "Ab7sus")],
          [(0, "Gbmaj7"), (2, "Fm7")], [(0, "Ebm7"), (2, "Abm7"), (3, "Db7")], [(0, "Gbmaj7"), (2, "Gbm6")],
          [(0, "Db/Ab"), (2, "Ab7sus"), (3, "Ab7")]]
B = [
    [(0, 1.5, "Bb5"), (1.5, .5, "Ab5"), (2, 2, "C6")],
    [(0, 1.5, "Bb5"), (1.5, .5, "Gb5"), (2, 2, "F5")],
    [(0, 1.5, "Bb5"), (1.5, .5, "Ab5"), (2, 1, "C6"), (3, 1, "Ab5")],
    [(0, 4, "Db6")],
    [(0, 1, "Bb5"), (1, 1, "Db6"), (2, 1.5, "C6"), (3.5, .5, "Ab5")],
    [(0, 1.5, "Gb5"), (1.5, .5, "Bb5"), (2, 1, "Cb6"), (3, 1, "Ab5")],
    [(0, 2, "Bb5"), (2, 2, "A5")],
    [(0, 2, "Ab5"), (2, 1, "Gb5"), (3, 1, "F5")],
]
INTRO = VERSE[:3] + [[(0, "Db/Ab"), (2, "Ab7sus"), (3, "Ab7")]]
INTRO_MEL = [[(0, 2, "F5"), (2, 2, "Eb5")], [(0, 2, "Db5"), (2, 2, "C5")], [(0, 2, "Bb4"), (2, 2, "A4")],
             [(0, 2, "Ab4"), (2, 2, "Gb4")]]
OUTRO = [[(0, "Gb"), (2, "Gbm6")], [(0, "Db/F"), (2, "Bbm7")], [(0, "Ebm7"), (2, "Ab7sus")], [(0, "Dbadd9")], [(0, "Dbadd9")]]
OUT_MEL = [[(0, 2, "Bb5"), (2, 2, "A5")], [(0, 2, "Ab5"), (2, 1, "F5"), (3, 1, "Db5")],
           [(0, 2, "Gb5"), (2, 1, "F5"), (3, 1, "Eb5")], [(0, 4, "Db5")], []]

# tên, hợp âm, giai điệu, kiểu đệm, lực giai điệu, lực đệm, quãng tám giai điệu (+12/-12/0), nhịp
SECTIONS = [
    ("mo-dau", INTRO, INTRO_MEL, "rai", 56, 42, 0, [68, 68, 66, 62]),
    ("doan-1", VERSE, A1, "phach", 56, 39, 0, [70, 70, 70, 67, 70, 70, 70, 66]),
    ("doan-2", VERSE, A2, "phach-bass", 60, 42, 0, [70, 70, 70, 67, 70, 70, 70, 66]),
    ("diep-khuc", BRIDGE, B, "moc-don", 66, 46, 0, [71, 71, 71, 68, 71, 71, 70, 66]),
    ("doan-3", VERSE, A2, "phach-day", 70, 50, 12, [71, 71, 71, 68, 71, 71, 70, 66]),
    ("diep-khuc-lon", BRIDGE, B, "moc-don-day", 80, 56, -12, [72, 72, 72, 69, 72, 71, 69, 64]),
    ("lang", VERSE[:4], A1[:4], "rai", 55, 40, 0, [66, 66, 64, 60]),
    ("ket", OUTRO, OUT_MEL, "rai", 52, 39, 0, [60, 57, 53, 48, 44]),
]


def build(seed=9):
    rng = np.random.default_rng(seed)
    notes, pedal, marks = [], [], []
    t = 0.0
    prev = None
    hj = lambda s=1.0: rng.normal(0, 0.006 * s)
    vel = lambda v: int(np.clip(v + rng.normal(0, 2.5), 15, 118))

    def add(tt, d, m, v, h):
        notes.append((max(0.0, tt), d, m, vel(v), h, 0, 0))

    for name, chs, mels, style, mv, cv, octv, bpms in SECTIONS:
        marks.append((name, round(t, 2)))
        nb = len(chs)
        for bi, (ch, mel, bpm) in enumerate(zip(chs, mels, bpms)):
            sp = 60 / bpm
            arc = 1 + 0.07 * np.sin(np.pi * (bi + 0.5) / nb)
            if name == "ket" and bi == nb - 1:
                t += 4 * sp          # ô cuối: chỉ để hợp âm kết ngân
                continue
            ext = 4 if (name == "ket" and bi == nb - 2) else 0
            for ci, (cb, cn) in enumerate(ch):
                ce = ch[ci + 1][0] if ci + 1 < len(ch) else 4
                span = ce - cb + ext
                pcs, third, sev, bpc = chord(cn if cn != "Dbadd9" else "Db")
                if cn == "Dbadd9":
                    pcs = pcs + [3]
                tc = t + cb * sp
                pedal.append(tc)
                # giai điệu trong khoảng này: đệm tránh nửa cung với nó, nằm dưới nó
                mm = [nm(x) for mb, md, x in mel if mb < ce - 1e-6 and mb + md > cb + 1e-6]
                ml = [nm(x) for mb, md, x in mel if mb < ce - 1e-6 and mb + md > cb + 1e-6 and md >= 0.75]
                if octv == -12:
                    mm += [q - 12 for q in mm]; ml += [q - 12 for q in ml]
                # chỉ tránh nốt nằm thấp hơn giai điệu nửa cung (tạo quãng chín thứ); nốt thoáng qua thì bỏ qua
                avoid = {(q - 1) % 12 for q in ml}
                top = min(mm) - 2 if mm else 66
                # bass tay trái
                bn = bass_note(bpc, 36)
                if style in ("phach-day", "moc-don-day") or (style == "rai" and name == "ket" and bi == nb - 2):
                    add(tc + hj(), span * sp, bn - 12 if bn - 12 >= 28 else bn, cv * arc - 2, "L")
                add(tc + hj(), span * sp, bn, cv * arc + 2, "L")
                n_v = 4 if style == "moc-don-day" else 3
                sh = voice(pcs, prev, n_v, 48, min(64, top), must=(third, sev), avoid=avoid) or voice(pcs, prev, n_v, 46, 66)
                prev = sh
                if style == "rai":
                    # hợp âm rải chậm, ngân bằng pedal
                    for k, m in enumerate(sh):
                        add(tc + 0.04 + k * (0.09 if ext else 0.05) + hj(0.3), span * sp, m, cv * arc - 6, "L")
                elif style.startswith("phach"):
                    # đệm đều trên từng phách, phách đầu hợp âm đậm hơn
                    for b in [b for b in (0, 1, 2, 3) if b < span - 0.05]:
                        for k, m in enumerate(sh):
                            add(tc + b * sp + 0.02 + k * 0.004 + hj(), 0.92 * sp, m, cv * arc + (0 if b == 0 else -6), "L")
                        if style == "phach-bass" and b == 2 and span == 4:
                            add(tc + b * sp + hj(), 2 * sp, bn + 7, cv * arc - 4, "L")
                else:
                    # móc đơn rải nhẹ trong hợp âm, đều trên phách
                    seq = sh + sh[-2:0:-1]
                    for k in range(int(round(span * 2))):
                        m = seq[k % len(seq)]
                        add(tc + k * 0.5 * sp + hj(), 0.5 * sp, m, cv * arc + (3 if k == 0 else (-2 if k % 2 else -5)), "L")
            # giai điệu
            for mb, md, x in mel:
                m = nm(x)
                c = [cn for cb, cn in ch if cb <= mb + 1e-6][-1]
                pcs = chord(c if c != "Dbadd9" else "Db")[0]
                tt = t + mb * sp + 0.014
                v = mv * arc * (1.06 if md >= 2 else 1.0)
                if name == "ket" and bi == nb - 2:
                    md = 8
                add(tt, md * sp, m, v, "M")
                if octv:
                    add(tt + 0.006, md * sp, m + octv, v - (10 if octv > 0 else 8), "M")
                if name in ("diep-khuc", "diep-khuc-lon") and md >= 1.5:
                    under = [k for k in range(m - 9, m - 2) if k % 12 in pcs]
                    if under:
                        add(tt + 0.01, md * sp, under[-1], v - 15, "M")
            t += 4 * sp
    pedal.append(t + 3.0)
    t_end = t
    return notes, sorted(pedal), marks, t_end


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mau", required=True)
    ap.add_argument("--ra", required=True)
    ap.add_argument("--ten", default="xuong-piano-thiet-tha")
    a = ap.parse_args()
    os.makedirs(a.ra, exist_ok=True)
    notes, pedal, marks, t_end = build()
    S = P.load_samples(a.mau)
    x = P.render(notes, [(p, 0) for p in pedal], t_end, S)
    x = sosfilt(butter(2, 30, btype="high", fs=SR, output="sos"), x, axis=1)
    x = x + 0.15 * sosfilt(butter(2, 2500, btype="high", fs=SR, output="sos"), x, axis=1)
    x = P.reverb(x.astype(np.float32), rt60=2.6, wet=0.25)
    e = int((t_end + 4.0) * SR); x = x[:, :e]
    f = int(3.0 * SR); x[:, -f:] *= np.linspace(1, 0, f) ** 2
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.7
    wav = os.path.join(a.ra, a.ten + "_tho.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x.T, -1, 1) * 32767).astype("<i2").tobytes())
    json.dump({"moc": marks, "dai": round(e / SR, 2)}, open(os.path.join(a.ra, a.ten + "_moc.json"), "w"), ensure_ascii=False)
    print("xong", round(e / SR, 1), "giây,", len(notes), "nốt")
    for k, v in marks:
        print(f"  {k:14s} {int(v // 60)}:{v % 60:05.2f}")


if __name__ == "__main__":
    main()
