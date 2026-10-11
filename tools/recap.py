#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RECAP SỰ KIỆN: bộ lệnh dựng nhanh clip tổng kết từ nhiều clip quay rời (điện thoại, máy ảnh) của một buổi.
Quy trình đầy đủ: skills/phim-recap-su-kien/SKILL.md. Mọi lệnh chạy từ gốc xưởng, nhận --du-an là
thư mục hồ sơ dự án ("../Du an/<YYYY-MM tên>" hoặc chỉ tên). Lệnh nặng có --gioi-han-giay để chạy lặp trong
giới hạn 180 giây mỗi lượt gọi của máy ảo; chạy lại cùng lệnh tới khi báo XONG.

    python3 tools/recap.py kiem-ke   "<thư mục nguồn>" --du-an "<dự án>"      # bảng clip theo giờ quay, cờ HDR/VFR/dọc
    python3 tools/recap.py doi-ten   --du-an "<dự án>" [--ghi | --hoan-tac]     # NNN_HHMM_<giai-doan>_<mo-ta>.mp4
    python3 tools/recap.py khao-sat  --du-an "<dự án>" [--gioi-han-giay 150]    # ảnh tổng quan + bảng khung từng clip
    python3 tools/recap.py nhac      --du-an "<dự án>" --nhac nhac-nen/<x>.mp3 [--bpm 66]   # LUFS, gainDb gợi ý, lưới phách
    python3 tools/recap.py cat       --du-an "<dự án>" [--gioi-han-giay 150]    # proxy 1080p theo bảng cảnh + silences
    python3 tools/recap.py timeline  --du-an "<dự án>" [--khung ngang] [--ghi-de]   # bảng cảnh -> timeline.json
    python3 tools/recap.py khop-nhip --du-an "<dự án>" [--map <bản nháp>.map.json] [--ghi]   # điểm cắt B-roll vào phách
    python3 tools/recap.py kiem      --du-an "<dự án>" [--muc-tieu 3:00]         # kiểm giấy trước khi dựng

Tệp trong hồ sơ dự án:
    recap/kiem-ke.json    danh sách clip (Claude điền "giai_doan", "mo_ta" sau khi xem ảnh khảo sát)
    recap/canh.json       BẢNG CẢNH do Claude viết sau chốt duyệt phương án, mỗi dòng một cảnh:
        {"id": "a1", "clip": "005", "tu": 8, "den": 12, "tieng": "tat"|"giu",
         "chuong": "Welcome", "chu": "do-hoa/ngang/tm-x.webm", "chu_at": 0.8, "chu_dai": 4.4,
         "mo": 0.4, "tat_dan": 0.4, "ghi_chu": "đón khách"}
        dòng thẻ đồ họa: {"the": "do-hoa/ngang/phan1.mp4"}
        "clip" là số thứ tự NNN (sau doi-ten) hoặc tên tệp nguồn; "tu"/"den" là giây trong tệp nguồn.
    recap/cat-meta.json   proxy đã cắt (đệm mỗi đầu, mốc in/out trong proxy)
    recap/nhip.json       nhịp và lưới phách của nhạc nền, LUFS, gainDb gợi ý
    nguon/<id>_<NNN>.mp4  proxy; transcript/<id>_<NNN>.silences.json cho cảnh giữ tiếng (để "snap" có tác dụng)
    _kt/khao-sat/         ảnh khảo sát (dọn khi anh duyệt)
