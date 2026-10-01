#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MỐC TỪ cho Bàn dựng và Dựng bằng lời: chép NGUYÊN VĂN từng âm tiết (giữ cả từ đệm "à, ờ, á, thì")
và mốc đầu-cuối của từng âm tiết, chạy offline trong VM Cowork.

Hai mô hình, đều giấy phép Apache 2.0 (tools/models/TAI-MODEL.md):
  - CHỮ: zipformer tiếng Việt của sherpa-onnx (VietASR, khoảng 70.000 giờ): ghi nguyên văn, giữ từ đệm.
  - MỐC: omnilingual-asr 300M CTC (Meta): căn khớp chữ vào tiếng [forced alignment], khung 20 ms.
Vì sao (thử nghiệm 2026-10-01 trên clip một dự án bài giảng, BAI-HOC chủ đề "Dựng bằng lời"):
  - mốc token của chính zipformer trôi tới 0,36 s theo điểm bắt đầu khúc, token đầu khúc luôn rơi vào khung 0;
  - chữ large-v3 bỏ phần lớn từ đệm (39 từ đệm so với 4) và có ảo giác, nên không dùng làm lớp chữ để dựng;
  - căn CTC: 73% điểm vào lời sau khoảng lặng lệch không quá 40 ms so với năng lượng tiếng, chạy lại
    với khúc dịch 0,3 s cho mốc y hệt.
large-v3 vẫn là bản gỡ băng cho phụ đề và đọc hiểu (tools/transcribe.py); file này không đụng tới nó.

Cách dùng (từ gốc xưởng):
  python3 tools/moc-tu.py "du-an/<x>" [--nguon "nguon/a.mp4" ...] [--gioi-han 150]
  Không truyền --nguon: lấy mọi file TIẾNG mà các timeline*.json của dự án dùng (audioSrc nếu có, không thì src).
  Chạy lại đúng lệnh tới khi báo "✓ Xong": mỗi lượt gọi lệnh trên máy giới hạn khoảng 180 s, tool làm
  từng khúc, lưu tạm, lượt sau làm tiếp. Bài 10 phút xong trong một lượt; bài 1 giờ khoảng ba lượt.

Đầu ra trong du-an/<x>/transcript/:
  <base>.tu.json          {"phienBan", "nguon", "moHinh", "nangLuong", "khuc", "tu": [{"w","s","e","c","k"}]}
                          w = âm tiết viết thường, s/e = giây trong file nguồn, c = độ tin cậy căn khớp (0-1),
                          k = số thứ tự khúc nói (khúc do VAD cắt, giữa hai khúc luôn có khoảng lặng)
  <base>.nang-luong.bin   năng lượng tiếng 100 lần mỗi giây, mỗi byte = dB + 100 (0 là câm, 100 là 0 dBFS),
                          dùng vẽ dạng sóng và hút điểm cắt (tools/ban_dung_loi.py)
  .moc-tu/<base>/         lưu tạm từng khúc; giữ lại cũng được, tool tự bỏ qua khi nguồn đổi
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time
import unicodedata
import wave

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if sys.platform.startswith("linux"):
    sys.path.insert(0, os.path.join(TOOLS_DIR, "pylib"))

import numpy as np  # noqa: E402

PHIEN_BAN = 1
SR = 16000
HZ = 100              # năng lượng: 100 khung mỗi giây
CTC_FR = 0.02         # omnilingual: 20 ms mỗi khung
KHUC_TOI_DA = 35.0    # omnilingual CTC nhận tối đa khoảng 40 s mỗi lượt
DEM = 0.25            # đệm hai đầu mỗi khúc khi nhận dạng và căn khớp
MO_HINH_CHU = "sherpa-onnx-zipformer-vi-int8-2025-04-20"
MO_HINH_MOC = "sherpa-onnx-omnilingual-asr-300M-ctc-int8-2025-11-12"


