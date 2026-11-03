#!/usr/bin/env python3
"""Bản pop-rock khí thế "Tin tiếp" (xưởng tự soạn): piano dẫn, bass, trống, pad synth.

Cảm hứng cấu trúc từ ballad arena rock: piano mở một mình, từng lớp nhạc cụ vào dần,
điệp khúc bùng lên ở phần sau. Riff, giai điệu, giọng (Rê trưởng) và nhịp (116) đều mới.
Piano: mẫu Salamander Grand Piano V3 (Alexander Holm, CC BY 3.0, phải ghi công khi dùng MP3).
Bass, trống, pad, tiếng vút: tổng hợp bằng code, không dùng mẫu của ai.
  python3 soan-pop-rock.py --mau <thư mục mẫu Salamander> --ra <thư mục>
Cần soan-piano-mau.py cùng thư mục; numpy, scipy, mido, ffmpeg.
"""
import argparse, importlib.util, os, json, wave
import numpy as np
from scipy.signal import butter, sosfilt, lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("piano_mau", os.path.join(HERE, "soan-piano-mau.py"))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
SR = P.SR
n = P.n
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)

# ---------------------------------------------------------------- hoà âm (Rê trưởng)
ROOT = {"D": 38, "A": 45, "Bm": 47, "G": 43, "Em": 40, "D/F#": 42, "Asus": 45}
PAD = {"D": [62, 66, 69, 74], "A": [61, 64, 69, 73], "Bm": [62, 66, 71, 74], "G": [62, 67, 71, 74],
       "Em": [62, 67, 71, 76], "D/F#": [62, 66, 69, 74], "Asus": [62, 64, 69, 74]}
# riff tay phải 3+3+2: hai nhát đầu thế chính, nhát thứ ba đổi nốt trên cho câu riff chuyển động
RIFF = {"D": ([66, 69, 74], [66, 69, 76]), "A": ([64, 69, 73], [64, 69, 71]),
        "Bm": ([66, 71, 74], [66, 71, 73]), "G": ([67, 71, 74], [67, 71, 76]),
        "Em": ([67, 71, 76], [67, 71, 74]), "D/F#": ([66, 69, 74], [66, 69, 76]),
        "Asus": ([64, 69, 74], [64, 69, 73])}

VERSE = ["D", "A", "Bm", "G"] * 2
BUILD = ["Bm", "G", "D", "A", "Bm", "G", "Em", "Asus"]
CHORUS = ["G", "A", "Bm", "D/F#", "G", "A", "D", "D"]

BUILD_MEL = [[(0, 3, "F#5"), (3, 1, "E5")], [(0, 4, "D5")], [(0, 3, "F#5"), (3, 1, "A5")], [(0, 4, "E5")],
             [(0, 3, "F#5"), (3, 1, "G5")], [(0, 4, "B5")], [(0, 2, "G5"), (2, 2, "B5")], [(0, 4, "A5")]]
CHORUS_MEL = [
    [(0, 1, "B4"), (1, .5, "D5"), (1.5, 1, "E5"), (2.5, 1.5, "D5")],
    [(0, 1, "C#5"), (1, .5, "E5"), (1.5, 1, "F#5"), (2.5, 1.5, "E5")],
    [(0, 1, "D5"), (1, .5, "F#5"), (1.5, 1, "A5"), (2.5, 1, "F#5"), (3.5, .5, "E5")],
    [(0, 3, "F#5"), (3, .5, "E5"), (3.5, .5, "D5")],
    [(0, 1, "B4"), (1, .5, "D5"), (1.5, 1, "G5"), (2.5, 1.5, "F#5")],
    [(0, 1, "E5"), (1, .5, "F#5"), (1.5, 1, "A5"), (2.5, 1, "G5"), (3.5, .5, "F#5")],
    [(0, 1, "A5"), (1, 1, "B5"), (2, 2, "A5")],
    [(0, 3, "F#5")],
]

