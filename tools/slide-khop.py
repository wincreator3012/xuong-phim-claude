#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KHỚP SLIDE với LỜI GIẢNG và đề xuất DÀN HÌNH (mặt / slide / cả hai) cho bài giảng có slide.

Đầu vào: du-an/<x>/slide/slide.json (từ slide-nguon.py) + transcript
         du-an/<x>/transcript/<clip>.transcript.json (từ transcribe.py).
Đầu ra:  du-an/<x>/slide/slide-khop.json  (mốc từng slide trong FILE NGUỒN + độ tin cậy)
         du-an/<x>/slide/DAN-HINH.md      (bảng đề xuất để user duyệt: mốc, slide, bố cục, lý do)
         du-an/<x>/slide/timeline-slide-nhap.json (đoạn segments nháp có layout/slide, Claude
                                                   chép vào timeline.json sau khi chỉnh)

Cách dùng (từ gốc "xuong-phim-claude"):
  python3 tools/slide-khop.py "du-an/<x>" --clip "<tên file nguồn không đuôi>"
      [--lech 12.5]   # quay màn hình bắt đầu TRỄ 12.5s so với quay mặt (mốc màn hình + lech = mốc mặt)
      [--bo-qua 1,2]  # slide không dùng (bìa, cảm ơn...)

Thuật toán khớp (khi không có mốc quay màn hình): mỗi slide → tập từ khoá (chữ trên slide +
ghi chú diễn giả); mỗi câu transcript → điểm trùng từ khoá với từng slide; quy hoạch động
ĐƠN ĐIỆU (slide đi theo thứ tự, mỗi slide chiếm một khối câu liên tiếp, có thể bỏ qua slide)
để tổng điểm lớn nhất. Độ tin cậy = tỉ lệ câu trong khối có trùng từ khoá. Slide tin cậy thấp
(< 0.35) được đánh dấu để Claude đọc transcript tự tay và user xác nhận.

Đề xuất bố cục theo quy tắc research-based (chi tiết trong skill phim-bai-giang-slide):
  - slide nhiều chữ / sơ đồ / số liệu (>= 40 từ hoặc có bảng) → "slide" (toàn khung, tránh chia chú ý)
  - slide vừa (12-39 từ) → "ca-hai" (slide chính, mặt nhỏ giữ kết nối xã hội)
  - slide ít chữ (< 12 từ: tiêu đề, trích dẫn, từ khoá, một hình) → "mat-chinh" (mặt chính, slide thẻ nhỏ)
  - quãng không có slide (dẫn nhập, kể chuyện, chuyển ý) → "mat"
  - "chia-doi" không tự đề xuất - Claude cân nhắc khi slide là hình ảnh/ảnh minh hoạ ít chữ