def chay(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def dau_van_tay(path):
    st = os.stat(path)
    return [st.st_size, int(st.st_mtime), PHIEN_BAN]


def tim_nguon(du_an):
    """Mọi file tiếng mà các timeline của dự án dùng (giữ thứ tự xuất hiện)."""
    tls = sorted(glob.glob(os.path.join(du_an, "timeline*.json")) +
                 glob.glob(os.path.join(du_an, "ke-hoach-dung", "timeline*.json")))
    ra = []
    for f in tls:
        try:
            tl = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for seg in tl.get("segments", []):
            if seg.get("type", "video") != "video":
                continue
            s = seg.get("audioSrc") or seg.get("src")
            if s and s not in ra:
                ra.append(s)
    return ra


def doc_wav(path):
    with wave.open(path, "rb") as f:
        assert f.getframerate() == SR and f.getnchannels() == 1
        return np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


def nang_luong(a):
    """dB theo cửa sổ 20 ms, bước 10 ms (100 Hz)."""
    hop = SR // HZ
    n = len(a) // hop
    x = np.pad(a, (0, hop * 2))
    sq = x.astype(np.float64) ** 2
    cs = np.concatenate([[0.0], np.cumsum(sq)])
    i = np.arange(n) * hop
    rms = np.sqrt((cs[i + 2 * hop] - cs[i]) / (2 * hop))
    db = 20 * np.log10(rms + 1e-9)
    return np.clip(np.round(db + 100), 0, 255).astype(np.uint8)


def cat_khuc(a):
    import sherpa_onnx
    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = os.path.join(TOOLS_DIR, "models", "silero_vad.onnx")
    cfg.silero_vad.threshold = 0.5
    cfg.silero_vad.min_silence_duration = 0.3
    cfg.silero_vad.min_speech_duration = 0.2
    cfg.silero_vad.max_speech_duration = KHUC_TOI_DA
    cfg.sample_rate = SR
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=KHUC_TOI_DA * 4)
    w = cfg.silero_vad.window_size
    ra = []

    def rut():
        while not vad.empty():
            ra.append([vad.front.start / SR, (vad.front.start + len(vad.front.samples)) / SR])
            vad.pop()
    for i in range(0, len(a), w):
        vad.accept_waveform(a[i:i + w])
        rut()
    vad.flush()
    rut()
    return [[round(s, 3), round(e, 3)] for s, e in ra]


class BoChu:
    def __init__(self):
        import sherpa_onnx
        d = os.path.join(TOOLS_DIR, "models", MO_HINH_CHU)
        self.rec = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=os.path.join(d, "encoder-epoch-12-avg-8.int8.onnx"),
            decoder=os.path.join(d, "decoder-epoch-12-avg-8.onnx"),
            joiner=os.path.join(d, "joiner-epoch-12-avg-8.int8.onnx"),
            tokens=os.path.join(d, "tokens.txt"), num_threads=4, decoding_method="greedy_search")

    def chep(self, x):
        st = self.rec.create_stream()
        st.accept_waveform(SR, x)
        self.rec.decode_stream(st)
        return [unicodedata.normalize("NFC", t.lower()) for t in st.result.text.split()]