# (tên, hợp âm, giai điệu, lớp nhạc cụ, lực piano)
# lớp: riff, bass (0 tắt / 1 nốt dài / 2 móc đơn / 3 móc đơn nảy quãng tám), trống (0-3), pad, vút
SECTIONS = [
    ("mo-dau", VERSE, None, dict(riff=1, bass=0, drum=0, pad=0), 58),
    ("doan-1", VERSE, None, dict(riff=1, bass=1, drum=0, pad=0), 62),
    ("doan-2", VERSE, None, dict(riff=1, bass=2, drum=1, pad=0), 64),
    ("don-nen", BUILD, BUILD_MEL, dict(riff=1, bass=2, drum=2, pad=1, vut=1), 68),
    ("diep-khuc-1", CHORUS, CHORUS_MEL, dict(riff=0, bass=3, drum=3, pad=2), 80),
    ("lang", VERSE[:4], None, dict(riff=1, bass=1, drum=0, pad=1), 62),
    ("don-nen-2", BUILD[4:], BUILD_MEL[4:], dict(riff=1, bass=2, drum=2, pad=1, vut=1), 70),
    ("diep-khuc-2", CHORUS * 2, CHORUS_MEL * 2, dict(riff=0, bass=3, drum=3, pad=2), 84),
    ("ket", VERSE, None, dict(riff=1, bass=1, drum=0, pad=1, ket=1), 58),
]
BPM = 116


def build(seed=3):
    rng = np.random.default_rng(seed)
    spb = 60 / BPM
    piano, bass, drums, pads, fx, marks, midi = [], [], [], [], [], [], []
    t_bar = []
    t = 0.0
    bar_no = 0
    for name, chords, mel, L, pv in SECTIONS:
        marks.append((name, round(t, 2)))
        nb = len(chords)
        for bi, c in enumerate(chords):
            # tempo: chậm dần ở 2 ô cuối bài
            sp = spb
            if L.get("ket") and bi >= nb - 2:
                sp = spb * (1.12 if bi == nb - 2 else 1.3)
            last = L.get("ket") and bi == nb - 1
            tk0 = bar_no * 4 * 480
            hum = lambda: rng.normal(0, 0.005)
            vel = lambda v: int(np.clip(v + rng.normal(0, 3), 15, 120))
            # piano riff
            if L["riff"]:
                a, b2 = RIFF[c]
                hits = [(0, 1.5, a), (1.5, 1.5, a), (3, 1, b2)] if not last else [(0, 8, a)]
                for hb, hd, vo in hits:
                    for k, m in enumerate(vo):
                        piano.append((t + hb * sp + hum() + k * 0.004, hd * sp * 0.92, m, vel(pv - 4 + (4 if hb == 0 else 0)), "R", tk0 + int(hb * 480), int(hd * 480)))
                r = ROOT[c]
                lo = r - 12 if r >= 40 else r
                lh = [(0, 1.5, [lo, lo + 12]), (1.5, 1.5, [lo + 12]), (3, 1, [lo + 7])] if not last else [(0, 8, [lo, lo + 12])]
                for hb, hd, ms in lh:
                    for m in ms:
                        piano.append((t + hb * sp + hum(), hd * sp * 0.95, m, vel(pv - 10), "L", tk0 + int(hb * 480), int(hd * 480)))
            else:
                # điệp khúc: tay trái quãng tám nốt gốc theo nửa nhịp
                r = ROOT[c]
                lo = r - 12 if r >= 40 else r
                for hb in (0, 2):
                    for m in (lo, lo + 12):
                        piano.append((t + hb * sp + hum(), 2 * sp * .95, m, vel(pv - 14), "L", tk0 + hb * 480, 960))
                    for m in RIFF[c][0][:2]:
                        piano.append((t + hb * sp + 0.75 * sp + hum(), 1.0 * sp, m - 12, vel(pv - 26), "L", tk0 + hb * 480 + 360, 480))
            # giai điệu: nốt và quãng tám (trên ở điệp khúc, dưới ở đoạn dồn)
            if mel:
                for mb, md, x in mel[bi]:
                    m = n(x)
                    tt = t + mb * sp + 0.012
                    piano.append((tt, md * sp, m, vel(pv + 4), "M", tk0 + int(mb * 480), int(md * 480)))
                    if name.startswith("diep"):
                        piano.append((tt + 0.006, md * sp, m + 12, vel(pv - 6), "M", tk0 + int(mb * 480), int(md * 480)))
            # bass
            r = ROOT[c] - 12 if ROOT[c] >= 43 else ROOT[c]
            if L["bass"] == 1:
                bass.append((t, (8 if last else 4) * sp * 0.97, r, 0.8, tk0, 1920))
            elif L["bass"] >= 2:
                for k in range(8):
                    m = r + (12 if (L["bass"] == 3 and k in (3, 7)) else 0)
                    bass.append((t + k * 0.5 * sp, 0.5 * sp * 0.82, m, 0.75 + (0.15 if k % 2 == 0 else 0), tk0 + k * 240, 200))
            # pad
            if L.get("pad"):
                pads.append((t, (8 if last else 4) * sp, PAD[c], 0.55 if L["pad"] == 1 else 0.85))
            # trống
            d = L["drum"]
            def hit(kind, b, v):
                drums.append((t + b * sp + rng.normal(0, 0.003), kind, v * (1 + rng.normal(0, 0.05)), tk0 + int(b * 480)))
            if d >= 1:
                for k in range(8):
                    hit("hat", 0.5 * k, 0.35 if k % 2 else 0.55)
                hit("kick", 0, 0.9); hit("kick", 2, 0.85)
                if d >= 2:
                    hit("snare", 1, 0.7); hit("snare", 3, 0.75)
                    if bi == nb - 1:   # trống dồn ô cuối đoạn dồn nền
                        for k in range(8):
                            hit("snare", 2 + 0.25 * k, 0.35 + 0.08 * k)
                if d >= 3:
                    hit("kick", 2.5, 0.7); hit("kick", 3.5 if bi % 2 else 1.5, 0.55)
                    hit("open", 3.5, 0.45)
                    if bi % 4 == 0:
                        hit("crash", 0, 0.9 if bi == 0 else 0.6)
                    if bi == nb - 1 and name == "diep-khuc-1":
                        for k, b in enumerate([2, 2.5, 3, 3.5]):
                            hit("tom", b, 0.7 + 0.05 * k)
            if L.get("vut") and bi == nb - 2:
                fx.append((t, 8 * sp))
            # tiếng chũm choẹ mở đầu đoạn kết sau điệp khúc lớn
            if name == "ket" and bi == 0:
                drums.append((t, "crash", 0.8, tk0))
            t_bar.append(t)
            t += 4 * sp
            bar_no += 1
    return piano, bass, drums, pads, fx, marks, t


