#!/usr/bin/env python3
"""Soạn nhạc nền gốc cho xưởng phim bằng tổng hợp âm thanh (numpy, scipy, ffmpeg).

Mọi nốt đều do code tạo ra từ sóng và bộ lọc, không dùng mẫu thu âm hay nhạc của ai,
nên không đơn vị nào đăng ký được Content ID cho các bản này.

Dùng:
  python3 tools/soan-nhac.py <tên bản> [--ra <thư mục>] [--hat <số>]
  python3 tools/soan-nhac.py --danh-sach
  python3 tools/soan-nhac.py --hieu-ung --ra <thư mục>   (whoosh, chuông, pop)

Mỗi bản có hạt ngẫu nhiên cố định (hat), chạy lại ra đúng bản cũ; đổi --hat để có biến thể.
Cần: python3, numpy, scipy (pip install numpy scipy) và ffmpeg.
Chuẩn hoá -15 LUFS tích hợp, true peak dưới -1,5 dB, mp3 192 kbps, 44,1 kHz stereo.
"""
import argparse, json, os, subprocess, sys, re
try:
    import numpy as np
    from scipy.signal import lfilter, oaconvolve, butter, sosfilt
except ImportError:
    sys.exit("Thiếu thư viện: chạy  python3 -m pip install numpy scipy  (cần thêm ffmpeg trong PATH)")

SR = 44100


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


# ---------------------------------------------------------------- bus trộn

class Mix:
    def __init__(self, dur):
        self.n = int(dur * SR)
        size = self.n + SR * 14
        self.dry = np.zeros((2, size), np.float32)
        self.send = np.zeros((2, size), np.float32)

    def add(self, sig, t, pan=0.0, gain=1.0, send=0.25):
        i = int(t * SR)
        if i < 0 or i >= self.dry.shape[1]:
            return
        j = min(i + len(sig), self.dry.shape[1])
        s = sig[: j - i].astype(np.float32) * gain
        a = (pan + 1) * np.pi / 4
        l, r = np.cos(a), np.sin(a)
        self.dry[0, i:j] += s * l
        self.dry[1, i:j] += s * r
        if send > 0:
            self.send[0, i:j] += s * l * send
            self.send[1, i:j] += s * r * send

    def render(self, rt60=2.8, wet=1.0, seed=7):
        rng = np.random.default_rng(seed)
        n = int(rt60 * 1.1 * SR)
        t = np.arange(n) / SR
        out = self.dry.copy()
        sos = butter(2, 5200, btype="low", fs=SR, output="sos")
        for ch in range(2):
            ir = rng.standard_normal(n) * np.exp(-6.9 * t / rt60)
            ir = sosfilt(sos, ir)
            ir[: int(0.02 * SR)] *= 0.0
            ir[int(0.02 * SR): int(0.06 * SR)] *= np.linspace(0, 1, int(0.06 * SR) - int(0.02 * SR))
            ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
            wetsig = oaconvolve(self.send[ch], ir)[: out.shape[1]]
            out[ch] += (wet * wetsig).astype(np.float32)
        return out[:, : self.n + int(SR * 6)]


# ---------------------------------------------------------------- nhạc cụ

def piano(m, dur, vel=0.6, rng=None, ring=1.6):
    """Piano mềm: các hoạ âm hơi lệch tần, hai dây lệch nhẹ, tiếng búa gõ ngắn."""
    rng = rng or np.random.default_rng(m)
    f = mtof(m)
    low = np.clip((m - 28) / 70.0, 0, 1)
    base = 1.0 + 4.5 * (1 - low)
    T = min(dur + ring + base, 10.0)
    t = np.arange(int(T * SR)) / SR
    B = 0.00018 * (1 + max(0, m - 60) / 30.0) ** 2
    sig = np.zeros_like(t)
    for n in range(1, 15):
        fn = f * n * np.sqrt(1 + B * n * n)
        if fn > 9500:
            break
        amp = (n ** -1.05) * (vel ** (0.35 * (n - 1)))
        tau = base / (1 + 0.55 * (n - 1))
        env = np.exp(-t / tau)
        for det in (-1, 1):
            ff = fn * (1 + det * 0.0003 * (1 + rng.random()))
            sig += amp * 0.5 * np.sin(2 * np.pi * ff * t + rng.random() * 6.28) * env
    # tiếng búa
    nb = int(0.012 * SR)
    hammer = rng.standard_normal(nb) * np.hanning(nb) * 0.04 * vel
    sig[:nb] += hammer
    sig *= 1 - np.exp(-t / 0.004)
    # nhả phím sau dur (có pedal nên rơi chậm)
    rel = np.where(t > dur, np.exp(-(t - dur) / ring), 1.0)
    sig *= rel
    return sig * vel * 0.9


