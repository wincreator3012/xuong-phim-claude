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
        self.rt60 = 2.8        # mỗi bản đặt lại được (bản vui, nhịp nhanh dùng phòng ngắn)
        self.fade_out = 5.0    # giây mờ cuối (bản có nốt kết dứt khoát đặt ngắn hơn)

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

    def render(self, rt60=None, wet=1.0, seed=7):
        rt60 = self.rt60 if rt60 is None else rt60
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


def bản_piano_diu_dang(hat=1):
    """Piano dịu dàng, 66 nhịp, Đô trưởng: giai điệu đơn giản như bài ru ở âm vực cao, tay trái rải nhẹ, chuông nhỏ lấp lánh."""
    rng = np.random.default_rng(hat)
    bpm = 66
    B = beat_len(bpm)
    bar = 4 * B
    # hợp âm: (nốt bass, bốn nốt rải tăng dần)
    CH = dict(
        C=(48, [55, 60, 64, 67]), G=(43, [50, 55, 59, 62]), Am=(45, [52, 57, 60, 64]),
        F=(41, [53, 57, 60, 65]), CE=(40, [55, 60, 64, 67]), Dm=(38, [50, 57, 60, 65]),
        Em=(40, [55, 59, 62, 67]), Gs=(43, [50, 55, 60, 62]),
    )
    A_ch = ["C", "G", "Am", "F", "CE", "F", "Dm", "Gs"]
    A2_ch = ["C", "G", "Am", "F", "CE", "F", "Dm", "C"]
    B_ch = ["F", "G", "Em", "Am", "F", "CE", "Dm", "G"]
    A_mel = [
        [(0, 76, 1.5), (1.5, 79, .5), (2, 81, 1), (3, 79, 1)],
        [(0, 74, 1.5), (1.5, 76, .5), (2, 79, 2)],
        [(0, 76, 1), (1, 81, 1.5), (2.5, 79, .5), (3, 76, 1)],
        [(0, 76, 1.5), (1.5, 74, .5), (2, 72, 2)],
        [(0, 76, 1), (1, 79, 1), (2, 84, 2)],
        [(0, 81, 1.5), (1.5, 79, .5), (2, 77, 1), (3, 81, 1)],
        [(0, 81, 1), (1, 77, 1), (2, 76, 1), (3, 74, 1)],
        [(0, 74, 2), (2, 71, 2)],
    ]
    A2_mel = A_mel[:7] + [[(0, 72, 4)]]
    B_mel = [
        [(0, 84, 2), (2, 81, 1), (3, 84, 1)],
        [(0, 83, 2), (2, 79, 2)],
        [(0, 79, 1), (1, 83, 1), (2, 81, 1), (3, 79, 1)],
        [(0, 76, 2), (2, 81, 2)],
        [(0, 81, 1.5), (1.5, 79, .5), (2, 77, 2)],
        [(0, 76, 1), (1, 79, 1), (2, 76, 2)],
        [(0, 77, 1), (1, 81, 1), (2, 79, 1), (3, 77, 1)],
        [(0, 74, 1), (1, 76, 1), (2, 74, 2)],
    ]
    # hình thức: dạo 2 ô nhịp, lượt 1 (A A' B A'), lượt 2 (A B A') có chuông
    plan = [("intro", [], ["C", "G"], False)]
    plan += [("A", A_mel, A_ch, False), ("A2", A2_mel, A2_ch, False), ("B", B_mel, B_ch, False), ("A2", A2_mel, A2_ch, False)]
    plan += [("A", A_mel, A_ch, True), ("B", B_mel, B_ch, True), ("A2", A2_mel, A2_ch, True)]
    nbar = sum(len(p[2]) for p in plan)
    total = nbar * bar + 8
    mix = Mix(total)
    arp = [None, 0, 1, 2, 3, 2, 1, 2]
    bi = 0
    for name, mel, chs, bells in plan:
        for k, cname in enumerate(chs):
            t0 = bi * bar
            bass, notes = CH[cname]
            mix.add(piano(bass, bar * 0.95, vel=0.36, rng=rng, ring=1.2), t0 + human(rng, 8), pan=-0.3, send=0.25)
            for j in range(1, 8):
                note = notes[arp[j]]
                mix.add(piano(note, B * 0.9, vel=0.20 + 0.06 * rng.random(), rng=rng, ring=1.0), t0 + j * B / 2 + human(rng, 8), pan=-0.1, send=0.3)
            if mel:
                for (b0, m, d) in mel[k]:
                    t = t0 + b0 * B + human(rng, 10)
                    mix.add(piano(m, d * B * 0.95, vel=0.46, rng=rng, ring=1.6), t, pan=0.15, send=0.35)
                    if bells and rng.random() < 0.55:
                        mix.add(mallet(m + 12, vel=0.15), t + 0.01, pan=0.3, send=0.4)
            if bells and k % 2 == 0:
                sp = [72, 76, 79, 84][int(rng.integers(0, 4))] + 12
                mix.add(bell(sp, vel=0.12, L=4.0), t0 + float(rng.choice([1.5, 2.5, 3.5])) * B, pan=float(rng.uniform(-0.4, 0.4)), send=0.5)
            bi += 1
    t_end = nbar * bar
    for k, n in enumerate([48, 55, 60, 64, 67, 72]):
        mix.add(piano(n, 3, vel=0.34 - 0.02 * k, rng=rng, ring=3.0), t_end + k * 0.14, pan=-0.1 + 0.05 * k, send=0.4)
    mix.add(bell(91, vel=0.14, L=5.0), t_end + 1.0, pan=0.3, send=0.5)
    return mix, total