# ---------------------------------------------------------------- tổng hợp

def adsr(N, a, d, s, r_start, r, sr=SR):
    t = np.arange(N) / sr
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = t > r_start
    e[rel] *= np.exp(-(t[rel] - r_start) / r)
    return e


def synth_bass(m, dur, vel):
    f = mtof(m)
    N = int((dur + 0.25) * SR)
    t = np.arange(N) / SR
    sine = np.sin(2 * np.pi * f * t)
    saw = 2 * ((f * t) % 1) - 1
    env = adsr(N, 0.006, 0.18, 0.7, dur, 0.06)
    fenv = 300 + 1400 * np.exp(-t / 0.09)
    # lọc thông thấp biến thiên theo từng khối nhỏ
    out = np.zeros(N)
    blk = 512
    zi = None
    for i in range(0, N, blk):
        fc = float(fenv[i])
        b, a = butter(2, fc, btype="low", fs=SR)
        seg, zi = lfilter(b, a, saw[i:i + blk], zi=zi if zi is not None else np.zeros(2))
        out[i:i + blk] = seg
    y = (0.75 * sine + 0.55 * out) * env * vel
    return np.tanh(1.6 * y) / 1.6


def kick(v):
    N = int(0.45 * SR); t = np.arange(N) / SR
    f = 46 + 110 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / 0.22)
    click = np.random.default_rng(1).standard_normal(N) * np.exp(-t / 0.003) * 0.25
    return np.tanh(1.5 * (y + click)) * v


def snare(v, rng):
    N = int(0.35 * SR); t = np.arange(N) / SR
    noise = sosfilt(butter(2, [1200, 9000], btype="band", fs=SR, output="sos"), rng.standard_normal(N))
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05) + 0.5 * np.sin(2 * np.pi * 330 * t) * np.exp(-t / 0.03)
    return (0.9 * noise * np.exp(-t / 0.13) + 0.7 * body) * v