Mỗi khối ngắn hơn 6 giây được gộp vào khối kề để không đổi bố cục liên tục.
"""
import argparse
import json
import os
import re
import unicodedata

STOP = set("""và là của có không được cho với này đó thì mà các những một trong để khi rất cũng
như từ về ở nhiều hơn hay hoặc nhưng nếu vì bởi nên đã sẽ đang đến tới ra vào lên xuống lại còn
chỉ thôi nhé nha ạ à ơi thế vậy đây kia ấy nào gì ai đâu bao sao rồi mình chúng ta tôi anh chị em
bạn các bạn người việc điều cái con sự cách phần bài the a an of to and in for is are on with""".split())


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def tokens(s):
    """Trả về (tập từ đơn, tập cụm 2 từ). Tiếng Việt đơn âm tiết nên từ đơn dễ trùng ngẫu nhiên;
    cụm 2 từ là tín hiệu mạnh (thuật ngữ, tên khung). Không bỏ dấu - bỏ dấu gây trùng giả
    (nói/nối, thể/thế)."""
    s = (s or "").lower()
    toks = re.findall(r"\w+", s, flags=re.UNICODE)
    uni = {t for t in toks if len(t) >= 2 and t not in STOP and not t.isdigit()}
    bi = {f"{a} {b}" for a, b in zip(toks, toks[1:]) if a not in STOP and b not in STOP}
    return uni, bi


def load_segments(project, clip):
    p = os.path.join(project, "transcript", f"{clip}.transcript.json")
    data = json.load(open(p, encoding="utf-8"))
    segs = data if isinstance(data, list) else data.get("segments", [])
    return [s for s in segs if "start" in s and "end" in s and s.get("text", "").strip()]


def align(real_slides, segs):
    """DP đơn điệu. Trả về dict slide_n → (a, b) chỉ số câu [a, b) hoặc None nếu bỏ qua.
    Giữa các slide có "khoảng trống" (câu không thuộc slide nào: dẫn nhập, kể chuyện) -
    mô hình bằng slide giả điểm 0 xen kẽ, để khối slide không phình ra nuốt cả lời dẫn."""
    slides = []
    for s in real_slides:
        slides.append({"n": None, "_gap": True})
        slides.append(s)
    slides.append({"n": None, "_gap": True})
    n, m = len(slides), len(segs)
    kw = [(set(), set()) if s.get("_gap") else tokens((s.get("text") or "") + "\n" + (s.get("notes") or ""))
          for s in slides]
    seg_tok = [tokens(s["text"]) for s in segs]
    # điểm câu j với slide i: từ đơn trùng x1, cụm 2 từ trùng x3; chỉ tính là "trúng" khi có
    # >= 1 cụm hoặc >= 2 từ đơn (một từ đơn trùng là ngẫu nhiên). Câu không trúng: phạt nhẹ
    # để khối slide không phình ra nuốt lời dẫn (khoảng trống điểm 0 sẽ thắng).
    score = [[0.0] * m for _ in range(n)]
    for i in range(n):
        uni, bi = kw[i]
        if not uni and not bi:
            continue
        norm = max(4.0, (len(uni) + 3 * len(bi)) ** 0.5)
        for j in range(m):
            u = len(uni & seg_tok[j][0])
            b = len(bi & seg_tok[j][1])
            val = (u + 3 * b) / norm
            score[i][j] = val if (b >= 1 or u >= 2) and val >= 0.3 else -0.25
    # prefix
    P = [[0.0] * (m + 1) for _ in range(n)]
    for i in range(n):
        for j in range(m):
            P[i][j + 1] = P[i][j] + score[i][j]
    NEG = float("-inf")
    # DP[i][b]: điểm tốt nhất khi đã xét slide 0..i-1 và ranh giới hiện tại ở câu b
    DP = [[NEG] * (m + 1) for _ in range(n + 1)]
    choice = [[None] * (m + 1) for _ in range(n + 1)]   # (a, skipped)
    DP[0][0] = 0.0
    for i in range(1, n + 1):
        SKIP = 0.0 if slides[i - 1].get("_gap") else -0.3
        # bỏ qua slide i-1
        for b in range(m + 1):
            if DP[i - 1][b] > NEG:
                v = DP[i - 1][b] + SKIP
                if v > DP[i][b]:
                    DP[i][b], choice[i][b] = v, (b, True)
        # nhận khối [a, b)
        best, best_a = NEG, -1
        for b in range(m + 1):
            if DP[i - 1][b] > NEG:
                cand = DP[i - 1][b] - P[i - 1][b]
                if cand > best:
                    best, best_a = cand, b
            if best > NEG and b > best_a:
                v = best + P[i - 1][b]
                if v > DP[i][b]:
                    DP[i][b], choice[i][b] = v, (best_a, False)
    # truy vết từ (n, m)
    res, real_score = {}, {}
    i, b = n, m
    while i > 0:
        a, skipped = choice[i][b]
        if not slides[i - 1].get("_gap"):
            res[slides[i - 1]["n"]] = None if skipped else (a, b)
            real_score[slides[i - 1]["n"]] = score[i - 1]
        i, b = i - 1, a
    return res, real_score


def layout_for(slide):
    t = (slide.get("text") or "")
    w = slide.get("so_tu", 0) or len(re.findall(r"\w+", t))
    if w == 0:
        return "ca-hai", "không đọc được chữ (ảnh/quay màn hình) - Claude XEM ảnh slide rồi chọn bố cục"
    if "|" in t or w >= 40:
        return "slide", f"{w} từ, nội dung dày - cho slide toàn khung để người học đọc được"
    if w >= 12:
        return "ca-hai", f"{w} từ, mức vừa - slide chính, mặt nhỏ giữ kết nối"
    return "mat-chinh", f"{w} từ, slide chỉ là điểm nhấn - mặt chính, slide thẻ nhỏ"


def fmt(t):
    return f"{int(t // 60):02d}:{t % 60:04.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--clip", required=True, help="tên file nguồn không đuôi (khớp transcript/<clip>.transcript.json)")
    ap.add_argument("--lech", type=float, default=0.0, help="mốc quay màn hình + lech = mốc file quay mặt")
    ap.add_argument("--bo-qua", default="", help="số thứ tự slide bỏ qua, cách nhau bằng dấu phẩy")
    ap.add_argument("--min-khoi", type=float, default=6.0, help="khối ngắn hơn (giây) thì gộp vào khối kề")
    args = ap.parse_args()

    sdir = os.path.join(args.project, "slide")
    meta = json.load(open(os.path.join(sdir, "slide.json"), encoding="utf-8"))
    skip = {int(x) for x in args.bo_qua.split(",") if x.strip()}
    slides = [s for s in meta["slides"] if s["n"] not in skip]
    segs = load_segments(args.project, args.clip)
    total = segs[-1]["end"] if segs else 0

    blocks = []  # {slide, start, end, conf, cach}
    if all("ts" in s for s in slides) and slides:
        # có mốc từ quay màn hình → dùng thẳng
        for k, s in enumerate(slides):
            start = s["ts"] + args.lech
            end = (slides[k + 1]["ts"] + args.lech) if k + 1 < len(slides) else total
            blocks.append({"slide": s["n"], "file": s["file"], "start": round(max(0, start), 2),
                           "end": round(end, 2), "conf": 1.0, "cach": "mốc quay màn hình"})
    else:
        res, score = align(slides, segs)
        for s in slides:
            r = res.get(s["n"])
            if not r:
                blocks.append({"slide": s["n"], "file": s["file"], "start": None, "end": None,
                               "conf": 0.0, "cach": "KHÔNG khớp được - đọc transcript tự đặt hoặc bỏ"})
                continue
            a, b = r
            hits = sum(1 for j in range(a, b) if score[s["n"]][j] > 0)
            conf = hits / max(1, b - a)
            blocks.append({"slide": s["n"], "file": s["file"], "start": round(segs[a]["start"], 2),
                           "end": round(segs[b - 1]["end"], 2), "conf": round(conf, 2),
                           "cach": f"khớp từ khoá {hits}/{b - a} câu",
                           "cau_dau": segs[a]["text"][:80]})

    # Gộp khối quá ngắn vào khối trước (giữ slide của khối dài hơn)
    placed = [b for b in blocks if b["start"] is not None]
    merged = []
    for b in placed:
        if merged and (b["end"] - b["start"]) < args.min_khoi:
            merged[-1]["end"] = b["end"]
            merged[-1]["gop"] = merged[-1].get("gop", []) + [b["slide"]]
        else:
            merged.append(dict(b))

    # Dàn hình nháp: xen "mat" vào các quãng trống
    by_n = {s["n"]: s for s in slides}
    plan = []
    cur = 0.0
    for b in merged:
        if b["start"] - cur >= args.min_khoi:
            plan.append({"in": round(cur, 2), "out": b["start"], "layout": "mat", "slide": None,
                         "ly_do": "không có slide - lời dẫn/kể chuyện, giữ kết nối mắt"})
        lay, why = layout_for(by_n[b["slide"]])
        plan.append({"in": b["start"], "out": b["end"], "layout": lay, "slide": f"slide/{b['file']}",
                     "ly_do": why, "conf": b["conf"], "gop": b.get("gop")})
        cur = b["end"]
    if total - cur >= args.min_khoi:
        plan.append({"in": round(cur, 2), "out": round(total, 2), "layout": "mat", "slide": None,
                     "ly_do": "kết bài, không slide"})

    json.dump({"clip": args.clip, "lech": args.lech, "khoi": blocks, "dan_hinh": plan},
              open(os.path.join(sdir, "slide-khop.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # timeline nháp
    tl_segs = []
    for p in plan:
        seg = {"type": "video", "src": f"nguon/{args.clip}.mp4", "in": p["in"], "out": p["out"],
               "snap": True, "layout": p["layout"]}
        if p["slide"]:
            seg["slide"] = p["slide"]
        tl_segs.append(seg)
    json.dump({"_ghi_chu": "NHÁP do slide-khop.py sinh - Claude chỉnh theo DAN-HINH.md đã duyệt rồi "
                           "chép vào timeline.json (kiểm lại đuôi file nguồn .mp4/.MP4/.mov)",
               "aspect": "ngang", "fps": 30, "segments": tl_segs},
              open(os.path.join(sdir, "timeline-slide-nhap.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # bảng duyệt
    lines = [f"# Dàn hình đề xuất - {args.clip}", "",
             "Mốc theo FILE NGUỒN (trước khi snap). Bố cục: mat = mặt toàn khung; slide = slide toàn khung; "
             "ca-hai = slide chính + mặt nhỏ; mat-chinh = mặt chính + slide thẻ nhỏ; chia-doi = cân bằng.",
             "Độ tin cậy < 0.35 → cần đọc transcript xác nhận tay.", "",
             "| # | Mốc | Dài | Slide | Bố cục | Tin cậy | Lý do |", "|---|---|---|---|---|---|---|"]
    for i, p in enumerate(plan, 1):
        conf = "" if p.get("conf") is None else (f"{p['conf']:.2f}" + (" ⚠" if p["conf"] < 0.35 else ""))
        sl = (p["slide"] or "-").replace("slide/", "") + (f" (+{p['gop']})" if p.get("gop") else "")
        lines.append(f"| {i} | {fmt(p['in'])} - {fmt(p['out'])} | {p['out'] - p['in']:.0f}s | {sl} | "
                     f"{p['layout']} | {conf} | {p['ly_do']} |")
    unplaced = [b for b in blocks if b["start"] is None]
    if unplaced:
        lines += ["", "Slide KHÔNG khớp được (cân nhắc bỏ hoặc đặt tay): " +
                  ", ".join(str(b["slide"]) for b in unplaced)]
    with open(os.path.join(sdir, "DAN-HINH.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n✓ slide-khop.json, DAN-HINH.md, timeline-slide-nhap.json → {sdir}/")


if __name__ == "__main__":
    main()
