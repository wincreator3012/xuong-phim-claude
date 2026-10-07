#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐĂNG TẢI: bộ đồ nghề của skill phim-dang-tai (mô tả YouTube, status Facebook, thumbnail).

Hai lệnh (từ gốc xưởng):

  1) JOB THUMBNAIL - đổi bản thiết kế thumbnail ngắn gọn thành job cho render-do-hoa.mjs:
       python3 tools/dang-tai.py job "../Du an/<x>/dang-tai/<video>/thumbnail.json"
     thumbnail.json (Claude soạn):
       {"theme": "light", "brandFile": "@xuong/brand/brand.json",   # "@xuong/" = gốc xưởng; đường khác tương đối so với file này
        "kicker": "TÊN CHUỖI",                                           # tuỳ chọn, dùng chung
        "logo": "<logo nhỏ>.png",                                          # tuỳ chọn, file trong brand/logo
        "ban": [
          {"out": "thumb-1.jpg", "aspect": "ngang", "layout": "chia-doi",
           "headline": "Kỹ năng của bạn\\nđang ở rổ nào?", "accent": "rổ nào?",
           "anh": ["k05", "k04"]},            # mã khung trong khung/khung.json; "k12#1" = mặt thứ 2
          ...]}
     Ra: thumbnail.job.json cạnh file (ảnh khung khai báo trong "assets", props "photos" đủ tâm mặt).
     Render trong sandbox: node tools/render-do-hoa.mjs <thumbnail.job.json> --studio <studio>

  2) KIỂM - cổng máy cho gói đăng tải, chạy TRƯỚC khi báo anh:
       python3 tools/dang-tai.py kiem "../Du an/<x>/dang-tai/<video>"
     Đọc dang-tai.json trong thư mục (schema: skills/phim-dang-tai/references/mau-dang-tai.md),
     kiểm giới hạn nền tảng, quy ước chữ của anh, mồi tương tác [engagement bait], chương YouTube,
     thumbnail (kích thước, tỉ lệ, 2 MB); ghi DANG-TAI.md (bản chép-dán) và soi-thumbnail.jpg (thumbnail
     ở cỡ thật trên bảng tin điện thoại, có nhãn thời lượng giả ở góc phải dưới) để Claude NHÌN.
     Mã thoát 0 = ĐẠT (có thể kèm lưu ý), 1 = KHÔNG ĐẠT.
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- job thumbnail

def co_chu(b):
    """Ước cỡ chữ tiêu đề (px trên khung 1920 hoặc 1080 rộng) đúng công thức fitSize của Thumbnail.tsx."""
    doc = b.get("aspect", "ngang") == "doc"
    W, H = (1080, 1920) if doc else (1920, 1080)
    u = min(W, H) / 100
    pad = u * 7
    n_anh = len(b.get("anh", []))
    lay = b.get("layout", "chia-doi")
    if doc:
        avail_w, avail_h, mx = W - pad * 2, H * 0.24 - u * 3.3 * 2.4, u * 14
    elif lay == "toan-anh":
        avail_w, avail_h, mx = W * 0.46 - pad * 1.4, H * 0.56, u * 17
    elif lay == "chia-doi":
        avail_w, avail_h, mx = W * (0.5 if n_anh > 1 else 0.44) - pad * 1.5, H * 0.6, u * 17
    else:
        arch = W * (0.36 if n_anh > 1 else 0.27)
        avail_w, avail_h, mx = W - arch - pad * 3.2, H * 0.62, u * 18
    lines = b["headline"].split("\n")
    longest = max(len(x) for x in lines)
    return b.get("headlineSize") or min(mx, avail_w / (longest * 0.6), avail_h / (len(lines) * 1.14)), doc