_pluck_cache = {}


def pluck(m, vel=0.5, dur=None, variant=0, g=0.9965, L=3.6):
    """Dây gảy kiểu Karplus-Strong có nội suy phân số để đúng cao độ, cộng cộng hưởng thùng đàn."""
    key = (m, variant, round(g, 4))
    if key not in _pluck_cache:
        f = mtof(m)
        desired = SR / f - 0.5
        N = int(np.floor(desired - 0.5))
        d = desired - N
        c = (1 - d) / (1 + d)
        den = np.zeros(N + 3)
        den[0] = 1.0
        den[1] += c
        den[N] -= g * 0.5 * c
        den[N + 1] -= g * 0.5 * (1 + c)
        den[N + 2] -= g * 0.5
        rng = np.random.default_rng(10000 + m * 7 + variant)
        exc = rng.uniform(-1, 1, N + 2)
        exc = np.convolve(exc, np.ones(7) / 7.0, "same")
        exc -= exc.mean()
        x = np.zeros(int(L * SR))
        x[: len(exc)] = exc
        y = lfilter([1.0], den, x)
        y = sosfilt(butter(2, 45, btype="high", fs=SR, output="sos"), y)
        y = sosfilt(butter(2, 2600, btype="low", fs=SR, output="sos"), y)
        # thùng đàn
        tb = np.arange(int(0.12 * SR)) / SR
        ir = (np.sin(2 * np.pi * 98 * tb) * np.exp(-tb / 0.05) + 0.7 * np.sin(2 * np.pi * 196 * tb) * np.exp(-tb / 0.035)
              + 0.4 * np.sin(2 * np.pi * 392 * tb) * np.exp(-tb / 0.02))
        ir /= np.abs(ir).max()
        y = y + 0.30 * oaconvolve(y, ir)[: len(y)]
        r = np.sqrt(np.mean(y[: int(0.5 * SR)] ** 2)) + 1e-9
        y = np.tanh(y / r * 0.35) / 0.9
        _pluck_cache[key] = y.astype(np.float32)
    y = _pluck_cache[key].copy()
    if dur is not None:
        t = np.arange(len(y)) / SR
        y *= np.where(t > dur, np.exp(-(t - dur) / 0.9), 1.0)
    return y * vel


def mallet(m, vel=0.5, L=1.6):
    f = mtof(m)
    t = np.arange(int(L * SR)) / SR
    sig = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9)
           + 0.28 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t / 0.22)
           + 0.07 * np.sin(2 * np.pi * f * 9.8 * t) * np.exp(-t / 0.09))
    sig *= 1 - np.exp(-t / 0.002)
    return sig * vel * 0.8


def bell(m, vel=0.4, L=7.0):
    f = mtof(m)
    t = np.arange(int(L * SR)) / SR
    sig = np.zeros_like(t)
    for r, a, tau in ((1.0, 1.0, 4.2), (2.76, 0.40, 2.6), (5.40, 0.20, 1.4), (8.93, 0.10, 0.7)):
        sig += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / tau)
    sig *= 1 - np.exp(-t / 0.003)
    return sig * vel * 0.6


