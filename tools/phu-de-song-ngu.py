#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHỤ ĐỀ SONG NGỮ ghi cứng cho clip ngang (chiếu tại sự kiện, khán giả hai thứ tiếng, người ngồi xa nghe không rõ).

Cue viết theo MỐC NGUỒN (giây trong file quay gốc), nên cắt lại phim thì phụ đề không phải làm lại: công cụ
chiếu từng cue sang mốc thành phẩm bằng `xuat-nhap/<tên>.map.json` do assemble.py ghi (mốc mới = start + (t - in)).

    python3 tools/phu-de-song-ngu.py khoi-tao "<dự án>" <tên>   # nháp phu-de/cues.json: chữ gốc từ transcript, phần dịch để trống
    python3 tools/phu-de-song-ngu.py dung "<dự án>" <tên>       # cues.json + map.json -> phu-de/<tên>.ass, .srt (song ngữ), .en.srt, .vi.srt, .bao-cao.txt
    python3 tools/phu-de-song-ngu.py burn "<dự án>" <tên>       # xuat-nhap/<tên>.mp4 + .ass -> xuat-nhap/<tên>-pd.mp4 (một lượt, trong 180 giây với clip tới khoảng 6 phút)
    python3 tools/phu-de-song-ngu.py khung "<dự án>" <tên> <giây> [<giây> ...]   # trích khung của bản -pd để nhìn tận mắt (output-seek)

<tên> là tên thành phẩm không đuôi (vd wishes-ngang); `<tên>-nhap1` dùng cùng cues.json cho bản nháp.
Dùng `--ra <tên-ra>` để ghi ra tên khác (thử kiểu chữ mà không đè bản đã giao).

cues.json (Du an/<x>/phu-de/cues.json):
  "kieu":    font, co-chu (px trên khung 1080), rong-dong (ký tự mỗi dòng), hop (nền mờ sau chữ), mau-2 (màu RGB hex của dòng thứ hai)
  "the-ten": (tuỳ chọn) bảng tên đầu clip: dong-1, dong-2, tu, den (giây thành phẩm)
  "cues":    [{"s": giây nguồn bắt đầu, "e": giây nguồn kết thúc,
               "c": [["chữ gốc", "bản dịch"], ...],     # nhiều cặp = một câu dài tách thành nhiều cue, tự neo vào khoảng ngừng
               "ghi-chu": "chỗ cần nghe lại"}]
Cặp dịch để trống thì `dung` dừng và liệt kê, không sinh phụ đề thiếu.

Quy tắc hiển thị (đã kiểm ở clip thật): hiện sớm 0,05 giây, kéo dài 0,25 giây sau lời, tối thiểu 1,3 giây nếu còn chỗ,
không chồng cue sau; cảnh báo khi đọc nhanh hơn 21 ký tự mỗi giây. ASS khai PlayResX/PlayResY đúng 1920x1080
(không dùng force_style: libass trên VM chỉ áp key đầu), hộp mờ bằng BorderStyle=3.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

sys.dont_write_bytecode = True

KIEU_MAC_DINH = {"font": "Lato", "co-chu": 64, "rong-dong": 42, "hop": True, "mau-2": "FFE9A8"}
THE_TEN_MAC_DINH = {"tu": 0.6, "den": 4.6}
NGUONG_DOC_NHANH = 21.0       # ký tự mỗi giây
HIEN_SOM, KEO_DAI, TOI_THIEU, KHE = 0.05, 0.25, 1.3, 0.04
GIOI_HAN_BURN_GIAY = 400      # clip dài hơn: burn quá 180 giây, chạy trên Mac


def duong(proj, *p):
    return os.path.join(proj, *p)


def doc_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ass_time(t):
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def mau_ass(rgb):
    rgb = rgb.lstrip("#").upper()
    if not re.fullmatch(r"[0-9A-F]{6}", rgb):
        sys.exit(f"Màu '{rgb}' không phải 6 chữ số hex RGB")
    return rgb[4:6] + rgb[2:4] + rgb[0:2]    # ASS dùng BGR