def cmd_job(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(spec_path))
    khung_path = os.path.join(base, spec.get("khung", "khung/khung.json"))
    khung = json.load(open(khung_path, encoding="utf-8"))
    by_id = {k["id"]: k for k in khung["ung_vien"]}
    khung_dir = os.path.dirname(khung_path)
    assets, jobs = [], []
    nho = []
    for b in spec["ban"]:
        size, doc = co_chu(b)
        nguong = 95 if doc else 110  # dưới ngưỡng này chữ còn chưa tới 10 px khi YouTube hiện thumbnail rộng 168 px (đẹp nhất từ 130)
        if size < nguong:
            nho.append(f"{b['out']}: chữ tiêu đề chỉ ~{size:.0f} px (cần từ {nguong}): rút dòng dài nhất"
                       f" (\"{max(b['headline'].split(chr(10)), key=len)}\") còn 8-10 ký tự hoặc bớt chữ")
        photos = []
        for ref in b.get("anh", []):
            kid, _, idx = ref.partition("#")
            k = by_id.get(kid)
            if not k:
                sys.exit(f"Không có khung {kid} trong {khung_path}")
            mat = k["mat"][int(idx or 0)]
            fname = f"{os.path.basename(base)[:40]}-{k['file']}"
            rel = os.path.relpath(os.path.join(khung_dir, k["file"]), base)
            if rel not in [a[0] for a in assets]:
                assets.append((rel, fname))
            p = {"file": fname, "w": k["w"], "h": k["h"], "cx": mat["cx"], "cy": mat["cy"], "faceH": mat["h"]}
            p.update(b.get("chinh_anh", {}).get(ref, {}))  # faceScale, focusX, focusY riêng từng ảnh
            photos.append(p)
        props = {"layout": b.get("layout", "chia-doi"), "headline": b["headline"], "accent": b.get("accent", ""),
                 "kicker": b.get("kicker", spec.get("kicker", "")), "photos": photos}
        if b.get("photoSide"):
            props["photoSide"] = b["photoSide"]
        for key in ("faceScale", "headlineSize"):
            if key in b:
                props[key] = b[key]
        logo = b.get("logo", spec.get("logo"))
        if logo:
            props["logoFile"] = logo
            rel = "@xuong/brand/logo/" + logo  # gốc xưởng, không phụ thuộc chỗ để dự án
            if rel not in [a[0] for a in assets]:
                assets.append((rel, logo))
        if b.get("theme"):
            props["theme"] = b["theme"]
        jobs.append({"comp": "Thumbnail", "out": b["out"], "still": True, "aspect": b.get("aspect", "ngang"),
                     "props": props})
    # render-do-hoa.mjs chép asset vào public/brand/: đổi tên để khung của hai video không đè nhau
    job = {"aspect": "ngang", "theme": spec.get("theme", "light"), "outDir": spec.get("outDir", "."),
           "assets": [{"from": rel, "as": fname} for rel, fname in assets], "jobs": jobs}
    if spec.get("brandFile"):
        job["brandFile"] = spec["brandFile"]
    out = os.path.join(base, "thumbnail.job.json")
    json.dump(job, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✓ {len(jobs)} bản thumbnail → {os.path.relpath(out, ROOT)}")
    for rel, fname in assets:
        print(f"   ảnh {rel} → public/brand/{fname}")
    for x in nho:
        print(f"  ✗ {x}")
    if nho:
        sys.exit(1)


# ---------------------------------------------------------------- kiểm

TU_CAM = [  # (mẫu, lời nhắc) - PHONG-CACH mục 4 và quy ước viết của anh
    (r"—", "gạch dài (—): dùng gạch ngang thường hoặc dấu hai chấm"),
    (r"\bdẫn dắt\b", "\"dẫn dắt\": dùng \"lãnh đạo\", \"hướng dẫn\""),
    (r"\bnhân văn\b", "\"nhân văn\": humanistic là \"nhân bản\""),
    (r"\bsang chấn\b", "\"sang chấn\": dùng \"chấn thương tâm lý\""),
    (r"\bđa mê tẩu\b", "\"đa mê tẩu\": dùng \"lý thuyết đa phế vị\""),
    (r"\blược đồ\b", "\"lược đồ\": schema là \"cấu trúc nhận thức\""),
    (r"\bthấu cảm\b", "\"thấu cảm\": empathy là \"đồng cảm\""),
    (r"\bnổi lên\b", "\"nổi lên\" (emergence): dùng \"khởi sinh\" nếu là thuật ngữ"),
]
TU_NHAC = [  # lưu ý, không chặn
    (r"\btrí tuệ nhân tạo\b", "văn bản công khai của anh dùng \"trí năng nhân tạo\" cho AI"),
    # cụm sáo văn AI (tầng cụm từ của khung chống văn AI): nhắc để viết lại cụ thể hơn
    (r"\btrong (bối cảnh|thời đại|kỷ nguyên)\b", "mở bằng khung chung chung, thay bằng chi tiết cụ thể"),
    (r"\bhãy cùng\b", "\"hãy cùng\": cụm sáo"), (r"\bhành trình\b", "\"hành trình\": chỉ dùng khi có chuyến đi thật"),
    (r"\bbạn đã bao giờ tự hỏi\b", "mở bằng câu hỏi sáo"), (r"\bbí mật\b", "\"bí mật\": dễ thành giật tít"),
    (r"\b(vô cùng|cực kỳ|đột phá|vượt trội|then chốt)\b", "từ phóng đại, thay bằng điều cụ thể"),
]
MOI_TUONG_TAC = [  # Meta hạ phân phối; YouTube coi là tương tác giả; trái giá trị của anh
    r"\b(comment|bình luận|gõ|thả tim|like)\b[^.\n?]{0,30}\bnếu\b",
    r"\bnếu\b[^.\n?]{0,40}\b(comment|bình luận|gõ \"?\w+\"?|thả tim|like|share|chia sẻ)\b",
    r"\btag\b[^.\n]{0,20}\b(bạn|người)\b", r"\bgắn thẻ\b[^.\n]{0,20}\b(bạn|người)\b",
    r"\bshare ngay\b", r"\bchia sẻ ngay\b", r"\bđừng bỏ lỡ\b", r"\bbỏ lại phía sau\b", r"\btụt hậu\b",
    r"\bbị bỏ lại\b", r"\bSỐC\b", r"\bsốc\b", r"\bbí mật (mà )?không ai\b", r"\bkhông thể tin\b",
    r"\bxem ngay\b", r"\bcuối video\b.{0,20}\bbất ngờ\b",
]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF⭐⭕‼⁉]")
URL = re.compile(r"https?://\S+|www\.\S+")
CHUONG = re.compile(r"^\s*((?:\d+:)?\d{1,2}:\d{2})\s+(.+)$")