def pad(notes, dur, att=2.5, rel=3.5, bright=0.45, vel=0.3, seed=1):
    rng = np.random.default_rng(seed)
    T = dur + rel
    t = np.arange(int(T * SR)) / SR
    env = np.minimum(1.0, t / att) ** 1.5
    env *= np.where(t > dur, np.exp(-(t - dur) / (rel / 3.0)), 1.0)
    sig = np.zeros_like(t)
    for m in notes:
        f = mtof(m)
        for cents in (-8, 0, 8):
            ff = f * 2 ** (cents / 1200.0)
            ph = rng.random() * 6.28
            for h in range(1, 7):
                sig += (bright ** (h - 1)) / h * np.sin(2 * np.pi * ff * h * t + ph * h)
    lfo = 1 + 0.07 * np.sin(2 * np.pi * (0.11 + 0.05 * rng.random()) * t + rng.random() * 6.28)
    sig *= env * lfo
    return sig * vel / max(1, len(notes)) ** 0.6 / 3.0


def air(dur, vel=0.02, seed=3):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n)
    sos = butter(2, [300, 2400], btype="band", fs=SR, output="sos")
    x = sosfilt(sos, x)
    t = np.arange(n) / SR
    x *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.045 * t + 1.0)
    x *= np.minimum(1, t / 6.0) * np.minimum(1, (dur - t) / 8.0)
    return x * vel


def shaker(vel=0.3, rng=None):
    rng = rng or np.random.default_rng(1)
    n = int(0.07 * SR)
    x = rng.standard_normal(n)
    sos = butter(2, 6000, btype="high", fs=SR, output="sos")
    x = sosfilt(sos, x) * np.exp(-np.arange(n) / (0.018 * SR))
    return x * vel


def human(rng, ms=9):
    return (rng.random() - 0.5) * 2 * ms / 1000.0


# ---------------------------------------------------------------- các bản

def beat_len(bpm):
    return 60.0 / bpm


def bản_guitar_am(hat=1):
    """Guitar mộc ấm, trưởng, 72 nhịp mỗi phút: dây gảy rải, nền dây mỏng, giai điệu thưa."""
    rng = np.random.default_rng(hat)
    bpm = 72
    B = beat_len(bpm)
    bar = 4 * B
    chords = [
        dict(bass=36, up=[55, 59, 62, 64, 67], mel=[64, 67, 69, 71, 72, 74, 76], pad=[48, 55, 59, 62]),   # Cmaj9
        dict(bass=33, up=[55, 59, 60, 64, 67], mel=[64, 67, 69, 71, 72, 74, 76], pad=[45, 52, 55, 60]),   # Am9
        dict(bass=41, up=[57, 60, 64, 65, 69], mel=[64, 65, 67, 69, 72, 74, 76], pad=[41, 48, 52, 57]),   # Fmaj7
        dict(bass=43, up=[55, 59, 62, 64, 67], mel=[62, 64, 67, 69, 71, 74, 76], pad=[43, 50, 55, 59]),   # G6
    ]
    loops = 26
    total = loops * 4 * bar + 8
    mix = Mix(total)
    pad_on = set(list(range(2, 5)) + list(range(8, 13)) + list(range(16, 21)) + [24])
    mel_on = set(list(range(4, 8)) + list(range(10, 15)) + list(range(18, 23)))
    thin = {0, 1, 25}
    pats = [
        [0, 1, 2, 3, 4, 5, 3, 2],
        [0, 2, 1, 3, 4, 2, 5, 3],
        [0, 1, 3, 2, 4, 5, 2, 1],
    ]
    for lp in range(loops):
        for ci, ch in enumerate(chords):
            t0 = (lp * 4 + ci) * bar
            pat = pats[rng.integers(0, len(pats))]
            for k, p in enumerate(pat):
                if lp in thin and k % 2 == 1:
                    continue
                t = t0 + k * B / 2 + human(rng)
                if p == 0:
                    sig = pluck(ch["bass"], vel=0.62, variant=int(rng.integers(0, 3)), g=0.9972)
                    mix.add(sig, t, pan=-0.2, send=0.18)
                elif p == 4:
                    sig = pluck(ch["bass"] + 7 if ch["bass"] < 40 else ch["bass"] + 12, vel=0.42, variant=int(rng.integers(0, 3)))
                    mix.add(sig, t, pan=-0.12, send=0.2)
                else:
                    idx = {1: 0, 2: 1, 3: 2, 5: 3}.get(p, 0)
                    note = ch["up"][idx % len(ch["up"])]
                    vel = 0.34 + 0.1 * rng.random()
                    sig = pluck(note, vel=vel, variant=int(rng.integers(0, 3)))
                    mix.add(sig, t, pan=0.18 + 0.1 * rng.random(), send=0.28)
            if lp in pad_on:
                mix.add(pad(ch["pad"], bar, att=1.6, rel=3.0, vel=0.20, seed=lp * 10 + ci), t0, pan=0.0, send=0.35)
            if lp in mel_on:
                tt = t0
                beats = 0.0
                while beats < 4.0:
                    if rng.random() < 0.38:
                        beats += 1.0
                        continue
                    ln = [1.0, 1.5, 2.0][rng.integers(0, 3)]
                    ln = min(ln, 4.0 - beats)
                    note = ch["mel"][rng.integers(0, len(ch["mel"]))] if beats > 0 else ch["mel"][rng.integers(0, 4)]
                    sig = pluck(note, vel=0.30, variant=int(rng.integers(0, 3)), g=0.9955, dur=ln * B)
                    mix.add(sig, t0 + beats * B + human(rng, 12), pan=0.3, send=0.38)
                    beats += ln
    # kết
    t_end = loops * 4 * bar
    for k, n in enumerate([36, 48, 55, 59, 62, 64]):
        mix.add(pluck(n, vel=0.5 - 0.03 * k, g=0.9975), t_end + k * 0.07, pan=-0.1 + 0.05 * k, send=0.3)
    mix.add(pad(chords[0]["pad"], 6, att=0.6, rel=4, vel=0.2, seed=99), t_end, send=0.35)
    return mix, total