def doc_map(proj, ten):
    p = duong(proj, "xuat-nhap", ten + ".map.json")
    if not os.path.exists(p):
        sys.exit(f"Chưa có {p}: dựng thành phẩm bằng assemble.py trước (map.json do assemble ghi).")
    mp = doc_json(p)
    parts = [x for x in mp["parts"] if x.get("kind") == "cut"]
    if not parts:
        sys.exit("map.json không có đoạn cắt nào (kind=cut)")
    return mp, parts


def khoang_ngung(proj, src):
    """Giữa các khoảng ngừng ngắn (>=0,1 giây) của lời nói gốc: điểm neo để tách cue trong một câu dài. Có nhớ đệm."""
    f = duong(proj, src) if not os.path.isabs(src) else src
    if not os.path.exists(f):
        return []
    dem = duong(proj, ".tam", "pd", "ngung.json")
    khoa = [os.path.getsize(f), int(os.path.getmtime(f))]
    if os.path.exists(dem):
        try:
            d = doc_json(dem)
            if d.get("khoa") == khoa:
                return d["ngung"]
        except Exception:
            pass
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", f, "-vn", "-ac", "1", "-ar", "16000",
                        "-af", "silencedetect=noise=-32dB:d=0.1", "-f", "null", "-"],
                       capture_output=True, text=True)
    ngung, st = [], None
    for dong in r.stderr.splitlines():
        a = re.search(r"silence_start:\s*([0-9.]+)", dong)
        b = re.search(r"silence_end:\s*([0-9.]+)", dong)
        if a:
            st = float(a.group(1))
        elif b and st is not None:
            ngung.append((st + float(b.group(1))) / 2)
            st = None
    os.makedirs(os.path.dirname(dem), exist_ok=True)
    with open(dem, "w") as fo:
        json.dump({"khoa": khoa, "ngung": ngung}, fo)
    return ngung


# ---------------------------------------------------------------- khoi-tao

def cmd_khoi_tao(a):
    proj = a.du_an
    mp, parts = doc_map(proj, a.ten)
    tdir = duong(proj, "transcript")
    tj = [x for x in os.listdir(tdir) if x.endswith(".transcript.json")] if os.path.isdir(tdir) else []
    if not tj:
        sys.exit("Chưa có transcript/*.transcript.json (gỡ băng trước, phim-transcript)")
    segs = doc_json(duong(tdir, sorted(tj)[0]))
    cues = []
    for p in parts:
        for sg in segs:
            if sg["end"] <= p["in"] or sg["start"] >= p["out"]:
                continue
            s, e = max(sg["start"], p["in"]), min(sg["end"], p["out"])
            if e - s < 0.3:
                continue
            c = {"s": round(s, 2), "e": round(e, 2), "c": [[sg["text"].strip(), ""]]}
            if len(sg["text"]) > 90 or e - s > 9:
                c["ghi-chu"] = "câu dài: tách thành nhiều cặp trong c để mỗi cue gọn trên hai dòng"
            cues.append(c)
    out = duong(proj, "phu-de", "cues.json")
    if os.path.exists(out) and not a.de:
        sys.exit(f"{out} đã có (thêm --de để ghi đè)")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    nguon = parts[0]["src"]
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"nguon": nguon, "kieu": KIEU_MAC_DINH, "cues": cues}, f, ensure_ascii=False, indent=1)
    print(f"Đã ghi {out}: {len(cues)} cue từ transcript. Việc kế: viết dịch cho từng cặp (chữ gốc cũng cần hiệu đính theo "
          f"tai nghe và ngữ cảnh, transcript chữ thường không dấu câu), tách câu dài, rồi chạy `dung`.")


# ---------------------------------------------------------------- dung