def secs(ts):
    parts = [int(x) for x in ts.split(":")]
    s = 0
    for p in parts:
        s = s * 60 + p
    return s


def van_ban_chung(ten, text, loi, nhac):
    for pat, msg in TU_CAM:
        if re.search(pat, text, flags=re.IGNORECASE if pat.startswith(r"\b") else 0):
            loi.append(f"{ten}: {msg}")
    for pat, msg in TU_NHAC:
        if re.search(pat, text, flags=re.IGNORECASE):
            nhac.append(f"{ten}: {msg}")
    for pat in MOI_TUONG_TAC:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            loi.append(f"{ten}: mồi tương tác / khung sợ hãi \"{m.group(0)}\" - viết lại thành lời mời thật")
    if EMOJI.search(text):
        loi.append(f"{ten}: có emoji")
    if "<" in text or ">" in text:
        loi.append(f"{ten}: có dấu < hoặc > (YouTube không nhận)")
    if re.search(r"!{2,}|\?{2,}", text):
        loi.append(f"{ten}: dấu câu lặp (!!, ??)")


def title_case(line):
    words = [w for w in re.findall(r"[^\W\d_]+", line) if len(w) > 1]
    if len(words) < 4:
        return False
    caps = sum(1 for w in words if w[0].isupper())
    return caps / len(words) > 0.6


def all_caps(line):
    letters = [c for c in line if c.isalpha()]
    return len(letters) > 8 and sum(c.isupper() for c in letters) / len(letters) > 0.6