"""
import argparse
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata

sys.dont_write_bytecode = True
TOOLS = os.path.dirname(os.path.abspath(__file__))
XUONG = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mts", ".mkv", ".avi"}
TONEMAP_VF = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
              "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")  # như tools/mau-sac.py
NHAC_DAN = -20.0   # LUFS mục tiêu của nhạc trước chuẩn hoá khi recap lấy nhạc làm chính (ít lời)
NHAC_LOI = -30.0   # LUFS mục tiêu của nhạc khi clip nói nhiều (nhạc làm nền dưới lời)


# ----------------------------------------------------------------------------- tiện ích chung
def du_an_path(s):
    if os.path.isdir(s):
        return os.path.abspath(s)
    try:
        import cau_hinh as CH
        p = os.path.join(CH.du_an(), s)
        if os.path.isdir(p):
            return p
    except Exception:
        pass
    sys.exit(f"DỪNG: không thấy thư mục dự án {s}")


def doc_json(p, mac_dinh=None):
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    return mac_dinh


def ghi_json(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def probe(path):
    p = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path],
                       capture_output=True, text=True)
    return json.loads(p.stdout) if p.returncode == 0 and p.stdout else None


def thoi_luong(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def ty_le(s):
    try:
        a, b = s.split("/")
        return float(a) / float(b) if float(b) else 0.0
    except Exception:
        return 0.0


def slug(s, toi_da=40):
    s = unicodedata.normalize("NFD", s or "").replace("đ", "d").replace("Đ", "D")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:toi_da].strip("-")


def mmss(t):
    t = max(0.0, float(t))
    return f"{int(t // 60)}:{t % 60:04.1f}"


def doc_giay(s):
    """'3:00', '180', '3p' -> giây"""
    s = str(s).strip().lower().replace("p", ":").rstrip(":")
    if ":" in s:
        m, sec = s.split(":", 1)
        return int(m) * 60 + float(sec or 0)
    return float(s)


class NganSach:
    def __init__(self, giay):
        self.t0, self.giay = time.time(), giay

    def het(self, du_phong=0.0):
        return time.time() - self.t0 > self.giay - du_phong


def kiem_ke_path(da):
    return os.path.join(da, "recap", "kiem-ke.json")


def nap_kiem_ke(da):
    kk = doc_json(kiem_ke_path(da))
    if not kk:
        sys.exit("DỪNG: chưa có recap/kiem-ke.json; chạy lệnh kiem-ke trước")
    return kk


def tim_clip(kk, khoa):
    """khoa: số thứ tự '005'/5 hoặc tên tệp (đầy đủ hay một phần)"""
    k = str(khoa)
    for c in kk["clip"]:
        if k.isdigit() and int(k) == c["stt"]:
            return c
    for c in kk["clip"]:
        if c["ten"] == k or c.get("ten_goc") == k:
            return c
    ung = [c for c in kk["clip"] if k in c["ten"] or k in c.get("ten_goc", "")]
    if len(ung) == 1:
        return ung[0]
    sys.exit(f"DỪNG: không xác định được clip '{khoa}' ({len(ung)} tệp khớp)")


# ----------------------------------------------------------------------------- kiem-ke
RE_TEN_GIO = re.compile(r"(20\d{2})(\d{2})(\d{2})[_-]?(\d{2})(\d{2})(\d{2})")
RE_DA_DOI = re.compile(r"^(\d{3})_(\d{2})(\d{2})_")


def gio_quay(path, info, lech_gio):
    ten = os.path.basename(path)
    m = RE_TEN_GIO.search(ten)
    if m:
        y, mo, d, h, mi, s = map(int, m.groups())
        return datetime.datetime(y, mo, d, h, mi, s), "tên tệp"
    tags = (info or {}).get("format", {}).get("tags", {}) or {}
    q = tags.get("com.apple.quicktime.creationdate")
    if q:
        try:
            dt = datetime.datetime.fromisoformat(q.replace("Z", "+00:00"))
            return dt.replace(tzinfo=None), "quicktime"
        except ValueError:
            pass
    c = tags.get("creation_time")
    if c:
        try:
            dt = datetime.datetime.fromisoformat(c.replace("Z", "+00:00")).replace(tzinfo=None)
            return dt + datetime.timedelta(hours=lech_gio), f"creation_time UTC+{lech_gio:g}"
        except ValueError:
            pass
    return datetime.datetime.fromtimestamp(os.path.getmtime(path)), "giờ sửa tệp (kém tin cậy)"


def lenh_kiem_ke(a):
    da = du_an_path(a.du_an)
    nguon = os.path.abspath(a.nguon)
    if not os.path.isdir(nguon):
        sys.exit(f"DỪNG: không thấy thư mục nguồn {nguon}")
    cu = doc_json(kiem_ke_path(da), {}) or {}
    cu_theo_ten = {}
    for c in cu.get("clip", []):
        cu_theo_ten[c["ten"]] = c
        if c.get("ten_goc"):
            cu_theo_ten[c["ten_goc"]] = c
    tep = sorted(f for f in os.listdir(nguon)
                 if os.path.splitext(f)[1].lower() in VIDEO_EXT and not f.startswith("."))
    ds = []
    for f in tep:
        p = os.path.join(nguon, f)
        info = probe(p)
        if not info:
            print(f"  BỎ QUA (ffprobe không đọc được): {f}")
            continue
        v = next((s for s in info["streams"] if s.get("codec_type") == "video"), None)
        au = next((s for s in info["streams"] if s.get("codec_type") == "audio"), None)
        if not v:
            continue
        dt, gnguon = gio_quay(p, info, a.lech_gio)
        m = RE_DA_DOI.match(f)
        rot = 0
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = int(abs(float(sd["rotation"]))) % 360
        rot = rot or int(abs(float((v.get("tags") or {}).get("rotate", 0) or 0))) % 360
        w, h = int(v.get("width", 0)), int(v.get("height", 0))
        if rot in (90, 270):
            w, h = h, w
        rf, af = ty_le(v.get("r_frame_rate", "0/1")), ty_le(v.get("avg_frame_rate", "0/1"))
        tr = v.get("color_transfer", "") or ""
        c = {
            "ten": f, "duong_dan": p,
            "gio": dt.strftime("%Y-%m-%d %H:%M:%S"), "nguon_gio": gnguon,
            "dai": round(float(info["format"].get("duration", 0) or 0), 3),
            "rong": w, "cao": h, "fps": round(rf, 3), "fps_tb": round(af, 3),
            "codec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
            "hdr": tr in ("smpte2084", "arib-std-b67"), "transfer": tr,
            "vfr": bool(rf and af and abs(rf - af) / rf > 0.01),
            "doc": h > w, "co_tieng": au is not None,
            "giai_doan": "", "mo_ta": "",
        }
        if m:
            c["stt_cu"] = int(m.group(1))
            phan = os.path.splitext(f)[0].split("_", 3)
            if len(phan) == 4:  # tên đã đổi kiểu NNN_HHMM_<giai-doan>_<mo-ta>: đọc lại hai trường
                c["giai_doan"], c["mo_ta"] = phan[2], phan[3]
        old = cu_theo_ten.get(f)
        if old:
            for k in ("giai_doan", "mo_ta", "ten_goc", "ti_le_tieng", "ghi_chu"):
                if old.get(k):
                    c[k] = old[k]
        ds.append(c)
    # thứ tự: theo giờ quay; tệp đã đổi tên giữ số cũ
    if ds and all("stt_cu" in c for c in ds):
        ds.sort(key=lambda c: c["stt_cu"])
    else:
        ds.sort(key=lambda c: (c["gio"], c["ten"]))
    cum, truoc = 1, None
    for i, c in enumerate(ds, 1):
        c["stt"] = i
        bd = datetime.datetime.strptime(c["gio"], "%Y-%m-%d %H:%M:%S")
        if truoc is not None and (bd - truoc).total_seconds() > a.khoang_phut * 60:
            cum += 1
        c["cum"] = cum
        truoc = bd + datetime.timedelta(seconds=c["dai"])
        c.pop("stt_cu", None)
    kk = {"_huong_dan": "Claude điền giai_doan (ngắn, theo pha của kịch bản: don-khach, khai-mac, phan1...) và mo_ta "
                        "(việc thấy trong clip) sau khi xem ảnh khảo sát; doi-ten dùng hai trường này.",
          "nguon": nguon, "lech_gio": a.lech_gio, "clip": ds}
    ghi_json(kiem_ke_path(da), kk)
    # bảng đọc nhanh
    dong = ["# Kiểm kê nguồn recap", "", f"Nguồn: `{nguon}`", "",
            "| STT | Giờ | Dài | Khung | Cờ | Cụm | Giai đoạn | Mô tả | Tệp |", "|---|---|---|---|---|---|---|---|---|"]
    for c in ds:
        co = ",".join(x for x, ok in (("HDR", c["hdr"]), ("VFR", c["vfr"]), ("dọc", c["doc"]),
                                      ("không tiếng", not c["co_tieng"]), ("10-bit", "10" in (c["pix_fmt"] or "")))
                      if ok)
        dong.append(f"| {c['stt']:03d} | {c['gio'][11:16]} | {mmss(c['dai'])} | {c['rong']}x{c['cao']} {c['fps']:g} | "
                    f"{co} | {c['cum']} | {c['giai_doan']} | {c['mo_ta']} | {c['ten']} |")
    with open(os.path.join(da, "recap", "KIEM-KE.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(dong) + "\n")
    tong = sum(c["dai"] for c in ds)
    print(f"Kiểm kê: {len(ds)} clip, tổng {tong / 60:.1f} phút, {cum} cụm thời gian (khoảng nghỉ > {a.khoang_phut:g} phút)")
    for nhan, k in (("HDR (cat sẽ tự tonemap)", "hdr"), ("VFR (cat ép khung đều)", "vfr"), ("khung dọc", "doc")):
        n = sum(1 for c in ds if c[k])
        if n:
            print(f"  {nhan}: {n}")
    dai = [c for c in ds if c["dai"] > a.dai_tu]
    if dai:
        print(f"  {len(dai)} clip dài hơn {a.dai_tu:g} giây: khảo sát thêm khung theo bước; nên gỡ băng nếu có lời cần dùng")
    nguon_gio = {c["nguon_gio"] for c in ds}
    print(f"  Giờ quay lấy từ: {', '.join(sorted(nguon_gio))}")
    print(f"→ {kiem_ke_path(da)}  và recap/KIEM-KE.md")


# ----------------------------------------------------------------------------- doi-ten
def ten_moi(c):
    hhmm = c["gio"][11:13] + c["gio"][14:16]
    m = RE_DA_DOI.match(c["ten"])
    if m and int(m.group(1)) == c["stt"]:
        hhmm = m.group(2) + m.group(3)   # tên đã đổi trước đó: giữ giờ đã ghi
    phan = [f"{c['stt']:03d}", hhmm]
    if slug(c.get("giai_doan")):
        phan.append(slug(c["giai_doan"], 24))
    if slug(c.get("mo_ta")):
        phan.append(slug(c["mo_ta"], 48))
    return "_".join(phan) + os.path.splitext(c["ten"])[1].lower()


def lenh_doi_ten(a):
    da = du_an_path(a.du_an)
    kk = nap_kiem_ke(da)
    nguon = kk["nguon"]
    so_do = os.path.join(nguon, "DOI-TEN.json")
    if a.hoan_tac:
        m = doc_json(so_do)
        if not m:
            sys.exit("DỪNG: không có DOI-TEN.json trong thư mục nguồn")
        for moi, cu in m["doi"].items():
            pm, pc = os.path.join(nguon, moi), os.path.join(nguon, cu)
            if os.path.exists(pm) and not os.path.exists(pc):
                os.rename(pm, pc)
        for c in kk["clip"]:
            if c.get("ten_goc"):
                c["ten"] = c.pop("ten_goc")
                c["duong_dan"] = os.path.join(nguon, c["ten"])
        ghi_json(kiem_ke_path(da), kk)
        print(f"Đã trả {len(m['doi'])} tệp về tên cũ (DOI-TEN.json giữ lại để đối chiếu)")
        return
    thieu = [c["stt"] for c in kk["clip"] if not slug(c.get("mo_ta"))]
    doi = []
    for c in kk["clip"]:
        moi = ten_moi(c)
        if moi != c["ten"]:
            doi.append((c, moi))
    trung = {m for _, m in doi if sum(1 for _, x in doi if x == m) > 1}
    for c, moi in doi:
        print(f"  {c['ten']}  →  {moi}" + ("   [TRÙNG]" if moi in trung else ""))
    if thieu:
        print(f"Lưu ý: {len(thieu)} clip chưa có mo_ta (STT {', '.join(f'{x:03d}' for x in thieu[:12])}"
              f"{'...' if len(thieu) > 12 else ''}): tên chỉ có số và giờ")
    if trung:
        sys.exit("DỪNG: có tên mới trùng nhau; sửa mo_ta trong recap/kiem-ke.json")
    if not a.ghi:
        print(f"(xem trước {len(doi)} tệp; thêm --ghi để đổi tên thật, --hoan-tac để trả lại)")
        return
    m = doc_json(so_do, {"doi": {}}) or {"doi": {}}
    for c, moi in doi:
        pc, pm = os.path.join(nguon, c["ten"]), os.path.join(nguon, moi)
        if os.path.exists(pm):
            sys.exit(f"DỪNG: đã có tệp {moi}")
        os.rename(pc, pm)
        goc = m["doi"].pop(c["ten"], c["ten"])  # đổi lần hai vẫn trỏ về tên gốc đầu tiên
        m["doi"][moi] = goc
        c.setdefault("ten_goc", goc)
        c["ten"], c["duong_dan"] = moi, pm
    ghi_json(so_do, m)
    dong = ["# Đổi tên nguồn", "", "Tên mới `NNN_HHMM_<giai đoạn>_<mô tả>`: NNN theo giờ quay. Trả lại tên cũ: "
            "`python3 tools/recap.py doi-ten --du-an \"<dự án>\" --hoan-tac`.", "", "| Tên mới | Tên gốc |", "|---|---|"]
    dong += [f"| {k} | {v} |" for k, v in sorted(m["doi"].items())]
    with open(os.path.join(nguon, "DOI-TEN.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(dong) + "\n")
    ghi_json(kiem_ke_path(da), kk)
    print(f"Đã đổi tên {len(doi)} tệp; đối chiếu ở DOI-TEN.md / DOI-TEN.json trong thư mục nguồn")


# ----------------------------------------------------------------------------- khao-sat
def nhan_tg(t):
    """nhãn thời gian không có dấu hai chấm (drawtext coi ':' là phân cách tuỳ chọn)"""
    t = max(0.0, float(t))
    return f"{int(t // 60)}m{int(t % 60):02d}"


def chup_o(src, t, out, w, h, nhan):
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
          f"drawtext=text='{nhan}':x=5:y=5:fontcolor=yellow:fontsize={max(14, h // 11)}:box=1:boxcolor=black@0.6")
    # -skip_frame nokey: chỉ giải mã khung khoá gần mốc, nhanh hơn khoảng 12 lần với HEVC 4K của điện thoại
    return subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-skip_frame", "nokey", "-ss", f"{t:.2f}", "-i", src,
                             "-frames:v", "1", "-vf", vf, "-q:v", "4", out],
                            stdin=subprocess.DEVNULL)


def ghep_luoi(thu_muc_o, cot, hang, out):
    n = len(glob.glob(os.path.join(thu_muc_o, "o_*.jpg")))
    if not n:
        return False
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-start_number", "0",
                    "-i", os.path.join(thu_muc_o, "o_%03d.jpg"), "-vf", f"tile={cot}x{hang}:padding=4:color=0x202020",
                    "-frames:v", "1", "-q:v", "4", out], check=False)
    return os.path.isfile(out)


def chay_viec(viec, song_song, ns):
    """viec: list (args cho chup_o). Trả về số việc chưa làm vì hết ngân sách."""
    dang = []
    con = list(viec)
    while con or dang:
        dang = [p for p in dang if p.poll() is None]
        while con and len(dang) < song_song and not ns.het(8):
            dang.append(chup_o(*con.pop(0)))
        if ns.het(8) and not dang:
            break
        time.sleep(0.1)
    return len(con)


def lenh_khao_sat(a):
    da = du_an_path(a.du_an)
    kk = nap_kiem_ke(da)
    ra = os.path.join(da, "_kt", "khao-sat")
    tam = os.path.join(ra, ".o")
    os.makedirs(tam, exist_ok=True)
    ns = NganSach(a.gioi_han_giay)
    ds = kk["clip"]
    # 1) ảnh tổng quan: mỗi clip một ô khung giữa, 5 x 4 ô mỗi trang
    moi_trang = 20
    for tr in range((len(ds) + moi_trang - 1) // moi_trang):
        out = os.path.join(ra, f"_tong-{tr + 1:02d}.jpg")
        if os.path.isfile(out):
            continue
        d = os.path.join(tam, f"tong{tr}")
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        viec = []
        for i, c in enumerate(ds[tr * moi_trang:(tr + 1) * moi_trang]):
            viec.append((c["duong_dan"], c["dai"] * 0.5, os.path.join(d, f"o_{i:03d}.jpg"), 320, 180,
                         f"{c['stt']:03d} {c['gio'][11:13]}h{c['gio'][14:16]} dai {nhan_tg(c['dai'])}"))
        if chay_viec(viec, a.song_song, ns):
            print("HẾT NGÂN SÁCH (ảnh tổng quan) - chạy lại cùng lệnh")
            return
        ghep_luoi(d, 5, 4, out)
        shutil.rmtree(d, ignore_errors=True)
    # 2) bảng khung từng clip: so_khung khung rải đều; clip dài thêm trang theo bước
    for c in ds:
        if ns.het(10):
            print("HẾT NGÂN SÁCH - chạy lại cùng lệnh để làm tiếp")
            return
        goc = f"{c['stt']:03d}"
        out = os.path.join(ra, f"{goc}.jpg")
        if not os.path.isfile(out):
            d = os.path.join(tam, goc)
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            k = a.so_khung
            viec = [(c["duong_dan"], c["dai"] * (i + 0.5) / k, os.path.join(d, f"o_{i:03d}.jpg"), 384, 216,
                     f"{goc} {nhan_tg(c['dai'] * (i + 0.5) / k)}") for i in range(k)]
            if chay_viec(viec, a.song_song, ns):
                print("HẾT NGÂN SÁCH - chạy lại cùng lệnh để làm tiếp")
                return
            ghep_luoi(d, 3, (k + 2) // 3, out)
            shutil.rmtree(d, ignore_errors=True)
        if c["dai"] > a.dai_tu:
            moc = [t for t in frange(a.buoc / 2, c["dai"], a.buoc)]
            for tr in range((len(moc) + 11) // 12):
                out2 = os.path.join(ra, f"{goc}-dai-{tr + 1:02d}.jpg")
                if os.path.isfile(out2):
                    continue
                d = os.path.join(tam, f"{goc}d{tr}")
                shutil.rmtree(d, ignore_errors=True)
                os.makedirs(d)
                viec = [(c["duong_dan"], t, os.path.join(d, f"o_{i:03d}.jpg"), 320, 180, f"{goc} {nhan_tg(t)}")
                        for i, t in enumerate(moc[tr * 12:(tr + 1) * 12])]
                if chay_viec(viec, a.song_song, ns):
                    print("HẾT NGÂN SÁCH - chạy lại cùng lệnh để làm tiếp")
                    return
                ghep_luoi(d, 4, 3, out2)
                shutil.rmtree(d, ignore_errors=True)
    # 3) tỉ lệ có tiếng (chỉ đọc tiếng, nhanh): gợi ý clip có lời
    if a.tieng:
        for c in ds:
            if "ti_le_tieng" in c or not c["co_tieng"]:
                continue
            if ns.het(10):
                ghi_json(kiem_ke_path(da), kk)
                print("HẾT NGÂN SÁCH (đo tiếng) - chạy lại cùng lệnh")
                return
            lang = phat_hien_lang(c["duong_dan"], -35, 0.5)
            im = sum(s["end"] - s["start"] for s in lang)
            c["ti_le_tieng"] = round(max(0.0, 1 - im / max(c["dai"], 0.1)), 2)
        ghi_json(kiem_ke_path(da), kk)
    shutil.rmtree(tam, ignore_errors=True)
    n = len(glob.glob(os.path.join(ra, "*.jpg")))
    print(f"XONG khảo sát: {n} ảnh ở {ra}")
    print("  Đọc _tong-*.jpg trước để có bản đồ cả buổi, rồi mở bảng khung của các clip cần chọn.")


def frange(a, b, s):
    t = a
    while t < b:
        yield t
        t += s


# ----------------------------------------------------------------------------- tiếng, lặng
def phat_hien_lang(src, nguong_db, toi_thieu):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", src, "-vn",
                        "-af", f"silencedetect=noise={nguong_db}dB:d={toi_thieu}", "-f", "null", "-"],
                       capture_output=True, text=True)
    out, st = [], None
    for line in p.stderr.splitlines():
        m1 = re.search(r"silence_start:\s*(-?[0-9.]+)", line)
        m2 = re.search(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", line)
        if m1:
            st = max(0.0, float(m1.group(1)))
        elif m2 and st is not None:
            out.append({"start": round(st, 3), "end": round(float(m2.group(1)), 3),
                        "duration": round(float(m2.group(2)), 3)})
            st = None
    if st is not None:
        d = thoi_luong(src)
        out.append({"start": round(st, 3), "end": round(d, 3), "duration": round(d - st, 3)})
    return out


def doc_pcm(src, sr=16000, tu=None, dai=None):
    import numpy as np
    cmd = ["ffmpeg", "-nostdin", "-v", "error"]
    if tu is not None:
        cmd += ["-ss", str(tu)]
    cmd += ["-i", src]
    if dai is not None:
        cmd += ["-t", str(dai)]
    cmd += ["-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True)
    return np.frombuffer(p.stdout, dtype=np.float32)


def lang_theo_nang_luong(src, cong_db=6.0, toi_thieu=0.25):
    """Khoảng lặng theo năng lượng ngắn hạn (RMS cửa sổ 50 ms, bước 10 ms) dưới ngưỡng = sàn ồn (phân vị 10)
    + cong_db. silencedetect so từng mẫu nên một tiếng lách cách là cắt quãng lặng: trong phòng hội thảo ồn
    nó trả về rỗng ở mọi ngưỡng hợp lý (BAI-HOC chủ đề 6 và 26). Trả (danh sách quãng lặng, ngưỡng dB)."""
    import numpy as np
    sr = 16000
    x = doc_pcm(src, sr=sr)
    if x.size < sr:
        return [], None
    win, hop = int(0.05 * sr), int(0.01 * sr)
    k = 1 + (x.size - win) // hop
    c = np.concatenate([[0.0], np.cumsum(x.astype(np.float64) ** 2)])
    e = (c[hop * np.arange(k) + win] - c[hop * np.arange(k)]) / win
    db = 10 * np.log10(e + 1e-12)
    nguong = float(np.percentile(db, 10)) + cong_db
    duoi = db < nguong
    out, i = [], 0
    while i < k:
        if duoi[i]:
            j = i
            while j < k and duoi[j]:
                j += 1
            st, en = i * hop / sr, ((j - 1) * hop + win) / sr
            if en - st >= toi_thieu:
                out.append({"start": round(st, 3), "end": round(en, 3), "duration": round(en - st, 3)})
            i = j
        else:
            i += 1
    return out, round(nguong, 1)


# ----------------------------------------------------------------------------- cat
def nap_bang(da, ten="canh.json"):
    p = os.path.join(da, "recap", ten)
    b = doc_json(p)
    if b is None:
        sys.exit(f"DỪNG: chưa có bảng cảnh {p}")
    if isinstance(b, dict):
        b = b.get("canh", [])
    ids = [r["id"] for r in b if "id" in r]
    trung = {i for i in ids if ids.count(i) > 1}
    if trung:
        sys.exit(f"DỪNG: id cảnh trùng: {', '.join(sorted(trung))}")
    return b


def lenh_cat(a):
    da = du_an_path(a.du_an)
    kk = nap_kiem_ke(da)
    bang = nap_bang(da, a.bang)
    meta_p = os.path.join(da, "recap", "cat-meta.json")
    meta = doc_json(meta_p, {}) or {}
    ra = os.path.join(da, "nguon")
    os.makedirs(ra, exist_ok=True)
    os.makedirs(os.path.join(da, "transcript"), exist_ok=True)
    ns = NganSach(a.gioi_han_giay)
    viec = []
    for r in bang:
        if "the" in r:
            continue
        c = tim_clip(kk, r["clip"])
        tu, den = float(r["tu"]), float(r["den"])
        if not (0 <= tu < den <= c["dai"] + 0.05):
            sys.exit(f"DỪNG: cảnh {r['id']}: {tu}-{den} nằm ngoài clip {c['stt']:03d} (dài {c['dai']:.1f} s)")
        st = max(0.0, tu - a.dem)
        en = min(c["dai"], den + a.dem)
        ten = f"{r['id']}_{c['stt']:03d}.mp4"
        ky = f"{c['ten']}|{st:.3f}|{en:.3f}|{a.rong}|{int(c['hdr'])}"
        m = {"file": f"nguon/{ten}", "clip": f"{c['stt']:03d}", "nguon": c["ten"], "tu": tu, "den": den,
             "in": round(tu - st, 3), "out": round(tu - st + (den - tu), 3), "dau_proxy": round(st, 3),
             "dai_proxy": round(en - st, 3), "tieng": r.get("tieng", "tat"), "hdr": c["hdr"], "ky": ky}
        out = os.path.join(ra, ten)
        cu = meta.get(r["id"])
        if os.path.isfile(out) and cu and cu.get("ky") == ky:
            meta[r["id"]] = {**cu, **{k: m[k] for k in ("tieng",)}}
            continue
        meta[r["id"]] = m
        viec.append((c, st, en - st, out, r["id"]))
    ghi_json(meta_p, meta)
    if viec:
        print(f"Cần cắt {len(viec)} proxy (đệm {a.dem:g} s mỗi đầu, rộng {a.rong} px)")
    dang, xong, loi = [], [], []
    while viec or dang:
        con_chay = []
        for p, tmp, out, sid in dang:
            if p.poll() is None:
                con_chay.append((p, tmp, out, sid))
            elif p.returncode == 0 and os.path.isfile(tmp):
                os.replace(tmp, out)
                xong.append(sid)
            else:
                print(f"  LỖI cắt {sid} (mã {p.returncode})")
                loi.append(sid)
                try:
                    os.remove(tmp)
                except OSError:
                    pass
        dang = con_chay
        while viec and len(dang) < a.song_song and not ns.het(25):
            c, st, d, out, sid = viec.pop(0)
            fps = c["fps"] if 20 <= c["fps"] <= 61 else 30
            fps_s = "30000/1001" if abs(fps - 29.97) < 0.02 else ("60000/1001" if abs(fps - 59.94) < 0.02 else f"{fps:g}")
            vf = []
            if c["hdr"]:
                vf.append(TONEMAP_VF)
            vf.append(f"scale='if(gt(iw,ih),{a.rong},-2)':'if(gt(iw,ih),-2,{a.rong})'")
            vf.append("format=yuv420p")
            tmp = out[:-4] + ".part.mp4"
            cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{st:.3f}", "-i", c["duong_dan"],
                   "-t", f"{d:.3f}", "-vf", ",".join(vf), "-r", fps_s,
                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                   "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", tmp]
            if not c["co_tieng"]:
                cmd[cmd.index("-c:a"):cmd.index("-movflags")] = ["-an"]
            dang.append((subprocess.Popen(cmd, stdin=subprocess.DEVNULL), tmp, out, sid))
        if ns.het(25) and viec and not dang:
            break
        time.sleep(0.3)
    if loi:
        sys.exit(f"DỪNG: {len(loi)} proxy cắt lỗi ({', '.join(loi)}); xem thông báo ffmpeg phía trên")
    if viec:
        print(f"HẾT NGÂN SÁCH: còn {len(viec)} proxy - chạy lại cùng lệnh")
        return
    # silences cho cảnh giữ tiếng (để "snap" của assemble.py hút điểm cắt về quãng lặng)
    n_sil = 0
    for sid, m in sorted(meta.items()):
        if m.get("tieng") != "giu":
            continue
        out = os.path.join(da, m["file"])
        if not os.path.isfile(out):
            continue
        stem = os.path.splitext(os.path.basename(out))[0]
        sp = os.path.join(da, "transcript", f"{stem}.silences.json")
        if os.path.isfile(sp) and os.path.getmtime(sp) >= os.path.getmtime(out):
            continue
        if ns.het(10):
            print("HẾT NGÂN SÁCH (khoảng lặng) - chạy lại cùng lệnh")
            return
        lang, ng = lang_theo_nang_luong(out, a.lang_cong, a.lang_toi_thieu)
        ghi_json(sp, lang)
        m["nguong_lang"], m["so_quang_lang"] = ng, len(lang)
        if not lang:
            print(f"  {sid}: không tìm thấy quãng lặng nào (snap sẽ không dời mép); nghe mép cắt bằng tai")
        n_sil += 1
    ghi_json(meta_p, meta)
    thieu = [sid for sid, m in meta.items() if not os.path.isfile(os.path.join(da, m["file"]))]
    du = sorted(set(os.path.basename(f) for f in glob.glob(os.path.join(ra, "*_*.mp4")))
                - {os.path.basename(m["file"]) for m in meta.values()}
                - {os.path.basename(f) for f in glob.glob(os.path.join(ra, "*.part.mp4"))})
    ids_bang = {r["id"] for r in bang if "id" in r}
    bo = [sid for sid in meta if sid not in ids_bang]
    for sid in bo:
        meta.pop(sid)
    ghi_json(meta_p, meta)
    print(f"XONG cắt: {len(meta)} proxy" + (f", {n_sil} tệp khoảng lặng mới" if n_sil else ""))
    if thieu:
        print(f"  THIẾU proxy: {', '.join(thieu)}")
    if du:
        print(f"  Proxy không còn trong bảng cảnh (dọn khi anh duyệt): {', '.join(du)}")


# ----------------------------------------------------------------------------- timeline
def lenh_timeline(a):
    da = du_an_path(a.du_an)
    bang = nap_bang(da, a.bang)
    meta = doc_json(os.path.join(da, "recap", "cat-meta.json"), {}) or {}
    tl_p = os.path.join(da, "timeline.json")
    cu = doc_json(tl_p)
    if cu is not None and cu == doc_json(os.path.join(TOOLS, "mau-du-an", "timeline.json")):
        cu = None   # timeline mẫu do du-an-moi.py chép vào: coi như chưa có
    segs = []
    for r in bang:
        if "the" in r:
            segs.append({"type": "insert", "src": r["the"]})
            continue
        m = meta.get(r["id"])
        if not m:
            sys.exit(f"DỪNG: cảnh {r['id']} chưa có proxy; chạy lệnh cat")
        giu = r.get("tieng", "tat") == "giu"
        s = {"type": "video", "src": m["file"], "in": m["in"], "out": m["out"], "snap": giu}
        if not giu:
            s["volumeDb"] = -90
        elif r.get("volumeDb") is not None:
            s["volumeDb"] = r["volumeDb"]
        if r.get("mo"):
            s["fadeIn"] = r["mo"]
        if r.get("tat_dan"):
            s["fadeOut"] = r["tat_dan"]
        if r.get("chuong"):
            s["chapter"] = r["chuong"]
        if r.get("chu"):
            ov = {"src": r["chu"], "at": r.get("chu_at", 0.5)}
            if r.get("chu_dai"):
                ov["duration"] = r["chu_dai"]
            s["overlay"] = ov
        s["_recap"] = r["id"]
        segs.append(s)
    tl = {"aspect": a.khung, "fps": 30, "fadeColor": "black"}
    for k in ("intro", "outro"):
        v = getattr(a, k) or (cu or {}).get(k)
        if v:
            tl[k] = v
    if a.chuong_dau:
        tl["chapterIntro"] = a.chuong_dau
    tl["segments"] = segs
    nh = doc_json(os.path.join(da, "recap", "nhip.json"))
    if (cu or {}).get("music"):
        tl["music"] = cu["music"]
    elif nh:
        tl["music"] = {"src": nh["src"], "mode": "full", "gainDb": nh["goi_y_gain_nhac_dan"], "duck": True,
                       "fadeIn": 2, "fadeOut": 4}
    if cu and cu.get("_chinhTay"):
        sys.exit("DỪNG: timeline.json có _chinhTay (anh đã chỉnh tay trên Bàn dựng): không sinh lại; sửa thẳng trên file")
    dich = tl_p if (cu is None or a.ghi_de) else os.path.join(da, "timeline.recap.json")
    ghi_json(dich, tl)
    print(f"→ {dich}  ({len(segs)} đoạn; trường _recap giữ id cảnh để đối chiếu)")
    if dich != tl_p:
        print("  timeline.json đã có: bản mới ghi riêng; so rồi thêm --ghi-de nếu muốn thay")


# ----------------------------------------------------------------------------- nhac
def do_lufs(src):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", src, "-vn", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s*(-?[0-9.]+) LUFS", p.stderr)
    return float(m[-1]) if m else None


def tim_nhip(src, bpm=None, giay=120):
    """Lưới phách: dòng năng lượng khởi âm [onset] (thông lượng phổ), tự tương quan tìm nhịp 50-180, dò pha."""
    import numpy as np
    sr, hop, n = 11025, 256, 1024
    x = doc_pcm(src, sr=sr, dai=giay)
    if x.size < sr * 5:
        sys.exit("DỪNG: nhạc quá ngắn để dò nhịp")
    k = 1 + (x.size - n) // hop
    idx = np.arange(n)[None, :] + hop * np.arange(k)[:, None]
    fr = x[idx] * np.hanning(n)[None, :]
    mag = np.log1p(10 * np.abs(np.fft.rfft(fr, axis=1)))
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(axis=1)
    flux = flux - np.convolve(flux, np.ones(16) / 16, mode="same")
    env = np.maximum(flux, 0)
    env /= (env.max() + 1e-9)
    fps = sr / hop
    ac = np.correlate(env, env, mode="full")[env.size - 1:]
    ung = []
    for b in np.arange(50, 180.01, 0.5):
        lag = fps * 60 / b
        l0 = int(lag)
        v = ac[l0] + (lag - l0) * (ac[l0 + 1] - ac[l0]) if l0 + 1 < ac.size else 0
        tro = np.exp(-0.5 * (np.log2(b / 100.0) / 0.9) ** 2)  # ưu tiên nhẹ quanh 100 nhịp
        ung.append((v * tro, b))
    ung.sort(reverse=True)
    dai_env = env.size / fps

    def luoi(bb):
        """điểm khớp tốt nhất của lưới phách nhịp bb (trung bình năng lượng khởi âm tại phách) và pha tương ứng"""
        TT = 60.0 / bb
        tot, best = -1.0, 0.0
        for off in np.arange(0, TT, 0.01):
            t = np.arange(off, dai_env, TT)
            sc = env[np.clip(np.round(t * fps).astype(int), 0, env.size - 1)].mean()
            if sc > tot:
                tot, best = sc, off
        return tot, best

    # tự tương quan cho nhịp thô (lượng tử theo bước khung ~23 ms nên lệch vài nhịp), rồi tinh chỉnh ±3 nhịp theo lưới
    b0 = ung[0][1]
    bpm_do = max(np.arange(b0 - 3, b0 + 3.01, 0.1), key=lambda bb: luoi(bb)[0])
    bpm_do = round(float(bpm_do), 1)
    b = float(bpm or bpm_do)
    return b, bpm_do, float(luoi(b)[1])


def nhip_cua_xuong(p):
    """Nhạc riêng (<khoá>_xuong-rieng.*): đọc số nhịp trong mô tả của bảng BAN ở tools/soan-nhac.py."""
    m = re.match(r"(.+)_xuong-rieng\.", os.path.basename(p))
    nguon = os.path.join(TOOLS, "soan-nhac.py")
    if not m or not os.path.isfile(nguon):
        return None
    s = open(nguon, encoding="utf-8").read()
    dong = re.search(r'"' + re.escape(m.group(1)) + r'"\s*:\s*\(([^)]*)\)', s)
    if not dong:
        return None
    if "không nhịp" in dong.group(1):
        return -1.0
    k = re.search(r"(\d+) nhịp", dong.group(1))
    return float(k.group(1)) if k else None


def lenh_nhac(a):
    da = du_an_path(a.du_an)
    src = a.nhac
    p = src if os.path.isabs(src) else os.path.join(XUONG, src)
    if not os.path.isfile(p):
        p = os.path.join(da, src)
    if not os.path.isfile(p):
        sys.exit(f"DỪNG: không thấy nhạc {src}")
    L = do_lufs(p)
    dai = thoi_luong(p)
    khong_nhip = False
    if not a.bpm:
        a.bpm = nhip_cua_xuong(p)
        if a.bpm == -1.0:
            khong_nhip, a.bpm = True, None
            print("  Nhạc riêng của xưởng ghi \"không nhịp\": không có phách để khop-nhip, cắt theo hình")
        elif a.bpm:
            print(f"  Nhạc riêng của xưởng: lấy nhịp {a.bpm:g} ghi trong tools/soan-nhac.py")
    b, bpm_do, off = tim_nhip(p, a.bpm)
    T = 60 / b
    phach = [round(off + i * T, 3) for i in range(int((dai - off) / T) + 1)]
    d = {"src": src, "lufs": L, "dai": round(dai, 2), "bpm": b, "bpm_do": bpm_do, "pha": round(off, 3),
         "khong_nhip": khong_nhip,
         "phach": phach,
         "goi_y_gain_nhac_dan": round(NHAC_DAN - L, 1) if L is not None else -5,
         "goi_y_gain_nen_loi": round(NHAC_LOI - L, 1) if L is not None else -15}
    ghi_json(os.path.join(da, "recap", "nhip.json"), d)
    print(f"Nhạc {os.path.basename(p)}: {mmss(dai)}, {L} LUFS")
    print(f"  Nhịp dùng {b:g} (máy dò {bpm_do:g}), phách đầu ở {off:.2f} s, một phách {T:.3f} s")
    if a.bpm and abs(bpm_do - a.bpm) > 2 and abs(bpm_do - 2 * a.bpm) > 3 and abs(2 * bpm_do - a.bpm) > 3:
        print("  LƯU Ý: nhịp máy dò khác xa nhịp truyền vào; nghe lại hoặc kiểm số trong soan-nhac.py")
    if not a.bpm:
        print(f"  Máy dò nhịp có thể nhầm gấp đôi hay một nửa ({b / 2:g} hoặc {b * 2:g}): nghe một lượt; "
              "nhịp đúng khác thì truyền --bpm")
    print(f"  gainDb gợi ý: recap ít lời (nhạc làm chính, nhạc khoảng {NHAC_DAN:g} LUFS) {d['goi_y_gain_nhac_dan']}; "
          f"clip nói nhiều (nhạc nền dưới lời, khoảng {NHAC_LOI:g} LUFS) {d['goi_y_gain_nen_loi']}")
    print(f"→ {os.path.join(da, 'recap', 'nhip.json')}")


# ----------------------------------------------------------------------------- dòng thời gian ước tính
def thoi_gian_phim(da, tl, map_p=None):
    """Trả list (đoạn, bắt đầu, dài) theo trục thành phẩm. Có map.json của bản nháp thì dùng mốc thật."""
    out = []
    if map_p:
        mp = doc_json(map_p)
        parts = [p for p in mp["parts"]]
        # bỏ intro/outro: đoạn segments khớp theo thứ tự part không phải intro/outro
        seg_parts = [p for p in parts if not (p["kind"] == "insert" and p["src"] in (tl.get("intro"), tl.get("outro"))
                                              and p["part"] in (0, len(parts) - 1))]
        if len(seg_parts) == len(tl["segments"]):
            return [(s, p["start"], p["dur"]) for s, p in zip(tl["segments"], seg_parts)]
        print(f"  (map.json có {len(seg_parts)} part, timeline {len(tl['segments'])} đoạn: không khớp, dùng ước tính)")
    t = thoi_luong(os.path.join(da, tl["intro"])) if tl.get("intro") else 0.0
    for s in tl["segments"]:
        d = thoi_luong(os.path.join(da, s["src"])) if s["type"] == "insert" else float(s["out"]) - float(s["in"])
        out.append((s, t, d))
        t += d
    return out


def la_cam(s):
    return s.get("type") == "video" and float(s.get("volumeDb", 0)) <= -60


# ----------------------------------------------------------------------------- khop-nhip
def lenh_khop_nhip(a):
    da = du_an_path(a.du_an)
    tl_p = os.path.join(da, "timeline.json")
    tl = doc_json(tl_p)
    nh = doc_json(os.path.join(da, "recap", "nhip.json"))
    if not tl or not nh:
        sys.exit("DỪNG: cần timeline.json và recap/nhip.json (lệnh nhac)")
    if tl.get("_chinhTay") and a.ghi:
        sys.exit("DỪNG: timeline có _chinhTay: chỉ xem trước, không ghi")
    if nh.get("khong_nhip"):
        sys.exit("DỪNG: nhạc nền không có phách rõ (recap/nhip.json khong_nhip); cắt theo hình, không khop-nhip")
    T = 60.0 / nh["bpm"]
    pha = nh["pha"]
    buoc = T * a.moi
    meta = doc_json(os.path.join(da, "recap", "cat-meta.json"), {}) or {}
    theo_file = {m["file"]: m for m in meta.values()}
    tg = thoi_gian_phim(da, tl, a.map)
    lech = 0.0   # tổng thời lượng đã đổi phía trước
    bao = []
    for s, bd, d in tg:
        bd2 = bd + lech
        if not la_cam(s):
            bao.append((s, bd2, d, d, None))
            continue
        m = theo_file.get(s["src"])
        dai_proxy = m["dai_proxy"] if m else thoi_luong(os.path.join(da, s["src"]))
        lo = a.ngan
        hi = min(a.dai, dai_proxy - float(s["in"]) - 0.04)
        ov = s.get("overlay")
        if ov:
            od = float(ov.get("duration") or thoi_luong(os.path.join(da, ov["src"])))
            lo = max(lo, float(ov.get("at", 0)) + od + 0.1)
        if hi < lo:
            bao.append((s, bd2, d, d, "không đủ phần đệm để kéo"))
            continue
        ket = bd2 + d
        k = round((ket - pha) / buoc)
        ung = sorted((abs(pha + j * buoc - ket), pha + j * buoc) for j in range(k - 3, k + 4))
        moi = None
        for _, g in ung:
            dd = g - bd2
            if lo <= dd <= hi:
                moi = dd
                break
        if moi is None:
            bao.append((s, bd2, d, d, "không có phách trong khoảng cho phép"))
            continue
        moi = round(round(moi * 30) / 30, 4)   # đúng khung 30 fps
        lech += moi - d
        bao.append((s, bd2, d, moi, None))
        if a.ghi:
            s["out"] = round(float(s["in"]) + moi, 4)
    print(f"Lưới phách {nh['bpm']:g} nhịp, cắt trên mỗi {a.moi} phách ({buoc:.3f} s); cảnh câm {a.ngan:g}-{a.dai:g} s")
    print(" id/nguồn                  bắt đầu   dài cũ → mới    mép cắt   lệch phách")
    for s, bd2, d, moi, ly_do in bao:
        ten = s.get("_recap") or os.path.basename(s["src"])
        ket = bd2 + moi
        lp = ((ket - pha + buoc / 2) % buoc) - buoc / 2
        nhan = "câm" if la_cam(s) else ("thẻ" if s["type"] == "insert" else "lời")
        print(f" {ten[:22]:22} {nhan:4} {mmss(bd2):>8} {d:6.2f} → {moi:6.2f} {mmss(ket):>9} {lp:+7.2f}"
              + (f"   ({ly_do})" if ly_do else ""))
    lien = [moi for s, _, _, moi, _ in bao if la_cam(s)]
    lap = sum(1 for x, y in zip(lien, lien[1:]) if abs(x - y) < 0.05)
    if lap >= 3:
        print(f"  Lưu ý: {lap} cặp cảnh câm liền nhau dài bằng nhau; nhịp đều dễ đoán, cân nhắc đổi --moi hoặc tay một vài cảnh")
    print(f"Tổng thời lượng đổi {lech:+.2f} s. Cảnh có lời giữ nguyên; sau bản nháp chạy lại với --map để khớp theo mốc thật.")
    if a.ghi:
        ghi_json(tl_p, tl)
        print(f"→ đã ghi {tl_p}")
    else:
        print("(xem trước; thêm --ghi để sửa timeline.json)")


# ----------------------------------------------------------------------------- kiem
def lenh_kiem(a):
    da = du_an_path(a.du_an)
    tl = doc_json(os.path.join(da, "timeline.json"))
    if not tl:
        sys.exit("DỪNG: chưa có timeline.json")
    tg = thoi_gian_phim(da, tl, a.map)
    can = []
    intro = thoi_luong(os.path.join(da, tl["intro"])) if tl.get("intro") else 0
    outro = thoi_luong(os.path.join(da, tl["outro"])) if tl.get("outro") else 0
    tong = intro + sum(d for _, _, d in tg) + outro
    loi = sum(d for s, _, d in tg if s["type"] == "video" and not la_cam(s))
    cam = sum(d for s, _, d in tg if la_cam(s))
    the = sum(d for s, _, d in tg if s["type"] == "insert") + intro + outro
    print(f"Ước tính {mmss(tong)}: hình có lời {loi:.0f} s ({loi / max(tong, 1):.0%}), cảnh câm dưới nhạc {cam:.0f} s "
          f"({cam / max(tong, 1):.0%}), thẻ đồ họa {the:.0f} s")
    if a.muc_tieu:
        mt = doc_giay(a.muc_tieu)
        if abs(tong - mt) > 0.15 * mt:
            can.append(f"thời lượng {mmss(tong)} lệch hơn 15% so với mục tiêu {mmss(mt)}")
    truoc = None
    for i, (s, bd, d) in enumerate(tg):
        ten = s.get("_recap") or os.path.basename(s["src"])
        if s["type"] != "video":
            truoc = None
            continue
        if la_cam(s):
            if d < 1.5:
                can.append(f"{ten} @ {mmss(bd)}: cảnh câm {d:.1f} s quá ngắn để nhìn kịp (dưới 1,5 s)")
            if d > 8:
                can.append(f"{ten} @ {mmss(bd)}: cảnh câm {d:.1f} s dài; giữ chỉ khi là khoảnh khắc cảm xúc")
            if s.get("snap"):
                can.append(f"{ten}: cảnh câm đặt snap:true (vô tác dụng, có thể dời mép); đặt false")
        else:
            stem = os.path.splitext(os.path.basename(s["src"]))[0]
            if s.get("snap") and not os.path.isfile(os.path.join(da, "transcript", f"{stem}.silences.json")):
                can.append(f"{ten}: cảnh có lời snap:true nhưng không có transcript/{stem}.silences.json "
                           "(snap không tác dụng; chạy recap.py cat để sinh)")
        ov = s.get("overlay")
        if ov:
            od = float(ov.get("duration") or thoi_luong(os.path.join(da, ov["src"])))
            if float(ov.get("at", 0)) + od > d + 0.05:
                can.append(f"{ten}: chữ nổi {ov['src']} ({ov.get('at', 0)} + {od:.1f} s) dài quá cảnh ({d:.1f} s)")
        goc = s["src"].rsplit("_", 1)[-1] if "_" in os.path.basename(s["src"]) else s["src"]
        if truoc and goc == truoc and la_cam(s) and la_cam(tg[i - 1][0]):
            can.append(f"{ten}: liền sau một cảnh câm cùng clip nguồn (cùng góc máy); xen cảnh khác cỡ hay góc")
        truoc = goc
    if tg and not tg[-1][0].get("fadeOut") and tg[-1][0]["type"] == "video":
        can.append("đoạn cuối trước thẻ kết chưa có fadeOut: khép mềm cảnh khép buổi")
    ch = [s.get("chapter") for s, _, _ in tg if s.get("chapter")]
    if ch and all(re.fullmatch(r"[\x20-\x7e]+", x) for x in ch) and not tl.get("chapterIntro"):
        can.append("tên chương toàn tiếng Anh nhưng chưa có chapterIntro (assemble mặc định ghi 'Mở đầu' cho intro)")
    mu = tl.get("music") or {}
    nh = doc_json(os.path.join(da, "recap", "nhip.json"))
    if not mu.get("src"):
        can.append("chưa có nhạc nền")
    else:
        if mu.get("mode") != "full":
            can.append("recap nên dùng nhạc mode full + duck")
        if nh and nh.get("src") == mu["src"]:
            goi_y = nh["goi_y_gain_nhac_dan"] if cam > loi else nh["goi_y_gain_nen_loi"]
            if abs(float(mu.get("gainDb", -22)) - goi_y) > 4:
                can.append(f"gainDb {mu.get('gainDb')} khác gợi ý {goi_y} (recap {'ít' if cam > loi else 'nhiều'} lời)")
            T = 60 / nh["bpm"]
            lp = [] if nh.get("khong_nhip") else [abs(((bd + d - nh["pha"] + T / 2) % T) - T / 2) for s, bd, d in tg if la_cam(s)]
            if lp:
                trung = sum(1 for x in lp if x <= 0.07)
                print(f"Mép cắt cảnh câm trúng phách (±0,07 s): {trung}/{len(lp)}")
    for x in can:
        print(f"  CẦN XEM: {x}")
    print(f"{'ĐẠT' if not can else f'{len(can)} điểm cần xem'} (kiểm giấy; cổng thật vẫn là nghiem-thu.py sau khi dựng)")


# -----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Bộ lệnh dựng recap sự kiện từ nhiều clip rời")
    sp = ap.add_subparsers(dest="lenh", required=True)

    p = sp.add_parser("kiem-ke", help="bảng clip theo giờ quay")
    p.add_argument("nguon")
    p.add_argument("--du-an", required=True)
    p.add_argument("--lech-gio", type=float, default=7.0, help="múi giờ khi chỉ có creation_time UTC (mặc định +7)")
    p.add_argument("--khoang-phut", type=float, default=8.0, help="khoảng nghỉ tách cụm thời gian")
    p.add_argument("--dai-tu", type=float, default=120.0)
    p.set_defaults(f=lenh_kiem_ke)

    p = sp.add_parser("doi-ten", help="đổi tên nguồn NNN_HHMM_<giai-doan>_<mo-ta>")
    p.add_argument("--du-an", required=True)
    p.add_argument("--ghi", action="store_true")
    p.add_argument("--hoan-tac", action="store_true")
    p.set_defaults(f=lenh_doi_ten)

    p = sp.add_parser("khao-sat", help="ảnh tổng quan và bảng khung từng clip")
    p.add_argument("--du-an", required=True)
    p.add_argument("--so-khung", type=int, default=6)
    p.add_argument("--dai-tu", type=float, default=120.0, help="clip dài hơn: thêm trang khung theo bước")
    p.add_argument("--buoc", type=float, default=20.0)
    p.add_argument("--tieng", action="store_true", help="đo tỉ lệ có tiếng từng clip")
    p.add_argument("--song-song", type=int, default=3)
    p.add_argument("--gioi-han-giay", type=float, default=150)
    p.set_defaults(f=lenh_khao_sat)

    p = sp.add_parser("nhac", help="LUFS, gainDb gợi ý, lưới phách")
    p.add_argument("--du-an", required=True)
    p.add_argument("--nhac", required=True)
    p.add_argument("--bpm", type=float)
    p.set_defaults(f=lenh_nhac)

    p = sp.add_parser("cat", help="cắt proxy theo bảng cảnh")
    p.add_argument("--du-an", required=True)
    p.add_argument("--bang", default="canh.json")
    p.add_argument("--dem", type=float, default=1.0)
    p.add_argument("--rong", type=int, default=1920)
    p.add_argument("--lang-toi-thieu", type=float, default=0.25, help="quãng lặng ngắn nhất (giây)")
    p.add_argument("--lang-cong", type=float, default=6.0, help="ngưỡng lặng = sàn ồn + số dB này")
    p.add_argument("--song-song", type=int, default=2)
    p.add_argument("--gioi-han-giay", type=float, default=150)
    p.set_defaults(f=lenh_cat)

    p = sp.add_parser("timeline", help="bảng cảnh -> timeline.json")
    p.add_argument("--du-an", required=True)
    p.add_argument("--bang", default="canh.json")
    p.add_argument("--khung", default="ngang", choices=["ngang", "doc"])
    p.add_argument("--intro")
    p.add_argument("--outro")
    p.add_argument("--chuong-dau", help="tên chương của intro (mặc định của assemble: 'Mở đầu')")
    p.add_argument("--ghi-de", action="store_true")
    p.set_defaults(f=lenh_timeline)

    p = sp.add_parser("khop-nhip", help="kéo mép cắt cảnh câm vào phách nhạc")
    p.add_argument("--du-an", required=True)
    p.add_argument("--moi", type=int, default=1, help="cắt trên mỗi N phách (1 với nhạc chậm, 2 với nhạc nhanh)")
    p.add_argument("--ngan", type=float, default=2.0)
    p.add_argument("--dai", type=float, default=7.0)
    p.add_argument("--map", help="map.json của bản nháp để dùng mốc thật (sau snap)")
    p.add_argument("--ghi", action="store_true")
    p.set_defaults(f=lenh_khop_nhip)

    p = sp.add_parser("kiem", help="kiểm giấy timeline recap")
    p.add_argument("--du-an", required=True)
    p.add_argument("--muc-tieu")
    p.add_argument("--map")
    p.set_defaults(f=lenh_kiem)

    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