def cmd_dung(a):
    proj, ten = a.du_an, a.ten
    ra = a.ra or ten
    cf = duong(proj, "phu-de", "cues.json")
    if not os.path.exists(cf):
        sys.exit(f"Chưa có {cf}: chạy `khoi-tao` hoặc soạn tay.")
    cfg = doc_json(cf)
    kieu = {**KIEU_MAC_DINH, **cfg.get("kieu", {})}
    mp, parts = doc_map(proj, ten)
    thieu = [c for c in cfg["cues"] for en, vi in c["c"] if not en.strip() or not vi.strip()]
    if thieu:
        for c in thieu[:15]:
            print(f"  thiếu chữ/dịch: nguồn {c['s']:.1f}-{c['e']:.1f} {c['c']}")
        sys.exit(f"{len(thieu)} cue còn trống chữ hoặc bản dịch; điền đủ rồi chạy lại.")

    ngung = None
    cues = []   # [s, e, en, vi, ghi_chu]
    for c in cfg["cues"]:
        s, e, pairs, note = c["s"], c["e"], c["c"], c.get("ghi-chu", "")
        if len(pairs) == 1:
            cues.append([s, e, pairs[0][0], pairs[0][1], note])
            continue
        if ngung is None:
            ngung = khoang_ngung(proj, cfg.get("nguon") or parts[0]["src"])
        L = [len(x[0]) for x in pairs]
        tot = sum(L)
        cat, acc = [], 0
        for l in L[:-1]:
            acc += l
            uoc = s + (e - s) * acc / tot
            gan = [q for q in ngung if abs(q - uoc) <= 0.9 and s + 0.4 < q < e - 0.4]
            cat.append(min(gan, key=lambda q: abs(q - uoc)) if gan else uoc)
        moc = [s] + cat + [e]
        for i, (en, vi) in enumerate(pairs):
            cues.append([moc[i], moc[i + 1], en, vi, note])

    final, loi = [], []
    for c in cues:
        s, e = c[0], c[1]
        trung = [p for p in parts if p["in"] - 0.3 <= s < p["out"] + 0.01]
        if not trung:
            loi.append(f"cue ngoài phần giữ lại (nguồn {s:.1f}s): {c[2][:40]}")
            continue
        p = trung[0]
        ns = p["start"] + max(0.0, s - p["in"])
        ne = p["start"] + min(e, p["out"]) - p["in"]
        final.append([ns, ne, c[2], c[3], c[4], s])
    final.sort(key=lambda x: x[0])
    for i, f in enumerate(final):
        nxt = final[i + 1][0] if i + 1 < len(final) else 1e9
        s = max(0.0, f[0] - HIEN_SOM)
        e = max(f[1] + KEO_DAI, s + TOI_THIEU)
        e = min(e, nxt - KHE)
        f[0], f[1] = s, e
        if f[1] <= f[0] + 0.3:
            loi.append(f"cue quá ngắn tại {f[0]:.2f}s: {f[2][:40]}")

    out = duong(proj, "phu-de")
    os.makedirs(out, exist_ok=True)
    W = int(a.rong_dong or kieu["rong-dong"])
    wrap = lambda t: "\\N".join(textwrap.wrap(t, W, break_long_words=False))
    with open(duong(out, ra + ".srt"), "w", encoding="utf-8") as fa, \
         open(duong(out, ra + ".en.srt"), "w", encoding="utf-8") as fe, \
         open(duong(out, ra + ".vi.srt"), "w", encoding="utf-8") as fv:
        for i, f in enumerate(final, 1):
            tm = f"{srt_time(f[0])} --> {srt_time(f[1])}\n"
            fa.write(f"{i}\n{tm}{f[2]}\n{f[3]}\n\n")
            fe.write(f"{i}\n{tm}{f[2]}\n\n")
            fv.write(f"{i}\n{tm}{f[3]}\n\n")

    hop = bool(kieu["hop"])
    c2 = mau_ass(kieu["mau-2"])
    hdr = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
           "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
           "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           f"Style: Sub,{kieu['font']},{kieu['co-chu']},&H00FFFFFF,&H00FFFFFF,{'&H78000000' if hop else '&H00000000'},&H96000000,1,0,0,0,100,100,0,0,"
           f"{3 if hop else 1},{12 if hop else 3.8},{0 if hop else 1.8},2,150,150,54,1\n"
           f"Style: Ten,{kieu['font']},72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,1,3.6,1.6,7,90,90,70,1\n"
           f"Style: TenPhu,{kieu['font']},46,&H00{c2},&H00{c2},&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,3,1.4,7,90,90,70,1\n\n"
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = [f"Dialogue: 0,{ass_time(f[0])},{ass_time(f[1])},Sub,,0,0,0,,{{\\fad(140,140)}}{wrap(f[2])}\\N{{\\c&H{c2}&}}{wrap(f[3])}"
          for f in final]
    th = cfg.get("the-ten")
    if th and not a.khong_the_ten:
        th = {**THE_TEN_MAC_DINH, **th}
        ev.append(f"Dialogue: 1,{ass_time(th['tu'])},{ass_time(th['den'])},Ten,,0,0,0,,{{\\fad(400,500)}}{th['dong-1']}")
        if th.get("dong-2"):
            ev.append(f"Dialogue: 1,{ass_time(th['tu'])},{ass_time(th['den'])},TenPhu,,0,0,150,,{{\\fad(400,500)}}{th['dong-2']}")
    with open(duong(out, ra + ".ass"), "w", encoding="utf-8") as fo:
        fo.write(hdr + "\n".join(ev) + "\n")

    rep = [f"{len(final)} cue, thành phẩm dài {mp['parts'][-1]['end']:.1f}s"]
    nhanh = 0
    for f in final:
        dur = f[1] - f[0]
        cps = max(len(f[2]), len(f[3])) / dur
        co = cps > NGUONG_DOC_NHANH
        nhanh += co
        rep.append(f"{srt_time(f[0])[:-4]} [{dur:4.1f}s {cps:4.1f} k/s] nguồn {f[5]:6.1f} | {f[2]} || {f[3]}" + ("  <- ĐỌC NHANH" if co else ""))
    rep += ["", "CHỖ CẦN NGHE LẠI (mốc thành phẩm):"]
    thay = set()
    for f in final:
        if f[4] and f[4] not in thay:
            thay.add(f[4])
            rep.append(f"- {srt_time(f[0])[:-4]}: {f[4]}")
    if not thay:
        rep.append("- không có")
    rep += ["", "LỖI: " + ("; ".join(loi) if loi else "không")]
    with open(duong(out, ra + ".bao-cao.txt"), "w", encoding="utf-8") as fo:
        fo.write("\n".join(rep))
    print("\n".join(rep))
    print(f"\nĐã ghi phu-de/{ra}.ass .srt .en.srt .vi.srt .bao-cao.txt" + (f"; {nhanh} cue đọc nhanh" if nhanh else ""))
    if loi:
        sys.exit(2)