class BoMoc:
    BLANK, SPACE = 0, 4

    def __init__(self):
        import onnxruntime as ort
        d = os.path.join(TOOLS_DIR, "models", MO_HINH_MOC)
        so = ort.SessionOptions()
        so.intra_op_num_threads = 4
        so.log_severity_level = 3
        self.m = ort.InferenceSession(os.path.join(d, "model.int8.onnx"), so, providers=["CPUExecutionProvider"])
        self.tok = {}
        for line in open(os.path.join(d, "tokens.txt"), encoding="utf-8"):
            line = line.rstrip("\n")
            if line:
                t, i = line.rsplit(" ", 1)
                self.tok.setdefault(t, int(i))

    def log_prob(self, x):
        x = (x - x.mean()) / (x.std() + 1e-7)
        y = self.m.run(None, {self.m.get_inputs()[0].name: x[None, :].astype(np.float32)})[0][0]
        y = y - y.max(-1, keepdims=True)
        return y - np.log(np.exp(y).sum(-1, keepdims=True))

    @staticmethod
    def viterbi(lp, labels):
        T = lp.shape[0]
        S = 2 * len(labels) + 1
        ext = np.zeros(S, dtype=np.int64)
        ext[1::2] = labels
        em = lp[:, ext]
        NEG = -1e18
        dp = np.full(S, NEG)
        dp[0] = em[0, 0]
        dp[1] = em[0, 1]
        bp = np.zeros((T, S), dtype=np.int8)
        nhay = np.zeros(S, bool)
        nhay[3::2] = ext[3::2] != ext[1:-2:2]
        for t in range(1, T):
            b = np.concatenate([[NEG], dp[:-1]])
            c = np.where(nhay, np.concatenate([[NEG, NEG], dp[:-2]]), NEG)
            st = np.stack([dp, b, c])
            k = st.argmax(0)
            dp = st[k, np.arange(S)] + em[t]
            bp[t] = k
        s = S - 1 if dp[S - 1] >= dp[S - 2] else S - 2
        path = np.zeros(T, dtype=np.int64)
        for t in range(T - 1, -1, -1):
            path[t] = s
            s -= int(bp[t, s])
        return path, em

    def can(self, x, t0, chu):
        """Trả [{w,s,e,c}] cho từng âm tiết; âm tiết không căn được thì s/e = None."""
        lp = self.log_prob(x)
        nhan, chu_cua = [], []
        for wi, w in enumerate(chu):
            if wi:
                nhan.append(self.SPACE)
                chu_cua.append(-1)
            for ch in w:
                if ch in self.tok:
                    nhan.append(self.tok[ch])
                    chu_cua.append(wi)
        ra = [{"w": w, "s": None, "e": None, "c": 0.0} for w in chu]
        if not nhan or 2 * len(nhan) + 1 > 2 * lp.shape[0]:
            return ra
        path, em = self.viterbi(lp, np.array(nhan))
        dau, cuoi, p = [None] * len(chu), [None] * len(chu), [[] for _ in chu]
        for t, s in enumerate(path):
            if s % 2 == 1:
                wi = chu_cua[s // 2]
                if wi >= 0:
                    dau[wi] = t if dau[wi] is None else dau[wi]
                    cuoi[wi] = t
                    p[wi].append(float(np.exp(em[t, s])))
        for wi in range(len(chu)):
            if dau[wi] is not None:
                ra[wi].update(s=round(t0 + dau[wi] * CTC_FR, 3), e=round(t0 + (cuoi[wi] + 1) * CTC_FR, 3),
                              c=round(float(np.mean(p[wi])), 3))
        return ra


def kiem_mo_hinh():
    thieu = [m for m in (MO_HINH_CHU, MO_HINH_MOC) if not os.path.isdir(os.path.join(TOOLS_DIR, "models", m))]
    if thieu:
        sys.exit("Thiếu model mốc lời trong tools/models/: " + ", ".join(thieu) +
                 ". Cách tải: tools/models/TAI-MODEL.md, mục \"Mốc âm tiết cho Bàn dựng và Dựng bằng lời\".")


def lam_mot_nguon(du_an, nguon, han_chot):
    src = os.path.join(du_an, nguon)
    if not os.path.isfile(src):
        print(f"  ✗ không thấy {nguon}")
        return False
    base = os.path.splitext(os.path.basename(src))[0]
    tdir = os.path.join(du_an, "transcript")
    tam = os.path.join(tdir, ".moc-tu", base)
    os.makedirs(tam, exist_ok=True)
    out_tu = os.path.join(tdir, f"{base}.tu.json")
    out_nl = os.path.join(tdir, f"{base}.nang-luong.bin")
    vt = dau_van_tay(src)
    if os.path.isfile(out_tu):
        try:
            if json.load(open(out_tu, encoding="utf-8")).get("vanTay") == vt:
                print(f"  ✓ {nguon}: đã có mốc từ")
                return True
        except ValueError:
            pass
    meta_p = os.path.join(tam, "meta.json")
    meta = json.load(open(meta_p, encoding="utf-8")) if os.path.isfile(meta_p) else {}
    if meta.get("vanTay") != vt:
        for f in glob.glob(os.path.join(tam, "k*.json")):
            os.replace(f, f + ".cu")
        meta = {"vanTay": vt}
    wav = os.path.join(tam, "a16.wav")
    if not os.path.isfile(wav) or meta.get("wav") != vt:
        print(f"  … {nguon}: tách tiếng 16 kHz")
        chay(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-vn", "-ac", "1",
              "-ar", str(SR), "-c:a", "pcm_s16le", wav])
        meta["wav"] = vt
    a = doc_wav(wav)
    if "khuc" not in meta:
        nl = nang_luong(a)
        with open(out_nl, "wb") as fh:
            fh.write(nl.tobytes())
        meta["san"] = round(float(np.percentile(nl.astype(np.float32) - 100, 10)), 1)
        meta["khuc"] = cat_khuc(a)
        print(f"  … {nguon}: {len(meta['khuc'])} khúc nói, sàn ồn {meta['san']} dB")
    json.dump(meta, open(meta_p, "w", encoding="utf-8"), ensure_ascii=False)
    khuc = meta["khuc"]
    con = [k for k in range(len(khuc)) if not os.path.isfile(os.path.join(tam, f"k{k:05d}.json"))]
    if con:
        chu, moc = BoChu(), BoMoc()
        for k in con:
            if time.time() > han_chot:
                print(f"  … {nguon}: còn {len([c for c in con if c >= k])}/{len(khuc)} khúc, chạy lại lệnh để làm tiếp")
                return False
            s, e = khuc[k]
            b = max(0.0, s - DEM)
            x = a[int(b * SR):int(min(len(a) / SR, e + DEM) * SR)]
            words = chu.chep(x)
            r = moc.can(x, b, words) if words else []
            for w in r:
                w["k"] = k
            json.dump(r, open(os.path.join(tam, f"k{k:05d}.json"), "w", encoding="utf-8"), ensure_ascii=False)
    tu = []
    for k in range(len(khuc)):
        tu += json.load(open(os.path.join(tam, f"k{k:05d}.json"), encoding="utf-8"))
    thieu = sum(1 for w in tu if w["s"] is None)
    # âm tiết không căn được: nội suy giữa hai láng giềng để vẫn bấm, nhảy tới được (c = 0)
    for i, w in enumerate(tu):
        if w["s"] is None:
            trai = next((tu[j]["e"] for j in range(i - 1, -1, -1) if tu[j]["e"] is not None), khuc[w["k"]][0])
            phai = next((tu[j]["s"] for j in range(i + 1, len(tu)) if tu[j]["s"] is not None), khuc[w["k"]][1])
            w["s"], w["e"] = round(trai, 3), round(max(trai, phai), 3)
    ket = {
        "phienBan": PHIEN_BAN, "nguon": nguon, "vanTay": vt,
        "moHinh": {"chu": MO_HINH_CHU, "moc": MO_HINH_MOC},
        "nangLuong": {"file": os.path.basename(out_nl), "hz": HZ, "san": meta["san"]},
        "khuc": khuc, "tu": tu,
    }
    tmp = out_tu + ".tmp"
    json.dump(ket, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, out_tu)
    print(f"  ✓ {nguon}: {len(tu)} âm tiết, {thieu} âm tiết nội suy, {len(khuc)} khúc")
    return True


def main():
    ap = argparse.ArgumentParser(description="Mốc từng âm tiết cho Dựng bằng lời")
    ap.add_argument("du_an")
    ap.add_argument("--nguon", action="append", help="file tiếng, tương đối với thư mục dự án; lặp được")
    ap.add_argument("--gioi-han", type=float, default=150, help="giây làm việc tối đa mỗi lượt")
    args = ap.parse_args()
    nguon = args.nguon or tim_nguon(args.du_an)
    if not nguon:
        sys.exit("Không tìm thấy file tiếng nào: truyền --nguon hoặc tạo timeline trước")
    kiem_mo_hinh()
    han = time.time() + args.gioi_han
    xong = all([lam_mot_nguon(args.du_an, n, han) for n in nguon])
    print("✓ Xong" if xong else "… chưa xong, chạy lại đúng lệnh")
    sys.exit(0 if xong else 3)


if __name__ == "__main__":
    main()