def bản_piano_tinh(hat=1):
    """Piano trầm lắng, 58 nhịp mỗi phút, Rê thứ: tay trái dài, tay phải thưa, nền dây rất nhẹ."""
    rng = np.random.default_rng(hat)
    bpm = 58
    B = beat_len(bpm)
    bar = 4 * B
    chords = [
        dict(bass=[38, 45], up=[53, 57, 60, 64, 65, 69], mel=[69, 72, 74, 76, 77, 79], pad=[50, 57, 60, 65]),   # Dm9
        dict(bass=[34, 41], up=[58, 62, 65, 69, 72], mel=[69, 70, 72, 74, 77, 79], pad=[46, 53, 57, 62]),       # Bbmaj7
        dict(bass=[31, 43], up=[58, 62, 65, 67, 69], mel=[67, 70, 72, 74, 77, 79], pad=[43, 50, 55, 58]),       # Gm9
        dict(bass=[33, 45], up=[57, 62, 64, 67, 69], mel=[69, 72, 74, 76, 79, 81], pad=[45, 52, 57, 62]),       # A7sus4
    ]
    loops = 20
    total = loops * 4 * bar + 10
    mix = Mix(total)
    pad_on = set(range(4, 9)) | set(range(12, 17))
    for lp in range(loops):
        for ci, ch in enumerate(chords):
            t0 = (lp * 4 + ci) * bar
            # tay trái
            mix.add(piano(ch["bass"][0], bar * 0.98, vel=0.55, rng=rng, ring=1.8), t0 + human(rng, 12), pan=-0.35, send=0.3)
            mix.add(piano(ch["bass"][1], bar * 0.9, vel=0.42, rng=rng, ring=1.6), t0 + 0.06 + human(rng, 10), pan=-0.3, send=0.3)
            # tay phải rải
            slots = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
            for k, s in enumerate(slots):
                if rng.random() < 0.45:
                    continue
                note = ch["up"][(k + int(rng.integers(0, 2))) % len(ch["up"])]
                mix.add(piano(note, B * 1.0, vel=0.28 + 0.1 * rng.random(), rng=rng, ring=1.4), t0 + s * B + human(rng, 14), pan=0.15, send=0.32)
            # giai điệu
            if lp >= 2 and rng.random() < 0.8:
                nm = int(rng.integers(1, 3))
                at = sorted(rng.choice([0.0, 1.0, 2.0, 2.5, 3.0], size=nm, replace=False))
                for a in at:
                    note = ch["mel"][int(rng.integers(0, len(ch["mel"])))]
                    ln = float(rng.choice([1.0, 1.5, 2.0]))
                    mix.add(piano(note, ln * B, vel=0.5, rng=rng, ring=2.2), t0 + a * B + human(rng, 18), pan=0.25, send=0.4)
            if lp in pad_on:
                mix.add(pad(ch["pad"], bar, att=2.2, rel=3.5, vel=0.14, bright=0.35, seed=lp * 10 + ci), t0, send=0.4)
    t_end = loops * 4 * bar
    for k, n in enumerate([38, 45, 53, 57, 60, 64]):
        mix.add(piano(n, 4, vel=0.45 - 0.03 * k, rng=rng, ring=3.0), t_end + k * 0.12, pan=-0.2 + 0.08 * k, send=0.4)
    return mix, total