# ---------------------------------------------------------------- burn

def cmd_burn(a):
    proj, ten = a.du_an, a.ten
    vao = duong(proj, "xuat-nhap", ten + ".mp4")
    ass = duong(proj, "phu-de", (a.ass or ten) + ".ass")
    ra = duong(proj, "xuat-nhap", (a.ra or ten + "-pd") + ".mp4")
    for p in (vao, ass):
        if not os.path.exists(p):
            sys.exit(f"Thiếu {p}")
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vao], capture_output=True, text=True)
    dur = float(r.stdout.strip())
    if dur > GIOI_HAN_BURN_GIAY and not a.du_gio:
        sys.exit(f"Clip dài {dur:.0f}s: burn 1080p mất khoảng {dur * 0.4:.0f}s, vượt 180 giây của một lượt device_bash. "
                 f"Chạy lệnh ffmpeg này trên Mac (không giới hạn giờ) hoặc thêm --du-gio để thử.")
    vf = f"ass={os.path.basename(ass)}" + (f":fontsdir={a.fontsdir}" if a.fontsdir else "")
    font = (doc_json(duong(proj, "phu-de", "cues.json")).get("kieu", {}).get("font") or KIEU_MAC_DINH["font"])
    fc = subprocess.run(["fc-list", font], capture_output=True, text=True) if shutil.which("fc-list") else None
    if fc is not None and not fc.stdout.strip() and not a.fontsdir:
        print(f"CẢNH BÁO: máy chưa thấy font '{font}' (fc-list); libass sẽ rơi về font khác. Cài font hoặc dùng --fontsdir <thư mục .ttf>.")
    ptmp = ra + ".part.mp4"
    # veryfast: clip 4 phút 1080p ra trong khoảng 100 giây; `fast` cùng crf từng vượt 180 giây và bỏ lại file cụt.
    lenh = ["ffmpeg", "-y", "-hide_banner", "-nostdin", "-i", vao, "-vf", vf,
            "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-c:a", "copy",
            "-movflags", "+faststart", ptmp]
    print("$", " ".join(lenh))
    kq = subprocess.run(lenh, cwd=os.path.dirname(ass), capture_output=True, text=True)
    if kq.returncode != 0:
        print(kq.stderr[-1500:])
        sys.exit("ffmpeg lỗi")
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ptmp], capture_output=True, text=True)
    d2 = float(pr.stdout.strip())
    if abs(d2 - dur) > 0.1:
        sys.exit(f"Bản burn dài {d2:.2f}s khác bản gốc {dur:.2f}s: file cụt, không dùng")
    try:
        os.replace(ptmp, ra)
    except OSError:      # máy không cho xoá/đổi tên đè (chưa cấp quyền xoá): chép đè
        shutil.copyfile(ptmp, ra)
        try:
            os.remove(ptmp)
        except OSError:
            print(f"(còn lại {ptmp}: dọn khi được phép xoá)")
    print(f"Đã ghi {ra} ({os.path.getsize(ra) / 1e6:.0f} MB, {d2:.3f}s). Burn là một lượt encode mới: chạy nghiem-thu.py video lên file này.")