def hat(v, rng, open_=False):
    L = 0.32 if open_ else 0.06
    N = int(L * SR); t = np.arange(N) / SR
    x = sosfilt(butter(4, 7500, btype="high", fs=SR, output="sos"), rng.standard_normal(N))
    return x * np.exp(-t / (0.11 if open_ else 0.018)) * v * 0.55


def crash(v, rng):
    N = int(2.6 * SR); t = np.arange(N) / SR
    x = sosfilt(butter(2, 3500, btype="high", fs=SR, output="sos"), rng.standard_normal(N))
    met = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (3120, 4370, 5210, 6830, 8090)) * 0.08
    return (x + met) * np.exp(-t / 0.7) * v * 0.5


def tom(v):
    N = int(0.4 * SR); t = np.arange(N) / SR
    f = 95 + 70 * np.exp(-t / 0.06)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18) * v


def supersaw(notes, dur, vel, rng):
    N = int((dur + 1.2) * SR); t = np.arange(N) / SR
    y = np.zeros((2, N))
    for m in notes:
        f = mtof(m)
        for k, det in enumerate((-0.12, -0.07, -0.025, 0.0, 0.025, 0.07, 0.12)):
            ff = f * 2 ** (det / 12)
            s = 2 * ((ff * t + rng.uniform()) % 1) - 1
            pan = (k - 3) / 3 * 0.7
            y[0] += s * np.cos((pan + 1) * np.pi / 4)
            y[1] += s * np.sin((pan + 1) * np.pi / 4)
    y = sosfilt(butter(2, 2200, btype="low", fs=SR, output="sos"), y, axis=1)
    env = adsr(N, 0.35, 1.0, 1.0, dur, 0.45)
    return y * env * vel / (len(notes) * 7)


def riser(dur, rng):
    N = int(dur * SR); t = np.arange(N) / SR
    x = rng.standard_normal(N)
    out = np.zeros(N)
    blk = 1024; zi = np.zeros(2)
    for i in range(0, N, blk):
        fc = 400 + 7000 * (i / N) ** 2
        b, a = butter(2, fc, btype="high", fs=SR)
        seg, zi = lfilter(b, a, x[i:i + blk], zi=zi)
        out[i:i + blk] = seg
    return out * (t / dur) ** 2.2 * 0.5


def place(buf, sig, t, pan=0.0):
    i = int(t * SR)
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)]) * 1.414
    j = min(i + sig.shape[1], buf.shape[1])
    if j > i:
        buf[:, i:j] += sig[:, : j - i]