def bản_thien_pad(hat=1):
    """Nền thiền: âm nền Rê kéo dài, thảm âm đổi chậm, chuông thưa, hơi gió rất nhẹ."""
    rng = np.random.default_rng(hat)
    total = 400.0
    mix = Mix(total)
    # âm nền
    mix.add(pad([38, 45, 50], total - 8, att=8, rel=8, vel=0.22, bright=0.35, seed=1), 0, send=0.3)
    chords = [
        [57, 62, 64, 69],      # Dsus2
        [55, 62, 66, 69],      # Gmaj9 gần
        [59, 62, 66, 69],      # Bm7
        [57, 62, 64, 71],      # Asus
    ]
    t = 2.0
    i = 0
    while t < total - 24:
        ln = 16 + 4 * rng.random()
        mix.add(pad(chords[i % len(chords)], ln, att=5, rel=6, vel=0.2, bright=0.4, seed=100 + i), t, pan=0.0, send=0.5)
        t += ln - 3
        i += 1
    # chuông
    penta = [74, 76, 78, 81, 83, 86, 62, 66]
    tt = 14.0
    while tt < total - 20:
        n = int(rng.choice(penta))
        mix.add(bell(n, vel=0.30 + 0.12 * rng.random()), tt, pan=float(rng.uniform(-0.5, 0.5)), send=0.6)
        tt += 7 + 9 * rng.random()
    mix.add(air(total - 2, vel=0.012), 0, send=0.1)
    return mix, total


