#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DÀN GÓC MULTICAM: nhận diện ai đang nói, chia session theo transcript, đề xuất chuỗi cắt góc
theo thực hành podcast/multicam hiệu quả, sinh timeline nháp cho assemble.py.

Cách dùng (từ gốc "xuong-phim-claude", sau multicam-khop.py và transcript của tiếng chủ):
  python3 tools/multicam-dan.py "../Du an/<x>" --transcript "<tên file transcript không đuôi>"
      [--che-do auto|podcast|bai-giang] [--phut 8] [--khong-session] [--tieng "nguon/tieng-chu.wav"]
      [--nguoi-noi auto|tieng|hinh|<file.json>] [--khoa overlay.json] [--cua-so A-B --hau-to clip1]
      [--gioi-han 150]

  --nguoi-noi  auto (mặc định): so năng lượng mic gần; nếu > 30% thời gian nói bị nhận là 'chong'
               (tiếng các góc gần như giống nhau: một mic tốt thu cả phòng, hoặc mỗi máy thu lọt tiếng
               người kia) thì tự chuyển sang 'hinh' - so CHUYỂN ĐỘNG mặt/tay ở từng góc cận.
               <file.json>: danh sách lượt nói soạn tay [{"start","end","ai"}] (trục chung).
  --khoa       JSON {"overlay": [{"src": "do-hoa/ngang/p01.webm", "at": <giây trục chung>, "dur": <giây>,
               "goc": "<góc bắt buộc, tuỳ chọn - ví dụ bảng tên>"}]}: mọi điểm cắt tránh khung
               [at - 0.25, at + dur + 0.25]; overlay được gắn sẵn vào segment chứa nó (at tương đối).
  --cua-so     chỉ dàn góc trong quãng A-B giây của trục chung (một buổi quay → nhiều clip độc lập);
               --hau-to thêm vào tên file đầu ra (DAN-GOC-clip1.md, timeline-multicam-nhap-clip1.json).
  --gioi-han   giây tối đa cho một lượt đo chuyển động (mỗi lượt gọi lệnh trên máy bị giới hạn ~180 s);
               phần đã đo được cache trong multicam/.chuyen-dong/, chạy lại đúng lệnh để đo tiếp.

Đầu vào: Du an/<x>/multicam.json (offset từng file), transcript/<tên>.transcript.json + .silences.json
  (transcript chạy trên TIẾNG CHỦ - nguon/tieng-chu.wav nếu đã --tron-tieng, hoặc file góc chủ).
Đầu ra: Du an/<x>/multicam/
  nguoi-noi.json          ai nói khi nào (podcast) - từ so năng lượng mic gần từng người
  session.json            ranh giới session + từ khoá + câu mở (Claude đặt tên rồi user duyệt)
  DAN-GOC.md              bảng duyệt: session, từng cú cắt (mốc, góc, lý do)
  timeline-multicam-nhap.json  segments có src góc + in/out theo file góc + audioSrc/audioIn theo
                          tiếng chủ; insert SectionTitle giữa các session; chapter
  job-session.json        job render SectionTitle cho từng session (render-do-hoa.mjs)

Luật cắt (rút từ thực hành podcast/multicam và nghiên cứu chú ý thị giác - xem
references/dan-goc-multicam.md của skill phim-multicam):
  PODCAST  cận người đang nói là mặc định; không đổi góc cho lượt nói < 1.5 s ("vâng", "đúng");
           cắt sang người mới 0.4 s SAU khi họ bắt đầu nói (tiếng dẫn hình - J-cut tự nhiên);
           lượt nói dài > 25 s: xen phản ứng người nghe 2.5-3.5 s tại chỗ ngắt hơi, hoặc góc toàn;
           hai người nói chồng > 1.5 s → góc toàn; mở/đóng session bằng góc toàn 4-6 s;
           giữ tối thiểu 3 s, tối đa 30 s trên một góc.
  BÀI GIẢNG (một người, nhiều góc) góc chính ~60%, góc phụ ~30%, toàn ~10%; đổi góc tại
           ranh giới câu sau khoảng ngắt hơi ≥ 0.6 s, mỗi góc giữ 12-25 s; ưu tiên đổi cỡ cảnh
           theo hướng VÀO (toàn → trung → cận) hơn hướng RA; mở session bằng toàn.
  Mọi điểm cắt hút về khoảng lặng của tiếng chủ (±0.6 s) - assemble dùng snap:false vì đã hút.