def rms_db(x):
    e = np.mean(x ** 2, axis=0)
    fr = e[: len(e) // 4410 * 4410].reshape(-1, 4410).mean(1)
    act = fr[fr > 1e-6 * fr.max()]
    return 10 * np.log10(np.mean(act) + 1e-12)


def write_midi(piano, bass, drums, pads, path):
    import mido
    mf = mido.MidiFile(ticks_per_beat=480)
    def track(name, ch, prog, evs):
        tr = mido.MidiTrack(); mf.tracks.append(tr)
        tr.append(mido.MetaMessage("track_name", name=name, time=0))
        e = [(0, 0, mido.Message("program_change", program=prog, channel=ch))]
        if ch == 0:
            e += [(0, 0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM))),
                  (0, 0, mido.MetaMessage("key_signature", key="D"))]
        for tk, dtk, m, v in evs:
            e.append((tk, 2, mido.Message("note_on", note=m, velocity=int(v), channel=ch)))
            e.append((tk + max(20, dtk - 10), 0, mido.Message("note_off", note=m, velocity=0, channel=ch)))
        e.sort(key=lambda z: (z[0], z[1]))
        last = 0
        for tk, _, msg in e:
            msg.time = tk - last; last = tk; tr.append(msg)
    track("Piano", 0, 0, [(x[5], x[6], x[2], x[3]) for x in piano])
    track("Bass", 1, 33, [(b[4], b[5], b[2], 70 + 40 * (b[3] - 0.7)) for b in bass])
    gm = {"kick": 36, "snare": 38, "hat": 42, "open": 46, "crash": 49, "tom": 45}
    track("Drums", 9, 0, [(d[3], 120, gm[d[1]], int(np.clip(d[2] * 110, 20, 127))) for d in drums])
    mf.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mau", required=True)
    ap.add_argument("--ra", required=True)
    ap.add_argument("--ten", default="xuong-pop-tin-tiep")
    a = ap.parse_args()
    os.makedirs(a.ra, exist_ok=True)
    rng = np.random.default_rng(7)
    piano, bass, drums, pads, fx, marks, t_end = build()
    total = int((t_end + 6) * SR)
    S = P.load_samples(a.mau)
    pedal = sorted({x[0] for x in piano if x[4] in ("R", "L")} | {x[0] for x in piano if x[4] == "M"})
    bp = P.render(piano, [(p, 0) for p in pedal], t_end, S)[:, :total]
    bp = np.pad(bp, ((0, 0), (0, max(0, total - bp.shape[1]))))
    bb = np.zeros((2, total)); bd = np.zeros((2, total)); bpad = np.zeros((2, total)); bfx = np.zeros((2, total))
    for t, d, m, v, *_ in bass:
        place(bb, synth_bass(m, d, v), t)
    pan = {"kick": 0, "snare": 0.05, "hat": 0.3, "open": 0.3, "crash": -0.35, "tom": -0.2}
    for t, kind, v, _ in drums:
        sig = {"kick": lambda: kick(v), "snare": lambda: snare(v, rng), "hat": lambda: hat(v, rng),
               "open": lambda: hat(v, rng, True), "crash": lambda: crash(v, rng), "tom": lambda: tom(v)}[kind]()
        place(bd, sig, t, pan[kind])
    for t, d, ns, v in pads:
        place(bpad, supersaw(ns, d, v, rng), t)
    for t, d in fx:
        place(bfx, riser(d, rng), t)
    # pad nhún nhẹ theo trống cái (kiểu nhạc pop hiện đại)
    duck = np.ones(total)
    for t, kind, v, _ in drums:
        if kind == "kick":
            i = int(t * SR); L = int(0.25 * SR)
            seg = 1 - 0.35 * np.exp(-np.arange(L) / (0.08 * SR))
            j = min(i + L, total); duck[i:j] = np.minimum(duck[i:j], seg[: j - i])
    bpad *= duck
    def norm(x, db):
        return x * 10 ** ((db - rms_db(x)) / 20) if np.any(x) else x
    # piano sáng hơn chút cho chất pop hiện đại (nâng dải trên 2,5 kHz khoảng 3 dB)
    bp = bp + 0.4 * sosfilt(butter(2, 2500, btype="high", fs=SR, output="sos"), bp, axis=1)
    bp = norm(bp, -18.5); bb = norm(bb, -23.0); bd = norm(bd, -21.5); bpad = norm(bpad, -27.0); bfx = norm(bfx, -30.0)
    bb = sosfilt(butter(2, 35, btype="high", fs=SR, output="sos"), bb, axis=1)
    dry = bp + bb + bd + bpad + bfx
    send = 0.22 * bp + 0.35 * bpad + 0.12 * bd + 0.3 * bfx
    x = dry + 0.5 * P.reverb(send, rt60=2.2, wet=1.0)[:, :total] - 0.5 * send
    x = sosfilt(butter(2, 28, btype="high", fs=SR, output="sos"), x, axis=1)
    e = int((t_end + 4.5) * SR); x = x[:, :e]
    f = int(3 * SR); x[:, -f:] *= np.linspace(1, 0, f) ** 2
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.7
    wav = os.path.join(a.ra, a.ten + "_tho.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x.T, -1, 1) * 32767).astype("<i2").tobytes())
    write_midi(piano, bass, drums, pads, os.path.join(a.ra, a.ten + ".mid"))
    json.dump({"moc": marks, "dai": round(e / SR, 2)}, open(os.path.join(a.ra, a.ten + "_moc.json"), "w"), ensure_ascii=False)
    print("xong", round(e / SR, 1), "giây")
    for k, v in marks:
        print(f"  {k:12s} {int(v // 60)}:{v % 60:05.2f}")


if __name__ == "__main__":
    main()