def bản_nhe_sang(hat=1):
    """Sáng và nhẹ, 100 nhịp mỗi phút, Son trưởng: dây gảy ngắn, mallet, shaker thưa."""
    rng = np.random.default_rng(hat)
    bpm = 100
    B = beat_len(bpm)
    bar = 4 * B
    chords = [
        dict(bass=43, up=[59, 62, 67, 71, 74], mel=[71, 74, 76, 79, 81], pad=[55, 59, 62, 67]),   # G
        dict(bass=38, up=[57, 62, 66, 69, 74], mel=[69, 71, 74, 78, 81], pad=[50, 57, 62, 66]),   # D
        dict(bass=40, up=[59, 62, 67, 71, 74], mel=[67, 71, 74, 76, 79], pad=[52, 59, 62, 67]),   # Em
        dict(bass=36, up=[55, 60, 64, 67, 72], mel=[67, 71, 72, 76, 79], pad=[48, 55, 60, 64]),   # C
    ]
    loops = 24
    total = loops * 4 * bar + 6
    mix = Mix(total)
    motif = [0, None, 2, 1, None, 3, 2, None]
    pad_on = set(range(2, 7)) | set(range(10, 15)) | set(range(18, 22))
    mel_on = set(range(4, 8)) | set(range(12, 16)) | set(range(18, 23))
    shk_on = set(range(6, 10)) | set(range(14, 18)) | set(range(20, 23))
    for lp in range(loops):
        for ci, ch in enumerate(chords):
            t0 = (lp * 4 + ci) * bar
            for k in range(8):
                t = t0 + k * B / 2 + human(rng, 6)
                if k in (0, 4):
                    mix.add(pluck(ch["bass"], vel=0.55, g=0.993, variant=int(rng.integers(0, 3)), L=2.4), t, pan=-0.2, send=0.15)
                else:
                    idx = [None, 0, 2, 1, None, 3, 2, 1][k]
                    note = ch["up"][idx]
                    mix.add(pluck(note, vel=0.3 + 0.08 * rng.random(), g=0.986, variant=int(rng.integers(0, 3)), L=1.6), t, pan=0.2, send=0.22)
            if lp in mel_on:
                for k, mi in enumerate(motif):
                    if mi is None or (lp % 2 == 1 and rng.random() < 0.3):
                        continue
                    note = ch["mel"][mi % len(ch["mel"])]
                    mix.add(mallet(note, vel=0.34), t0 + k * B / 2 + human(rng, 8), pan=0.3, send=0.35)
            if lp in pad_on:
                mix.add(pad(ch["pad"], bar, att=1.0, rel=2.0, vel=0.16, bright=0.4, seed=lp * 10 + ci), t0, send=0.3)
            if lp in shk_on:
                for k in range(8):
                    if k % 2 == 1:
                        mix.add(shaker(vel=0.16 + 0.05 * rng.random(), rng=rng), t0 + k * B / 2, pan=0.4, send=0.1)
    t_end = loops * 4 * bar
    for k, n in enumerate([43, 55, 59, 62, 67, 71]):
        mix.add(pluck(n, vel=0.5 - 0.03 * k, g=0.995), t_end + k * 0.06, pan=-0.1 + 0.05 * k, send=0.3)
    return mix, total


BAN = {
    "xuong-guitar-am": (bản_guitar_am, "acoustic-am", "Guitar mộc ấm, Đô trưởng, 72 nhịp"),
    "xuong-piano-tinh": (bản_piano_tinh, "piano-tinh-lang", "Piano trầm lắng, Rê thứ, 58 nhịp"),
    "xuong-thien-pad": (bản_thien_pad, "thien-ambient", "Nền thiền Rê, thảm âm và chuông thưa, không nhịp"),
    "xuong-nhe-sang": (bản_nhe_sang, "nang-luong-nhe", "Sáng và nhẹ, Son trưởng, 100 nhịp"),
}


# ---------------------------------------------------------------- hiệu ứng

def sfx_whoosh(dur, f0=350, f1=4800, rng=None, vel=0.8):
    rng = rng or np.random.default_rng(5)
    n = int(dur * SR)
    t = np.arange(n) / SR
    bands = 14
    centers = np.geomspace(f0, f1, bands)
    out = np.zeros(n)
    for i, c in enumerate(centers):
        sos = butter(2, [c / 1.25, c * 1.25], btype="band", fs=SR, output="sos")
        x = sosfilt(sos, rng.standard_normal(n))
        tc = dur * (0.15 + 0.6 * i / (bands - 1))
        w = dur * 0.22
        out += x * np.exp(-0.5 * ((t - tc) / w) ** 2)
    out *= np.minimum(1, t / (0.12 * dur)) * np.minimum(1, (dur - t) / (0.3 * dur))
    out /= np.abs(out).max() + 1e-9
    return out * vel


def sfx_chime(m1, m2, vel=0.5):
    a = bell(m1, vel=vel, L=3.0)
    b = bell(m2, vel=vel * 0.85, L=3.0)
    out = np.zeros(int(3.2 * SR))
    out[: len(a)] += a
    k = int(0.14 * SR)
    out[k: k + len(b)] += b[: len(out) - k]
    return out


def sfx_pop(vel=0.6):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    f = 200 + 520 * np.exp(-t / 0.018)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.045) * (1 - np.exp(-t / 0.002)) * vel