# ---------------------------------------------------------------- khung

def cmd_khung(a):
    proj, ten = a.du_an, a.ten
    vid = duong(proj, "xuat-nhap", (a.vao or ten + "-pd") + ".mp4")
    if not os.path.exists(vid):
        sys.exit(f"Thiếu {vid}")
    out = duong(proj, ".tam", "pd")
    os.makedirs(out, exist_ok=True)
    files = []
    for t in a.giay:
        f = duong(out, f"khung-{t:07.2f}.jpg")
        # -ss SAU -i (output-seek): đặt trước -i làm lệch PTS nên libass không khớp cue và khung ra không chữ
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-nostdin", "-i", vid, "-ss", str(t), "-frames:v", "1", "-q:v", "3", f],
                       capture_output=True)
        files.append(f)
    print("Đã trích:\n" + "\n".join(files))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="lenh", required=True)
    for ten in ("khoi-tao", "dung", "burn", "khung"):
        p = sp.add_parser(ten)
        p.add_argument("du_an")
        p.add_argument("ten")
        if ten == "khoi-tao":
            p.add_argument("--de", action="store_true")
        if ten == "dung":
            p.add_argument("--ra")
            p.add_argument("--rong-dong", type=int)
            p.add_argument("--khong-the-ten", action="store_true")
        if ten == "burn":
            p.add_argument("--ra")
            p.add_argument("--ass")
            p.add_argument("--preset", default="veryfast")
            p.add_argument("--crf", type=int, default=17)
            p.add_argument("--du-gio", action="store_true")
            p.add_argument("--fontsdir")
        if ten == "khung":
            p.add_argument("--vao")
            p.add_argument("giay", type=float, nargs="+")
    a = ap.parse_args()
    a.du_an = os.path.abspath(a.du_an)    # ffmpeg chạy trong thư mục phu-de/: mọi đường dẫn phải tuyệt đối
    {"khoi-tao": cmd_khoi_tao, "dung": cmd_dung, "burn": cmd_burn, "khung": cmd_khung}[a.lenh](a)


if __name__ == "__main__":
    main()