def kiem_chuong(desc, loi, nhac, chuong_file):
    rows = []
    for line in desc.splitlines():
        m = CHUONG.match(line)
        if m:
            rows.append((secs(m.group(1)), m.group(1), m.group(2).strip()))
    if not rows:
        nhac.append("mô tả YouTube: không có chương (bài dài từ 3 phút nên có)")
        return
    if rows[0][0] != 0:
        loi.append("chương YouTube: chương đầu phải là 0:00")
    if len(rows) < 3:
        loi.append("chương YouTube: cần tối thiểu 3 chương")
    for (a, ta, _), (b, tb, nb) in zip(rows, rows[1:]):
        if b <= a:
            loi.append(f"chương YouTube: {tb} không tăng dần")
        elif b - a < 10:
            loi.append(f"chương YouTube: {ta} → {tb} ngắn hơn 10 giây")
    if chuong_file and os.path.exists(chuong_file):
        goc = [ln.split(" ", 1)[0] for ln in open(chuong_file, encoding="utf-8").read().splitlines() if ln.strip()]
        if [r[1] for r in rows] != goc:
            loi.append(f"chương YouTube: mốc khác {os.path.basename(chuong_file)} (mốc phải lấy từ tool, không gõ tay)")


def kiem_anh(path, khung, loi, nhac):
    try:
        from PIL import Image
    except ImportError:
        nhac.append("không có PIL: bỏ qua kiểm kích thước ảnh")
        return None
    if not os.path.exists(path):
        loi.append(f"thumbnail: thiếu {os.path.basename(path)}")
        return None
    im = Image.open(path)
    w, h = im.size
    size = os.path.getsize(path)
    ten = os.path.basename(path)
    if size > 2 * 1024 * 1024:
        loi.append(f"{ten}: {size / 1048576:.2f} MB, vượt 2 MB")
    if khung == "ngang":
        if abs(w / h - 16 / 9) > 0.01:
            loi.append(f"{ten}: tỉ lệ {w}x{h} không phải 16:9")
        if w < 1280:
            loi.append(f"{ten}: rộng {w} px, YouTube khuyên từ 1280 px")
    else:
        if abs(w / h - 9 / 16) > 0.01:
            loi.append(f"{ten}: tỉ lệ {w}x{h} không phải 9:16")
    return im.convert("RGB")