def soan_hieu_ung(ra):
    rng = np.random.default_rng(11)
    bo = {
        "whoosh-manh-xuong": sfx_whoosh(1.5, 400, 5200, rng, 0.8),
        "whoosh-cham-xuong": sfx_whoosh(3.0, 250, 4200, rng, 0.8),
        "whoosh-nhanh-xuong": sfx_whoosh(1.1, 500, 6000, rng, 0.8),
        "chime-mem-xuong-1": sfx_chime(88, 93),
        "chime-mem-xuong-2": sfx_chime(86, 91),
        "pop-nhe-xuong": sfx_pop(),
    }
    kq = []
    os.makedirs(ra, exist_ok=True)
    for ten, x in bo.items():
        m = Mix(len(x) / SR + 0.1)
        m.add(x, 0.02, send=0.18 if ten.startswith(("whoosh", "chime")) else 0.05)
        st = m.render(rt60=1.2)
        n = st.shape[1]
        peak = np.abs(st).max()
        st = st / (peak + 1e-9) * 0.7
        import wave
        tmp = os.path.join(ra, f".{ten}.wav")
        pcm = (np.clip(st.T, -1, 1) * 32767).astype("<i2")
        with wave.open(tmp, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
        out = os.path.join(ra, f"{ten}.mp3")
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", tmp, "-af", "silenceremove=stop_periods=1:stop_duration=0.3:stop_threshold=-60dB,afade=t=out:st=0:d=0", "-c:a", "libmp3lame", "-b:a", "192k", out], check=True)
        os.remove(tmp)
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
        kq.append(dict(ten=ten, giay=round(d, 2)))
    print(json.dumps(kq, ensure_ascii=False))


# ---------------------------------------------------------------- hoàn thiện

def ebur(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr
    i = txt.rfind("Summary")
    seg = txt[i:]
    I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", seg).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", seg).group(1))
    return I, tp


def hoan_thien(stereo, ten, ra, muc=-15.0):
    import wave
    n = stereo.shape[1]
    # cắt đuôi im, fade
    env = np.abs(stereo).max(axis=0)
    idx = np.where(env > 1e-4)[0]
    n = min(n, int(idx[-1]) + int(0.2 * SR)) if len(idx) else n
    x = stereo[:, :n].copy()
    fi = int(0.8 * SR)
    fo = int(5.0 * SR)
    x[:, :fi] *= np.linspace(0, 1, fi) ** 1.5
    x[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
    sos = butter(2, 28, btype="high", fs=SR, output="sos")
    x = sosfilt(sos, x, axis=1)
    x /= np.abs(x).max() + 1e-9
    x *= 0.5
    tmp = os.path.join(ra, f".{ten}.wav")
    pcm = (np.clip(x.T, -1, 1) * 32767).astype("<i2")
    with wave.open(tmp, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    I, tp = ebur(tmp)
    gain = muc - I
    out = os.path.join(ra, f"{ten}.mp3")
    af = f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=5:release=60:level=disabled"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", tmp, "-af", af, "-c:a", "libmp3lame", "-b:a", "192k", out], check=True)
    os.remove(tmp)
    I2, tp2 = ebur(out)
    dur = n / SR
    return dict(ten=ten, file=out, giay=round(dur, 1), lufs=I2, true_peak=tp2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ban", nargs="?")
    ap.add_argument("--ra", default=".")
    ap.add_argument("--hat", type=int, default=1)
    ap.add_argument("--danh-sach", action="store_true")
    ap.add_argument("--hieu-ung", action="store_true", help="soạn bộ hiệu ứng (whoosh, chuông, pop) vào --ra")
    a = ap.parse_args()
    if a.hieu_ung:
        soan_hieu_ung(a.ra)
        return
    if a.danh_sach or not a.ban:
        for k, (_, nhom, mt) in BAN.items():
            print(f"{k:20s} nhóm {nhom:18s} {mt}")
        return
    fn, nhom, mt = BAN[a.ban]
    os.makedirs(a.ra, exist_ok=True)
    mix, total = fn(a.hat)
    st = mix.render()
    kq = hoan_thien(st, a.ban, a.ra)
    kq["nhom"] = nhom
    kq["mo_ta"] = mt
    kq["hat"] = a.hat
    print(json.dumps(kq, ensure_ascii=False))


if __name__ == "__main__":
    main()
