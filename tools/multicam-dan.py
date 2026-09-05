#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DÀN GÓC MULTICAM: nhận diện ai đang nói, chia session theo transcript, đề xuất chuỗi cắt góc
theo thực hành podcast/multicam hiệu quả, sinh timeline nháp cho assemble.py.

Cách dùng (từ gốc "xuong-phim-claude", sau multicam-khop.py và transcript của tiếng chủ):
  python3 tools/multicam-dan.py "du-an/<x>" --transcript "<tên file transcript không đuôi>"
      [--che-do auto|podcast|bai-giang] [--phut 8] [--khong-session] [--tieng "nguon/tieng-chu.wav"]

Đầu vào: du-an/<x>/multicam.json (offset từng file), transcript/<tên>.transcript.json + .silences.json
  (transcript chạy trên TIẾNG CHỦ - nguon/tieng-chu.wav nếu đã --tron-tieng, hoặc file góc chủ).
Đầu ra: du-an/<x>/multicam/
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


# ---------------------------------------------------------------- session
def split_sessions(segs, total, target_min):
    """Ranh giới session = khoảng ngắt dài + đổi từ vựng + cụm chuyển ý; tham lam theo độ dài mục tiêu."""
    if not segs:
        return [{"start": 0.0, "end": total}]
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
    bounds, last = [0.0], 0.0
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

    sessions = [{"start": 0.0, "end": total, "tu_khoa": [], "cau_mo": "", "ten": ""}] if args.khong_session \
        else split_sessions(segs, total, args.phut)
    for i, s in enumerate(sessions, 1):
        s["so"] = i
    json.dump(sessions, open(os.path.join(out_dir, "session.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    turns = None
    if mode == "podcast":
        turns, _ = detect_speakers(project, mc, total)
        if not turns:
            raise SystemExit("! Podcast cần >= 2 góc cận có tiếng để biết ai đang nói (hoặc dùng --che-do bai-giang)")
        json.dump(turns, open(os.path.join(out_dir, "nguoi-noi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        angles = {g["ten"]: g["ten"] for g in can}
        shots = plan_podcast(turns, sessions, angles, wide, snap, total)
        fallback = wide or can[0]["ten"]
    else:
        main_g = args.chinh or (can[0]["ten"] if can else mc["truc_chuan"])
        second = next((g["ten"] for g in can if g["ten"] != main_g), None) or wide or main_g
        shots = plan_lecture(segs, sessions, main_g, second, wide, snap)
        fallback = main_g

    tl_segs = absorb_short(to_segments(shots, mc, audio_src, fallback, audio_off), mc)

    # chèn SectionTitle giữa các session + chapter
    final_segs, jobs, chapters = [], [], []
    if len(sessions) > 1:
        for s in sessions:
            title_file = f"do-hoa/ngang/session-{s['so']:02d}.mp4"
            final_segs.append({"type": "insert", "src": title_file, "chapter": f"Session {s['so']}: <tên>"})
            jobs.append({"comp": "SectionTitle", "out": f"session-{s['so']:02d}.mp4",
                         "props": {"title": s["ten"] or f"<tên session {s['so']}>",
                                   "subtitle": f"Phần {s['so']}", "durationInSeconds": 4}})
            final_segs += [x for x in tl_segs if s["start"] <= x["_truc"][0] < s["end"]]
    else:
        final_segs = tl_segs

    # thống kê
    by_goc = {}
    for x in tl_segs:
        by_goc[x["_goc"]] = by_goc.get(x["_goc"], 0) + (x["_truc"][1] - x["_truc"][0])
    cuts = len(tl_segs)
    avg = (total / cuts) if cuts else 0

    lines = [f"# Dàn góc đề xuất - {os.path.basename(project)} ({mode})", "",
             f"Trục thời gian chung (góc chuẩn `{mc['truc_chuan']}`), tiếng chủ `{audio_src}`. "
             f"{cuts} cú cắt, trung bình {avg:.1f} s/cú. Tỉ lệ góc: " +
             ", ".join(f"{g} {v / total * 100:.0f}%" for g, v in sorted(by_goc.items(), key=lambda x: -x[1])), ""]
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
    open(os.path.join(out_dir, "DAN-GOC.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

    tl = {"_ghi_chu": "NHÁP do multicam-dan.py sinh. in/out theo file GÓC; audioSrc/audioIn theo tiếng chủ "
                      "(trục chung). Claude chỉnh theo DAN-GOC.md đã duyệt, đặt tên session trong job-session.json, "
                      "render SectionTitle rồi chép vào timeline.json. Không dùng snap (điểm cắt đã hút về khoảng lặng).",
          "aspect": "ngang", "fps": 30, "segments": final_segs}
    json.dump(tl, open(os.path.join(out_dir, "timeline-multicam-nhap.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    if jobs:
        json.dump({"aspect": "ngang", "theme": "light", "brandFile": "../../../brand/brand.json",
                   "outDir": "ngang", "jobs": jobs},
                  open(os.path.join(out_dir, "job-session.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(lines[:40]))
    print(f"\n✓ {out_dir}/: DAN-GOC.md, timeline-multicam-nhap.json, session.json"
          + (", nguoi-noi.json" if turns else "") + (", job-session.json" if jobs else ""))


if __name__ == "__main__":
    main()