def soi_thumbnail(imgs, out):
    """Ảnh soi: mỗi thumbnail ngang ở ba cỡ thật trên điện thoại (168, 246, 360 px) trên nền bảng tin sáng
    và tối, có nhãn thời lượng giả ở góc phải dưới như YouTube; bản dọc ở 120 và 200 px."""
    from PIL import Image, ImageDraw
    ngang = [(n, im) for n, im, k in imgs if k == "ngang"]
    doc = [(n, im) for n, im, k in imgs if k != "ngang"]
    widths = [168, 246, 360]
    row_h = int(360 * 9 / 16) + 40
    W = 40 + (sum(widths) + 40 * len(widths)) * 2
    H = 40 + row_h * max(1, len(ngang)) + (380 if doc else 0)
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    d.rectangle([W // 2, 0, W, H], fill=(15, 15, 15))
    y = 30
    for name, im in ngang:
        for half, bg in ((0, (255, 255, 255)), (1, (15, 15, 15))):
            x = 30 + half * (W // 2)
            for w in widths:
                h = int(w * 9 / 16)
                t = im.resize((w, h), Image.LANCZOS)
                td = ImageDraw.Draw(t)
                bw, bh = max(24, int(w * 0.12)), max(12, int(w * 0.07))
                td.rounded_rectangle([w - bw - 4, h - bh - 4, w - 4, h - 4], radius=3, fill=(0, 0, 0))
                td.text((w - bw, h - bh - 3), "12:34", fill=(255, 255, 255))
                sheet.paste(t, (x, y))
                x += w + 40
        d.text((30, y + row_h - 34), name, fill=(90, 90, 90))
        y += row_h
    x = 30
    for name, im in doc:
        for w in (120, 200):
            t = im.resize((w, int(w * 16 / 9)), Image.LANCZOS)
            sheet.paste(t, (x, y))
            x += w + 30
        d.text((x - 250, y + 360), name, fill=(90, 90, 90))
    sheet.save(out, quality=90)


def tim_tep(folder, p):
    """Đường dẫn trong dang-tai.json: ưu tiên tương đối với thư mục gói (gói tự đủ trong Thanh pham/),
    rồi mới tới gốc repo (kiểu cũ)."""
    if not p:
        return None
    if os.path.isabs(p):
        return p
    for goc in (folder, ROOT):
        c = os.path.normpath(os.path.join(goc, p))
        if os.path.exists(c):
            return c
    return os.path.normpath(os.path.join(folder, p))


def cmd_kiem(folder):
    path = os.path.join(folder, "dang-tai.json")
    if not os.path.exists(path):
        sys.exit(f"Thiếu {path} (mẫu: skills/phim-dang-tai/references/mau-dang-tai.md)")
    d = json.load(open(path, encoding="utf-8"))
    loi, nhac = [], []
    tu_khoa = [k.lower() for k in d.get("tu_khoa", [])]
    if not tu_khoa:
        loi.append("dang-tai.json: thiếu \"tu_khoa\" (1-2 cụm từ khoá chính)")

    yt = d.get("youtube")
    if yt:
        tds = yt.get("tieu_de", [])
        if not tds:
            loi.append("YouTube: thiếu tiêu đề")
        for i, td in enumerate(tds, 1):
            ten = f"tiêu đề {i}"
            if len(td) > 100:
                loi.append(f"{ten}: {len(td)} ký tự, vượt 100")
            elif len(td) > 70:
                nhac.append(f"{ten}: {len(td)} ký tự, điện thoại có thể cắt sau khoảng 60-70 ký tự")
            if tu_khoa and not any(k in td[:70].lower() for k in tu_khoa):
                nhac.append(f"{ten}: từ khoá chính không nằm trong 70 ký tự đầu")
            if title_case(td):
                loi.append(f"{ten}: đang viết Title Case, dùng sentence case")
            if all_caps(td):
                loi.append(f"{ten}: viết hoa toàn bộ")
            van_ban_chung(ten, td, loi, nhac)
        mo_ta = yt.get("mo_ta", "")
        if not mo_ta:
            loi.append("YouTube: thiếu mô tả")
        else:
            if len(mo_ta) > 5000:
                loi.append(f"mô tả YouTube: {len(mo_ta)} ký tự, vượt 5000")
            nb = len(mo_ta.encode("utf-8"))
            if nb > 5000:
                nhac.append(f"mô tả YouTube: {nb} byte UTF-8; dán tay trong Studio thì được, qua API/công cụ lên lịch có thể bị cắt ở 5000 byte")
            dau = mo_ta.strip().split("\n")[0][:160].lower()
            if tu_khoa and not any(k in dau for k in tu_khoa):
                loi.append("mô tả YouTube: câu đầu (phần hiện trước \"Xem thêm\") chưa chứa từ khoá chính")
            kiem_chuong(mo_ta, loi, nhac, tim_tep(folder, d.get("chuong_file")))
            tags = re.findall(r"(?<![\w/])#[\wÀ-ỹ]+", mo_ta)
            if len(tags) > 3:
                nhac.append(f"mô tả YouTube: {len(tags)} hashtag; chỉ 3 cái đầu hiện trên tiêu đề, giữ 1-3")
            if "?" not in mo_ta:
                loi.append("mô tả YouTube: chưa có câu hỏi mở mời người xem chiêm nghiệm")
            if d.get("nhac_ccby") and d["nhac_ccby"] not in mo_ta:
                loi.append("mô tả YouTube: thiếu dòng ghi công nhạc CC-BY")
            for ten_ng in d.get("chuc_danh", []):
                if ten_ng not in mo_ta:
                    loi.append(f"mô tả YouTube: thiếu chức danh nguyên văn \"{ten_ng}\"")
            van_ban_chung("mô tả YouTube", mo_ta, loi, nhac)
        the = yt.get("the", [])
        tong = sum(len(t) + (2 if " " in t else 0) for t in the) + max(0, len(the) - 1)
        if tong > 500:
            loi.append(f"thẻ YouTube: {tong} ký tự, vượt 500")
        if len(the) > 15:
            nhac.append(f"thẻ YouTube: {len(the)} thẻ; thẻ đóng vai trò nhỏ, 5-12 thẻ là đủ")

    fb = d.get("facebook")
    if fb:
        st = fb.get("status", "")
        if not st:
            loi.append("Facebook: thiếu status")
        else:
            van_ban_chung("status Facebook", st, loi, nhac)
            if URL.search(st):
                nhac.append("status Facebook: có link trong thân bài; đặt link YouTube ở bình luận đầu, video tải thẳng lên Facebook")
            dong = [ln for ln in st.strip().splitlines() if ln.strip() and not ln.strip().startswith("#")]
            if dong and "?" not in dong[-1] and "?" not in " ".join(dong[-2:]):
                loi.append("status Facebook: chưa kết bằng một câu hỏi mở thật")
            if dong and len(dong[0]) > 140:
                nhac.append(f"status Facebook: dòng đầu {len(dong[0])} ký tự; điện thoại chỉ hiện chừng 2-3 dòng trước \"Xem thêm\"")
            ht = re.findall(r"(?<![\w/])#[\wÀ-ỹ]+", st)
            if len(ht) > 3:
                loi.append(f"status Facebook: {len(ht)} hashtag, giữ 0-3")
            for ten_ng in d.get("chuc_danh_fb", []):
                if ten_ng not in st:
                    loi.append(f"status Facebook: thiếu chức danh nguyên văn \"{ten_ng}\"")
        if fb.get("binh_luan_dau"):
            van_ban_chung("bình luận đầu", fb["binh_luan_dau"], loi, nhac)

    imgs = []
    for t in d.get("thumbnail", []):
        f = t["file"] if isinstance(t, dict) else t
        k = (t.get("khung") if isinstance(t, dict) else None) or ("doc" if "doc" in os.path.basename(f) else "ngang")
        im = kiem_anh(os.path.join(folder, f), k, loi, nhac)
        if im is not None:
            imgs.append((os.path.basename(f), im, k))
    if yt and not [1 for _, _, k in imgs if k == "ngang"]:
        loi.append("thumbnail: chưa có bản ngang 16:9 cho YouTube")
    if imgs:
        soi_thumbnail(imgs, os.path.join(folder, "soi-thumbnail.jpg"))

    ghi_md(folder, d)
    print(f"Gói đăng tải: {folder}")
    for n in nhac:
        print(f"  lưu ý: {n}")
    for e in loi:
        print(f"  ✗ {e}")
    if loi:
        print(f"KHÔNG ĐẠT ({len(loi)} lỗi). Sửa dang-tai.json rồi chạy lại.")
        sys.exit(1)
    print("ĐẠT" + (f" ({len(nhac)} lưu ý)" if nhac else "") + " - đã ghi DANG-TAI.md" +
          (" và soi-thumbnail.jpg (mở ra NHÌN trước khi báo anh)" if imgs else ""))


def ghi_md(folder, d):
    L = [f"# Gói đăng tải: {d.get('ten', os.path.basename(os.path.abspath(folder)))}", ""]
    if d.get("ghi_chu_kiem"):
        L += ["## Cần anh xem lại trước khi đăng", ""] + [f"- {x}" for x in d["ghi_chu_kiem"]] + [""]
    yt = d.get("youtube")
    if yt:
        L += ["## YouTube", "", "### Tiêu đề (chọn một; hai cái còn lại dùng cho thử nghiệm A/B)", ""]
        L += [f"{i}. {t}" for i, t in enumerate(yt.get("tieu_de", []), 1)] + [""]
        L += ["### Mô tả", "", "```", yt.get("mo_ta", "").strip(), "```", ""]
        if yt.get("the"):
            L += ["### Thẻ [tags]", "", "```", ", ".join(yt["the"]), "```", ""]
    fb = d.get("facebook")
    if fb:
        L += ["## Facebook", "", "### Status", "", "```", fb.get("status", "").strip(), "```", ""]
        if fb.get("binh_luan_dau"):
            L += ["### Bình luận đầu tiên", "", "```", fb["binh_luan_dau"].strip(), "```", ""]
        if fb.get("goi_y"):
            L += [f"- {x}" for x in fb["goi_y"]] + [""]
    th = d.get("thumbnail", [])
    if th:
        L += ["## Thumbnail", ""]
        for t in th:
            if isinstance(t, dict):
                L.append(f"- `{t['file']}`: {t.get('y_do', '')}")
            else:
                L.append(f"- `{t}`")
        L.append("")
    open(os.path.join(folder, "DANG-TAI.md"), "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("job", "kiem"):
        print(__doc__)
        sys.exit(2)
    cmd_job(sys.argv[2]) if sys.argv[1] == "job" else cmd_kiem(sys.argv[2])
