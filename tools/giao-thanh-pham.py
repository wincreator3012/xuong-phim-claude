#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GIAO TRỌN GÓI thành phẩm của một dự án vào thư mục giao (thuMucGiao, vd thư mục đồng bộ Google Drive).

Chạy SAU KHI anh nói "duyệt". Không xoá gì ở nguồn.

    python3 tools/giao-thanh-pham.py "2026-10 Ten du an"            # xem trước (mặc định)
    python3 tools/giao-thanh-pham.py "2026-10 Ten du an" --ghi      # chép thật
    ... --ghi --gioi-han-giay 150      # dừng êm sau 150 giây, chạy lại để chép tiếp (bỏ qua file đã đủ)
    ... --ghi --chi "Short 05"         # chỉ một thư mục con

Kết quả: <thuMucGiao>/<dự án>/ gồm mỗi thư mục thành phẩm con (00 Video day du, Short NN <slug>) CHÉP NGUYÊN:
video, file nghiệm thu, dang-tai/ (nội dung đăng tải, thumbnail, khung) và thêm transcript/ của nguồn:
  - 00 Video day du/transcript/: gỡ băng cả buổi (large-v3 nếu có, và bản nhanh), dạng srt, txt, json
  - Short NN <slug>/transcript/: phu-de.srt (phụ đề đã burn, theo giờ clip), loi-noi.txt (chữ lời nói trong clip),
    trich-nguon.txt (gỡ băng nguồn của đúng các quãng đã dùng, giờ trục nguồn)