"""
import argparse
import json
import math
import os
import re
import subprocess

# Thư viện Python cài riêng vào tools/pylib (tools/cai-dat.py lo việc này) - VM Cowork
# không giữ pip install qua các phiên, nên thư viện phải nằm trong thư mục xưởng.
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylib"))
import numpy as np

SR = 8000
HOP = 800          # 0.1 s
CUE = ["tiếp theo", "phần tiếp", "chuyển sang", "câu hỏi tiếp", "bây giờ chúng ta", "bước tiếp",
       "điểm thứ", "phần thứ", "cuối cùng", "tóm lại", "kết lại", "quay lại", "nói về", "chủ đề"]


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"! Lệnh lỗi: {' '.join(cmd)}\n{p.stderr.decode(errors='ignore')[-600:]}")
    return p


def audio_env_db(path):
    p = sh(["ffmpeg", "-hide_banner", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
            "-f", "s16le", "-acodec", "pcm_s16le", "-"])
    x = np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    n = len(x) // HOP
    e = (x[: n * HOP].reshape(n, HOP) ** 2).mean(axis=1)
    return 10 * np.log10(e + 1e-10)


def load_json(p, default=None):
    if os.path.isfile(p):
        return json.load(open(p, encoding="utf-8"))
    return default


def fmt(t):
    return f"{int(t // 60):02d}:{t % 60:04.1f}"


# ---------------------------------------------------------------- ai đang nói
def detect_speakers(project, mc, total):
    """Trả mảng nhãn theo 0.1 s: tên góc cận có mic to nhất (so với sàn riêng), 'chong' khi >= 2
    góc cùng to, None khi im. Chỉ dùng góc loai=can có tiếng."""
    n = int(math.ceil(total * 10)) + 1
    tracks = {}
    for g in mc["goc"]:
        if g["loai"] != "can":
            continue
        act = np.full(n, np.nan, dtype=np.float32)
        for fe in g["files"]:
            if fe.get("offset") is None:
                continue
            db = audio_env_db(os.path.join(project, fe["file"]))
            floor = np.percentile(db, 20)
            a = db - floor                       # dB trên sàn của chính mic đó
            k0 = int(round(fe["offset"] * 10))
            for k in range(len(a)):
                j = k0 + k
                if 0 <= j < n:
                    act[j] = a[k]
        tracks[g["ten"]] = act
    if len(tracks) < 2:
        return None, tracks
    names = list(tracks)
    A = np.vstack([tracks[nm] for nm in names])          # (góc, thời gian)
    A = np.where(np.isnan(A), -1e3, A)
    labels = [None] * n
    for j in range(n):
        col = A[:, j]
        order = np.argsort(col)[::-1]
        top, sec = col[order[0]], col[order[1]]
        if top < 6:
            continue
        if top - sec < 3 and sec >= 6:
            labels[j] = "chong"
        else:
            labels[j] = names[order[0]]
    # làm trơn: cửa sổ 0.7 s lấy nhãn phổ biến nhất, rồi xoá run < 1.0 s
    def smooth(lbl, w=7):
        out = list(lbl)
        for j in range(len(lbl)):
            win = [x for x in lbl[max(0, j - w // 2): j + w // 2 + 1] if x]
            out[j] = max(set(win), key=win.count) if win else None
        return out
    labels = smooth(labels)
    runs = []
    for j, l in enumerate(labels):
        if runs and runs[-1][2] == l:
            runs[-1][1] = j + 1
        else:
            runs.append([j, j + 1, l])
    # gộp run ngắn vào run trước
    merged = []
    for r in runs:
        if merged and (r[1] - r[0]) < 10 and r[2] != "chong":
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    turns = [{"start": round(a / 10, 1), "end": round(b / 10, 1), "ai": l} for a, b, l in merged if l]
    return turns, tracks


# ---------------------------------------------------------------- ai đang nói: theo chuyển động hình
MOTION_FPS = 5
MOTION_CHUNK = 300.0   # giây mỗi mảnh cache: mỗi lượt gọi lệnh trên máy có giới hạn thời gian


def probe_dur(path):
    p = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(p.stdout.decode().strip() or 0)


def motion_file(path, cache_dir, deadline):
    """Năng lượng chuyển động 5 lần/giây của một file góc cận: trung bình |khung - khung trước| trên
    ảnh xám 64x36, bỏ viền hai bên và dải đáy (giữ vùng mặt + tay). Cache từng mảnh 300 s."""
    import time
    dur = probe_dur(path)
    key = re.sub(r"[^\w.-]", "_", os.path.basename(os.path.dirname(path)) + "_" + os.path.basename(path))
    parts, k = [], 0
    while k * MOTION_CHUNK < dur:
        cf = os.path.join(cache_dir, f"{key}.{k:03d}.npy")
        if not os.path.isfile(cf):
            if time.time() > deadline:
                return None
            w, h = 64, 36
            p = sh(["ffmpeg", "-hide_banner", "-v", "error", "-ss", str(k * MOTION_CHUNK), "-t", str(MOTION_CHUNK),
                    "-i", path, "-an", "-vf", f"fps={MOTION_FPS},scale={w}:{h},format=gray",
                    "-f", "rawvideo", "-pix_fmt", "gray", "-"])
            x = np.frombuffer(p.stdout, dtype=np.uint8)
            x = x[: (len(x) // (w * h)) * w * h].reshape(-1, h, w).astype(np.float32)
            x = x[:, : int(h * 0.9), int(w * 0.12): int(w * 0.88)]
            d = np.abs(np.diff(x, axis=0)).mean(axis=(1, 2)) if len(x) > 1 else np.zeros(0, dtype=np.float32)
            d = np.concatenate([[d[0] if len(d) else 0.0], d]).astype(np.float32)
            np.save(cf, d)
        parts.append(np.load(cf))
        k += 1
    return np.concatenate(parts) if parts else np.zeros(0, dtype=np.float32)


def detect_speakers_motion(project, mc, total, cache_dir, budget=150.0):
    """Ai đang nói theo CHUYỂN ĐỘNG ở từng góc cận: người nói cử động miệng, đầu, tay nhiều hơn người
    nghe. Mỗi góc chuẩn hoá theo trung vị của chính nó (bù khác biệt cỡ cảnh, ánh sáng), làm trơn 5 s,
    góc lớn hơn rõ rệt (>= 1.15 lần) là người nói; vùng lưỡng lự giữ người đang nói; lượt < 4 s nhập
    lượt trước. Trả (turns, tracks); turns None khi chưa đo xong trong giới hạn thời gian."""
    import time
    deadline = time.time() + budget
    os.makedirs(cache_dir, exist_ok=True)
    n = int(math.ceil(total)) + 1                 # lưới 1 s
    tracks = {}
    for g in mc["goc"]:
        if g["loai"] != "can":
            continue
        act = np.full(n, np.nan, dtype=np.float32)
        for fe in g["files"]:
            if fe.get("offset") is None or not fe.get("co_hinh", True):
                continue
            m = motion_file(os.path.join(project, fe["file"]), cache_dir, deadline)
            if m is None:
                return None, None
            sec = len(m) // MOTION_FPS
            per_s = m[: sec * MOTION_FPS].reshape(sec, MOTION_FPS).mean(axis=1)
            k0 = int(round(fe["offset"]))
            for k in range(sec):
                if 0 <= k0 + k < n:
                    act[k0 + k] = per_s[k]
        med = float(np.nanmedian(act)) if np.any(~np.isnan(act)) else 0.0
        tracks[g["ten"]] = act / (med if med > 0 else 1.0)
    if len(tracks) < 2:
        return [], tracks
    names = list(tracks)
    A = np.where(np.isnan(np.vstack([tracks[nm] for nm in names])), 0.0, np.vstack([tracks[nm] for nm in names]))
    ker = np.ones(5) / 5
    S = np.vstack([np.convolve(a, ker, mode="same") for a in A])
    labels, cur = [None] * n, None
    for j in range(n):
        col = S[:, j]
        order = np.argsort(col)[::-1]
        top, sec_ = col[order[0]], col[order[1]]
        if top > 0 and (sec_ <= 0 or top / sec_ >= 1.15):
            cur = names[order[0]]
        labels[j] = cur
    runs = []
    for j, lb in enumerate(labels):
        if runs and runs[-1][2] == lb:
            runs[-1][1] = j + 1
        else:
            runs.append([j, j + 1, lb])
    merged = []
    for r in runs:
        if merged and ((r[1] - r[0]) < 4 or merged[-1][2] == r[2]):
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    turns = [{"start": float(a), "end": float(b), "ai": lb, "nguon": "hinh"} for a, b, lb in merged if lb]
    return turns, tracks


# ---------------------------------------------------------------- khoá overlay: không cắt ngang pill/bảng tên
LOCK_MARGIN = 0.25


def load_locks(path):
    d = load_json(path, {})
    items = d.get("overlay", []) if isinstance(d, dict) else d
    return sorted(({"src": o["src"], "at": float(o["at"]), "dur": float(o["dur"]), "goc": o.get("goc")}
                   for o in items), key=lambda o: o["at"])


def apply_locks(shots, locks, lo, hi):
    """Dời mọi điểm cắt rơi vào [at - 0.25, at + dur + 0.25] của một overlay ra mép gần nhất; không
    dời được (cú bên cạnh quá ngắn) thì nhập hai cú. Overlay có 'goc' bắt buộc (bảng tên người nói)
    rơi vào cú xen (phản ứng, toàn) thì đổi cú đó sang góc yêu cầu; rơi vào cú cận người nói khác
    thì cảnh báo (bảng tên đặt sai lượt nói)."""
    def inside(t):
        for o in locks:
            a, b = o["at"] - LOCK_MARGIN, o["at"] + o["dur"] + LOCK_MARGIN
            if a < t < b:
                return a, b
        return None
    for _ in range(8):
        changed, i = False, 0
        while i < len(shots) - 1:
            t = shots[i]["end"]
            box = inside(t)
            if box:
                left, right = box[0] - 0.02, box[1] + 0.02
                can_l = left - shots[i]["start"] >= 1.5 and left > lo
                can_r = shots[i + 1]["end"] - right >= 1.5 and right < hi
                if can_l and (not can_r or t - left <= right - t):
                    nt = left
                elif can_r:
                    nt = right
                else:
                    shots[i]["end"] = shots[i + 1]["end"]
                    shots[i]["ly_do"] += " (nhập cú sau: không cắt ngang overlay)"
                    del shots[i + 1]
                    changed = True
                    continue
                shots[i]["end"] = shots[i + 1]["start"] = round(nt, 2)
                changed = True
            i += 1
        if not changed:
            break
    warns = []
    for o in locks:
        if not o.get("goc"):
            continue
        s_ = next((x for x in shots if x["start"] <= o["at"] < x["end"]), None)
        if s_ and s_["goc"] != o["goc"]:
            if s_["ly_do"].startswith("cận người nói"):
                warns.append(f"{os.path.basename(o['src'])} tại {fmt(o['at'])} cần góc {o['goc']} nhưng lúc đó "
                             f"{s_['goc']} đang nói - dời mốc bảng tên vào lượt nói của {o['goc']}")
            else:
                s_["goc"] = o["goc"]
                s_["ly_do"] += f" (đổi sang {o['goc']} cho {os.path.basename(o['src'])})"
    return shots, warns


def refill_long(shots, locks, angles, wide, snap, max_hold=32.0):
    """Sau khi khoá overlay, vài cú xen bị gỡ khiến cận người nói kéo dài > 32 s. Chèn lại cú xen
    3-4 s (phản ứng người nghe xen kẽ góc toàn) ở chỗ trống không đụng overlay nào."""
    def free(a, b):
        return all(not (a < o["at"] + o["dur"] + LOCK_MARGIN and b > o["at"] - LOCK_MARGIN) for o in locks)
    out, k = [], 0
    for sh_ in shots:
        if not sh_["ly_do"].startswith("cận người nói") or sh_["end"] - sh_["start"] <= max_hold:
            out.append(sh_)
            continue
        others = [g for g in angles.values() if g != sh_["goc"]]
        pos = sh_["start"]
        while sh_["end"] - pos > max_hold:
            cut = None
            cands = sorted((pos + 12 + 0.5 * i for i in range(int((sh_["end"] - pos - 20) / 0.5) + 1)),
                           key=lambda x: abs(x - (pos + 22)))
            for base in cands:
                t = snap(base, 0.5)
                if t < pos + 10 or t > sh_["end"] - 8:
                    continue
                if free(t - 0.3, t + 3.6 + (k % 3) * 0.4):
                    cut = t
                    break
            if cut is None:
                break
            react = others[k % len(others)] if others and (k % 2 == 0 or not wide) else wide
            r_end = round(cut + 3.2 + (k % 3) * 0.4, 2)
            out.append({**sh_, "start": round(pos, 2), "end": round(cut, 2)})
            out.append({"start": round(cut, 2), "end": r_end, "goc": react,
                        "ly_do": "phản ứng người nghe (chèn sau khoá overlay)" if react != wide else "góc toàn xen giữa lượt dài (chèn sau khoá overlay)"})
            pos, k = r_end, k + 1
        out.append({**sh_, "start": round(pos, 2)})
    return out


def fix_long_reactions(shots, bounds, max_react=5.0):
    """Khoá overlay có thể kéo một cú xen (phản ứng/toàn) từ 3 s thành 8-23 s trong lúc người kia đang nói.
    Cú xen dài quá max_react được trả về cho người nói (nhập vào cú cận liền trước); refill_long sẽ chèn
    lại cú xen ngắn ở chỗ trống nếu cú cận thành quá dài. Không nhập vắt qua ranh giới session (thẻ chương)."""
    def is_react(x):
        return x["ly_do"].startswith("phản ứng") or x["ly_do"].startswith("góc toàn xen giữa lượt dài")
    bset = set(round(b, 2) for b in bounds)
    out = []
    for sh_ in shots:
        if (is_react(sh_) and sh_["end"] - sh_["start"] > max_react and out
                and not is_react(out[-1]) and out[-1]["goc"] != sh_["goc"]
                and abs(out[-1]["end"] - sh_["start"]) < 0.05):
            out[-1]["end"] = sh_["end"]
            out[-1]["ly_do"] += " (cú xen dài bị khoá overlay: trả về người nói)"
            continue
        if (out and out[-1]["goc"] == sh_["goc"] and abs(out[-1]["end"] - sh_["start"]) < 0.05
                and round(sh_["start"], 2) not in bset and out[-1]["ly_do"].startswith("cận người nói")
                and sh_["ly_do"].startswith("cận người nói")):
            out[-1]["end"] = sh_["end"]
            continue
        out.append(sh_)
    return out


def split_at_boundaries(shots, bounds):
    """Cú cắt phải nằm đúng trên ranh giới session (chỗ chèn thẻ chương); tách cú vắt qua ranh giới."""
    out = []
    for sh_ in shots:
        cur = sh_
        for b in sorted(bounds):
            if cur["start"] + 0.05 < b < cur["end"] - 0.05:
                out.append({**cur, "end": round(b, 2)})
                cur = {**cur, "start": round(b, 2)}
        out.append(cur)
    return out


def attach_overlays(tl_segs, locks):
    """Gắn overlay vào segment chứa trọn nó (at tương đối từ đầu segment)."""
    warns = []
    for o in locks:
        a, b = o["at"], o["at"] + o["dur"]
        seg = next((x for x in tl_segs if x.get("type") == "video"
                    and x["_truc"][0] - 1e-3 <= a and b <= x["_truc"][1] + 1e-3), None)
        if not seg:
            warns.append(f"{os.path.basename(o['src'])} tại {fmt(a)} vắt qua điểm cắt (thường do đổi file góc) - kiểm tay")
            continue
        ov = {"src": o["src"], "at": round(a - seg["_truc"][0], 2)}
        cur = seg.get("overlay")
        seg["overlay"] = ov if not cur else (cur if isinstance(cur, list) else [cur]) + [ov]
    return warns


# ---------------------------------------------------------------- session
def split_sessions(segs, total, target_min, start=0.0):
    """Ranh giới session = khoảng ngắt dài + đổi từ vựng + cụm chuyển ý; tham lam theo độ dài mục tiêu."""
    if not segs:
        return [{"start": start, "end": total}]
    words = lambda s: set(w for w in re.findall(r"\w+", s.lower()) if len(w) > 2)
    cands = []
    for i in range(1, len(segs)):
        gap = segs[i]["start"] - segs[i - 1]["end"]
        before = set().union(*[words(s["text"]) for s in segs[max(0, i - 8): i]])
        after = set().union(*[words(s["text"]) for s in segs[i: i + 8]])
        jac = 1 - len(before & after) / max(1, len(before | after))
        cue = any(c in segs[i]["text"].lower()[:60] for c in CUE)
        score = min(gap, 4.0) / 4.0 * 0.5 + jac * 0.35 + (0.4 if cue else 0)
        if gap >= 0.8 or cue:
            cands.append((segs[i]["start"], score, gap, cue))
    target = target_min * 60
    bounds, last = [start], start
    while True:
        window = [c for c in cands if last + target * 0.6 <= c[0] <= last + target * 1.5]
        if not window or total - last < target * 1.3:
            break
        best = max(window, key=lambda c: c[1] - 0.15 * abs(c[0] - (last + target)) / target)
        bounds.append(best[0])
        last = best[0]
    bounds.append(total)
    sessions = []
    for a, b in zip(bounds, bounds[1:]):
        inside = [s for s in segs if a <= s["start"] < b]
        text = " ".join(s["text"] for s in inside)
        toks = [w for w in re.findall(r"\w+", text.lower()) if len(w) > 3]
        freq = {}
        for w in toks:
            freq[w] = freq.get(w, 0) + 1
        kw = [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:6]]
        sessions.append({"start": round(a, 2), "end": round(b, 2), "tu_khoa": kw,
                         "cau_mo": inside[0]["text"][:120] if inside else "", "ten": ""})
    return sessions


# ---------------------------------------------------------------- hút về khoảng lặng
def snapper(silences):
    pts = sorted(((s["start"] + s["end"]) / 2 for s in silences))

    def snap(t, tol=0.6):
        best = None
        for p in pts:
            if abs(p - t) <= tol and (best is None or abs(p - t) < abs(best - t)):
                best = p
        return best if best is not None else t
    return snap


# ---------------------------------------------------------------- dàn góc
def plan_podcast(turns, sessions, angles, wide, snap, total):
    """angles: {nguoi/ten góc: tên góc}; wide: tên góc toàn hoặc None."""
    shots = []

    def add(a, b, goc, why):
        if b - a < 0.3:
            return
        if shots and shots[-1]["goc"] == goc and abs(shots[-1]["end"] - a) < 0.05:
            shots[-1]["end"] = b
            return
        shots.append({"start": round(a, 2), "end": round(b, 2), "goc": goc, "ly_do": why})

    for s in sessions:
        t = s["start"]
        s_end = s["end"]
        # mở session: toàn 4-6 s (nếu có)
        if wide:
            t_open = snap(t + 5.0)
            add(t, min(t_open, s_end), wide, "mở session: góc toàn thiết lập không gian")
            t = min(t_open, s_end)
        in_turns = [tr for tr in turns if tr["end"] > t and tr["start"] < s_end]
        cur_goc = None
        for tr in in_turns:
            a, b = max(t, tr["start"]), min(s_end, tr["end"])
            if b <= a:
                continue
            if tr["ai"] == "chong":
                if b - a >= 1.5 and wide:
                    cut = snap(a + 0.3)
                    if shots:
                        shots[-1]["end"] = round(max(shots[-1]["start"] + 0.3, cut), 2)
                    add(cut, b, wide, "hai người nói chồng - góc toàn")
                    cur_goc = wide
                    t = b
                continue
            goc = angles.get(tr["ai"])
            if not goc:
                continue
            if b - a < 1.5:
                continue  # "vâng/đúng rồi" - không đổi góc
            cut = a + 0.4 if goc != cur_goc else a
            cut = snap(cut, 0.4)
            if shots and cut > shots[-1]["end"]:
                shots[-1]["end"] = round(cut, 2)   # góc trước giữ tới lúc cắt (tiếng dẫn hình)
            # lượt dài: xen phản ứng/toàn mỗi ~22-28 s
            pos = cut
            k = 0
            while b - pos > 30:
                hold_to = snap(pos + 24 + (k % 3) * 2)
                add(pos, hold_to, goc, "cận người nói")
                others = [g for p, g in angles.items() if g != goc]
                react = others[k % len(others)] if others and (k % 2 == 0 or not wide) else wide
                r_end = snap(hold_to + 3.0, 0.5)
                add(hold_to, r_end, react, "phản ứng người nghe" if react != wide else "góc toàn xen giữa lượt dài")
                pos = r_end
                k += 1
            add(pos, b, goc, "cận người nói")
            cur_goc = goc
            t = b
        # đóng session: 3 s cuối về toàn nếu session dài
        if wide and shots and s_end - s["start"] > 60:
            c = snap(s_end - 3.0)
            if shots[-1]["goc"] != wide and c > shots[-1]["start"] + 3:
                shots[-1]["end"] = round(c, 2)
                add(c, s_end, wide, "đóng session: góc toàn")
        if shots and shots[-1]["end"] < s_end:
            shots[-1]["end"] = round(s_end, 2)
    return enforce_holds(shots, snap)


def plan_lecture(segs, sessions, main, second, wide, snap):
    """Một người nhiều góc: đổi góc tại ranh giới câu, giữ 12-25 s, tỉ lệ ~60/30/10."""
    shots = []
    pattern = [main, second, main, second, main, wide or second, main, second]
    bounds = sorted(set([s["start"] for s in segs] + [s["end"] for s in segs]))
    pi = 0
    for s in sessions:
        t = s["start"]
        s_end = s["end"]
        if wide:
            t_open = snap(t + 4.5)
            shots.append({"start": round(t, 2), "end": round(t_open, 2), "goc": wide, "ly_do": "mở session: góc toàn"})
            t = t_open
        k = 0
        while t < s_end - 0.5:
            goc = pattern[pi % len(pattern)] or main
            hold = 14 + (k * 7) % 12                      # 14..25 s, lệch nhịp để không máy móc
            target = t + hold
            nxt = [b for b in bounds if b >= target and b <= target + 6 and b < s_end]
            end = snap(nxt[0]) if nxt else min(s_end, target)
            if s_end - end < 6:
                end = s_end
            why = {main: "góc chính", second: "góc phụ - đổi nhịp tại ranh giới câu", wide: "góc toàn - nghỉ mắt"}.get(goc, "góc")
            shots.append({"start": round(t, 2), "end": round(end, 2), "goc": goc, "ly_do": why})
            t = end
            pi += 1
            k += 1
    return enforce_holds(shots, snap)


def enforce_holds(shots, snap, min_hold=3.0):
    out = []
    for sh_ in shots:
        if out and (sh_["end"] - sh_["start"]) < min_hold:
            out[-1]["end"] = sh_["end"]            # cú quá ngắn: nhập vào cú trước
        elif out and out[-1]["goc"] == sh_["goc"]:
            out[-1]["end"] = sh_["end"]
        else:
            out.append(dict(sh_))
    return out


# ---------------------------------------------------------------- map lên file góc
def angle_file_at(mc, goc, t):
    g = next(x for x in mc["goc"] if x["ten"] == goc)
    for fe in g["files"]:
        if fe.get("offset") is None or not fe.get("co_hinh", True):
            continue
        if fe["offset"] - 0.01 <= t < fe["ket_thuc"] - 0.01:
            return fe
    return None


def to_segments(shots, mc, audio_src, fallback, audio_off=0.0):
    """Mỗi cú cắt → 1+ segment (tách khi góc đổi file giữa cú); góc không phủ → góc dự phòng."""
    segs = []
    for sh_ in shots:
        t = sh_["start"]
        while t < sh_["end"] - 0.05:
            fe = angle_file_at(mc, sh_["goc"], t)
            goc = sh_["goc"]
            if fe is None:
                fe = angle_file_at(mc, fallback, t)
                goc = fallback
                if fe is None:
                    t += 0.5
                    continue
            end = min(sh_["end"], fe["ket_thuc"])
            drift = fe.get("drift_ppm", 0) * 1e-6
            mid = (t + end) / 2 - fe["offset"]
            corr = drift * mid
            segs.append({"type": "video", "src": fe["file"],
                         "in": round(t - fe["offset"] + corr, 3), "out": round(end - fe["offset"] + corr, 3),
                         "snap": False, "audioSrc": audio_src, "audioIn": round(t - audio_off, 3),
                         "_goc": goc, "_ly_do": sh_["ly_do"], "_truc": [round(t, 2), round(end, 2)]})
            t = end
    return segs


def absorb_short(segs, mc, min_len=1.0):
    """Mảnh < 1 s (sinh ra khi góc đổi file giữa cú cắt) → nhập vào segment kề: kéo dài segment
    trước nếu file của nó còn phủ, không thì kéo segment sau bắt đầu sớm hơn."""
    out = []
    i = 0
    while i < len(segs):
        s = segs[i]
        d = s["out"] - s["in"]
        if d >= min_len or s.get("type") == "insert":
            out.append(s)
            i += 1
            continue
        a, b = s["_truc"]
        done = False
        if out and out[-1].get("type") != "insert":
            p = out[-1]
            fe = next((f for g in mc["goc"] for f in g["files"] if f["file"] == p["src"]), None)
            if fe and fe["ket_thuc"] >= b - 0.01:
                p["out"] = round(p["out"] + d, 3)
                p["_truc"][1] = b
                done = True
        if not done and i + 1 < len(segs) and segs[i + 1].get("type") != "insert":
            n = segs[i + 1]
            fe = next((f for g in mc["goc"] for f in g["files"] if f["file"] == n["src"]), None)
            if fe and fe["offset"] <= a + 0.01:
                n["in"] = round(n["in"] - d, 3)
                n["audioIn"] = round(n["audioIn"] - d, 3)
                n["_truc"][0] = a
                done = True
        if not done:
            out.append(s)
        i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--transcript", required=True, help="tên file transcript không đuôi (của tiếng chủ)")
    ap.add_argument("--che-do", default="auto", choices=["auto", "podcast", "bai-giang"])
    ap.add_argument("--phut", type=float, default=8.0, help="độ dài session mục tiêu (phút)")
    ap.add_argument("--khong-session", action="store_true")
    ap.add_argument("--tieng", default=None, help="file tiếng chủ (mặc định: multicam.json tieng_chu hoặc góc chuẩn)")
    ap.add_argument("--chinh", default=None, help="bài giảng: góc chính (mặc định góc cận đầu tiên)")
    ap.add_argument("--nguoi-noi", default="auto", help="auto | tieng | hinh | <file lượt nói .json>")
    ap.add_argument("--khoa", default=None, help="JSON overlay cần giữ nguyên một cú (pill, bảng tên)")
    ap.add_argument("--cua-so", default=None, help="A-B: chỉ dàn góc trong quãng này của trục chung")
    ap.add_argument("--hau-to", default="", help="hậu tố tên file đầu ra, ví dụ clip1")
    ap.add_argument("--gioi-han", type=float, default=150.0, help="giây tối đa mỗi lượt đo chuyển động")
    ap.add_argument("--session-file", default=None, help="JSON [{start,ten,phu,the}] tự chia session theo thẻ chương "
                    "(the=false: mở đầu, không có thẻ); ghi đè việc tự chia của split_sessions")
    args = ap.parse_args()
    project = args.project.rstrip("/")
    mc = load_json(os.path.join(project, "multicam.json"))
    if not mc:
        raise SystemExit("! Chưa có multicam.json - chạy multicam-khop.py trước")
    total = mc["tong_dai"]
    out_dir = os.path.join(project, "multicam")
    os.makedirs(out_dir, exist_ok=True)

    tdir = os.path.join(project, "transcript")
    tj = load_json(os.path.join(tdir, f"{args.transcript}.transcript.json"), [])
    segs = tj if isinstance(tj, list) else tj.get("segments", [])
    segs = [s for s in segs if s.get("text", "").strip()]
    silences = load_json(os.path.join(tdir, f"{args.transcript}.silences.json"), [])
    snap = snapper(silences)

    # tiếng chủ
    if args.tieng:
        audio_src = args.tieng
    elif mc.get("tieng_chu"):
        audio_src = mc["tieng_chu"]["file"]
    else:
        master = next(g for g in mc["goc"] if g["ten"] == mc["truc_chuan"])
        audio_src = master["files"][0]["file"]
    # tiếng chủ là một file góc có offset ≠ 0 (--tieng): transcript đo theo đồng hồ file đó → dời lên
    # trục chung; audioIn trong timeline theo đồng hồ file đó → trừ offset khi ghi
    audio_off = 0.0
    for g in mc["goc"]:
        for fe in g["files"]:
            if fe["file"] == audio_src:
                audio_off = float(fe.get("offset", 0.0))
    if mc.get("tieng_chu") and mc["tieng_chu"]["file"] == audio_src:
        audio_off = float(mc["tieng_chu"].get("offset", 0.0))
    if abs(audio_off) > 1e-3:
        print(f"  tiếng chủ {audio_src} bắt đầu tại {audio_off:+.3f}s trên trục chung → dời mốc transcript theo")
        for s in segs:
            s["start"] = float(s["start"]) + audio_off
            s["end"] = float(s["end"]) + audio_off
        silences = [{**sl, "start": float(sl["start"]) + audio_off, "end": float(sl["end"]) + audio_off}
                    for sl in silences]
        snap = snapper(silences)

    can = [g for g in mc["goc"] if g["loai"] == "can"]
    wide = next((g["ten"] for g in mc["goc"] if g["loai"] == "toan"), None)
    mode = args.che_do
    if mode == "auto":
        people = {g.get("nguoi") or g["ten"] for g in can}
        mode = "podcast" if len(people) >= 2 else "bai-giang"
    print(f"Chế độ: {mode} | góc cận: {[g['ten'] for g in can]} | toàn: {wide} | tiếng chủ: {audio_src}")

    lo, hi = 0.0, total
    if args.cua_so:
        lo, hi = (float(x) for x in args.cua_so.split("-", 1))
        segs = [x for x in segs if x["end"] > lo and x["start"] < hi]
        print(f"  cửa sổ {fmt(lo)} - {fmt(hi)} ({(hi - lo) / 60:.1f} phút)")
    sfx = f"-{args.hau_to}" if args.hau_to else ""
    if args.session_file:
        fp = args.session_file if os.path.isabs(args.session_file) else os.path.join(project, args.session_file)
        raw = sorted(load_json(fp, []), key=lambda x: x["start"])
        raw = [x for x in raw if lo <= x["start"] < hi]
        if not raw or raw[0]["start"] > lo + 0.01:
            raw.insert(0, {"start": lo, "ten": "", "the": False})
        sessions = []
        for i, x in enumerate(raw):
            end = raw[i + 1]["start"] if i + 1 < len(raw) else hi
            sessions.append({"start": round(x["start"], 2), "end": round(end, 2), "tu_khoa": [], "cau_mo": "",
                             "ten": x.get("ten", ""), "phu": x.get("phu", ""), "the": x.get("the", True),
                             "chuong": x.get("chuong", x.get("ten", ""))})
        print(f"  session theo {os.path.basename(fp)}: {len(sessions)} phần")
    else:
        sessions = [{"start": lo, "end": hi, "tu_khoa": [], "cau_mo": "", "ten": ""}] if args.khong_session \
            else split_sessions(segs, hi, args.phut, lo)
    for i, s in enumerate(sessions, 1):
        s["so"] = i
    json.dump(sessions, open(os.path.join(out_dir, f"session{sfx}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    turns = None
    if mode == "podcast":
        src_nn = args.nguoi_noi
        if src_nn not in ("auto", "tieng", "hinh"):
            fp = src_nn if os.path.isabs(src_nn) else os.path.join(project, src_nn)
            turns = load_json(fp)
            if not turns:
                raise SystemExit(f"! Không đọc được lượt nói từ {fp}")
            print(f"  người nói: đọc từ {src_nn} ({len(turns)} lượt)")
        if turns is None and src_nn in ("auto", "tieng"):
            try:
                turns, _ = detect_speakers(project, mc, total)
            except SystemExit as e:        # góc không có tiếng (proxy chỉ hình) → thử theo hình
                if src_nn == "tieng":
                    raise
                print(f"  ! không so được tiếng các góc ({str(e).splitlines()[0][:80]}) → theo chuyển động hình")
                turns = None
            if turns and src_nn == "auto":
                spoken = sum(t["end"] - t["start"] for t in turns) or 1.0
                chong = sum(t["end"] - t["start"] for t in turns if t["ai"] == "chong")
                if chong / spoken > 0.3:
                    print(f"  ! {chong / spoken:.0%} thời gian nói bị nhận là 'chong' (tiếng các góc gần như "
                          f"giống nhau) → nhận diện người nói theo chuyển động hình")
                    turns = None
        if not turns and src_nn in ("auto", "hinh"):
            turns, _ = detect_speakers_motion(project, mc, total, os.path.join(out_dir, ".chuyen-dong"), args.gioi_han)
            if turns is None:
                raise SystemExit("⏸ Đang đo chuyển động hình (phần xong đã cache) - chạy lại đúng lệnh này để đo tiếp")
        if not turns:
            raise SystemExit("! Podcast cần >= 2 góc cận có tiếng hoặc có hình để biết ai đang nói (hoặc dùng --che-do bai-giang)")
        json.dump(turns, open(os.path.join(out_dir, "nguoi-noi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        angles = {g["ten"]: g["ten"] for g in can}
        shots = plan_podcast(turns, sessions, angles, wide, snap, total)
        fallback = wide or can[0]["ten"]
    else:
        main_g = args.chinh or (can[0]["ten"] if can else mc["truc_chuan"])
        second = next((g["ten"] for g in can if g["ten"] != main_g), None) or wide or main_g
        shots = plan_lecture(segs, sessions, main_g, second, wide, snap)
        fallback = main_g

    warns = []
    locks = load_locks(args.khoa if os.path.isabs(args.khoa) else os.path.join(project, args.khoa)) if args.khoa else []
    if locks:
        locks = [o for o in locks if lo <= o["at"] < hi]
        shots, w = apply_locks(shots, locks, lo, hi)
        warns += w
        shots = enforce_holds(shots, snap)
        if mode == "podcast":
            shots = fix_long_reactions(shots, [x["start"] for x in sessions[1:]])
            shots = refill_long(shots, locks, angles, wide, snap)
    if len(sessions) > 1:
        shots = split_at_boundaries(shots, [x["start"] for x in sessions[1:]])
    tl_segs = absorb_short(to_segments(shots, mc, audio_src, fallback, audio_off), mc)
    if locks:
        warns += attach_overlays(tl_segs, locks)
        print(f"  khoá {len(locks)} overlay; {len(warns)} cảnh báo")

    # chèn SectionTitle giữa các session + chapter
    final_segs, jobs, chapters = [], [], []
    if len(sessions) > 1:
        for s in sessions:
            if s.get("the", True):
                title_file = f"do-hoa/ngang/session-{s['so']:02d}.mp4"
                final_segs.append({"type": "insert", "src": title_file,
                                   "chapter": s.get("chuong") or f"Session {s['so']}: <tên>"})
                jobs.append({"comp": "SectionTitle", "out": f"session-{s['so']:02d}.mp4",
                             "props": {"title": s["ten"] or f"<tên session {s['so']}>",
                                       "kicker": s.get("phu") or f"Phần {s['so']}", "durationInSeconds": 4}})
            final_segs += [x for x in tl_segs if s["start"] <= x["_truc"][0] < s["end"]]
    else:
        final_segs = tl_segs

    # thống kê
    by_goc = {}
    for x in tl_segs:
        by_goc[x["_goc"]] = by_goc.get(x["_goc"], 0) + (x["_truc"][1] - x["_truc"][0])
    cuts = len(tl_segs)
    span = hi - lo
    avg = (span / cuts) if cuts else 0

    lines = [f"# Dàn góc đề xuất - {os.path.basename(project)} ({mode})", "",
             f"Trục thời gian chung (góc chuẩn `{mc['truc_chuan']}`), tiếng chủ `{audio_src}`. "
             f"{cuts} cú cắt, trung bình {avg:.1f} s/cú. Tỉ lệ góc: " +
             ", ".join(f"{g} {v / span * 100:.0f}%" for g, v in sorted(by_goc.items(), key=lambda x: -x[1])), ""]
    if warns:
        lines += ["## Cảnh báo overlay", ""] + [f"- {w}" for w in warns] + [""]
    if len(sessions) > 1:
        lines += ["## Session (Claude đặt tên theo nội dung, user duyệt)", "",
                  "| # | Mốc | Dài | Từ khoá | Câu mở |", "|---|---|---|---|---|"]
        for s in sessions:
            lines.append(f"| {s['so']} | {fmt(s['start'])} - {fmt(s['end'])} | {(s['end'] - s['start']) / 60:.1f} phút | "
                         f"{', '.join(s['tu_khoa'])} | {s['cau_mo']} |")
        lines.append("")
    if turns:
        lines += ["## Ai đang nói (rút gọn)", "", "| Mốc | Ai |", "|---|---|"]
        for tr in turns[:80]:
            lines.append(f"| {fmt(tr['start'])} - {fmt(tr['end'])} | {tr['ai']} |")
        if len(turns) > 80:
            lines.append(f"| … | còn {len(turns) - 80} lượt trong nguoi-noi.json |")
        lines.append("")
    lines += ["## Chuỗi cắt góc", "", "| # | Mốc trục chung | Dài | Góc | File góc | Lý do |", "|---|---|---|---|---|---|"]
    for i, x in enumerate(tl_segs, 1):
        a, b = x["_truc"]
        lines.append(f"| {i} | {fmt(a)} - {fmt(b)} | {b - a:.1f}s | {x['_goc']} | {os.path.basename(x['src'])} | {x['_ly_do']} |")
    open(os.path.join(out_dir, f"DAN-GOC{sfx}.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

    tl = {"_ghi_chu": "NHÁP do multicam-dan.py sinh. in/out theo file GÓC; audioSrc/audioIn theo tiếng chủ "
                      "(trục chung). Claude chỉnh theo DAN-GOC.md đã duyệt, đặt tên session trong job-session.json, "
                      "render SectionTitle rồi chép vào timeline.json. Không dùng snap (điểm cắt đã hút về khoảng lặng).",
          "aspect": "ngang", "fps": 30, "segments": final_segs}
    json.dump(tl, open(os.path.join(out_dir, f"timeline-multicam-nhap{sfx}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    if jobs:
        brand_rel = "@xuong/brand/brand.json"  # gốc xưởng (render-do-hoa.mjs hiểu), dự án nằm ngoài repo
        json.dump({"aspect": "ngang", "theme": "light", "brandFile": brand_rel,
                   "outDir": "ngang", "jobs": jobs},
                  open(os.path.join(out_dir, f"job-session{sfx}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(lines[:40]))
    for w in warns:
        print(f"  ⚠ {w}")
    print(f"\n✓ {out_dir}/: DAN-GOC{sfx}.md, timeline-multicam-nhap{sfx}.json, session{sfx}.json"
          + (", nguoi-noi.json" if turns else "") + (", job-session.json" if jobs else ""))


if __name__ == "__main__":
    main()