# ---------------------------------------------------------------- bản Halloween vui (nhạc cụ riêng của bản)

def _xylo(m, vel=0.5, L=0.9):
    f = mtof(m)
    t = np.arange(int(L * SR)) / SR
    sig = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.17)
           + 0.35 * np.sin(2 * np.pi * f * 3.0 * t) * np.exp(-t / 0.07)
           + 0.12 * np.sin(2 * np.pi * f * 6.0 * t) * np.exp(-t / 0.03))
    sig *= 1 - np.exp(-t / 0.0015)
    return sig * vel * 0.8


def _kick(vel=0.7):
    n = int(0.28 * SR)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.11) * (1 - np.exp(-t / 0.002)) * vel


def _snap(vel=0.5, rng=None):
    rng = rng or np.random.default_rng(2)
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    x = sosfilt(butter(2, [900, 5200], btype="band", fs=SR, output="sos"), rng.standard_normal(n))
    env = np.exp(-t / 0.035) * 0.6 + np.where(t > 0.012, np.exp(-np.clip(t - 0.012, 0, None) / 0.03), 0) * 0.4
    return x * env * vel


def _wood(m=84, vel=0.4):
    f = mtof(m)
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.3 * t)) * np.exp(-t / 0.02) * vel * 0.6


def _ghost(m, dur, vel=0.3, glide_from=None, vib=5.5, glide_t=0.18):
    """Tiếng ma hú kiểu theremin: sóng sin có vuốt cao độ và rung chậm dần vào."""
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    f = mtof(m) * np.ones(n)
    if glide_from is not None:
        f = np.where(t < glide_t, mtof(glide_from) + (mtof(m) - mtof(glide_from)) * (t / glide_t), f)
    f = f * (1 + 0.012 * np.minimum(1, t / 0.4) * np.sin(2 * np.pi * vib * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.08) * np.where(t > dur, np.exp(-(t - dur) / 0.12), 1.0)
    return sig * env * vel


def bản_halloween_vui(hat=1):
    """Halloween vui nhộn, 112 nhịp, La thứ nhảy nhót kiểu oom-pah: bass gảy, đàn gảy đánh nghịch phách,
    xylophone chạy giai điệu có nốt nửa cung "ma quái", đoạn giữa sáng lên (Đô trưởng), đoạn tiếng ma hú rón rén,
    kết bằng cú hú tụt xuống, một nhát đàn dứt khoát rồi hộp nhạc ru dịu khép bằng hợp âm La trưởng."""
    rng = np.random.default_rng(hat)
    bpm = 112
    B = beat_len(bpm)
    bar = 4 * B
    CH = {
        "Am": (45, 52, [57, 60, 64]), "Dm": (50, 57, [57, 62, 65]), "F": (41, 48, [57, 60, 65]),
        "E7": (40, 47, [56, 59, 62, 64]), "C": (48, 55, [55, 60, 64]), "G": (43, 50, [55, 59, 62]),
    }
    MA = {  # giai điệu Phần A, mỗi ô nhịp: (phách, nốt, độ dài theo phách)
        "Am": [(0, 69, .5), (.5, 72, .5), (1, 76, 1), (2.5, 75, .5), (3, 76, .5), (3.5, 72, .5)],
        "Am2": [(0, 69, .5), (.5, 72, .5), (1, 76, 1), (2.5, 74, .5), (3, 72, .5), (3.5, 71, .5)],
        "F": [(0, 69, .5), (.5, 72, .5), (1, 77, 1), (2.5, 76, .5), (3, 74, .5), (3.5, 72, .5)],
        "E7": [(0, 71, .5), (.5, 74, .5), (1, 76, 1), (2, 68, 1), (3, 71, 1)],
        "Dm": [(0, 69, .5), (.5, 74, .5), (1, 77, 1), (2.5, 76, .5), (3, 74, .5), (3.5, 72, .5)],
        "E7b": [(0, 71, .5), (.5, 68, .5), (1, 71, .5), (1.5, 74, .5), (2, 76, 1), (3, 75, .5), (3.5, 76, .5)],
        "Amend": [(0, 69, 2), (2.5, 64, .5), (3, 69, .5), (3.5, 72, .5)],
    }
    MB = {  # Phần B sáng
        "C": [(0, 72, .5), (.5, 76, .5), (1, 79, 1), (2, 77, .5), (2.5, 76, .5), (3, 74, 1)],
        "G": [(0, 74, .5), (.5, 79, .5), (1, 83, 1), (2, 81, .5), (2.5, 79, .5), (3, 78, 1)],
        "F": [(0, 72, .5), (.5, 77, .5), (1, 81, 1), (2, 79, .5), (2.5, 77, .5), (3, 76, 1)],
        "E7": [(0, 71, .5), (.5, 74, .5), (1, 76, .5), (1.5, 80, .5), (2, 83, 1), (3, 80, 1)],
        "Cend": [(0, 72, .5), (.5, 76, .5), (1, 79, 1), (2, 84, 1), (3, 79, .5), (3.5, 76, .5)],
    }
    A1 = [("Am", "Am"), ("Am", "Am2"), ("F", "F"), ("E7", "E7"), ("Am", "Am"), ("Dm", "Dm"), ("E7", "E7b"), ("Am", "Amend")]
    BB = [("C", "C"), ("G", "G"), ("F", "F"), ("E7", "E7"), ("C", "C"), ("G", "G"), ("F", "F"), ("E7", "E7")]
    CC = [("Am", None), ("Am", None), ("Dm", None), ("E7", None), ("Am", None), ("Dm", None), ("E7", None), ("Am", None)]
    ghost = [  # (ô nhịp trong đoạn C, phách, nốt, dài phách, vuốt từ)
        (0, 0, 69, 3.0, 64), (1, 0, 72, 1.5, None), (1, 2, 71, 2.0, None), (2, 0, 74, 3.0, 69), (3, 0, 76, 2.0, None), (3, 2, 75, 2.0, None),
        (4, 0, 69, 3.0, 64), (5, 0, 77, 1.5, None), (5, 2, 76, 2.0, None), (6, 0, 74, 1.5, None), (6, 2, 71, 2.0, 76), (7, 0, 69, 3.5, None),
    ]
    plan = [("intro", [("Am", None), ("Am", None)]), ("A1", A1), ("A2", A1), ("B1", BB), ("A3", A1), ("C", CC), ("A4", A1)]
    nbar = sum(len(p[1]) for p in plan) + 6  # + phần kết có hộp nhạc
    total = nbar * bar + 8
    mix = Mix(total)
    mix.rt60 = 1.3
    mix.fade_out = 1.2
    bi = 0
    for name, bars in plan:
        for k, (cname, mkey) in enumerate(bars):
            t0 = bi * bar
            root, fifth, notes = CH[cname]
            full = name != "intro"
            ghostly = name == "C"
            # bass gảy: gốc phách 1, quãng năm phách 3 (oom-pah)
            mix.add(pluck(root, vel=0.62, g=0.992, variant=int(rng.integers(0, 3)), L=1.1), t0 + human(rng, 4), pan=-0.25, send=0.08)
            mix.add(pluck(fifth, vel=0.5, g=0.992, variant=int(rng.integers(0, 3)), L=1.0), t0 + 2 * B + human(rng, 4), pan=-0.25, send=0.08)
            if name.startswith("A") or name.startswith("B"):
                mix.add(pluck(root + 12, vel=0.28, g=0.99, variant=1, L=0.6), t0 + 3.5 * B + human(rng, 4), pan=-0.2, send=0.08)
            # đàn gảy đánh nghịch phách (phách 2 và 4)
            if full and not ghostly:
                for beat in (1, 3):
                    for j, nn in enumerate(notes):
                        mix.add(pluck(nn, vel=0.22 + 0.04 * rng.random(), g=0.985, variant=2, L=0.5),
                                t0 + beat * B + j * 0.011 + human(rng, 4), pan=0.25, send=0.12)
            # nhịp: kick phách 1-3, snap phách 2-4, shaker nửa phách, mộc ở nghịch phách
            for beat in range(4):
                tt = t0 + beat * B
                if full and not ghostly:
                    if beat in (0, 2):
                        mix.add(_kick(0.55), tt, send=0.02)
                    else:
                        mix.add(_snap(0.30, rng), tt + human(rng, 3), pan=0.1, send=0.1)
                elif ghostly and beat in (0, 2):
                    mix.add(_kick(0.30), tt, send=0.02)
                for h in (0, 0.5):
                    if full or h == 0.5:
                        mix.add(shaker(vel=0.10 + 0.06 * rng.random() * (1 if h else 0.6), rng=rng), tt + h * B, pan=0.35, send=0.05)
                if (not full) or name in ("A2", "A4") or ghostly:
                    if beat in (1, 3):
                        mix.add(_wood(88 if beat == 1 else 84, 0.30), tt + 0.5 * B, pan=-0.3, send=0.1)
            # giai điệu
            if mkey and name != "intro":
                mel = (MB if name.startswith("B") else MA)[mkey]
                hi = 12 if name in ("A2", "A4") else 0
                for (b0, m, d) in mel:
                    tt = t0 + b0 * B + human(rng, 5)
                    mix.add(_xylo(m, vel=0.40), tt, pan=0.15, send=0.15)
                    if name in ("A2", "B1", "B2", "A4"):
                        mix.add(mallet(m + 12, vel=0.15, L=0.8), tt + 0.01, pan=0.35, send=0.25)
                    if hi and rng.random() < 0.5:
                        mix.add(bell(m + 12, vel=0.10, L=1.6), tt, pan=-0.3, send=0.35)
            # tiếng ma hú ở cuối các lượt A3 để chuyển sang đoạn giữa
            if name == "A3" and k == 7:
                mix.add(_ghost(81, 1.0, vel=0.22, glide_from=69, glide_t=0.5), t0 + 2 * B, pan=0.0, send=0.35)
            bi += 1
        if name == "C":
            t_c = (bi - 8) * bar
            for (kb, beat, m, d, gf) in ghost:
                mix.add(_ghost(m, d * B * 0.95, vel=0.20, glide_from=gf), t_c + kb * bar + beat * B, pan=0.1, send=0.45)
    # kết: cú hú tụt xuống, nhát dứt khoát, rồi hộp nhạc ru dịu và hợp âm La trưởng (lên tông sáng cho cái kết gia đình)
    t_end = bi * bar
    mix.add(_ghost(52, 1.9 * B, vel=0.24, glide_from=88, glide_t=1.4 * B, vib=6.5), t_end, pan=0.0, send=0.4)
    t_hit = t_end + 2 * B
    for nn, g in ((45, 0.7), (57, 0.5), (60, 0.42), (64, 0.42)):
        mix.add(pluck(nn, vel=g, g=0.995, variant=0, L=2.0), t_hit, pan=-0.1 + 0.05 * (nn % 3), send=0.2)
    mix.add(_kick(0.7), t_hit, send=0.02)
    mix.add(bell(93, vel=0.16, L=3.0), t_hit + 0.02, pan=0.3, send=0.5)
    mix.add(_xylo(81, vel=0.5), t_hit + 0.02, pan=0.2, send=0.3)
    t_box = t_hit + 1.5 * B
    for k, nn in enumerate((69, 72, 76, 81)):
        mix.add(bell(nn + 12, vel=0.17, L=2.4), t_box + k * B, pan=-0.2 + 0.15 * k, send=0.55)
        mix.add(mallet(nn, vel=0.22, L=1.4), t_box + k * B, pan=0.2, send=0.4)
    t_fin = t_box + 4.5 * B
    for nn, g in ((57, 0.20), (64, 0.18), (69, 0.20), (73, 0.20), (76, 0.20)):
        mix.add(bell(nn + 12, vel=g, L=5.0), t_fin, pan=0.0, send=0.6)
    mix.add(pad([45, 57, 61, 64], 4.0, att=0.4, rel=3.0, vel=0.12, bright=0.3, seed=99), t_fin, send=0.4)
    mix.fade_out = 3.2
    return mix, total



BAN = {
    "xuong-guitar-am": (bản_guitar_am, "acoustic-am", "Guitar mộc ấm, Đô trưởng, 72 nhịp"),
    "xuong-piano-tinh": (bản_piano_tinh, "piano-tinh-lang", "Piano trầm lắng, Rê thứ, 58 nhịp"),
    "xuong-thien-pad": (bản_thien_pad, "thien-ambient", "Nền thiền Rê, thảm âm và chuông thưa, không nhịp"),
    "xuong-nhe-sang": (bản_nhe_sang, "nang-luong-nhe", "Sáng và nhẹ, Son trưởng, 100 nhịp"),
    "xuong-halloween-vui": (bản_halloween_vui, "nang-luong-nhe", "Halloween vui nhộn, La thứ oom-pah, 112 nhịp, xylophone và tiếng ma hú"),
    "xuong-piano-diu-dang": (bản_piano_diu_dang, "piano-tinh-lang", "Piano dịu dàng, Đô trưởng, 66 nhịp, âm vực cao, chuông nhỏ"),
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


def hoan_thien(stereo, ten, ra, muc=-15.0, fade_out=5.0):
    import wave
    n = stereo.shape[1]
    # cắt đuôi im, fade
    env = np.abs(stereo).max(axis=0)
    idx = np.where(env > 1e-4)[0]
    n = min(n, int(idx[-1]) + int(0.2 * SR)) if len(idx) else n
    x = stereo[:, :n].copy()
    fi = int(0.8 * SR)
    fo = int(fade_out * SR)
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
    kq = hoan_thien(st, a.ban, a.ra, fade_out=mix.fade_out)
    kq["nhom"] = nhom
    kq["mo_ta"] = mt
    kq["hat"] = a.hat
    print(json.dumps(kq, ensure_ascii=False))


if __name__ == "__main__":
    main()