Cuối cùng ghi MUC-LUC.md ở thư mục dự án.
"""
import argparse, json, os, re, shutil, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cau_hinh as CH


def kich_thuoc(p):
    t = 0
    for r, _, fs in os.walk(p):
        for f in fs:
            t += os.path.getsize(os.path.join(r, f))
    return t


def doc_srt(p):
    s = open(p, encoding="utf-8").read().replace("\r", "")
    out = []
    for kh in re.split(r"\n\s*\n", s.strip()):
        ls = kh.split("\n")
        if len(ls) < 3:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", ls[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        out.append((a, b, " ".join(ls[2:]).strip()))
    return out


def gio(t, ms=True):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}" if ms else f"{h:02d}:{m:02d}:{int(s):02d}"


def ass_sang_srt(p):
    cues = []
    for l in open(p, encoding="utf-8"):
        if not l.startswith("Dialogue:"):
            continue
        f = l.rstrip("\n").split(",", 9)
        def t(x):
            h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
        cues.append((t(f[1]), t(f[2]), f[9].replace("\\N", "\n").replace("\\n", "\n")))
    cues.sort()
    return cues


def ghi_srt(cues):
    r = []
    for i, (a, b, tx) in enumerate(cues, 1):
        r.append(f"{i}\n{gio(a).replace('.', ',')} --> {gio(b).replace('.', ',')}\n{tx}\n")
    return "\n".join(r)


def chep(src, dst, ghi, han):
    """chép một file nếu chưa đủ (cùng cỡ). Trả về (đã chép, byte, hết giờ)"""
    if os.path.isfile(dst) and os.path.getsize(dst) == os.path.getsize(src):
        return False, 0, False
    if han and time.time() > han:
        return False, 0, True
    n = os.path.getsize(src)
    if ghi:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tam = dst + ".dang-chep"
        shutil.copyfile(src, tam)
        if os.path.getsize(tam) != n:
            os.remove(tam) if os.access(tam, os.W_OK) else None
            raise IOError("chép lỗi (khác cỡ): " + src)
        os.replace(tam, dst)
    return True, n, False


def ghi_van_ban(dst, nd, ghi):
    if os.path.isfile(dst) and open(dst, encoding="utf-8").read() == nd:
        return False
    if ghi:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "w", encoding="utf-8").write(nd)
    return True


def srt_nguon(da):
    for ten in ("transcript-large-v3", "transcript"):
        d = os.path.join(da, ten)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".srt"):
                    return os.path.join(d, f)
    return None


def van_ban_transcript_dai(da):
    """(tên đích, file nguồn) các file gỡ băng đáng giao của cả buổi"""
    out = []
    for ten, nhan in (("transcript-large-v3", "large-v3"), ("transcript", "ban-nhanh")):
        d = os.path.join(da, ten)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith((".srt", ".txt", ".transcript.json", ".tu.json")) and not f.startswith("_") and "khuc" not in f and "silences" not in f:
                out.append((f"{nhan}/{f}", os.path.join(d, f)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("du_an", help='tên thư mục dự án, vd "2026-10 Ten du an"')
    ap.add_argument("--ghi", action="store_true", help="chép thật (mặc định chỉ xem trước)")
    ap.add_argument("--chi", help="chỉ thư mục con có tên chứa chuỗi này")
    ap.add_argument("--gioi-han-giay", type=int, default=0, help="dừng êm sau N giây (chạy lại để chép tiếp)")
    a = ap.parse_args()

    giao = CH.giao()
    if not giao:
        sys.exit('Chưa có "thuMucGiao" trong cau-hinh.json (đường dẫn thư mục giao, vd ../../Thanh pham giao).')
    if not os.path.isdir(giao):
        sys.exit("Thư mục giao chưa có hoặc chưa gắn vào phiên: " + giao)
    nguon = os.path.join(CH.thanh_pham(), a.du_an)
    da = os.path.join(CH.du_an(), a.du_an)
    if not os.path.isdir(nguon):
        sys.exit("Không thấy thành phẩm: " + nguon)
    dich = os.path.join(giao, a.du_an)
    han = time.time() + a.gioi_han_giay if a.gioi_han_giay else None
    srt_goc = srt_nguon(da) if os.path.isdir(da) else None
    goc = doc_srt(srt_goc) if srt_goc else []
    print(("GHI" if a.ghi else "XEM TRƯỚC"), "|", nguon, "->", dich)

    tong, hetgio, muc = 0, False, []
    for ten in sorted(os.listdir(nguon)):
        sp = os.path.join(nguon, ten)
        if not os.path.isdir(sp) or (a.chi and a.chi not in ten):
            continue
        n_file, n_byte = 0, 0
        for r, ds, fs in os.walk(sp):
            ds[:] = [d for d in ds if d != "transcript"]
            for f in sorted(fs):
                s = os.path.join(r, f)
                d = os.path.join(dich, ten, os.path.relpath(s, sp))
                ok, n, het = chep(s, d, a.ghi, han)
                hetgio |= het
                if ok:
                    n_file += 1; n_byte += n
        # transcript
        tr = os.path.join(dich, ten, "transcript")
        ghi_t = 0
        if ten.startswith("00 "):
            for dt, s in van_ban_transcript_dai(da) if os.path.isdir(da) else []:
                ok, n, het = chep(s, os.path.join(tr, dt), a.ghi, han)
                hetgio |= het
                if ok:
                    ghi_t += 1; n_byte += n
        else:
            m = re.match(r"Short \d+ (.+)$", ten)
            slug = m.group(1) if m else None
            ass = os.path.join(da, "clip-ngan", slug or "_", "phu-de", f"{slug}-doc.ass")
            mp = os.path.join(da, "xuat-nhap", f"{slug}-doc.map.json")
            if slug and os.path.isfile(ass):
                cues = ass_sang_srt(ass)
                ghi_t += ghi_van_ban(os.path.join(tr, "phu-de.srt"), ghi_srt(cues), a.ghi)
                ghi_t += ghi_van_ban(os.path.join(tr, "loi-noi.txt"), "\n".join(c[2].replace("\n", " ") for c in cues) + "\n", a.ghi)
            if slug and os.path.isfile(mp) and goc:
                parts = [p for p in json.load(open(mp, encoding="utf-8"))["parts"] if p.get("kind") == "cut" and p.get("audio_in") is not None]
                dong = ["Gỡ băng của nguồn cho đúng các quãng đã dùng trong clip (giờ theo trục nguồn của cả buổi; clip có thể bỏ ngập ngừng nên chữ phụ đề đã chỉnh lại).", ""]
                for p in parts:
                    a0 = p["audio_in"]; b0 = a0 + p["dur"]
                    dong.append(f"== Trong clip {gio(p['start'], False)} - {gio(p['end'], False)} | nguồn {gio(a0, False)} - {gio(b0, False)} ==")
                    for x, y, tx in goc:
                        if y > a0 and x < b0:
                            dong.append(f"[{gio(x)}] {tx}")
                    dong.append("")
                ghi_t += ghi_van_ban(os.path.join(tr, "trich-nguon.txt"), "\n".join(dong), a.ghi)
        tong += n_byte
        ten_hien = ""
        dj = os.path.join(sp, "dang-tai", "dang-tai.json")
        if os.path.isfile(dj):
            try:
                ten_hien = json.load(open(dj, encoding="utf-8")).get("ten", "")
            except ValueError:
                pass
        muc.append((ten, ten_hien))
        print(f"  {ten}: {n_file} file cần chép ({n_byte/1e6:.1f} MB), transcript {ghi_t} tệp mới/đổi")

    if a.ghi and not hetgio and not a.chi:
        md = [f"# {a.du_an}: mục lục thành phẩm", "",
              "Mỗi thư mục con tự đủ: video hoàn chỉnh, file nghiệm thu, `dang-tai/` (tiêu đề, mô tả, status, thumbnail), `transcript/` của nguồn.", ""]
        for t, h in muc:
            md.append(f"- `{t}`" + (f": {h}" if h else ""))
        ghi_van_ban(os.path.join(dich, "MUC-LUC.md"), "\n".join(md) + "\n", True)
    print(f"Tổng cần/đã chép {tong/1e6:.1f} MB" + (" | HẾT GIỜ, chạy lại lệnh để chép tiếp" if hetgio else ""))
    if not a.ghi:
        print("(xem trước, chưa chép gì; thêm --ghi để chép thật)")


if __name__ == "__main__":
    main()
